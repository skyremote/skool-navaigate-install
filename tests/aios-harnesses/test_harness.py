"""Unit tests for the aios-harnesses pack. Run: python3 -m unittest discover -s tests/aios-harnesses"""
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plugins/aios-harnesses'))
from aios_harnesses import harness as h  # noqa: E402
from aios_harnesses import tomlmini  # noqa: E402
from aios_harnesses.cli import main  # noqa: E402


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-harness-test-', dir='/tmp')
        base = Path(self.tmp.name).resolve()
        self.home = base / 'home'
        self.folder = base / 'acme-aios'
        self.home.mkdir()
        self.folder.mkdir()
        self.env = {'HOME': str(self.home), 'PATH': '/usr/bin:/bin'}
        self.p = h.Paths(self.folder, env=self.env)

    def tearDown(self):
        self.tmp.cleanup()

    def skill(self, root, name):
        d = Path(root) / name
        d.mkdir(parents=True)
        (d / 'SKILL.md').write_text('---\nname: %s\ndescription: Fictional skill.\n---\nBody\n' % name)
        return d

    def setup_folder(self):
        log, notes = h.setup(self.p, rng=random.Random(4))
        return log, notes

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        old = dict(os.environ)
        os.environ.update(self.env)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = main(['--folder', str(self.folder)] + list(argv))
        finally:
            os.environ.clear()
            os.environ.update(old)
        return code, out.getvalue(), err.getvalue()


class TomlTests(unittest.TestCase):
    SAMPLE = '''# comment
model = "gpt-fictional"
model_reasoning_effort = "medium"

[projects."/tmp/acme aios"]
trust_level = "trusted"

[mcp_servers.acme-notes]
command = "npx"
args = ["-y", "@acme/notes-mcp"]
env = { "ACME_MODE" = "read", OTHER = 'x' }
enabled = true

[mcp_servers.remote]
url = "https://mcp.acme.example/mcp"

[[skills.config]]
path = "/ignored"
'''

    def test_fallback_parser_matches_expected(self):
        data = tomlmini.loads(self.SAMPLE, force_fallback=True)
        self.assertEqual(data['model_reasoning_effort'], 'medium')
        self.assertEqual(data['projects']['/tmp/acme aios']['trust_level'], 'trusted')
        self.assertEqual(data['mcp_servers']['acme-notes']['args'], ['-y', '@acme/notes-mcp'])
        self.assertEqual(data['mcp_servers']['acme-notes']['env'], {'ACME_MODE': 'read', 'OTHER': 'x'})
        self.assertIs(data['mcp_servers']['acme-notes']['enabled'], True)
        self.assertEqual(data['mcp_servers']['remote']['url'], 'https://mcp.acme.example/mcp')
        self.assertNotIn('skills', data)

    def test_multiline_array_and_numbers(self):
        data = tomlmini.loads('a = [\n "x", # c\n "y",\n]\nn = 1_000\nf = 1.5\nb = false\n', force_fallback=True)
        self.assertEqual(data, {'a': ['x', 'y'], 'n': 1000, 'f': 1.5, 'b': False})

    def test_split_key(self):
        self.assertEqual(tomlmini.split_key('mcp_servers."my.server"'), ['mcp_servers', 'my.server'])
        with self.assertRaises(tomlmini.TomlError):
            tomlmini.split_key('a..b')


class SetupTests(Case):
    def test_setup_creates_rules_bridge_and_mcp_list(self):
        log, notes = self.setup_folder()
        self.assertEqual(notes, [])
        self.assertEqual((self.folder / 'CLAUDE.md').read_text(), '@AGENTS.md\n')
        agents = (self.folder / 'AGENTS.md').read_text()
        self.assertRegex(agents, r'Rules check phrase: [a-z]+-[a-z]+-\d\d')
        self.assertEqual(json.loads((self.folder / '.aios/mcp.json').read_text()), {'mcpServers': {}})
        self.assertTrue((self.home / '.agents/skills').is_dir())

    def test_setup_never_overwrites_existing_rules(self):
        (self.folder / 'AGENTS.md').write_text('# Acme rules\n- Be brief.\n')
        (self.folder / 'CLAUDE.md').write_text('Old Claude-only rules\n')
        log, notes = self.setup_folder()
        self.assertIn('- Be brief.', (self.folder / 'AGENTS.md').read_text())
        self.assertIn('Rules check phrase:', (self.folder / 'AGENTS.md').read_text())
        self.assertEqual((self.folder / 'CLAUDE.md').read_text(), 'Old Claude-only rules\n')
        self.assertTrue(any('CLAUDE.md has its own text' in n for n in notes))

    def test_dry_run_writes_nothing(self):
        log, _ = h.setup(self.p, dry_run=True)
        self.assertTrue(any(line.startswith('Would create') for line in log))
        self.assertEqual(list(self.folder.iterdir()), [])


