"""tools-memory: share any app's SQLite database between your machines on your own Turso, and recall what you copied."""
import argparse
import sqlite3
import sys
from pathlib import Path

from . import __version__, audit

INSTALL = {
    'turso': 'brew install tursodatabase/tap/turso (Mac) or curl -sSfL https://get.tur.so/install.sh | bash, then turso auth signup',
    'db-sync': 'git clone https://github.com/skyremote/db-sync ~/.claude/skills/db-sync',
    'rich-clipboard': 'git clone https://github.com/skyremote/rich-clipboard-skill ~/.claude/skills/rich-clipboard',
    'paste': 'Install Paste (pasteapp.io), then Settings, turn on its MCP server; add http://127.0.0.1:39725/mcp to your harness',
}


def doctor(_args):
    print('tools-memory ' + __version__)
    print('Your chats and notes: that is the aios-brain pack (module 5). This pack is for app databases and the clipboard.')
    state = audit.installed()
    for name, ok in state.items():
        print('%-15s %s' % (name, 'ready' if ok else 'not set up. ' + INSTALL[name]))
    private = audit.env_file_private()
    if private is False:
        print('WARNING: ~/.config/db-sync/db-sync.env can be read by others. Run: chmod 600 ~/.config/db-sync/db-sync.env')
        return 1
    return 0 if state['turso'] and state['db-sync'] else 2


def check(args):
    problems, notes = audit.audit(args.database)
    for note in notes:
        print('  ' + note)
    if problems:
        print('NOT READY to share: %d thing(s) to fix first' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('READY to share: outside file-sync folders, and no table numbers its own rows.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    risky = folder / 'acme-orders_v1.db'
    safe = folder / 'acme-orders_v2.db'
    for path in (risky, safe):
        if path.exists():
            path.unlink()
    con = sqlite3.connect(risky)
    con.executescript('CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, cake TEXT);'
                      "INSERT INTO orders (customer, cake) VALUES ('Northwind Bakery', 'Lemon sponge');")
    con.close()
    con = sqlite3.connect(safe)
    con.executescript('CREATE TABLE orders (id TEXT PRIMARY KEY, customer TEXT, cake TEXT);'
                      "INSERT INTO orders VALUES ('01JBR8Z4Q4N2S8W0T6YH3K9M7C', 'Northwind Bakery', 'Lemon sponge');")
    con.close()
    print('Two practice databases for the fictional Acme Studio:')
    print('  %s  (numbers its own rows: not ready to share)' % risky)
    print('  %s  (ids made on the machine: ready)' % safe)
    print('Next: tools-memory check %s' % risky)
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-memory', description=__doc__)
    p.add_argument('--version', action='version', version='tools-memory ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Turso, db-sync, Paste and rich-clipboard').set_defaults(run=doctor)
    s = sub.add_parser('check', help='is this database safe to share between machines? (read-only)')
    s.add_argument('database')
    s.set_defaults(run=check)
    s = sub.add_parser('sample', help='two practice databases')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except sqlite3.DatabaseError as error:
        print('Could not read the database: %s' % error, file=sys.stderr)
        return 1
