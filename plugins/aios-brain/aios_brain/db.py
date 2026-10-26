"""One local SQLite file, including its derived FTS5 index. Python 3.9+."""
import contextlib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from .errors import InputError
from .privacy import redact

SCHEMA = '''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS items(
 ref TEXT PRIMARY KEY, source TEXT NOT NULL, device TEXT NOT NULL,
 path TEXT, file_hash TEXT NOT NULL, modified REAL NOT NULL,
 latest REAL NOT NULL, updated REAL NOT NULL, title TEXT NOT NULL DEFAULT '',
 url TEXT, digest TEXT);
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY, ref TEXT NOT NULL REFERENCES items(ref) ON DELETE CASCADE,
 kind TEXT NOT NULL, role TEXT NOT NULL, body TEXT NOT NULL, ts REAL NOT NULL);
CREATE INDEX IF NOT EXISTS documents_ref ON documents(ref);
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
 body, content=documents, content_rowid=rowid, tokenize='unicode61');
CREATE TRIGGER IF NOT EXISTS doc_insert AFTER INSERT ON documents BEGIN
 INSERT INTO search_index(rowid,body) VALUES(new.rowid,new.body); END;
CREATE TRIGGER IF NOT EXISTS doc_delete AFTER DELETE ON documents BEGIN
 INSERT INTO search_index(search_index,rowid,body) VALUES('delete',old.rowid,old.body); END;
CREATE TRIGGER IF NOT EXISTS doc_update AFTER UPDATE ON documents BEGIN
 INSERT INTO search_index(search_index,rowid,body) VALUES('delete',old.rowid,old.body);
 INSERT INTO search_index(rowid,body) VALUES(new.rowid,new.body); END;
CREATE TABLE IF NOT EXISTS file_state(
 path TEXT PRIMARY KEY, ref TEXT NOT NULL, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
 file_hash TEXT NOT NULL, message_hash TEXT NOT NULL, warnings TEXT NOT NULL DEFAULT '[]');
CREATE TABLE IF NOT EXISTS health_pending(path TEXT PRIMARY KEY,since REAL NOT NULL);
CREATE TABLE IF NOT EXISTS failures(
 scope TEXT PRIMARY KEY, message TEXT NOT NULL, at REAL NOT NULL);
'''


def data_path():
    return Path.home() / '.local/share/aios-brain/brain.db'


def connect(create=False):
    path = data_path()
    if not create and not path.exists():
        raise ValueError('Brain is not initialised. Run: brain init')
    if create:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    # Rollback journal leaves just one database file when idle.
    conn.execute('PRAGMA journal_mode=DELETE')
    if create:
        conn.executescript(SCHEMA)
        conn.execute('INSERT OR IGNORE INTO meta VALUES(?,?)', ('device', uuid.uuid4().hex[:12]))
        conn.execute('INSERT OR IGNORE INTO meta VALUES(?,?)', ('schema_version', '1'))
        conn.commit()
    # Add local-only cache tables to existing phase-1 databases too.
    conn.executescript(SCHEMA)
    if not conn.execute("SELECT 1 FROM meta WHERE key='redaction_version'").fetchone():
        with conn:
            for row in conn.execute('SELECT id,body FROM documents').fetchall():
                body=redact(row['body'])
                if body!=row['body']:
                    conn.execute('UPDATE documents SET body=? WHERE id=?',(body,row['id']))
                    conn.execute('UPDATE items SET updated=max(updated+0.000001,?) WHERE ref=(SELECT ref FROM documents WHERE id=?)',(time.time(),row['id']))
            for row in conn.execute('SELECT ref,title,digest FROM items').fetchall():
                title,digest=redact(row['title']),redact(row['digest'])
                if (title,digest)!=(row['title'],row['digest']):
                    conn.execute('UPDATE items SET title=?,digest=?,updated=max(updated+0.000001,?) WHERE ref=?',(title,digest,time.time(),row['ref']))
            for row in conn.execute('SELECT scope,message FROM failures').fetchall():
                message=('Previous invalid-header transport failure; check the token privately and acknowledge this row'
                         if 'invalid header value' in row['message'].lower() else redact(row['message']))
                conn.execute('UPDATE failures SET message=? WHERE scope=?',(message,row['scope']))
            conn.execute("INSERT OR REPLACE INTO meta VALUES('redaction_version','1')")
    os.chmod(path, 0o600)
    return conn