class RulesTests(Case):
    def test_clean_folder_matches(self):
        self.setup_folder()
        rules = h.inspect_rules(self.p)
        self.assertEqual(rules['claude'][0], h.OK)
        self.assertEqual(rules['claude'][1], 'bridge')
        self.assertEqual(rules['codex'][0], h.OK)
        self.assertEqual(rules['cursor'][0], h.OK)
        self.assertEqual(rules['grok'][0], h.ASK)

    def test_missing_agents_md_is_a_difference(self):
        rules = h.inspect_rules(self.p)
        self.assertEqual(rules['codex'][0], h.DIFF)

    def test_claude_md_without_bridge(self):
        self.setup_folder()
        (self.folder / 'CLAUDE.md').write_text('# Old rules\n- Use American spelling.\n')
        self.assertEqual(h.inspect_rules(self.p)['claude'][0], h.DIFF)

    def test_claude_md_bridge_plus_extra(self):
        self.setup_folder()
        (self.folder / 'CLAUDE.md').write_text('@AGENTS.md\n- Claude only rule\n')
        status, summary, issues = h.inspect_rules(self.p)['claude']
        self.assertEqual((status, summary), (h.DIFF, 'bridge + extra'))

    def test_html_comment_does_not_count(self):
        self.setup_folder()
        (self.folder / 'CLAUDE.md').write_text('<!-- bridge -->\n@AGENTS.md\n')
        self.assertEqual(h.inspect_rules(self.p)['claude'][0], h.OK)

    def test_codex_override_file(self):
        self.setup_folder()
        (self.folder / 'AGENTS.override.md').write_text('- Different\n')
        self.assertEqual(h.inspect_rules(self.p)['codex'][0], h.DIFF)

    def test_cursor_always_apply_rule_differs_but_glob_rule_warns(self):
        self.setup_folder()
        rules = self.folder / '.cursor/rules'
        rules.mkdir(parents=True)
        (rules / 'globbed.mdc').write_text('---\nglobs: "*.ts"\nalwaysApply: false\n---\n- TS only\n')
        self.assertEqual(h.inspect_rules(self.p)['cursor'][0], h.WARN)
        (rules / 'old.mdc').write_text('---\nalwaysApply: true\n---\n- Old rule\n')
        self.assertEqual(h.inspect_rules(self.p)['cursor'][0], h.DIFF)

    def test_global_personal_rules_only_warn(self):
        self.setup_folder()
        (self.home / '.codex').mkdir()
        (self.home / '.codex/AGENTS.md').write_text('- personal\n')
        self.assertEqual(h.inspect_rules(self.p)['codex'][0], h.WARN)


