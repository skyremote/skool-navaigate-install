"""Unit tests for the aios-verify pack. Run from the repository root:
python3 -m unittest discover -s tests/aios-verify -v

Fake secrets are built by joining strings, so no secret-shaped text sits in this file.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins' / 'aios-verify'
SAMPLE = PACK / 'examples' / 'sample-app'
sys.path.insert(0, str(PACK))

from aios_verify import checks, gate, guard, screenshot, setup  # noqa: E402
from aios_verify.cli import main  # noqa: E402

FAKE = {
    'anthropic': 'sk-' + 'ant-' + 'a1B2c3D4' * 4,
    'aws': 'AK' + 'IA' + 'ABCDEFGHIJKLMNOP',
    'github': 'gh' + 'p_' + 'x' * 36,
    'key': '-----BEGIN ' + 'RSA PRIVATE KEY-----',
    'setting': 'api_key = "' + 'q' * 24 + '"',
}


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Acme', '-c', 'user.email=a@example.com'] + list(args),
                          cwd=str(cwd), capture_output=True, text=True, check=True)


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-verify-test-')
        self.repo = Path(self.tmp.name) / 'acme'
        shutil.copytree(SAMPLE, self.repo)
        git(self.repo, 'init', '-q')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', 'Start')

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def break_code(self):
        path = self.repo / 'prices.py'
        path.write_text(path.read_text().replace('{:02d}', '{:d}'))


class DestructiveGitTests(unittest.TestCase):
    def deny(self, command):
        decision, reason = guard.decide(command)
        self.assertEqual(decision, 'deny', command)
        self.assertIn('no destructive git', reason)

    def test_denied(self):
        for command in ('git push --force', 'git push -f origin feature', 'git push origin +feature',
                        'git push --mirror', 'git push origin --delete old', 'git push origin :old',
                        'git reset --hard', 'git reset --hard HEAD~2', 'git clean -fd', 'git clean -xfd',
                        'git clean --force', 'git checkout -- .', 'git checkout .', 'git restore .',
                        'git branch -D old', 'git branch --delete --force old', 'git stash drop',
                        'git stash clear', 'git filter-branch --tree-filter x', 'git reflog expire --all',
                        'git update-ref -d refs/heads/x', 'git gc --prune=now',
                        'cd app && git push --force', 'echo hi; git reset --hard', 'FOO=1 git -C repo push -f',
                        'sudo git clean -f', '/usr/bin/git reset --hard'):
            self.deny(command)

    def test_allowed(self):
        for command in ('git status', 'git push', 'git push origin feature', 'git push --force-with-lease',
                        'git reset --soft HEAD~1', 'git reset HEAD file.py', 'git clean -n',
                        'git checkout -- app.py', 'git checkout -b new', 'git restore --staged .',
                        'git restore app.py', 'git branch -d merged', 'git stash', 'git stash pop',
                        'git log --oneline', 'echo "git reset --hard"', 'rm -rf build'):
            decision, _ = guard.decide(command, cwd=tempfile.gettempdir())
            self.assertNotEqual(decision, 'deny', command)

    def test_unbalanced_quotes_do_not_crash(self):
        self.assertEqual(guard.decide("git push --force 'oops")[0], 'deny')


class ProductionTests(Repo):
    def ask(self, command, cwd=None):
        decision, reason = guard.decide(command, cwd=str(cwd or self.repo))
        self.assertEqual(decision, 'ask', command)
        self.assertIn('confirm before live production', reason)

    def test_deploy_commands_ask(self):
        for command in ('vercel --prod', 'vercel deploy --prod --yes', 'npx vercel --prod', 'netlify deploy --prod',
                        'npm publish', 'pnpm publish --access public', 'twine upload dist/*', 'fly deploy',
                        'railway up', 'firebase deploy', 'wrangler deploy', 'terraform apply -auto-approve',
                        'kubectl apply -f prod.yaml', 'supabase db push', 'gh release create v1.0',
                        'docker push acme/app', 'git push heroku main', 'npm test && npm publish'):
            self.ask(command)

    def test_preview_deploys_do_not_ask(self):
        for command in ('vercel', 'vercel deploy', 'netlify deploy', 'terraform plan', 'npm pack', 'kubectl get pods'):
            self.assertIsNone(guard.decide(command, cwd=str(self.repo))[0], command)

    def test_push_to_main_asks_explicit_and_implicit(self):
        self.ask('git push origin main')
        self.ask('git push origin HEAD:main')
        self.ask('git push origin feature:refs/heads/master')
        self.ask('git push')  # current branch of the fixture is main or master
        git(self.repo, 'checkout', '-qb', 'feature')
        self.assertIsNone(guard.decide('git push', cwd=str(self.repo))[0])
        self.assertIsNone(guard.decide('git push origin feature', cwd=str(self.repo))[0])

    def test_custom_production_commands(self):
        (self.repo / '.aios').mkdir()
        (self.repo / '.aios/verify.json').write_text(json.dumps(
            {'checks': [{'name': 't', 'run': 'true'}], 'production_commands': [r'\./deploy\.sh', '[bad']}))
        extra = guard.load_extra(self.repo)
        self.assertEqual(guard.decide('./deploy.sh live', str(self.repo), extra)[0], 'ask')
        self.assertIsNone(guard.decide('./build.sh', str(self.repo), extra)[0])

    def test_destructive_wins_over_production(self):
        self.assertEqual(guard.decide('git push --force origin main', cwd=str(self.repo))[0], 'deny')


class SecretTests(Repo):
    def stage(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        git(self.repo, 'add', name)

    def test_each_secret_kind_blocks_commit(self):
        for kind, value in FAKE.items():
            with self.subTest(kind=kind):
                self.stage('config_%s.py' % kind, 'VALUE = %r\n%s\n' % (value, value))
                decision, reason = guard.decide('git commit -m "add config"', cwd=str(self.repo))
                self.assertEqual(decision, 'deny')
                self.assertIn('no secrets in commits', reason)
                self.assertIn('config_%s.py' % kind, reason)
                self.assertNotIn(value, reason)
                git(self.repo, 'reset', '-q')
                (self.repo / ('config_%s.py' % kind)).unlink()

    def test_env_file_blocks_but_example_does_not(self):
        self.stage('.env', 'NAME=acme\n')
        self.assertEqual(guard.decide('git commit -m x', cwd=str(self.repo))[0], 'deny')
        git(self.repo, 'reset', '-q')
        (self.repo / '.env').unlink()
        self.stage('.env.example', 'API_KEY=\n')
        self.assertIsNone(guard.decide('git commit -m x', cwd=str(self.repo))[0])

    def test_clean_commit_allowed(self):
        self.stage('notes.md', 'Ordinary text, password policy is in the handbook.\n')
        self.assertIsNone(guard.decide('git commit -m notes', cwd=str(self.repo))[0])

    def test_commit_all_scans_unstaged_tracked_changes(self):
        path = self.repo / 'prices.py'
        path.write_text(path.read_text() + '\nTOKEN = %r\n' % FAKE['github'])
        self.assertIsNone(guard.decide('git commit -m x', cwd=str(self.repo))[0])
        self.assertEqual(guard.decide('git commit -am x', cwd=str(self.repo))[0], 'deny')
        self.assertEqual(guard.decide('git commit --all -m x', cwd=str(self.repo))[0], 'deny')

    def test_git_dash_c_scans_that_repo(self):
        self.stage('k.pem', 'x\n')
        decision, _ = guard.decide('git -C %s commit -m x' % self.repo, cwd=tempfile.gettempdir())
        self.assertEqual(decision, 'deny')

    def test_scan_command(self):
        self.stage('a.py', FAKE['aws'] + '\n')
        code, out, _ = self.run_cli('scan', '--path', str(self.repo))
        self.assertEqual(code, 1)
        self.assertIn('a.py: AWS access key', out)
        self.assertNotIn(FAKE['aws'], out)


class HookPayloadTests(Repo):
    def test_hook_json_shape(self):
        answer = guard.hook({'tool_name': 'Bash', 'cwd': str(self.repo), 'tool_input': {'command': 'git reset --hard'}})
        output = answer['hookSpecificOutput']
        self.assertEqual((output['hookEventName'], output['permissionDecision']), ('PreToolUse', 'deny'))
        self.assertIsNone(guard.hook({'tool_name': 'Read', 'tool_input': {'file_path': 'x'}}))
        self.assertIsNone(guard.hook({'tool_name': 'Bash', 'cwd': str(self.repo), 'tool_input': {'command': 'ls'}}))

    def test_bin_guard_reads_stdin_and_never_crashes(self):
        payload = json.dumps({'tool_name': 'Bash', 'cwd': str(self.repo), 'tool_input': {'command': 'vercel --prod'}})
        proc = subprocess.run([str(PACK / 'bin/aios-verify'), 'guard'], input=payload, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)['hookSpecificOutput']['permissionDecision'], 'ask')
        proc = subprocess.run([str(PACK / 'bin/aios-verify'), 'guard'], input='not json', capture_output=True, text=True)
        self.assertEqual((proc.returncode, proc.stdout), (0, ''))

    def test_hooks_json_points_at_bin(self):
        hooks = json.loads((PACK / 'hooks/hooks.json').read_text())['hooks']
        self.assertEqual(hooks['PreToolUse'][0]['matcher'], 'Bash')
        self.assertIn('aios-verify guard', hooks['PreToolUse'][0]['hooks'][0]['command'])
        self.assertIn('aios-verify gate', hooks['Stop'][0]['hooks'][0]['command'])
        self.assertIn('${CLAUDE_PLUGIN_ROOT}', hooks['Stop'][0]['hooks'][0]['command'])


class SetupTests(Repo):
    def test_init_writes_everything_once(self):
        written, skipped = setup.apply(self.repo)
        for name in ('.aios/verify.json', '.claude/skills/verify/SKILL.md', 'REVIEW.md', '.github/pull_request_template.md'):
            self.assertIn(name, written)
            self.assertTrue((self.repo / name).exists())
        config = json.loads((self.repo / '.aios/verify.json').read_text())
        names = [c['name'] for c in config['checks']]
        self.assertEqual(names, ['tests', 'build', 'screenshot'])
        self.assertIs(config['checks'][2]['gate'], False)
        self.assertIn('.aios/verify-state.json', (self.repo / '.gitignore').read_text())
        (self.repo / 'REVIEW.md').write_text('mine')
        written, skipped = setup.apply(self.repo)
        self.assertEqual(written, [])
        self.assertIn('REVIEW.md', skipped)
        self.assertEqual((self.repo / 'REVIEW.md').read_text(), 'mine')

    def test_templates_have_the_required_sections(self):
        template = (PACK / 'templates/github/pull_request_template.md').read_text()
        for heading in ('## Testing', '## Risk', '## How to revert'):
            self.assertIn(heading, template)
        skill = (PACK / 'templates/verify-SKILL.md').read_text()
        self.assertIn('name: verify\n', skill)
        self.assertIn('aios-verify run', skill)

    def test_git_hook_and_dry_run(self):
        written, _ = setup.apply(self.repo, git_hook=True, dry_run=True)
        self.assertIn('.git/hooks/pre-commit', written)
        self.assertFalse((self.repo / '.aios').exists())
        setup.apply(self.repo, git_hook=True)
        self.assertTrue(os.access(self.repo / '.git/hooks/pre-commit', os.X_OK))
        with tempfile.TemporaryDirectory() as plain:
            with self.assertRaises(ValueError):
                setup.apply(plain, git_hook=True)

    def test_detect_node_and_make(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'package.json').write_text(json.dumps({'scripts': {'test': 'vitest', 'build': 'vite build'}}))
            (root / 'pnpm-lock.yaml').write_text('')
            self.assertEqual([c['run'] for c in setup.detect_checks(root)], ['pnpm test', 'pnpm run build'])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'Makefile').write_text('test:\n\techo ok\nbuild:\n\techo ok\n')
            self.assertEqual([c['run'] for c in setup.detect_checks(tmp)], ['make test', 'make build'])
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(setup.detect_checks(tmp), [])
            config = dict((p, c) for p, c, _ in setup.plan(tmp))
            self.assertIn('exit 1', config['.aios/verify.json'])


class ChecksTests(Repo):
    def setUp(self):
        super().setUp()
        setup.apply(self.repo)

    def test_run_passes_then_fails_with_output(self):
        results = checks.run_checks(self.repo, gate_only=True)
        self.assertEqual([r['passed'] for r in results], [True, True])
        self.break_code()
        failed = checks.run_checks(self.repo, gate_only=True)[0]
        self.assertFalse(failed['passed'])
        self.assertIn('£0.05', failed['tail'])
        self.assertIn('FAIL  tests', checks.format_results([failed]))

    def test_cli_run_exit_codes(self):
        self.assertEqual(self.run_cli('run', '--path', str(self.repo), '--gate-only')[0], 0)
        self.break_code()
        code, out, _ = self.run_cli('run', '--path', str(self.repo), '--gate-only')
        self.assertEqual(code, 1)
        self.assertIn('1 of 2 checks passed', out)
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(self.run_cli('run', '--path', empty)[0], 2)

    def test_timeout(self):
        (self.repo / '.aios/verify.json').write_text(json.dumps({'checks': [{'name': 'slow', 'run': 'sleep 5'}]}))
        result = checks.run_checks(self.repo, timeout=1)[0]
        self.assertEqual(result['exit'], 124)
        self.assertIn('Timed out', result['tail'])

    def test_bad_config(self):
        (self.repo / '.aios/verify.json').write_text('{"checks": []}')
        with self.assertRaises(checks.ConfigError):
            checks.load(self.repo)
        (self.repo / '.aios/verify.json').write_text('{oops')
        with self.assertRaises(checks.ConfigError):
            checks.load(self.repo)


class GateTests(Repo):
    def setUp(self):
        super().setUp()
        setup.apply(self.repo)
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', 'Add verification')
        self.payload = {'cwd': str(self.repo), 'hook_event_name': 'Stop', 'stop_hook_active': False}

    def test_no_config_means_no_gate(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(gate.evaluate({'cwd': plain}))

    def test_passing_project_is_allowed_and_cached(self):
        self.assertIsNone(gate.evaluate(self.payload))
        state = gate.read_state(self.repo)
        self.assertEqual(state['passed'], gate.fingerprint(self.repo))
        (self.repo / '.aios/verify.json').write_text(json.dumps({'checks': [{'name': 'boom', 'run': 'exit 1'}]}))
        # Only .aios changed, which the fingerprint ignores, so the cached pass stands.
        self.assertIsNone(gate.evaluate(self.payload))

    def test_failing_change_blocks_with_output_then_gives_up(self):
        self.break_code()
        for attempt in (1, 2, 3):
            answer = gate.evaluate(self.payload)
            self.assertEqual(answer['decision'], 'block')
            self.assertIn('attempt %d of 3' % attempt, answer['reason'])
            self.assertIn('£0.05', answer['reason'])
        final = gate.evaluate(dict(self.payload, stop_hook_active=True))
        self.assertNotIn('decision', final)
        self.assertIn('Do not treat the work as done', final['systemMessage'])

    def test_fix_resets_and_passes(self):
        self.break_code()
        self.assertEqual(gate.evaluate(self.payload)['decision'], 'block')
        git(self.repo, 'checkout', '-q', 'prices.py')
        self.assertIsNone(gate.evaluate(self.payload))

    def test_new_untracked_file_changes_fingerprint(self):
        before = gate.fingerprint(self.repo)
        (self.repo / 'new.py').write_text('x = 1\n')
        self.assertNotEqual(before, gate.fingerprint(self.repo))

    def test_screenshot_check_not_in_gate(self):
        config = json.loads((self.repo / '.aios/verify.json').read_text())
        config['checks'][2]['run'] = 'exit 1'
        (self.repo / '.aios/verify.json').write_text(json.dumps(config))
        (self.repo / 'new.py').write_text('x = 1\n')
        self.assertIsNone(gate.evaluate(self.payload))

    def test_bin_gate_outputs_block_json(self):
        self.break_code()
        proc = subprocess.run([str(PACK / 'bin/aios-verify'), 'gate'], input=json.dumps(self.payload),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)['decision'], 'block')

    def test_bad_config_does_not_trap(self):
        (self.repo / '.aios/verify.json').write_text('{oops')
        self.assertIn('skipped', gate.evaluate(self.payload)['systemMessage'])


class ScreenshotTests(Repo):
    def test_missing_file_and_missing_browser(self):
        with self.assertRaises(FileNotFoundError):
            screenshot.target_url('dist/index.html', cwd=self.repo)
        old = os.environ.get('AIOS_VERIFY_BROWSER')
        os.environ['AIOS_VERIFY_BROWSER'] = '/nonexistent/browser'
        try:
            original = screenshot.CANDIDATES
            screenshot.CANDIDATES = []
            with self.assertRaises(RuntimeError):
                screenshot.take('https://example.com', cwd=self.repo)
        finally:
            screenshot.CANDIDATES = original
            if old is None:
                os.environ.pop('AIOS_VERIFY_BROWSER', None)
            else:
                os.environ['AIOS_VERIFY_BROWSER'] = old

    def test_real_screenshot_when_a_browser_exists(self):
        if not screenshot.find_browser():
            self.skipTest('no Chrome, Chromium or Edge on this machine')
        subprocess.run([sys.executable, 'build.py'], cwd=str(self.repo), check=True, capture_output=True)
        out = screenshot.take('dist/index.html', cwd=self.repo)
        self.assertGreater(out.stat().st_size, 1000)
        self.assertEqual(out.read_bytes()[:4], b'\x89PNG')


class PackTests(unittest.TestCase):
    def test_manifest_and_entry(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual((data['name'], data['version'], data['dependencies']), ('aios-verify', '2.0.0', ['aios']))
        self.assertEqual(data['author']['name'], 'skyremote')
        self.assertEqual(json.loads((PACK / 'MARKETPLACE_ENTRY.json').read_text())['source'], './plugins/aios-verify')

    def test_try_command(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(['try', 'git push --force'])
        self.assertTrue(out.getvalue().startswith('DENY'))

    def test_three_evals_load_aios(self):
        prompts = sorted((PACK / 'evals').glob('*/prompt.md'))
        self.assertEqual(len(prompts), 3)
        for prompt in prompts:
            self.assertIn('"../../../aios"', prompt.read_text())



class TourAndModuleTests(unittest.TestCase):
    def test_module_number_and_tour(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(data['metadata'], {'module': 8})
        self.assertEqual(data['dependencies'], ['aios'])
        tour = (PACK / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('/aios learn 8', tour)
        for label in ('**Do:**', '**Command:**', '**They should see:**', '**Check:**'):
            self.assertIn(label, tour)


if __name__ == '__main__':
    unittest.main()
