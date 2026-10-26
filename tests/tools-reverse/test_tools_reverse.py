"""Unit tests for tools-reverse. Local only."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-reverse'
sys.path.insert(0, str(PACK))

from tools_reverse import cli, report  # noqa: E402


class Check(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(report.check(report.SAMPLE), [])

    def test_template_basis_and_bypass(self):
        self.assertIn('placeholders', report.check(report.SCOPE.format(target='t', question='q'))[0])
        no_basis = report.SAMPLE.replace('Basis: my own software', 'Basis: curiosity')
        self.assertTrue(any('Basis must be' in p for p in report.check(no_basis)))
        bypass = report.SAMPLE.replace('Question: how does', 'Question: how do I bypass the licence and see how does')
        self.assertTrue(any('does not help' in p for p in report.check(bypass)))

    def test_findings_rules(self):
        no_evidence = report.SAMPLE.replace(' | Evidence: ev_js_0001 (calculatePrice in main.js)', '')
        self.assertTrue(any('no evidence' in p for p in report.check(no_evidence)))
        hedged = report.SAMPLE.replace('The unit rate drops', 'The unit rate probably drops')
        self.assertTrue(any('cannot say probably' in p for p in report.check(hedged)))
        bad_status = report.SAMPLE.replace('Status: inferred', 'Status: guessed')
        self.assertTrue(any('Status must be' in p for p in report.check(bad_status)))
        no_unknowns = report.SAMPLE.split('## Unknowns')[0]
        self.assertTrue(any('Unknowns' in p for p in report.check(no_unknowns)))


class Cli(unittest.TestCase):
    def test_rea_skill_detection(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertFalse(cli.rea_skill(home))
            path = Path(home, '.agents/skills/reverse-engineer-anything')
            path.mkdir(parents=True)
            (path / 'SKILL.md').write_text('x')
            self.assertTrue(cli.rea_skill(home))

    def test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-reverse'), *a], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/acme-calculator_investigation_v1.md').returncode, 0)
            self.assertEqual(run('new', tmp + '/n.md', '--target', 't', '--question', 'q').returncode, 0)
            self.assertEqual(run('check', tmp + '/n.md').returncode, 1)
            self.assertEqual(run('new', tmp + '/n.md', '--target', 't', '--question', 'q').returncode, 1)
            self.assertEqual(run('doctor').returncode, 2)


if __name__ == '__main__':
    unittest.main()