class SkillTests(Case):
    def test_shared_skill_needs_a_link_for_claude_only(self):
        self.skill(self.home / '.agents/skills', 'acme-weekly-report')
        skills, notes, count = h.inspect_skills(self.p)
        self.assertEqual(count, 1)
        self.assertEqual(skills['claude'][0], h.DIFF)
        self.assertEqual(skills['codex'][0], h.OK)
        self.assertEqual(skills['cursor'][0], h.OK)
        h.sync(self.p)
        link = self.home / '.claude/skills/acme-weekly-report'
        self.assertTrue(link.is_symlink())
        self.assertEqual(h.inspect_skills(self.p)[0]['claude'][0], h.OK)

    def test_skill_outside_shared_folder_is_reported(self):
        self.skill(self.home / '.claude/skills', 'claude-only')
        _, notes, _ = h.inspect_skills(self.p)
        self.assertTrue(any('claude-only' in n and 'Claude Code and Cursor' in n for n in notes))

    def test_sync_leaves_real_folders_alone(self):
        self.skill(self.home / '.agents/skills', 'acme-invoice')
        self.skill(self.home / '.claude/skills', 'acme-invoice')
        log, conflicts = h.sync(self.p)
        self.assertTrue(any('real folder' in c for c in conflicts))
        self.assertFalse((self.home / '.claude/skills/acme-invoice').is_symlink())

    def test_broken_link_is_reported_and_replaced(self):
        self.skill(self.home / '.agents/skills', 'acme-brief')
        (self.home / '.claude/skills').mkdir(parents=True)
        (self.home / '.claude/skills/acme-brief').symlink_to(self.home / 'gone')
        _, notes, _ = h.inspect_skills(self.p)
        self.assertTrue(any('Broken skill link' in n for n in notes))
        h.sync(self.p)
        self.assertTrue((self.home / '.claude/skills/acme-brief/SKILL.md').is_file())

    def test_claude_config_dir_is_honoured(self):
        env = dict(self.env, CLAUDE_CONFIG_DIR=str(self.home / 'alt-claude'))
        p = h.Paths(self.folder, env=env)
        self.skill(self.home / '.agents/skills', 'acme-brief')
        h.sync(p)
        self.assertTrue((self.home / 'alt-claude/skills/acme-brief').is_symlink())


class McpTests(Case):
    def test_add_writes_every_harness_and_check_passes(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['-y', '@acme/notes-mcp'],
                  env={'ACME_TOKEN': '${ACME_TOKEN}', 'ACME_MODE': 'read'})
        claude = json.loads((self.folder / '.mcp.json').read_text())['mcpServers']['acme-notes']
        cursor = json.loads((self.folder / '.cursor/mcp.json').read_text())['mcpServers']['acme-notes']
        codex = tomlmini.loads((self.folder / '.codex/config.toml').read_text(), force_fallback=True)['mcp_servers']['acme-notes']
        self.assertEqual(claude['env']['ACME_TOKEN'], '${ACME_TOKEN}')
        self.assertEqual(cursor['env']['ACME_TOKEN'], '${env:ACME_TOKEN}')
        self.assertEqual(codex['env_vars'], ['ACME_TOKEN'])
        self.assertEqual(codex['env'], {'ACME_MODE': 'read'})
        report = h.check(self.p)
        self.assertEqual(report['differs'], [])

    def test_secret_literal_is_refused(self):
        self.setup_folder()
        with self.assertRaises(ValueError):
            h.mcp_add(self.p, 'acme', command='x', env={'ACME_API_KEY': 'abcdefgh12345'})

    def test_missing_server_in_codex_is_a_difference_and_sync_fixes_it(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['@acme/notes-mcp'])
        (self.folder / '.codex/config.toml').write_text('')
        mcp, _, _ = h.inspect_mcp(self.p)
        self.assertEqual(mcp['codex'][0], h.DIFF)
        self.assertIn('missing MCP server "acme-notes"', mcp['codex'][2][0])
        h.sync(self.p)
        self.assertEqual(h.inspect_mcp(self.p)[0]['codex'][1], '1/1')

    def test_different_command_is_a_difference(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['@acme/notes-mcp'])
        data = json.loads((self.folder / '.cursor/mcp.json').read_text())
        data['mcpServers']['acme-notes']['args'] = ['@acme/old-notes']
        (self.folder / '.cursor/mcp.json').write_text(json.dumps(data))
        self.assertEqual(h.inspect_mcp(self.p)[0]['cursor'][0], h.DIFF)

    def test_user_level_servers_count(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['@acme/notes-mcp'])
        (self.folder / '.cursor/mcp.json').unlink()
        (self.home / '.cursor').mkdir()
        (self.home / '.cursor/mcp.json').write_text(json.dumps({'mcpServers': {'acme-notes': {'command': 'npx', 'args': ['@acme/notes-mcp']}}}))
        self.assertEqual(h.inspect_mcp(self.p)[0]['cursor'][0], h.OK)

    def test_extra_server_only_warns(self):
        self.setup_folder()
        (self.home / '.cursor').mkdir()
        (self.home / '.cursor/mcp.json').write_text(json.dumps({'mcpServers': {'other': {'command': 'x'}}}))
        self.assertEqual(h.inspect_mcp(self.p)[0]['cursor'][0], h.WARN)

    def test_codex_member_tables_are_kept_and_clashes_refused(self):
        self.setup_folder()
        codex = self.folder / '.codex/config.toml'
        codex.write_text('[mcp_servers.mine]\ncommand = "mine"\n')
        h.mcp_add(self.p, 'acme-notes', command='npx', args=[])
        text = codex.read_text()
        self.assertIn('[mcp_servers.mine]', text)
        self.assertIn(h.BEGIN, text)
        self.assertEqual(text.count(h.BEGIN), 1)
        h.sync(self.p)
        self.assertEqual(codex.read_text().count(h.BEGIN), 1)
        codex.write_text(text + '\n[mcp_servers.dup]\ncommand = "a"\n')
        data = json.loads((self.folder / '.aios/mcp.json').read_text())
        data['mcpServers']['dup'] = {'command': 'b', 'args': []}
        (self.folder / '.aios/mcp.json').write_text(json.dumps(data))
        _, conflicts = h.sync(self.p)
        self.assertTrue(any('already defines dup' in c for c in conflicts))

    def test_remove_cleans_json_files(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=[])
        h.mcp_remove(self.p, 'acme-notes')
        self.assertNotIn('acme-notes', json.loads((self.folder / '.mcp.json').read_text())['mcpServers'])
        self.assertNotIn('acme-notes', (self.folder / '.codex/config.toml').read_text())

    def test_backup_only_when_someone_else_wrote_the_file(self):
        self.setup_folder()
        h.mcp_add(self.p, 'a', command='x', args=[])
        before = sorted(x.name for x in self.folder.iterdir())
        h.mcp_add(self.p, 'b', command='y', args=[])
        self.assertEqual(before, sorted(x.name for x in self.folder.iterdir()))
        (self.folder / '.mcp.json').write_text('{"mcpServers": {}}')
        h.sync(self.p)
        self.assertTrue(any(x.name.startswith('.mcp.json.backup-') for x in self.folder.iterdir()))

    def test_claude_approval_states(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=[])
        self.assertEqual(h.claude_approval(self.p, 'acme-notes'), 'pending')
        (self.home / '.claude.json').write_text(json.dumps({'projects': {str(self.folder): {'disabledMcpjsonServers': ['acme-notes']}}}))
        self.assertEqual(h.inspect_mcp(self.p)[0]['claude'][0], h.DIFF)
        (self.home / '.claude.json').write_text(json.dumps({'projects': {str(self.folder): {'enabledMcpjsonServers': ['acme-notes']}}}))
        self.assertEqual(h.claude_approval(self.p, 'acme-notes'), 'approved')