@contextlib.contextmanager
def database(create=False):
    conn = connect(create)
    try:
        yield conn
    finally:
        conn.close()


def device(conn):
    return conn.execute("SELECT value FROM meta WHERE key='device'").fetchone()[0]


def failure(conn, scope, message):
    with conn:
        conn.execute('INSERT OR REPLACE INTO failures VALUES(?,?,?)', (scope, redact(message), time.time()))


def clear_failure(conn, scope):
    with conn:
        conn.execute('DELETE FROM failures WHERE scope=?', (scope,))


def put_item(conn, item, documents):
    """All messages and index changes precede the real hash, in one transaction."""
    item=dict(item)
    documents=[dict(d,body=redact(d['body'])) for d in documents]
    item['title']=redact(item.get('title') or '')
    item['digest']=redact(item.get('digest'))
    fields = ('ref','source','device','path','file_hash','modified','latest','updated','title','url','digest')
    with conn:
        conn.execute('INSERT OR IGNORE INTO items(ref,source,device,file_hash,modified,latest,updated) '
                     'VALUES(?,?,?,\'pending\',0,0,0)', (item['ref'],item['source'],item['device']))
        conn.execute('DELETE FROM documents WHERE ref=?', (item['ref'],))
        conn.executemany('INSERT INTO documents(id,ref,kind,role,body,ts) VALUES(?,?,?,?,?,?)',
                         [(d['id'],item['ref'],d['kind'],d['role'],d['body'],d['ts']) for d in documents])
        conn.execute('UPDATE items SET ' + ','.join(f'{k}=?' for k in fields[1:]) + ' WHERE ref=?',
                     [item.get(k) for k in fields[1:]] + [item['ref']])
        stored = conn.execute('SELECT file_hash FROM items WHERE ref=?',(item['ref'],)).fetchone()[0]
        count = conn.execute('SELECT count(*) FROM documents WHERE ref=?',(item['ref'],)).fetchone()[0]
        if stored != item['file_hash'] or count != len(documents):
            raise ValueError('Capture read-back failed')


def bundle(conn, ref):
    row = conn.execute('SELECT * FROM items WHERE ref=?',(ref,)).fetchone()
    if not row:
        raise InputError('Unknown ref. Run brain search first.')
    docs = [dict(d) for d in conn.execute('SELECT * FROM documents WHERE ref=? ORDER BY id',(ref,))]
    return {'item':dict(row), 'documents':docs}


def serialise(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',',':'))


def prune_failures(conn):
    """Expired files and invalid old requests are not permanent failures."""
    from .media import canonical_url
    rows=conn.execute('SELECT scope FROM failures').fetchall()
    with conn:
        for row in rows:
            scope=row['scope']
            gone=scope.startswith('capture:') and not Path(scope[8:]).exists()
            if scope.startswith('digest:'):
                gone=not conn.execute('SELECT 1 FROM items WHERE ref=?',(scope[7:],)).fetchone()
            if scope.startswith('media:'):
                try:
                    canonical=canonical_url(scope[6:])[0]
                except InputError:
                    gone=True
                else:
                    if canonical!=scope[6:]:
                        conn.execute('INSERT OR IGNORE INTO failures SELECT ?,message,at FROM failures WHERE scope=?',('media:'+canonical,scope))
                        gone=True
            if gone:
                conn.execute('DELETE FROM failures WHERE scope=?',(scope,))


def next_version(previous=0):
    """Keep local edits newer than a known remote version despite clock skew."""
    return max(time.time(),float(previous)+0.000001)
