"""Unit tests for tools-memory. Local only."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-memory'
sys.path.insert(0, str(PACK))

from tools_memory import audit  # noqa: E402


def db(path, sql):
    con = sqlite3.connect(path)
    con.executescript(sql)
    con.close()
    return path


class Audit(unittest.TestCase):
    def test_cloud_folders(self):
        self.assertEqual(audit.in_cloud_folder('/Users/x/Library/CloudStorage/Dropbox/a.db'), 'CloudStorage')
        self.assertEqual(audit.in_cloud_folder('/Users/x/Library/Mobile Documents/com~apple~CloudDocs/a.db'), 'Library/Mobile Documents')
        self.assertEqual(audit.in_cloud_folder('/tmp/a.db'), '')

    def test_row_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            auto = db(Path(tmp) / 'a.db', 'CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, x TEXT);')
            plain = db(Path(tmp) / 'b.db', 'CREATE TABLE t (id INTEGER PRIMARY KEY, x TEXT);')
            text = db(Path(tmp) / 'c.db', 'CREATE TABLE t (id TEXT PRIMARY KEY, x TEXT); CREATE TABLE j (a TEXT, b TEXT, PRIMARY KEY (a, b));')
            self.assertEqual(len(audit.audit(auto)[0]), 1)
            self.assertEqual(len(audit.audit(plain)[0]), 1)
            self.assertEqual(audit.audit(text)[0], [])

    def test_not_sqlite_and_open_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / 'x.db'
            junk.write_text('hello')
            self.assertIn('not a SQLite', audit.audit(junk)[0][0])
            good = db(Path(tmp) / 'g.db', 'CREATE TABLE t (id TEXT PRIMARY KEY);')
            Path(str(good) + '-wal').write_text('')
            self.assertTrue(any('-wal' in n for n in audit.audit(good)[1]))

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = db(Path(tmp) / 'r.db', 'CREATE TABLE t (id TEXT PRIMARY KEY);')
            before = path.stat().st_mtime_ns
            audit.audit(path)
            self.assertEqual(before, path.stat().st_mtime_ns)

    def test_installed_and_env_file(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertFalse(audit.installed(home)['db-sync'])
            (Path(home) / '.claude/skills/db-sync').mkdir(parents=True)
            (Path(home) / '.claude/skills/db-sync/SKILL.md').write_text('x')
            self.assertTrue(audit.installed(home)['db-sync'])
            env = Path(home) / 'db-sync.env'
            self.assertIsNone(audit.env_file_private(env))
            env.write_text('x')
            env.chmod(0o644)
            self.assertFalse(audit.env_file_private(env))
            env.chmod(0o600)
            self.assertTrue(audit.env_file_private(env))

    def test_paste_probe_closed_port(self):
        self.assertFalse(audit.paste_running(port=1))


class Cli(unittest.TestCase):
    def test_sample_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-memory'), *a], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/acme-orders_v1.db').returncode, 1)
            self.assertEqual(run('check', tmp + '/acme-orders_v2.db').returncode, 0)
            self.assertEqual(run('sample', tmp).returncode, 0)


if __name__ == '__main__':
    unittest.main()