class GrokTests(Case):
    def test_without_report_grok_is_ask(self):
        self.setup_folder()
        report = h.check(self.p)
        statuses = [row['grok'][0] for _, row in report['rows']]
        self.assertEqual(statuses, [h.ASK, h.ASK, h.ASK])

    def test_report_compared(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['@acme/notes-mcp'])
        phrase = h.check_phrase((self.folder / 'AGENTS.md').read_text())
        (self.folder / '.aios/grok-bot.txt').write_text('RULES: %s\nMCP:\nweb-search\n' % phrase)
        report = h.check(self.p)
        self.assertTrue(any('Grok Bot is missing MCP server "acme-notes"' in d for d in report['differs']))
        (self.folder / '.aios/grok-bot.txt').write_text('RULES: %s\nMCP:\nacme-notes\n' % phrase)
        self.assertEqual(h.check(self.p)['differs'], [])

    def test_instructions_name_env_but_never_values(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=['@acme/notes-mcp'], env={'ACME_TOKEN': '${ACME_TOKEN}'})
        text = h.grok_instructions(self.p)
        self.assertIn('Name: acme-notes', text)
        self.assertIn('ACME_TOKEN', text)
        self.assertNotIn('${ACME_TOKEN}', text)
        self.assertIn('Rules check phrase', text.replace('rules check phrase', 'Rules check phrase'))


