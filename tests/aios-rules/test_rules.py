"""Unit tests for the aios-rules pack. Run: python3 -m unittest discover -s tests/aios-rules -v"""
import datetime
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins' / 'aios-rules'
sys.path.insert(0, str(PACK))

from aios_rules import audit, check, cli, frontmatter, setup  # noqa: E402


class Sandbox(unittest.TestCase):
    """Each test gets a fresh fake HOME and project folder under /tmp."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='aios-rules-test-', dir='/tmp')).resolve()
        self.home = self.tmp / 'home'
        self.project = self.home / 'acme'
        self.project.mkdir(parents=True)
        self.env = {}

    def tearDown(self):
        subprocess.run(['rm', '-rf', str(self.tmp)])

    def write(self, relative, text, base=None):
        path = (base or self.project) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self, harness='claude', budgets=None, project=None):
        return check.run(project or self.project, [harness], budgets, home=self.home, env=self.env)[0]

    def paths(self, result, loaded='always'):
        return [i['path'] for i in result['items'] if i['loaded'] == loaded]


class FrontmatterTests(unittest.TestCase):
    def test_list_comma_and_block(self):
        block, body = frontmatter.split('---\npaths:\n  - "a/**"\n  - b/*.md\ndescription: >\n  one\n  two\nx: "y"\n---\nBody\n')
        meta = frontmatter.parse(block)
        self.assertEqual(meta['paths'], ['a/**', 'b/*.md'])
        self.assertEqual(meta['description'], 'one two')
        self.assertEqual(meta['x'], 'y')
        self.assertEqual(body, 'Body\n')
        self.assertEqual(frontmatter.as_list('a/**, b/**'), ['a/**', 'b/**'])
        self.assertEqual(frontmatter.parse(frontmatter.split('---\npaths: [a/**, "b/**"]\n---\n')[0])['paths'], ['a/**', 'b/**'])

    def test_no_frontmatter(self):
        self.assertEqual(frontmatter.split('# Title\n'), (None, '# Title\n'))


class InitTests(Sandbox):
    def test_fresh_folder_gets_everything(self):
        report = setup.init(self.project, 'Acme Studio', 'Sam Rivera')
        created = {Path(p).relative_to(self.project).as_posix() for a, p, _ in report if a == 'created'}
        for name in setup.FOLDERS + ['AGENTS.md', 'CLAUDE.md', '.claude/rules/finance.md']:
            self.assertIn(name, created)
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), '@AGENTS.md\n')
        agents = (self.project / 'AGENTS.md').read_text()
        self.assertIn('Acme Studio', agents)
        self.assertNotIn('{{BUSINESS}}', agents)
        self.assertLess(agents.count('\n'), 150)

    def test_second_run_keeps_member_edits(self):
        setup.init(self.project)
        self.write('AGENTS.md', '# My own rules\n')
        report = setup.init(self.project)
        self.assertEqual((self.project / 'AGENTS.md').read_text(), '# My own rules\n')
        self.assertFalse([p for a, p, _ in report if a == 'created'])

    def test_existing_claude_md_is_never_edited(self):
        self.write('CLAUDE.md', '# Old notes\n')
        report = setup.init(self.project, make_folders=False)
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), '# Old notes\n')
        self.assertIn('action', [a for a, p, _ in report if Path(p).name == 'CLAUDE.md'])
        self.assertFalse((self.project / '00_inbox').exists())

    def test_dry_run_writes_nothing(self):
        setup.init(self.project, dry_run=True)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_starter_template_is_under_150_lines(self):
        self.assertLess(len((PACK / 'templates' / 'AGENTS.md').read_text().splitlines()), 150)
        self.assertEqual((PACK / 'templates' / 'CLAUDE.md').read_text(), '@AGENTS.md\n')


class ClaudeCheckTests(Sandbox):
    def test_bridge_imports_agents_and_scopes_rules(self):
        setup.init(self.project, 'Acme Studio', 'Sam Rivera', make_folders=False)
        self.write('.claude/rules/style.md', '# Always\n- British English.\n')
        result = self.run_check()
        self.assertEqual(self.paths(result), ['./CLAUDE.md', './AGENTS.md', './.claude/rules/style.md'])
        self.assertEqual(len(self.paths(result, 'on-demand')), 3)
        agents = [i for i in result['items'] if i['path'] == './AGENTS.md'][0]
        self.assertEqual(agents['imported_by'], './CLAUDE.md')
        self.assertEqual(agents['tokens'], check.approx_tokens(agents['chars']))

    def test_agents_md_alone_is_read(self):
        self.write('AGENTS.md', '# Rules\n')
        self.assertEqual(self.paths(self.run_check()), ['./AGENTS.md'])

    def test_user_claude_md_does_not_block_agents_md(self):
        self.write('.claude/CLAUDE.md', '# Me\n', base=self.home)
        self.write('AGENTS.md', '# Rules\n')
        self.assertEqual(self.paths(self.run_check()), ['~/.claude/CLAUDE.md', './AGENTS.md'])

    def test_claude_md_without_import_hides_agents_md(self):
        self.write('CLAUDE.md', '# Notes\nRead AGENTS.md first.\n')
        self.write('AGENTS.md', '# Rules\n')
        result = self.run_check()
        self.assertEqual(self.paths(result), ['./CLAUDE.md'])
        self.assertTrue(any('@AGENTS.md' in f['message'] for f in result['flags']))

    def test_over_budget_fails(self):
        self.write('AGENTS.md', '- rule\n' * 250)
        result = self.run_check()
        self.assertEqual(result['status'], 'over')
        self.assertEqual(check.exit_code([result]), 1)
        self.assertTrue(any('250 lines' in f['message'] for f in result['flags']))

    def test_target_warns_but_passes(self):
        self.write('AGENTS.md', '- rule\n' * 170)
        result = self.run_check()
        self.assertEqual(result['status'], 'warn')
        self.assertEqual(check.exit_code([result]), 0)

    def test_token_budget(self):
        self.write('AGENTS.md', ('x' * 400 + '\n') * 20)
        self.assertEqual(self.run_check(budgets={'total_tokens_max': 1000})['status'], 'over')

    def test_imports_skip_code_emails_and_flag_missing(self):
        self.write('notes.md', 'notes\n')
        self.write('CLAUDE.md', '@notes.md\nMail sam@acme.example\n`@notes.md`\n```\n@fenced.md\n```\n@docs/missing.md\n')
        result = self.run_check()
        self.assertEqual(self.paths(result), ['./CLAUDE.md', './notes.md'])
        messages = ' '.join(f['message'] for f in result['flags'])
        self.assertIn('docs/missing.md', messages)
        self.assertNotIn('fenced', messages)

    def test_home_and_spaced_imports(self):
        self.write('shared/my notes.md', 'mine\n', base=self.home)
        self.write('CLAUDE.md', '@~/shared/my\\ notes.md\n')
        self.assertIn('~/shared/my notes.md', self.paths(self.run_check()))

    def test_import_depth_stops_after_four_hops(self):
        for n in range(6):
            self.write('f%d.md' % n, '@f%d.md\n' % (n + 1))
        self.write('CLAUDE.md', '@f0.md\n')
        self.write('f6.md', 'end\n')
        result = self.run_check()
        self.assertEqual(self.paths(result), ['./CLAUDE.md', './f0.md', './f1.md', './f2.md', './f3.md'])

    def test_cycles_load_once(self):
        self.write('CLAUDE.md', '@AGENTS.md\n')
        self.write('AGENTS.md', '@CLAUDE.md\n')
        self.assertEqual(self.paths(self.run_check()), ['./CLAUDE.md', './AGENTS.md'])

    def test_parent_folder_rules_are_counted(self):
        self.write('CLAUDE.md', '# Parent\n', base=self.home)
        self.write('CLAUDE.md', '@AGENTS.md\n')
        self.write('AGENTS.md', '# Rules\n')
        self.assertEqual(self.paths(self.run_check()), ['~/CLAUDE.md', './CLAUDE.md', './AGENTS.md'])

    def test_bad_paths_frontmatter_warns(self):
        self.write('.claude/rules/broken.md', '---\npaths:\n---\n# Rule\n')
        result = self.run_check()
        self.assertIn('./.claude/rules/broken.md', self.paths(result))
        self.assertTrue(any('paths field' in f['message'] for f in result['flags']))

    def test_user_rules_and_custom_config_dir(self):
        config = self.tmp / 'cfg'
        self.write('rules/me.md', '# Me\n', base=config)
        self.write('rules/py.md', '---\npaths: "**/*.py"\n---\n# Py\n', base=config)
        self.env = {'CLAUDE_CONFIG_DIR': str(config)}
        result = self.run_check()
        self.assertTrue(any(p.endswith('cfg/rules/me.md') for p in self.paths(result)))
        self.assertTrue(any(p.endswith('cfg/rules/py.md') for p in self.paths(result, 'on-demand')))

    def test_skill_listing_respects_hiding(self):
        long = 'x' * 1600
        self.write('.claude/skills/long/SKILL.md', '---\nname: long\ndescription: %s\n---\n' % long, base=self.home)
        self.write('.claude/skills/hidden/SKILL.md', '---\nname: hidden\ndescription: secret\ndisable-model-invocation: true\n---\n', base=self.home)
        self.write('.claude/skills/short/SKILL.md', '---\nname: short\ndescription: %s\n---\n' % ('y' * 500), base=self.home)
        self.write('.claude/settings.json', json.dumps({'skillOverrides': {'short': 'name-only'}}), base=self.home)
        result = self.run_check()
        listing = [i for i in result['items'] if i['kind'] == 'skill-listing']
        self.assertEqual(len(listing), 2)
        self.assertTrue(any('1600 characters' in f['message'] for f in result['flags']))
        self.assertEqual(min(i['chars'] for i in listing), len('- short\n'))
        self.assertEqual(result['totals']['lines'], 0)

    def test_memory_index_is_cut_at_200_lines(self):
        memory = self.home / '.claude' / 'projects' / check.memory_folder_name(self.project) / 'memory' / 'MEMORY.md'
        memory.parent.mkdir(parents=True)
        memory.write_text('- note\n' * 260)
        result = self.run_check()
        item = [i for i in result['items'] if i['kind'] == 'auto-memory'][0]
        self.assertEqual(item['lines'], 200)
        self.assertTrue(any('MEMORY.md' in f['message'] for f in result['flags']))

    def test_placeholders_warn(self):
        setup.init(self.project, make_folders=False)
        flags = self.run_check()['flags']
        self.assertTrue(any('placeholders' in f['message'] for f in flags))

    def test_empty_folder_says_run_init(self):
        self.assertTrue(any('aios-rules init' in f['message'] for f in self.run_check()['flags']))


class CodexCursorTests(Sandbox):
    def git(self, folder):
        subprocess.run(['git', 'init', '-q', str(folder)], check=True)

    def test_codex_reads_root_to_folder_with_override(self):
        self.git(self.project)
        self.write('AGENTS.md', '# Root\n')
        self.write('10_clients/AGENTS.md', '# Clients\n')
        self.write('10_clients/AGENTS.override.md', '# Override\n')
        self.write('.codex/AGENTS.md', '# Global\n', base=self.home)
        result = self.run_check('codex', project=self.project / '10_clients')
        self.assertEqual(self.paths(result), ['~/.codex/AGENTS.md', '~/acme/AGENTS.md', './AGENTS.override.md'])

    def test_codex_byte_limit(self):
        self.git(self.project)
        self.write('AGENTS.md', 'x' * (33 * 1024))
        result = self.run_check('codex', budgets={'total_tokens_max': 10 ** 6, 'total_lines_max': 10 ** 6})
        self.assertEqual(result['status'], 'over')
        self.assertTrue(any('Codex stops reading' in f['message'] for f in result['flags']))

    def test_cursor_always_and_scoped(self):
        self.write('AGENTS.md', '# Rules\n')
        self.write('.cursor/rules/a.mdc', '---\nalwaysApply: true\n---\n# A\n')
        self.write('.cursor/rules/b.mdc', '---\nglobs: 30_finance/**\nalwaysApply: false\n---\n# B\n')
        result = self.run_check('cursor')
        self.assertEqual(self.paths(result), ['./AGENTS.md', './.cursor/rules/a.mdc'])
        self.assertEqual(self.paths(result, 'on-demand'), ['./.cursor/rules/b.mdc'])

    def test_cursor_mirror_keeps_member_rules(self):
        setup.init(self.project, make_folders=False)
        self.write('.claude/rules/always.md', '# Always on\n- one\n')
        self.write('.cursor/rules/content.mdc', '# My own Cursor rule\n')
        report = setup.cursor_rules(self.project)
        self.assertIn('kept', [a for a, p, _ in report if Path(p).name == 'content.mdc'])
        self.assertEqual((self.project / '.cursor/rules/content.mdc').read_text(), '# My own Cursor rule\n')
        finance = (self.project / '.cursor/rules/finance.mdc').read_text()
        self.assertIn('globs: 30_finance/**', finance)
        self.assertIn('alwaysApply: false', finance)
        self.assertIn('alwaysApply: true', (self.project / '.cursor/rules/always.mdc').read_text())
        result = self.run_check('cursor')
        self.assertIn('./.cursor/rules/finance.mdc', self.paths(result, 'on-demand'))
        setup.cursor_rules(self.project)  # a second run rewrites only its own files
        self.assertIn('generated by aios-rules', (self.project / '.cursor/rules/finance.mdc').read_text())


class AuditTests(Sandbox):
    def fake_claude(self, body):
        script = self.tmp / 'fake-claude'
        script.write_text('#!/bin/sh\n' + body)
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
        return script

    def audit(self, **kwargs):
        old = dict(os.environ)
        try:
            os.environ['HOME'] = str(self.home)
            os.environ.pop('CLAUDE_CONFIG_DIR', None)
            os.environ.pop('CODEX_HOME', None)
            if 'claude' in kwargs:
                os.environ['AIOS_RULES_CLAUDE'] = str(kwargs.pop('claude'))
            return audit.audit(self.project, today=datetime.date(2026, 11, 1), **kwargs)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_writes_dated_file_with_both_reports(self):
        setup.init(self.project, 'Acme Studio', 'Sam Rivera')
        fake = self.fake_claude('echo "Report for $2"\n')
        path, status = self.audit(claude=fake)
        self.assertEqual(path, self.project / '80_aios/audits/2026-11-01_rules-audit_v1.md')
        text = path.read_text()
        self.assertIn('Report for /doctor prompt-audit', text)
        self.assertIn('Report for /skill-doctor', text)
        self.assertIn('Always loaded', text)
        self.assertEqual(status, {'budget': 'ok', 'prompt_audit': 'ok', 'skill_doctor': 'ok'})
        path2, _ = self.audit(claude=fake)
        self.assertTrue(path2.name.endswith('_v2.md'))

    def test_read_only_flags_are_passed(self):
        fake = self.fake_claude('echo "$@"\n')
        path, _ = self.audit(claude=fake)
        self.assertIn('--disallowedTools Edit,Write,Bash,NotebookEdit', path.read_text())

    def test_unavailable_command_is_reported_not_invented(self):
        fake = self.fake_claude('echo "\\`/skill-doctor\\` isn\'t installed in this session."\n')
        path, status = self.audit(claude=fake)
        self.assertEqual(status['skill_doctor'], 'unavailable')
        self.assertIn('Not available in this session', path.read_text())

    def test_failure_and_missing_claude(self):
        fake = self.fake_claude('echo boom >&2; exit 3\n')
        _, status = self.audit(claude=fake)
        self.assertEqual(status['prompt_audit'], 'failed')
        _, status = self.audit(claude=self.tmp / 'nope')
        self.assertEqual(status['prompt_audit'], 'failed')
        _, status = self.audit(run_claude=False)
        self.assertEqual(status['skill_doctor'], 'skipped')


class CliTests(Sandbox):
    def test_json_and_exit_codes(self):
        self.write('AGENTS.md', '- rule\n' * 250)
        old = dict(os.environ)
        os.environ['HOME'] = str(self.home)
        os.environ.pop('CLAUDE_CONFIG_DIR', None)
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli.main(['check', '--dir', str(self.project), '--json'])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out.getvalue())[0]['status'], 'over')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['check', '--dir', str(self.project), '--file-lines', '400', '--max-lines', '400']), 0)
                self.assertEqual(cli.main([]), 2)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_launcher_runs_through_a_symlink(self):
        link = self.tmp / 'bin' / 'aios-rules'
        link.parent.mkdir()
        link.symlink_to(PACK / 'bin' / 'aios-rules')
        out = subprocess.run([str(link), '--version'], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), 'aios-rules 2.0.0')


if __name__ == '__main__':
    unittest.main()
