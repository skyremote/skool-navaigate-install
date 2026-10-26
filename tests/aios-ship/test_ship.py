"""Unit tests for plugins/aios-ship (ship-pack). Standard library only; everything lives in /tmp."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins/aios-ship'
sys.path.insert(0, str(PACK))
from ship_pack.cli import TODO, bump_version, check_pack, main  # noqa: E402


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


def fill(pack):
    """Replace every placeholder the way a member would."""
    for path in pack.rglob('*'):
        if path.is_file():
            text = path.read_text()
            if TODO in text:
                text = text.replace(TODO + ': ', '').replace(TODO + '-a-word-the-right-answer-always-contains', 'quote')
                text = text.replace(TODO, 'filled')
                path.write_text(text)


SKILL = """---
name: acme-quotes
description: Write a quote for an Acme Studio job from a short brief. Use for /acme-quotes or "write a quote".
---

# Acme quotes

1. Ask for the client and the job.
2. Write the quote.
"""


class Scaffold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-ship-test-', dir='/tmp')
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_new_creates_full_layout(self):
        code, out, _ = run('new', 'acme-quotes', '--dir', str(self.base), '--author', 'Acme Studio', '--depends', 'aios')
        self.assertEqual(code, 0)
        pack = self.base / 'acme-quotes'
        manifest = json.loads((pack / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['version'], '0.1.0')
        self.assertEqual(manifest['dependencies'], ['aios'])
        for rel in ('skills/acme-quotes/SKILL.md', 'tests/test_pack.py', 'install.sh', 'README.md', 'CHANGELOG.md',
                    'MARKETPLACE_ENTRY.json', 'evals/happy-path/prompt.md', 'evals/edge-case/graders/result.md',
                    'evals/must-refuse/graders/skill-fired.md'):
            self.assertTrue((pack / rel).is_file(), rel)
        self.assertTrue(os.access(pack / 'install.sh', os.X_OK))
        self.assertIn('claude plugin validate', out)

    def test_fresh_scaffold_fails_check_until_filled(self):
        run('new', 'acme-quotes', '--dir', str(self.base))
        pack = self.base / 'acme-quotes'
        errors, _ = check_pack(pack)
        self.assertTrue(any(TODO in e for e in errors))
        fill(pack)
        errors, warnings = check_pack(pack)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(run('check', str(pack))[0], 0)

    def test_scaffolded_tests_pass(self):
        run('new', 'acme-quotes', '--dir', str(self.base))
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', str(self.base / 'acme-quotes/tests')],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_never_overwrites(self):
        run('new', 'acme-quotes', '--dir', str(self.base))
        code, _, err = run('new', 'acme-quotes', '--dir', str(self.base))
        self.assertEqual(code, 2)
        self.assertIn('already exists', err)
        self.assertEqual(run('new', 'Bad Name', '--dir', str(self.base))[0], 2)

    def test_from_skill_copies_and_uses_description(self):
        skill = self.base / 'src/acme-quotes'
        (skill / 'references').mkdir(parents=True)
        (skill / 'SKILL.md').write_text(SKILL)
        (skill / 'references/rates.md').write_text('Day rate: 600\n')
        code, out, err = run('from-skill', str(skill), '--dir', str(self.base / 'out'))
        self.assertEqual(code, 0, err)
        pack = self.base / 'out/acme-quotes'
        self.assertEqual((pack / 'skills/acme-quotes/SKILL.md').read_text(), SKILL)
        self.assertTrue((pack / 'skills/acme-quotes/references/rates.md').exists())
        manifest = json.loads((pack / '.claude-plugin/plugin.json').read_text())
        self.assertIn('Write a quote', manifest['description'])

    def test_from_skill_refuses_secrets_and_home_paths(self):
        skill = self.base / 'src/acme-quotes'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text(SKILL + '\nKey: sk-' + 'a' * 30 + '\nSee /Users/' + 'jane/notes.md\n')
        code, _, err = run('from-skill', str(skill), '--dir', str(self.base / 'out'))
        self.assertEqual(code, 2)
        self.assertIn('Anthropic or OpenAI style key', err)
        self.assertIn('personal home path', err)
        self.assertFalse((self.base / 'out/acme-quotes').exists())

    def test_from_skill_needs_frontmatter(self):
        skill = self.base / 'src/plain'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('# no frontmatter\n')
        self.assertEqual(run('from-skill', str(skill))[0], 2)


class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-ship-test-', dir='/tmp')
        run('new', 'acme-quotes', '--dir', self.tmp.name)
        self.pack = Path(self.tmp.name) / 'acme-quotes'
        fill(self.pack)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, **changes):
        path = self.pack / '.claude-plugin/plugin.json'
        data = json.loads(path.read_text())
        data.update(changes)
        path.write_text(json.dumps(data))

    def test_secret_user_config_must_be_sensitive(self):
        self.manifest(userConfig={'api_token': {'type': 'string', 'title': 'Token', 'description': 'Your token'}})
        errors, _ = check_pack(self.pack)
        self.assertTrue(any('sensitive' in e for e in errors))
        self.manifest(userConfig={'api_token': {'type': 'string', 'title': 'Token', 'description': 'Your token', 'sensitive': True}})
        self.assertEqual(check_pack(self.pack)[0], [])

    def test_bad_version_long_skill_and_few_evals(self):
        self.manifest(version='v1')
        skill = self.pack / 'skills/acme-quotes/SKILL.md'
        skill.write_text(skill.read_text() + 'line\n' * 500)
        for case in ('edge-case', 'must-refuse'):
            (self.pack / 'evals' / case / 'prompt.md').unlink()
        errors = ' | '.join(check_pack(self.pack)[0])
        self.assertIn('version must look like 1.2.3', errors)
        self.assertIn('under 500', errors)
        self.assertIn('1 eval case(s)', errors)

    def test_marketplace_version_mismatch_and_bin_not_executable(self):
        (self.pack / 'MARKETPLACE_ENTRY.json').write_text(json.dumps({'name': 'acme-quotes', 'version': '9.9.9'}))
        (self.pack / 'bin').mkdir()
        (self.pack / 'bin/acme').write_text('#!/bin/sh\n')
        errors = ' | '.join(check_pack(self.pack)[0])
        self.assertIn('does not match plugin.json', errors)
        self.assertIn('not executable', errors)

    def test_skill_name_must_match_folder(self):
        skill = self.pack / 'skills/acme-quotes/SKILL.md'
        skill.write_text(skill.read_text().replace('name: acme-quotes', 'name: other'))
        self.assertTrue(any('must match its folder' in e for e in check_pack(self.pack)[0]))

    def test_bump_updates_all_three_files(self):
        code, out, _ = run('bump', str(self.pack), 'minor', '--note', 'Adds VAT lines')
        self.assertEqual(code, 0)
        self.assertIn('0.1.0 -> 0.2.0', out)
        self.assertEqual(json.loads((self.pack / '.claude-plugin/plugin.json').read_text())['version'], '0.2.0')
        self.assertEqual(json.loads((self.pack / 'MARKETPLACE_ENTRY.json').read_text())['version'], '0.2.0')
        changelog = (self.pack / 'CHANGELOG.md').read_text()
        self.assertLess(changelog.index('## 0.2.0'), changelog.index('## 0.1.0'))
        self.assertIn('Adds VAT lines', changelog)
        self.assertEqual(check_pack(self.pack)[0], [])
        self.assertEqual(run('bump', str(self.pack), 'patch', '--note', ' ')[0], 2)

    def test_bump_version_maths(self):
        self.assertEqual(bump_version('1.2.3', 'patch'), '1.2.4')
        self.assertEqual(bump_version('1.2.3', 'minor'), '1.3.0')
        self.assertEqual(bump_version('1.2.3', 'major'), '2.0.0')

    def test_marketplace_create_then_update(self):
        market = Path(self.tmp.name) / '.claude-plugin/marketplace.json'
        self.assertEqual(run('marketplace', str(self.pack), '--file', str(market))[0], 2)
        code, out, _ = run('marketplace', str(self.pack), '--file', str(market), '--name', 'acme-tools', '--owner', 'Acme Studio')
        self.assertEqual(code, 0)
        data = json.loads(market.read_text())
        self.assertEqual(data['plugins'][0]['source'], './acme-quotes')
        run('bump', str(self.pack), 'patch', '--note', 'Fix')
        code, out, _ = run('marketplace', str(self.pack), '--file', str(market))
        self.assertIn('Updated', out)
        data = json.loads(market.read_text())
        self.assertEqual(len(data['plugins']), 1)
        self.assertEqual(data['plugins'][0]['version'], '0.1.1')


class Installer(unittest.TestCase):
    def test_install_links_refuses_and_uninstalls(self):
        with tempfile.TemporaryDirectory(prefix='aios-ship-test-', dir='/tmp') as tmp:
            run('new', 'acme-quotes', '--dir', tmp)
            pack = Path(tmp) / 'acme-quotes'
            (pack / 'bin').mkdir()
            (pack / 'bin/acme-quote').write_text('#!/bin/sh\necho quote\n')
            (pack / 'bin/acme-quote').chmod(0o755)
            home = Path(tmp) / 'home'
            home.mkdir()
            env = dict(os.environ, HOME=str(home))
            first = subprocess.run([str(pack / 'install.sh')], env=env, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            for parent in ('.codex/skills', '.cursor/skills', '.agents/skills'):
                link = home / parent / 'acme-quotes'
                self.assertTrue(link.is_symlink())
                self.assertTrue((link / 'SKILL.md').exists())
            self.assertTrue((home / '.local/bin/acme-quote').is_symlink())
            again = subprocess.run([str(pack / 'install.sh')], env=env, text=True, capture_output=True)
            self.assertEqual(again.returncode, 0)
            self.assertIn('Already linked', again.stdout)
            (home / '.cursor/skills/acme-quotes').unlink()
            (home / '.cursor/skills/acme-quotes').mkdir()
            blocked = subprocess.run([str(pack / 'install.sh')], env=env, text=True, capture_output=True)
            self.assertEqual(blocked.returncode, 1)
            self.assertIn('not this pack', blocked.stderr)
            gone = subprocess.run([str(pack / 'install.sh'), '--uninstall'], env=env, text=True, capture_output=True)
            self.assertEqual(gone.returncode, 0, gone.stderr)
            self.assertFalse((home / '.codex/skills/acme-quotes').exists())
            self.assertTrue((home / '.cursor/skills/acme-quotes').is_dir())
            self.assertFalse((home / '.local/bin/acme-quote').exists())


class OwnPack(unittest.TestCase):
    def test_skills_short(self):
        for skill in (PACK / 'skills').glob('*/SKILL.md'):
            self.assertLess(len(skill.read_text().splitlines()), 500)

    def test_wrapper(self):
        result = subprocess.run([str(PACK / 'bin/ship-pack'), '--help'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('from-skill', result.stdout)



class TourAndManifest(unittest.TestCase):
    def test_tour_is_short_and_manifest_has_module(self):
        import json as _json
        pack = Path(__file__).resolve().parents[2] / 'plugins/aios-ship'
        tour = (pack / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('## Step 1', tour)
        manifest = _json.loads((pack / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['dependencies'], ['aios'])
        self.assertIsInstance(manifest['metadata']['module'], int)


if __name__ == '__main__':
    unittest.main()
