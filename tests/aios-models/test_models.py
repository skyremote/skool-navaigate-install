"""Unit tests for plugins/aios-models. Fake CLIs on PATH; every home lives in /tmp."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins/aios-models'
TOOL = PACK / 'bin/models-check'
sys.path.insert(0, str(PACK))
from aios_models.check import redact, toml_values  # noqa: E402

FAKE_CLAUDE = '''#!/bin/sh
if [ "$1 $2" = "auth status" ]; then
  case "$CLAUDE_CONFIG_DIR" in
    *claude-work) echo '{"loggedIn": false, "authMethod": "none"}' ;;
    *) echo '{"loggedIn": true, "authMethod": "claude.ai", "subscriptionType": "max", "email": "owner@acme.example"}' ;;
  esac
fi
'''
FAKE_CODEX = '''#!/bin/sh
echo "Logged in using ChatGPT as owner@acme.example token sk-$(printf 'abcdefgh%.0s' 1 2 3 4)"
'''
FAKE_CURSOR = '''#!/bin/sh
echo "Not logged in"
exit 1
'''
FAKE_BB = '''#!/bin/sh
echo '{"accounts": [{"provider": "claude", "enabled": true, "label": "owner@acme.example"},
 {"provider": "claude", "enabled": true}, {"provider": "codex", "enabled": false}]}'
'''


class ModelsCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-models-test-', dir='/tmp')
        self.home = Path(self.tmp.name) / 'home'
        self.bin = Path(self.tmp.name) / 'bin'
        self.project = Path(self.tmp.name) / 'acme-site'
        for d in (self.home / '.claude', self.home / '.codex', self.bin, self.project / '.claude'):
            d.mkdir(parents=True)
        self.tools = {'claude': FAKE_CLAUDE, 'codex': FAKE_CODEX, 'cursor-agent': FAKE_CURSOR, 'bb': FAKE_BB}
        self.write_tools()

    def tearDown(self):
        self.tmp.cleanup()

    def write_tools(self):
        for name in list(self.bin.iterdir()):
            name.unlink()
        for name, body in self.tools.items():
            path = self.bin / name
            path.write_text(body)
            path.chmod(0o755)

    def settings(self, data, where='user'):
        path = {'user': self.home / '.claude/settings.json',
                'project': self.project / '.claude/settings.json',
                'local': self.project / '.claude/settings.local.json'}[where]
        path.write_text(json.dumps(data))

    def run_check(self, *args, env=None):
        base = {'HOME': str(self.home), 'PATH': str(self.bin) + ':/usr/bin:/bin'}
        base.update(env or {})
        return subprocess.run([sys.executable, str(TOOL), '--project', str(self.project), *args],
                              text=True, capture_output=True, env=base)

    def test_reports_model_effort_advisor_and_sources(self):
        self.settings({'model': 'sonnet', 'advisorModel': 'opus',
                       'modelSettings': {'claude-sonnet-5-5': {'effortLevel': 'medium'}}})
        out = self.run_check().stdout
        self.assertIn('model    sonnet   <- user', out)
        self.assertIn('effort   medium   <- modelSettings', out)
        self.assertIn('advisor  opus', out)
        self.assertIn('signed in (claude.ai, max)', out)

    def test_project_and_local_settings_win(self):
        self.settings({'model': 'sonnet'})
        self.settings({'model': 'opus'}, 'project')
        self.settings({'model': 'haiku'}, 'local')
        self.assertIn('model    haiku   <- local', self.run_check().stdout)

    def test_env_overrides_and_routing_warnings(self):
        self.settings({'model': 'sonnet'})
        result = self.run_check(env={'ANTHROPIC_MODEL': 'opus', 'CLAUDE_CODE_EFFORT_LEVEL': 'high',
                                     'ANTHROPIC_API_KEY': 'sk-ant-secret-value-that-must-not-print'})
        self.assertIn('model    opus   <- env ANTHROPIC_MODEL', result.stdout)
        self.assertIn('effort   high   <- env CLAUDE_CODE_EFFORT_LEVEL', result.stdout)
        self.assertIn('metered API', result.stdout)
        self.assertNotIn('secret-value', result.stdout)

    def test_xhigh_warns_and_strict_exits_1(self):
        self.settings({'effortLevel': 'xhigh'})
        result = self.run_check('--strict')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Start on medium', result.stdout)
        self.assertIn('older key', result.stdout)
        self.settings({})
        self.assertEqual(self.run_check('--strict').returncode, 0)

    def test_never_prints_emails_or_tokens(self):
        out = self.run_check().stdout + self.run_check('--json').stdout
        self.assertNotIn('owner@acme.example', out)
        self.assertNotIn('sk-' + 'abcdefgh' * 4, out)
        self.assertIn('<email>', out)

    def test_codex_cursor_and_bb_pool(self):
        (self.home / '.codex/config.toml').write_text('model = "gpt-acme"\nmodel_reasoning_effort = "medium"\n\n[profiles.work]\nmodel = "other"\n')
        out = self.run_check().stdout
        self.assertIn('Codex [default] ~/.codex', out)
        self.assertIn('model    gpt-acme   <- config.toml', out)
        self.assertIn('profiles work', out)
        self.assertIn('Cursor CLI', out)
        self.assertIn('login    signed out', out.split('Cursor CLI')[1])
        self.assertIn('bb account pool: 2 claude enabled, 1 codex disabled', out)
        self.assertIn('Claude logins ready for failover: 2', out)

    def test_missing_clis_are_reported_not_crashed(self):
        self.tools = {}
        self.write_tools()
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('claude not installed', result.stdout)
        self.assertIn('codex not installed', result.stdout)
        self.assertNotIn('bb account pool', result.stdout)
        self.assertIn('add a second one', result.stdout)

    def test_login_add_records_second_login(self):
        result = self.run_check('login', 'add', 'work')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / '.claude-work').is_dir())
        saved = json.loads((self.home / '.config/aios-models/logins.json').read_text())
        self.assertEqual(saved['logins'], [{'label': 'work', 'claude_config_dir': '~/.claude-work'}])
        self.assertIn("alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'", result.stdout)
        out = self.run_check().stdout
        self.assertIn('Claude Code [work] ~/.claude-work', out)
        self.assertIn('signed out', out.split('[work]')[1])
        self.assertEqual(self.run_check('login', 'add', 'Bad Label').returncode, 2)

    def test_env_token_is_not_counted_as_a_folder_login(self):
        self.run_check('login', 'add', 'work')
        out = self.run_check(env={'ANTHROPIC_AUTH_TOKEN': 'eyJ' + 'hbGciOiJIUzI1NiJ9-not-printed'}).stdout
        self.assertIn('through the environment (ANTHROPIC_AUTH_TOKEN)', out)
        self.assertIn('Claude logins ready for failover: 2', out)  # from the fake bb pool, not the folders
        self.assertIn('folder logins are not checked', out)
        self.assertNotIn('not-printed', out)
        self.tools.pop('bb')
        self.write_tools()
        out = self.run_check(env={'ANTHROPIC_AUTH_TOKEN': 'x'}).stdout
        self.assertIn('Claude logins ready for failover: 0', out)

    def test_json_shape(self):
        data = json.loads(self.run_check('--json').stdout)
        self.assertEqual([h['harness'] for h in data['harnesses']], ['Claude Code', 'Codex', 'Cursor CLI'])
        self.assertIn('warnings', data)


class Helpers(unittest.TestCase):
    def test_redact(self):
        self.assertEqual(redact('a@b.co eyJabcdefghijklmnop'), '<email> <hidden>')

    def test_toml_top_level_only(self):
        values, profiles = toml_values('model = "a"\n[profiles.fast]\nmodel = "b"\n', ('model',))
        self.assertEqual(values, {'model': 'a'})
        self.assertEqual(profiles, ['fast'])

    def test_skills_short(self):
        for skill in (PACK / 'skills').glob('*/SKILL.md'):
            self.assertLess(len(skill.read_text().splitlines()), 500)



class TourAndManifest(unittest.TestCase):
    def test_tour_is_short_and_manifest_has_module(self):
        import json as _json
        pack = Path(__file__).resolve().parents[2] / 'plugins/aios-models'
        tour = (pack / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('## Step 1', tour)
        manifest = _json.loads((pack / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['dependencies'], ['aios'])
        self.assertIsInstance(manifest['metadata']['module'], int)


if __name__ == '__main__':
    unittest.main()