class LiveTests(Case):
    def test_live_uses_cli_answers(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=[])
        phrase = h.check_phrase((self.folder / 'AGENTS.md').read_text())
        bindir = self.home / 'bin'
        bindir.mkdir()
        for name in ('claude', 'codex', 'cursor-agent'):
            script = bindir / name
            script.write_text('#!/bin/sh\necho ok\n')
            script.chmod(0o755)
        env = dict(self.env, PATH=str(bindir) + ':/usr/bin:/bin')
        p = h.Paths(self.folder, env=env)

        def runner(cmd, **kw):
            if 'mcp' in cmd:
                out = 'acme-notes: npx' if cmd[0] != 'codex' else 'nothing'
            else:
                out = phrase if cmd[0] != 'cursor-agent' else 'wrong-phrase-00'
            return subprocess.CompletedProcess(cmd, 0, out, '')
        results = h.run_live(p, h.canonical_servers(p), runner=runner)
        self.assertEqual(results['claude'][0], h.OK)
        self.assertEqual(results['codex'][0], h.DIFF)
        self.assertEqual(results['cursor'][0], h.DIFF)

    def test_live_skips_missing_cli(self):
        self.setup_folder()
        results = h.run_live(self.p, {}, runner=lambda *a, **k: None)
        self.assertEqual(results['claude'][0], h.WARN)


class DefaultsTests(Case):
    def test_apply_defaults_is_valid_toml_and_idempotent(self):
        self.setup_folder()
        h.mcp_add(self.p, 'acme-notes', command='npx', args=[])
        h.apply_defaults(self.p)
        text = (self.folder / '.codex/config.toml').read_text()
        data = tomlmini.loads(text, force_fallback=True)
        self.assertEqual(data['model_reasoning_effort'], 'medium')
        self.assertIn('acme-notes', data['mcp_servers'])
        h.apply_defaults(self.p)
        self.assertEqual((self.folder / '.codex/config.toml').read_text(), text)
        h.sync(self.p)
        self.assertEqual(tomlmini.loads((self.folder / '.codex/config.toml').read_text())['model_reasoning_effort'], 'medium')
        self.assertEqual(json.loads((self.folder / '.claude/settings.json').read_text())['effortLevel'], 'medium')

    def test_defaults_rows(self):
        rows = h.defaults(self.p)
        self.assertEqual([r[0] for r in rows], ['claude', 'codex', 'cursor', 'grok'])


class CliTests(Case):
    def test_check_exit_codes_and_json(self):
        code, out, _ = self.run_cli('check')
        self.assertEqual(code, 1)
        self.assertIn('What differs', out)
        self.run_cli('setup')
        code, out, _ = self.run_cli('check', '--json')
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)['ok'])

    def test_mcp_add_list_remove(self):
        self.run_cli('setup')
        code, out, _ = self.run_cli('mcp', 'add', 'acme-notes', '--', 'npx', '-y', '@acme/notes-mcp')
        self.assertEqual(code, 0, out)
        code, out, _ = self.run_cli('mcp', 'list')
        self.assertIn('acme-notes: npx -y @acme/notes-mcp', out)
        code, out, _ = self.run_cli('mcp', 'add', 'tok', '--env', 'TOK=${TOK}', '--', 'npx', '-y', 'tok-mcp')
        self.assertEqual(code, 0, out)
        server = json.loads((self.folder / '.aios/mcp.json').read_text())['mcpServers']['tok']
        self.assertEqual(server, {'command': 'npx', 'args': ['-y', 'tok-mcp'], 'env': {'TOK': '${TOK}'}})
        code, out, err = self.run_cli('mcp', 'add', 'leak', '--env', 'ACME_API_KEY=abcd1234efgh5678', '--', 'npx')
        self.assertEqual(code, 2)
        self.assertIn('looks like a secret', err)
        code, out, err = self.run_cli('mcp', 'add', 'bad name', '--', 'x')
        self.assertEqual(code, 2)
        code, out, _ = self.run_cli('mcp', 'remove', 'acme-notes')
        self.assertEqual(code, 0)

    def test_grok_and_defaults_commands(self):
        self.run_cli('setup')
        code, out, _ = self.run_cli('grok')
        self.assertIn('Grok Bot setup', out)
        code, out, _ = self.run_cli('defaults')
        self.assertIn('Claude Code', out)

    def test_bin_script_runs(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'plugins/aios-harnesses/bin/harness'), '--version'],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn('2.0.0', proc.stdout)


if __name__ == '__main__':
    unittest.main()
