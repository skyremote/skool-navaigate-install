"""Unit tests for tools-offers. A fake engine install stands in for the public repo."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-offers'
sys.path.insert(0, str(PACK))

from tools_offers import engine  # noqa: E402


def fake_install(home, harness='claude'):
    skills, agent = engine.HARNESS_DIRS[harness]
    for s in engine.SKILLS:
        folder = Path(home) / skills / s
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('Read <CORPUS_ROOT>/offers/corpus first.\n')
    if agent:
        (Path(home) / agent).parent.mkdir(parents=True, exist_ok=True)
        (Path(home) / agent).write_text('corpus: <CORPUS_ROOT>\n')


class Engine(unittest.TestCase):
    def test_installed_and_pointed(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertEqual(engine.pointed(home), 'missing')
            found, agent = engine.installed(home)
            self.assertFalse(any(found.values()))
            fake_install(home)
            found, agent = engine.installed(home)
            self.assertTrue(all(found.values()) and agent)
            self.assertEqual(engine.pointed(home), 'placeholder')

    def test_point_dry_run_then_write(self):
        with tempfile.TemporaryDirectory() as home:
            fake_install(home)
            corpus = Path(home) / 'My corpus'
            corpus.mkdir()
            changed = engine.point(home, corpus)
            self.assertEqual(len(changed), 6)
            self.assertEqual(engine.pointed(home), 'placeholder')
            engine.point(home, corpus, write=True)
            self.assertEqual(engine.pointed(home), 'set')
            self.assertIn(str(corpus.resolve()), (Path(home) / '.claude/agents/hormozi.md').read_text())
            self.assertEqual(engine.point(home, corpus, write=True), [])
            with self.assertRaises(engine.EngineError):
                engine.point(home, '/tmp/a|b')

    def test_codex_layout(self):
        with tempfile.TemporaryDirectory() as home:
            fake_install(home, 'codex')
            self.assertTrue(engine.installed(home, 'codex')[1])
            self.assertEqual(len(engine.point(home, home, 'codex')), 6)

    def test_corpus_init_and_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'c'
            self.assertEqual(len(engine.init(root)), 7)
            self.assertEqual(engine.init(root), [])
            (root / 'offers/corpus/ch01.md').write_text('Value [p.12] and [p. 13].')
            (root / 'leads/corpus/ch01.md').write_text('No markers yet.')
            report = engine.coverage(root)
            self.assertEqual(report['offers'], {'chapters': 1, 'with_pages': 1, 'page_markers': 2})
            self.assertEqual(report['leads']['with_pages'], 0)
            with self.assertRaises(engine.EngineError):
                engine.coverage(Path(tmp) / 'missing')


class Cli(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home)
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-offers'), *a], env=env, capture_output=True, text=True)
            self.assertEqual(run('doctor').returncode, 2)
            fake_install(home)
            self.assertEqual(run('doctor').returncode, 0)
            self.assertEqual(run('corpus', 'init', home + '/c').returncode, 0)
            self.assertEqual(run('corpus', 'check', home + '/c').returncode, 1)
            self.assertEqual(run('corpus', 'point', home + '/c').returncode, 1)
            self.assertEqual(run('corpus', 'point', home + '/c', '--yes').returncode, 0)
            self.assertIn('pointed at your own corpus', run('doctor').stdout)


if __name__ == '__main__':
    unittest.main()
