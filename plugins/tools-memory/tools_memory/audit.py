"""Before a database is shared between machines: is it safe to share, and where will two machines collide?"""
import os
import shutil
import socket
import sqlite3
from pathlib import Path

CLOUD = ('CloudStorage', 'Google Drive', 'My Drive', 'Dropbox', 'OneDrive', 'Library/Mobile Documents', 'iCloud',
         'SynologyDrive', 'Box Sync', 'pCloud')
PASTE_PORT = 39725


def in_cloud_folder(path):
    text = str(Path(path).expanduser().resolve())
    return next((n for n in CLOUD if n in text), '')


def is_sqlite(path):
    path = Path(path).expanduser()
    if not path.is_file():
        return False
    with open(path, 'rb') as handle:
        return handle.read(16) == b'SQLite format 3\x00'


def audit(path):
    """Return (problems, notes) for one database file. Opens it read-only."""
    path = Path(path).expanduser()
    problems, notes = [], []
    if not is_sqlite(path):
        return ['%s is not a SQLite database file.' % path], notes
    folder = in_cloud_folder(path)
    if folder:
        problems.append('It sits inside a file-sync folder (%s). File sync corrupts a live database: move it out first.' % folder)
    for suffix in ('-wal', '-journal'):
        if Path(str(path) + suffix).exists():
            notes.append('A %s file is next to it: an app has it open. Close the app before seeding the copy.' % suffix)
    con = sqlite3.connect('file:%s?mode=ro' % path, uri=True)
    try:
        notes.append('Journal mode: ' + con.execute('PRAGMA journal_mode').fetchone()[0])
        tables = con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        notes.append('%d table(s).' % len(tables))
        for name, sql in tables:
            sql = (sql or '').upper()
            columns = con.execute('PRAGMA table_info("%s")' % name.replace('"', '""')).fetchall()
            integer_key = [c[1] for c in columns if c[5] and 'INT' in (c[2] or '').upper()]
            if 'AUTOINCREMENT' in sql or (integer_key and len([c for c in columns if c[5]]) == 1):
                problems.append('Table "%s" numbers its rows itself (%s). Two machines adding rows at once can pick the '
                                'same number: give new rows a ULID or UUIDv7 id made on the machine.' % (name, integer_key[0] if integer_key else 'rowid'))
    finally:
        con.close()
    return problems, notes


def paste_running(port=PASTE_PORT, host='127.0.0.1'):
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def installed(home=None):
    home = Path(home or Path.home())
    skills = [home / d for d in ('.claude/skills', '.agents/skills', '.codex/skills')]
    return {'turso': bool(shutil.which('turso')),
            'db-sync': any((s / 'db-sync/SKILL.md').is_file() for s in skills),
            'rich-clipboard': any((s / 'rich-clipboard/SKILL.md').is_file() for s in skills),
            'paste': paste_running()}


def env_file_private(path=None):
    path = Path(path or Path.home() / '.config/db-sync/db-sync.env')
    if not path.exists():
        return None
    return not (os.stat(path).st_mode & 0o077)
