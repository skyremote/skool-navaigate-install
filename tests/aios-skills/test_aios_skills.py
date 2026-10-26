"""Unit tests for the aios-skills pack. Run from the repository root:
python3 -m unittest discover -s tests/aios-skills -v
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins' / 'aios-skills'
sys.path.insert(0, str(PACK))

from aios_skills import audit, check, frontmatter, hide, scaffold  # noqa: E402
from aios_skills.cli import main  # noqa: E402

GOOD = 'Turn meeting notes into an action list with owners. Use when someone pastes notes and asks for actions.'


class Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-skills-test-')
        self.home = Path(self.tmp.name) / 'home'
        self.cwd = Path(self.tmp.name) / 'project'
        self.home.mkdir()
        self.cwd.mkdir()
        self.env = patch.dict(os.environ, {'HOME': str(self.home)})
        self.env.start()
        self.old = os.getcwd()
        os.chdir(self.cwd)

    def tearDown(self):
        os.chdir(self.old)
        self.env.stop()
        self.tmp.cleanup()

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def fill(self, folder):
        """Replace every TODO marker, as a member would after scaffolding."""
        for path in folder.rglob('*.md'):
            path.write_text(path.read_text().replace('TODO:', 'Done:'))


class FrontmatterTests(unittest.TestCase):
    def test_simple_and_folded(self):
        text = '---\nname: x\ndescription: first line\n  second line\n---\nbody\n'
        meta, body, lines = frontmatter.split(text)
        self.assertEqual(meta['description'], 'first line second line')
        self.assertEqual(body, 'body')
        self.assertEqual(lines, 5)

    def test_block_scalar_and_quotes(self):
        meta, _, _ = frontmatter.split('---\nname: "q"\ndescription: >\n  a\n  b\n---\n')
        self.assertEqual(meta, {'name': 'q', 'description': 'a b'})

    def test_no_frontmatter(self):
        self.assertEqual(frontmatter.split('# title')[0], {})
        self.assertEqual(frontmatter.split('---\nname: x\n')[0], {})

    def test_sentences(self):
        self.assertEqual(frontmatter.sentences('One. Two.'), 2)
        self.assertEqual(frontmatter.sentences('No full stop'), 1)
        self.assertEqual(frontmatter.sentences('Use tools, e.g. Excel. Then stop.'), 2)
        self.assertEqual(frontmatter.sentences(''), 0)
        self.assertEqual(frontmatter.sentences('Version 2.0 is here.'), 1)


class ScaffoldTests(Temp):
    def test_creates_skill_manifest_and_three_cases(self):
        target, files = scaffold.create('meeting-actions', GOOD)
        self.assertEqual(target, self.home / '.claude/skills/meeting-actions')
        self.assertIn('SKILL.md', files)
        manifest = json.loads((target / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['skills'], ['./'])
        cases = check.eval_cases(target)
        self.assertEqual(sorted(cases), ['edge-case', 'should-fire', 'should-not-fire'])
        quiet = (target / 'evals/should-not-fire/graders/skill-quiet.md').read_text()
        self.assertIn('max: 0', quiet)
        self.assertIn('arm: both', quiet)
        self.assertIn('meeting-actions', quiet)

    def test_project_scope(self):
        target, _ = scaffold.create('meeting-actions', GOOD, project=True)
        self.assertTrue(str(target).endswith('project/.claude/skills/meeting-actions'))

    def test_never_overwrites(self):
        scaffold.create('meeting-actions', GOOD)
        marker = self.home / '.claude/skills/meeting-actions/SKILL.md'
        marker.write_text('mine')
        with self.assertRaises(scaffold.ScaffoldError):
            scaffold.create('meeting-actions', GOOD)
        self.assertEqual(marker.read_text(), 'mine')

    def test_rejects_bad_names_and_descriptions(self):
        for name in ('Meeting', 'two words', '-lead', 'x' * 65, ''):
            with self.assertRaises(scaffold.ScaffoldError):
                scaffold.create(name, GOOD)
        for description in ('', 'One. Two. Three.', 'x' * 1100):
            with self.assertRaises(scaffold.ScaffoldError):
                scaffold.create('ok-name', description)

    def test_description_with_colon_is_quoted_and_parses(self):
        target, _ = scaffold.create('colon-skill', 'Format invoices: totals and VAT. Use for invoices.')
        meta, _, _ = frontmatter.split((target / 'SKILL.md').read_text())
        self.assertEqual(meta['description'], 'Format invoices: totals and VAT. Use for invoices.')

    def test_validate_passes_on_scaffold(self):
        """The scaffold is a valid skills-directory plugin for Claude Code."""
        if subprocess.run(['which', 'claude'], capture_output=True).returncode:
            self.skipTest('claude CLI not installed')
        target, _ = scaffold.create('meeting-actions', GOOD)
        result = subprocess.run(['claude', 'plugin', 'validate', str(target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class CheckTests(Temp):
    def test_fresh_scaffold_fails_on_todo_then_passes(self):
        target, _ = scaffold.create('meeting-actions', GOOD)
        report = check.check_skill(target / 'SKILL.md')
        self.assertFalse(report['ok'])
        self.assertTrue(any('TODO' in e for e in report['errors']))
        self.fill(target)
        report = check.check_skill(target / 'SKILL.md')
        self.assertTrue(report['ok'], report['errors'])
        self.assertEqual(report['warnings'], [])
        self.assertEqual(len(report['eval_cases']), 3)

    def test_long_body_too_many_sentences_and_missing_evals(self):
        folder = self.cwd / 'skills' / 'bloated'
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('---\nname: bloated\ndescription: A. B. C.\n---\n' + 'line\n' * 520)
        report = check.check_skill(folder / 'SKILL.md')
        joined = ' '.join(report['errors'])
        self.assertIn('3 sentences', joined)
        self.assertIn('520 lines', joined)
        self.assertIn('0 eval cases', joined)
        self.assertTrue(any('plugin manifest' in w for w in report['warnings']))

    def test_missing_description_and_bad_name(self):
        folder = self.cwd / 'Bad_Name'
        folder.mkdir()
        (folder / 'SKILL.md').write_text('# no frontmatter\n')
        report = check.check_skill(folder / 'SKILL.md')
        joined = ' '.join(report['errors'])
        self.assertIn('No frontmatter', joined)
        self.assertIn('No description', joined)
        self.assertIn('lowercase', joined)

    def test_long_description_warns_then_errors(self):
        folder = self.cwd / 'wordy'
        folder.mkdir()
        (folder / 'SKILL.md').write_text('---\nname: wordy\ndescription: %s\n---\n' % ('w' * 400))
        self.assertTrue(any('400 characters' in w for w in check.check_skill(folder / 'SKILL.md')['warnings']))
        (folder / 'SKILL.md').write_text('---\nname: wordy\ndescription: %s\n---\n' % ('w' * 1100))
        self.assertTrue(any('1100 characters' in e for e in check.check_skill(folder / 'SKILL.md')['errors']))

    def test_results_folder_is_not_a_case(self):
        target, _ = scaffold.create('meeting-actions', GOOD)
        stale = target / 'evals/results/2026/should-fire'
        stale.mkdir(parents=True)
        (stale / 'prompt.md').write_text('old run')
        self.assertEqual(len(check.eval_cases(target)), 3)

    def test_custom_eval_dir_from_manifest(self):
        target, _ = scaffold.create('meeting-actions', GOOD)
        manifest = target / '.claude-plugin/plugin.json'
        data = json.loads(manifest.read_text())
        data['experimental'] = {'evals': 'quality'}
        manifest.write_text(json.dumps(data))
        (target / 'evals').rename(target / 'quality')
        self.assertEqual(len(check.eval_cases(target)), 3)

    def test_find_skills_shapes(self):
        self.assertEqual(len(check.find_skills(PACK)), 2)
        self.assertEqual(len(check.find_skills(PACK / 'skills/skill-craft')), 1)
        self.assertEqual(check.find_skills(self.cwd), [])

    def test_shipped_pack_and_example_pass(self):
        for path in (PACK, PACK / 'examples/meeting-actions'):
            code, out, _ = self.run_cli('check', str(path))
            self.assertEqual(code, 0, out)

    def test_cli_json_and_exit_code(self):
        target, _ = scaffold.create('meeting-actions', GOOD)
        code, out, _ = self.run_cli('check', str(target), '--json')
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)[0]['ok'])
        code, _, err = self.run_cli('check', str(self.cwd))
        self.assertEqual(code, 1)
        self.assertIn('No SKILL.md', err)


class HideTests(Temp):
    def test_local_scope_creates_then_is_idempotent(self):
        path, backup, changed = hide.apply('weekly-report', 'name-only')
        self.assertEqual(path.resolve(), (self.cwd / '.claude/settings.local.json').resolve())
        self.assertTrue(changed)
        self.assertIsNone(backup)
        self.assertEqual(json.loads(path.read_text()), {'skillOverrides': {'weekly-report': 'name-only'}})
        self.assertFalse(hide.apply('weekly-report', 'name-only')[2])

    def test_preserves_other_settings_and_backs_up(self):
        path = self.home / '.claude/settings.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'model': 'sonnet', 'skillOverrides': {'a': 'off'}}))
        _, backup, _ = hide.apply('b', 'user-invocable-only', scope='user')
        data = json.loads(path.read_text())
        self.assertEqual(data['model'], 'sonnet')
        self.assertEqual(data['skillOverrides'], {'a': 'off', 'b': 'user-invocable-only'})
        self.assertEqual(json.loads(backup.read_text())['skillOverrides'], {'a': 'off'})

    def test_on_removes_entry(self):
        hide.apply('a', 'off', scope='project')
        path, _, _ = hide.apply('a', 'on', scope='project')
        self.assertEqual(json.loads(path.read_text()), {})

    def test_refuses_plugin_skill_bad_state_and_bad_json(self):
        with self.assertRaises(hide.HideError) as caught:
            hide.plan('aios-skills:skill-craft', 'off')
        self.assertIn('/plugin', str(caught.exception))
        with self.assertRaises(hide.HideError):
            hide.plan('a', 'hidden')
        bad = self.cwd / '.claude/settings.local.json'
        bad.parent.mkdir(parents=True)
        bad.write_text('{broken')
        with self.assertRaises(hide.HideError):
            hide.apply('a', 'off')
        self.assertEqual(bad.read_text(), '{broken')

    def test_cli_dry_run_writes_nothing(self):
        code, out, _ = self.run_cli('hide', 'a', 'off', '--dry-run')
        self.assertEqual(code, 0)
        self.assertIn('"a": "off"', out)
        self.assertFalse((self.cwd / '.claude/settings.local.json').exists())
        code, _, err = self.run_cli('hide', 'x:y', 'off')
        self.assertEqual(code, 1)
        self.assertIn('plugin skill', err)


class AuditTests(Temp):
    def test_sorted_by_cost_and_respects_overrides(self):
        scaffold.create('short-one', 'Short. Use rarely.')
        scaffold.create('long-one', 'A much longer description of a much bigger job here. Use often.')
        scaffold.create('project-one', 'Project skill. Use here.', project=True)
        hide.apply('short-one', 'off', scope='user')
        rows = audit.collect()
        self.assertEqual(rows[0]['skill'], 'long-one')
        states = {row['skill']: row for row in rows}
        self.assertEqual(states['short-one']['tokens_estimate'], 0)
        self.assertEqual(states['project-one']['where'], 'project')
        text = audit.format_rows(rows)
        self.assertIn('/skill-doctor', text)
        self.assertIn('across 3 skills', text)

    def test_home_as_project_is_not_counted_twice(self):
        os.chdir(self.home)
        scaffold.create('only-one', GOOD)
        self.assertEqual(len(audit.collect()), 1)

    def test_empty(self):
        self.assertIn('No personal or project skills', audit.format_rows(audit.collect()))


class CommandTests(Temp):
    def test_bin_runs_through_a_symlink(self):
        link = self.home / '.local/bin/aios-skill'
        link.parent.mkdir(parents=True)
        link.symlink_to(PACK / 'bin/aios-skill')
        result = subprocess.run([str(link), '--version'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('2.0.0', result.stdout)

    def test_new_command_end_to_end(self):
        code, out, _ = self.run_cli('new', 'meeting-actions', '--description', GOOD, '--project')
        self.assertEqual(code, 0)
        self.assertIn('aios-skill check', out)
        code, _, err = self.run_cli('new', 'meeting-actions', '--description', GOOD, '--project')
        self.assertEqual(code, 1)
        self.assertIn('already exists', err)


class ManifestTests(unittest.TestCase):
    def test_manifest_rules(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(data['version'], '2.0.0')
        self.assertEqual(data['dependencies'], ['aios'])
        self.assertEqual(data['author']['name'], 'skyremote')
        entry = json.loads((PACK / 'MARKETPLACE_ENTRY.json').read_text())
        self.assertEqual(entry['source'], './plugins/aios-skills')
        self.assertEqual(entry['version'], data['version'])

    def test_skill_files_under_limits(self):
        for skill in PACK.glob('skills/*/SKILL.md'):
            meta, body, _ = frontmatter.split(skill.read_text())
            self.assertLess(len(body.splitlines()), 500)
            self.assertLessEqual(frontmatter.sentences(meta['description']), 2)

    def test_three_eval_cases_each_with_a_skill_grader(self):
        cases = check.eval_cases(PACK)
        self.assertGreaterEqual(len(cases), 3)
        for name, (_, graders) in cases.items():
            kinds = [frontmatter.split(g.read_text())[0].get('type') for g in graders]
            self.assertIn('tool_used', kinds, name)



class TourAndModuleTests(unittest.TestCase):
    def test_module_number_and_tour(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(data['metadata'], {'module': 6})
        self.assertEqual(data['dependencies'], ['aios'])
        tour = (PACK / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('/aios learn 6', tour)
        for label in ('**Do:**', '**Command:**', '**They should see:**', '**Check:**'):
            self.assertIn(label, tour)


if __name__ == '__main__':
    unittest.main()
