"""Unit tests for tools-whatsapp. Local only, fictional chat."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-whatsapp'
sys.path.insert(0, str(PACK))

from tools_whatsapp import chat  # noqa: E402


def write(rows):
    folder = tempfile.mkdtemp()
    path = Path(folder) / 'transcript.jsonl'
    path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    return path


class Chat(unittest.TestCase):
    def test_load_and_errors(self):
        rows = chat.load(write(chat.SAMPLE))
        self.assertEqual(len(rows), 5)
        with self.assertRaises(chat.ChatError):
            chat.load('/nonexistent/transcript.jsonl')
        bad = write([])
        bad.write_text('{not json}\n')
        with self.assertRaises(chat.ChatError):
            chat.load(bad)

    def test_find_filters(self):
        rows = chat.load(write(chat.SAMPLE))
        self.assertEqual(len(chat.find(rows, kind='voice')), 2)
        self.assertEqual(len(chat.find(rows, since='2026-10-20')), 1)
        self.assertEqual(len(chat.find(rows, until='2026-10-19', who='me')), 2)
        self.assertEqual(len(chat.find(rows, contains='SKIP')), 2)

    def test_extract_money_dates_times(self):
        found = chat.extract(chat.load(write(chat.SAMPLE)))
        values = {(f['kind'], f['value']) for f in found}
        for item in [('money', '£350'), ('money', '£1,240'), ('date', 'Thursday'), ('date', '24th October'),
                     ('time', '8am'), ('date', 'Friday')]:
            self.assertIn(item, values)
        self.assertTrue(all(f['text'] for f in found))
        more = chat.extract([{'at': '2026-10-01', 'who': 'x', 'type': 'text',
                              'text': 'It is 500 quid, or $20.50, meet 14:30 on 3/11 or 5 Nov'}])
        values = {f['value'] for f in more}
        self.assertTrue({'500 quid', '$20.50', '14:30', '3/11', '5 Nov'} <= values)


class Cli(unittest.TestCase):
    def test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-whatsapp'), *a], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('extract', tmp + '/transcript.jsonl').returncode, 0)
            self.assertEqual(run('find', tmp + '/transcript.jsonl', '--contains', 'nothing like this').returncode, 1)
            self.assertEqual(run('find', tmp + '/missing.jsonl').returncode, 1)
            out = run('find', tmp + '/transcript.jsonl', '--type', 'voice', '--json')
            self.assertEqual(len(json.loads(out.stdout)), 2)


if __name__ == '__main__':
    unittest.main()
