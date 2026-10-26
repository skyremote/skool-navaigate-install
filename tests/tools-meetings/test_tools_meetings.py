"""Unit tests for tools-meetings. No network: the Granola API is replaced by a fake."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-meetings'
sys.path.insert(0, str(PACK))

from tools_meetings import cli, config, granola, mcp_server, record, sample  # noqa: E402

GOOD = """# Decision record: Northwind kick-off

## Decisions
- Cakes only in the first version. (quote: "cakes only for now")

## Actions
- Send the page layout | Owner: Me | Due: Friday 31 October | Quote: "I will send the page layout by Friday 31 October"
- Send the cake photos | Owner: Tom | Due: not stated | Quote: "Tom will send you the photos of the six cakes we sell most"

## Open questions
- Whether a 20 percent deposit is fine for VAT: Priya asks the accountant.

## Source
transcript.txt
"""


class Config(unittest.TestCase):
    def test_order_shell_then_option_then_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'env'
            path.write_text('GRANOLA_API_KEY=grn_file\n')
            path.chmod(0o600)
            self.assertEqual(config.get('GRANOLA_API_KEY', 'granola_api_key', env={'GRANOLA_API_KEY': 'grn_shell'}, path=path), 'grn_shell')
            self.assertEqual(config.get('GRANOLA_API_KEY', 'granola_api_key',
                                        env={'CLAUDE_PLUGIN_OPTION_GRANOLA_API_KEY': 'grn_opt'}, path=path), 'grn_opt')
            self.assertEqual(config.get('GRANOLA_API_KEY', 'granola_api_key', env={}, path=path), 'grn_file')
            self.assertEqual(config.where('GRANOLA_API_KEY', 'granola_api_key', env={}, path=path),
                             'private file ~/.config/aios-tools/env')

    def test_open_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'env'
            path.write_text('GRANOLA_API_KEY=grn_file\n')
            path.chmod(0o644)
            with self.assertRaises(config.KeyError_):
                config.get('GRANOLA_API_KEY', env={}, path=path)

    def test_missing_and_wrong_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = {'HOME': tmp}
            old = os.environ.get('HOME')
            os.environ['HOME'] = tmp
            try:
                with self.assertRaises(granola.GranolaError) as caught:
                    granola.api_key(env=empty)
                self.assertIn('Settings, Connectors, API keys', str(caught.exception))
                with self.assertRaises(granola.GranolaError):
                    granola.api_key(env={'GRANOLA_API_KEY': 'sk-wrong'})
            finally:
                os.environ['HOME'] = old


class Granola(unittest.TestCase):
    def test_pagination_stops_at_limit(self):
        pages = {None: {'notes': [{'id': 'n%d' % i, 'title': 'T%d' % i} for i in range(10)], 'hasMore': True, 'cursor': 'c1'},
                 'c1': {'notes': [{'id': 'm%d' % i, 'title': 'U%d' % i} for i in range(10)], 'hasMore': False}}
        calls = []

        def fake(path, key):
            calls.append(path)
            return pages['c1' if 'cursor=c1' in path else None]
        notes = granola.list_notes(15, 'grn_x', get=fake)
        self.assertEqual(len(notes), 15)
        self.assertEqual(len(calls), 2)

    def test_transcript_turns_and_raw(self):
        note = {'transcript': [
            {'text': 'Hello.', 'speaker': {'source': 'microphone'}, 'start_time': '2026-10-20T10:00:01Z'},
            {'text': 'Welcome.', 'speaker': {'source': 'microphone'}, 'start_time': '2026-10-20T10:00:02Z'},
            {'text': 'Thanks.', 'speaker': {'source': 'speaker'}, 'start_time': '2026-10-20T10:00:05Z'}]}
        self.assertEqual(granola.transcript_text(note, me='Sam'), 'Sam: Hello. Welcome.\nOthers: Thanks.')
        self.assertIn('[10:00:05] Others: Thanks.', granola.transcript_text(note, raw=True))

    def test_attendees(self):
        self.assertEqual(granola.attendees_of({'attendees': [{'name': 'Priya'}, {'email': 'a@example.com'}, 'Tom']}),
                         ['Priya', 'a@example.com', 'Tom'])


class Record(unittest.TestCase):
    def test_good_record_passes(self):
        self.assertEqual(record.check(GOOD, sample.TRANSCRIPT), [])

    def test_invented_owner_number_and_quote_fail(self):
        bad = GOOD.replace('Owner: Tom', 'Owner: Jordan').replace('20 percent', '25 percent').replace(
            '"cakes only for now"', '"cakes and bread from day one"')
        problems = record.check(bad, sample.TRANSCRIPT)
        self.assertTrue(any('Jordan' in p for p in problems))
        self.assertTrue(any('25' in p for p in problems))
        self.assertTrue(any('Quote not found' in p for p in problems))

    def test_template_and_missing_parts_fail(self):
        empty = record.TEMPLATE.format(title='x', date='y', source='z')
        self.assertIn('placeholders', record.check(empty, sample.TRANSCRIPT)[0])
        no_fields = '## Decisions\n## Actions\n- Do it\n## Open questions\n## Source\nx\n'
        problems = record.check(no_fields, sample.TRANSCRIPT)
        self.assertTrue(any('no Owner' in p for p in problems))
        self.assertTrue(any('no Due' in p for p in problems))
        self.assertTrue(any('Missing section' in p for p in record.check('## Decisions\n', 'x')))


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(list(args))
        return code, out.getvalue()

    def test_sample_new_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, text = self.run_cli('sample', tmp)
            self.assertEqual(code, 0)
            transcript = Path(tmp) / 'northwind-kickoff_transcript_v1.txt'
            self.assertTrue(transcript.exists())
            good = Path(tmp) / 'good_v1.md'
            good.write_text(GOOD)
            self.assertEqual(self.run_cli('check', str(good), '--source', str(transcript))[0], 0)
            self.assertEqual(self.run_cli('check', str(Path(tmp) / 'northwind-kickoff_record_v1.md'), '--source', str(transcript))[0], 1)
            self.assertEqual(self.run_cli('new', str(good), '--title', 't', '--source', 's')[0], 1)

    def test_doctor_without_key_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp)
            env.pop('GRANOLA_API_KEY', None)
            env.pop('CLAUDE_PLUGIN_OPTION_GRANOLA_API_KEY', None)
            proc = subprocess.run([sys.executable, str(PACK / 'bin/tools-meetings'), 'doctor'], env=env,
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('not set', proc.stdout)
            self.assertNotIn('grn_', proc.stdout.replace('starts grn_', '').replace('GRANOLA_API_KEY=grn_...', ''))


class Mcp(unittest.TestCase):
    def test_handshake_list_and_error(self):
        requests = [{'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
                    {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                    {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                    {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'nope', 'arguments': {}}},
                    {'jsonrpc': '2.0', 'id': 4, 'method': 'unknown'}]
        out = io.StringIO()
        old = os.environ.pop('GRANOLA_API_KEY', None)
        try:
            mcp_server.serve(io.StringIO('\n'.join(json.dumps(r) for r in requests)), out)
        finally:
            if old:
                os.environ['GRANOLA_API_KEY'] = old
        replies = [json.loads(l) for l in out.getvalue().splitlines()]
        self.assertEqual([r['id'] for r in replies], [1, 2, 3, 4])
        self.assertEqual(replies[0]['result']['serverInfo']['name'], 'tools-meetings')
        self.assertEqual({t['name'] for t in replies[1]['result']['tools']}, {'meetings_list', 'meetings_transcript'})
        self.assertTrue(replies[2]['result']['isError'])
        self.assertEqual(replies[3]['error']['code'], -32601)

    def test_call_uses_fake_api(self):
        def fake(path, key):
            if path.startswith('/notes?'):
                return {'notes': [{'id': 'n1', 'title': 'Northwind kick-off', 'created_at': '2026-10-20T10:00'},
                                  {'id': 'n2', 'title': 'Dentist'}], 'hasMore': False}
            return {'note': {'id': 'n1', 'transcript': [{'text': 'Cakes only.', 'speaker': {'source': 'speaker'}}]}}
        listed = mcp_server.call('meetings_list', {'query': 'northwind'}, key='grn_x', get=fake)
        self.assertIn('[n1]', listed)
        self.assertNotIn('Dentist', listed)
        self.assertEqual(mcp_server.call('meetings_transcript', {'id': 'n1'}, key='grn_x', get=fake), 'Others: Cakes only.')

if __name__ == '__main__':
    unittest.main()
