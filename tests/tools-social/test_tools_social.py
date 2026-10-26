"""Unit tests for tools-social. No network."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-social'
sys.path.insert(0, str(PACK))

from tools_social import posts, release  # noqa: E402

POST = 'mcp__blotato__blotato_create_post'


def future(days=3):
    return (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%dT09:00')


class Release(unittest.TestCase):
    def test_live_needs_explicit_words(self):
        self.assertEqual(release.live('publish now please')['level'], 'live')
        self.assertEqual(release.live('Post it now')['level'], 'live')
        for words in ('I love it', 'approved, go ahead', 'get it online', 'publish this', ''):
            with self.assertRaises(release.ReleaseError):
                release.live(words)

    def test_scheduled_needs_time_zone_and_future(self):
        r = release.scheduled('Tuesday at 9am', future(), 'Europe/London')
        self.assertTrue(r['utc'].endswith('Z'))
        with self.assertRaises(release.ReleaseError):
            release.scheduled('Tuesday morning', future(), 'Europe/London')
        with self.assertRaises(release.ReleaseError):
            release.scheduled('at 9:00', future(), 'Mars/Base')
        with self.assertRaises(release.ReleaseError):
            release.scheduled('at 9:00', '2020-01-01T09:00', 'Europe/London')
        with self.assertRaises(release.ReleaseError):
            release.scheduled('at 9:00', 'Tuesday', 'Europe/London')

    def test_timezone_conversion(self):
        r = release.scheduled('at 9am', '2099-07-01T09:00', 'Europe/London')
        self.assertEqual(r['utc'], '2099-07-01T08:00:00Z')

    def test_decide(self):
        self.assertIsNone(release.decide('mcp__blotato__blotato_list_accounts', {}, None))
        self.assertIsNone(release.decide('Bash', {}, None))
        self.assertIn('No release', release.decide(POST, {}, None))
        live = release.live('publish now')
        self.assertIsNone(release.decide(POST, {'text': 'x'}, live))
        self.assertIn('schedules', release.decide(POST, {'scheduledTime': '2099-01-01T00:00:00Z'}, live))
        sched = release.scheduled('at 9am', '2099-07-01T09:00', 'Europe/London')
        self.assertIsNone(release.decide(POST, {'scheduledTime': '2099-07-01T08:00:00Z'}, sched))
        self.assertIsNone(release.decide(POST, {'scheduledTime': '2099-07-01T09:00:00+01:00'}, sched))
        self.assertIn('not the time', release.decide(POST, {'scheduledTime': '2099-07-01T09:00:00Z'}, sched))
        self.assertIn('publish now', release.decide(POST, {}, sched))
        self.assertIn('no timezone', release.decide(POST, {'scheduledTime': '2099-07-01T08:00:00'}, sched))
        self.assertIn('next free slot', release.decide(POST, {'useNextFreeSlot': True}, sched))
        self.assertIsNotNone(release.decide('mcp__blotato__blotato_update_schedule', {}, None))

    def test_receipt_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'r.json'
            release.save(release.live('publish now'), path)
            self.assertIsNotNone(release.load(path))
            self.assertIsNone(release.load(path, now=time.time() + release.TTL + 5))


class Posts(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(posts.check(posts.SAMPLE), [])

    def test_problems(self):
        pack = {'posts': [
            {'platform': 'Twitter/X', 'hooks': ['a', 'b'], 'body': 'x' * 300},
            {'platform': 'YouTube', 'hooks': ['a', 'b', 'c'], 'body': 'See [link]', 'title': 'T' * 80},
            {'platform': 'Instagram', 'hooks': ['a', 'b', 'c'], 'body': 'Comment GUIDE and I will send you the guide.'}]}
        text = ' '.join(posts.check(pack))
        self.assertIn('three hook', text)
        self.assertIn('over the 280 limit', text)
        self.assertIn('title under 70', text)
        self.assertIn('placeholder', text)
        self.assertIn('resource_url', text)
        pack['posts'][2]['resource_url'] = 'https://acme.example/guide'
        self.assertFalse(any('Instagram' in p for p in posts.check(pack)))
        self.assertEqual(posts.check({}), ['No posts in the pack.'])


class Cli(unittest.TestCase):
    def test_gate_and_release_through_the_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp, XDG_DATA_HOME=tmp)
            run = lambda *a, stdin=None: subprocess.run([sys.executable, str(PACK / 'bin/tools-social'), *a], env=env,
                                                         capture_output=True, text=True, input=stdin)
            event = json.dumps({'tool_name': POST, 'tool_input': {}})
            self.assertIn('deny', run('gate', stdin=event).stdout)
            self.assertEqual(run('release', 'now', '--words', 'looks great').returncode, 1)
            self.assertEqual(run('release', 'now', '--words', 'publish now').returncode, 0)
            self.assertEqual(run('gate', stdin=event).stdout, '')
            self.assertEqual(run('release', 'clear').returncode, 0)
            self.assertIn('deny', run('gate', stdin=event).stdout)
            self.assertEqual(run('gate', stdin='nonsense').returncode, 0)

    def test_manifest_wires_mcp_and_hook(self):
        mcp = json.loads((PACK / '.mcp.json').read_text())['mcpServers']['blotato']
        self.assertEqual(mcp['headers']['blotato-api-key'], '${user_config.blotato_api_key}')
        hook = json.loads((PACK / 'hooks/hooks.json').read_text())['hooks']['PreToolUse'][0]
        self.assertIn('blotato', hook['matcher'])


if __name__ == '__main__':
    unittest.main()
