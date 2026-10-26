"""Unit tests for tools-inbox. No network: Composio is replaced by a fake."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-inbox'
sys.path.insert(0, str(PACK))

from tools_inbox import cli, composio, guard, triage  # noqa: E402

ACCOUNTS = {'items': [
    {'id': 'ca_gmail1', 'toolkit': {'slug': 'gmail'}, 'status': 'ACTIVE', 'user_id': 'owner@example.com'},
    {'id': 'ca_cal', 'toolkit': {'slug': 'googlecalendar'}, 'status': 'ACTIVE', 'user_id': 'owner@example.com'},
    {'id': 'ca_old', 'toolkit': 'gmail', 'status': 'EXPIRED', 'user_id': 'old@example.com'}]}


class Fake:
    def __init__(self, accounts=ACCOUNTS, send_ok=True):
        self.accounts, self.send_ok, self.calls = accounts, send_ok, []

    def __call__(self, method, path, key, body=None):
        self.calls.append((method, path, body))
        if path.startswith('/connected_accounts'):
            return self.accounts
        return {'successful': self.send_ok, 'error': None if self.send_ok else 'bad account'}


class Guard(unittest.TestCase):
    def test_blocks_sending_tools(self):
        for name in ('mcp__composio-gmail__GMAIL_SEND_EMAIL', 'mcp__composio-gmail__GMAIL_REPLY_TO_THREAD',
                     'mcp__gmail__send_email', 'mcp__composio-gmail__GMAIL_FORWARD_MESSAGE',
                     'mcp__composio-gmail__GMAIL_SEND_DRAFT', 'mcp__outlook__OUTLOOK_SEND_EMAIL'):
            self.assertIsNotNone(guard.decide(name), name)

    def test_allows_reading_drafting_and_other_tools(self):
        for name in ('mcp__composio-gmail__GMAIL_CREATE_EMAIL_DRAFT', 'mcp__composio-gmail__GMAIL_FETCH_EMAILS',
                     'mcp__composio-gmail__GMAIL_CREATE_REPLY_DRAFT', 'mcp__blotato__blotato_send_message',
                     'mcp__slack__send_message', 'Bash', 'Write'):
            self.assertIsNone(guard.decide(name), name)

    def test_hook_output_shape(self):
        out = io.StringIO()
        guard.main(io.StringIO(json.dumps({'tool_name': 'mcp__composio-gmail__GMAIL_SEND_EMAIL'})), out)
        decision = json.loads(out.getvalue())['hookSpecificOutput']
        self.assertEqual(decision['permissionDecision'], 'deny')
        self.assertEqual(decision['hookEventName'], 'PreToolUse')
        quiet = io.StringIO()
        guard.main(io.StringIO('not json'), quiet)
        self.assertEqual(quiet.getvalue(), '')


class Triage(unittest.TestCase):
    def test_sample_passes_and_counts(self):
        self.assertEqual(triage.check(cli.SAMPLE), [])
        self.assertEqual(triage.count(cli.SAMPLE), {'Action needed': 2, 'Waiting on': 1, 'FYI': 1})

    def test_missing_fields_and_send_claims_fail(self):
        bad = cli.SAMPLE.replace('| Subject: Layout sign-off ', '').replace('Draft: none', 'Draft: I have sent it')
        problems = triage.check(bad)
        self.assertTrue(any('no Subject' in p for p in problems))
        self.assertTrue(any('never sends' in p for p in problems))
        self.assertIn('placeholders', triage.check(triage.TEMPLATE.format(date='x'))[0])
        self.assertTrue(any('read-only' in p for p in triage.check(cli.SAMPLE.replace('Read-only', 'Read'))))
        self.assertTrue(any('Missing pile' in p for p in triage.check('Read-only\n## FYI\n- none\n')))


class Composio(unittest.TestCase):
    def test_accounts_parse_both_shapes(self):
        rows = composio.accounts('k', Fake())
        self.assertEqual([r['toolkit'] for r in rows], ['gmail', 'googlecalendar', 'gmail'])

    def test_remind_goes_only_to_own_address(self):
        fake = Fake()
        self.assertEqual(composio.remind('k', 'Hi', 'Body', call=fake), 'owner@example.com')
        sent = fake.calls[-1][2]
        self.assertEqual(sent['arguments']['recipient_email'], 'owner@example.com')
        self.assertEqual(sent['connected_account_id'], 'ca_gmail1')
        with self.assertRaises(composio.ComposioError):
            composio.remind('k', 'Hi', 'Body', call=Fake(), to='someone@else.com')

    def test_remind_refuses_unclear_accounts(self):
        two = {'items': ACCOUNTS['items'][:1] + [{'id': 'ca_g2', 'toolkit': 'gmail', 'status': 'ACTIVE', 'user_id': 'b@example.com'}]}
        with self.assertRaises(composio.ComposioError):
            composio.remind('k', 's', 'b', call=Fake(two))
        self.assertEqual(composio.remind('k', 's', 'b', call=Fake(two), account_id='ca_g2'), 'b@example.com')
        with self.assertRaises(composio.ComposioError):
            composio.remind('k', 's', 'b', call=Fake({'items': []}))
        no_address = {'items': [{'id': 'ca_x', 'toolkit': 'gmail', 'status': 'ACTIVE', 'user_id': 'default'}]}
        with self.assertRaises(composio.ComposioError):
            composio.remind('k', 's', 'b', call=Fake(no_address))
        with self.assertRaises(composio.ComposioError):
            composio.remind('k', 's', 'b', call=Fake(send_ok=False))


class Cli(unittest.TestCase):
    def test_remind_needs_yes(self):
        self.assertEqual(cli.main(['remind', '--subject', 's', '--body', 'b']), 1)

    def test_doctor_without_key_and_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k: v for k, v in os.environ.items() if 'COMPOSIO' not in k}
            env['HOME'] = tmp
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-inbox'), *a], env=env, capture_output=True, text=True)
            doctor = run('doctor')
            self.assertEqual(doctor.returncode, 2)
            self.assertIn('Sending guard: on', doctor.stdout)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', str(Path(tmp) / 'inbox-brief_practice_v1.md')).returncode, 0)
            self.assertEqual(run('new', str(Path(tmp) / 'inbox-brief_practice_v1.md')).returncode, 1)
            line = run('schedule', '--subject', "Owner's day", '--body', 'x').stdout
            self.assertIn("'Owner'\\''s day'", line)
            self.assertIn('0 8 * * 1-5', line)

    def test_hooks_json_points_at_guard(self):
        hooks = json.loads((PACK / 'hooks/hooks.json').read_text())
        entry = hooks['hooks']['PreToolUse'][0]
        self.assertEqual(entry['matcher'], 'mcp__.*')
        self.assertIn('tools-inbox guard', entry['hooks'][0]['command'])


if __name__ == '__main__':
    unittest.main()
