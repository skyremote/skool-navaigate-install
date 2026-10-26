"""Unit tests for tools-notebooklm. Local only."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-notebooklm'
sys.path.insert(0, str(PACK))

from tools_notebooklm import plan  # noqa: E402


class Plan(unittest.TestCase):
    def test_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.pdf').write_bytes(b'%PDF-1.4')
            (root / 'b.md').write_text('words ' * 10)
            (root / 'empty.txt').write_text('')
            (root / 'c.pages').write_text('x')
            (root / '.hidden.md').write_text('x')
            (root / 'sub').mkdir()
            (root / 'sub/d.txt').write_text('hello')
            (root / 'links.txt').write_text('https://example.org/a\nnot a link\nhttp://example.org/b\n')
            rows = {r['source']: r for r in plan.inventory(root)}
            self.assertTrue(rows['a.pdf']['ok'])
            self.assertTrue(rows['sub/d.txt']['ok'])
            self.assertFalse(rows['c.pages']['ok'])
            self.assertFalse(rows['empty.txt']['ok'])
            self.assertNotIn('.hidden.md', rows)
            self.assertIn('https://example.org/a', rows)
            self.assertIn('http://example.org/b', rows)
            self.assertNotIn('links.txt', rows)
        with self.assertRaises(ValueError):
            plan.inventory('/nonexistent/folder')

    def test_word_limit_and_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = plan.MAX_WORDS
            plan.MAX_WORDS = 5
            try:
                Path(tmp, 'long.txt').write_text('one two three four five six')
                self.assertFalse(plan.inventory(tmp)[0]['ok'])
            finally:
                plan.MAX_WORDS = old
        rows = [{'ok': True}] * 120 + [{'ok': False}]
        self.assertEqual([len(b) for b in plan.batches(rows)], [50, 50, 20])


class Cli(unittest.TestCase):
    def test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp, PATH='/usr/bin:/bin')
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-notebooklm'), *a], env=env, capture_output=True, text=True)
            self.assertEqual(run('doctor').returncode, 2)
            self.assertEqual(run('sample', tmp + '/s').returncode, 0)
            out = run('plan', tmp + '/s')
            self.assertEqual(out.returncode, 0)
            self.assertIn('3 source(s) can go in, 1 cannot', out.stdout)
            Path(tmp, 'only-bad').mkdir()
            Path(tmp, 'only-bad/x.pages').write_text('x')
            self.assertEqual(run('plan', tmp + '/only-bad').returncode, 1)


if __name__ == '__main__':
    unittest.main()
