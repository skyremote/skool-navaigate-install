"""One local SQLite file, including its derived FTS5 index. Python 3.9+."""
import contextlib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path

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
        conn.execute('INSERT OR REPLACE INTO failures VALUES(?,?,?)', (scope, message, time.time()))


def clear_failure(conn, scope):
    with conn:
        conn.execute('DELETE FROM failures WHERE scope=?', (scope,))


def put_item(conn, item, documents):
    """All messages and index changes precede the real hash, in one transaction."""
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
        raise ValueError('Unknown ref. Run brain search first.')
    docs = [dict(d) for d in conn.execute('SELECT * FROM documents WHERE ref=? ORDER BY id',(ref,))]
    return {'item':dict(row), 'documents':docs}


def serialise(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',',':'))
