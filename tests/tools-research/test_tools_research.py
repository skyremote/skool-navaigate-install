"""Unit tests for tools-research. No network: every source is replaced by a fake."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-research'
sys.path.insert(0, str(PACK))

from tools_research import cli, ledger, sources  # noqa: E402


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = replies, []

    def __call__(self, url, headers=None, data=None):
        self.calls.append((url, headers, data))
        for key, value in self.replies.items():
            if key in url:
                return value
        raise AssertionError('unexpected ' + url)


class Papers(unittest.TestCase):
    def test_relevance_default_and_email(self):
        fake = Fake({'openalex': {'results': [{'display_name': 'P', 'publication_year': 2024, 'cited_by_count': 3,
                                              'doi': 'https://doi.org/10.1/x', 'open_access': {'oa_url': 'https://x/pdf'}}]}})
        rows = sources.papers('bakery', 2, get=fake, env={'OPENALEX_EMAIL': 'me@example.com'})
        self.assertEqual(rows[0]['free_pdf'], 'https://x/pdf')
        self.assertNotIn('sort=', fake.calls[0][0])
        self.assertIn('mailto=me%40example.com', fake.calls[0][0])
        sources.papers('bakery', 2, get=fake, env={'HOME': '/nonexistent'}, most_cited=True)
        self.assertIn('sort=cited_by_count', fake.calls[1][0])
        self.assertNotIn('mailto', fake.calls[1][0])


class Substack(unittest.TestCase):
    def test_base_and_slug(self):
        self.assertEqual(sources.substack_base('lenny'), 'https://lenny.substack.com')
        self.assertEqual(sources.substack_base('www.lennysnewsletter.com'), 'https://www.lennysnewsletter.com')
        self.assertEqual(sources.substack_base('https://a.substack.com/p/x?y=1'), 'https://a.substack.com')
        self.assertEqual(sources.substack_slug('https://a.substack.com/p/my-post?utm=1'), 'my-post')
        with self.assertRaises(sources.SourceError):
            sources.substack_slug('https://a.substack.com/about')

    def test_archive_and_post(self):
        fake = Fake({'/archive': [{'title': 'T', 'post_date': '2026-10-01T00:00Z', 'audience': 'only_paid', 'slug': 's'}],
                     '/posts/s': {'title': 'T', 'body_html': '<p>Hello <b>there</b></p><script>x()</script>', 'audience': 'everyone'}})
        rows = sources.substack_archive('pub', 1, get=fake)
        self.assertTrue(rows[0]['paid'])
        self.assertEqual(rows[0]['url'], 'https://pub.substack.com/p/s')
        post = sources.substack_post('https://pub.substack.com/p/s', get=fake)
        self.assertEqual(post['text'], 'Hello there')

    def test_text_of(self):
        self.assertEqual(sources.text_of('<h1>A</h1><p>b &amp; c</p>'), 'A\nb & c')


class Reddit(unittest.TestCase):
    def test_needs_own_app(self):
        with self.assertRaises(sources.SourceError) as caught:
            sources.reddit_token(env={'HOME': '/nonexistent'})
        self.assertIn('reddit.com/prefs/apps', str(caught.exception))

    def test_token_search_thread(self):
        fake = Fake({'access_token': {'access_token': 'T'},
                     '/search': {'data': {'children': [{'data': {'title': 'Q', 'subreddit': 'smallbusiness', 'score': 5,
                                                                  'num_comments': 2, 'permalink': '/r/x/comments/ab1/q/', 'id': 'ab1'}}]}},
                     '/comments/ab1': [{'data': {'children': [{'data': {'title': 'Q', 'selftext': 'body', 'permalink': '/r/x/comments/ab1/q/'}}]}},
                                       {'data': {'children': [{'kind': 't1', 'data': {'score': 9, 'body': 'top'}}, {'kind': 'more', 'data': {}}]}}]})
        env = {'REDDIT_CLIENT_ID': 'id', 'REDDIT_CLIENT_SECRET': 'sec'}
        rows = sources.reddit_search('q', 1, subreddit='smallbusiness', get=fake, env=env)
        self.assertEqual(rows[0]['url'], 'https://reddit.com/r/x/comments/ab1/q/')
        self.assertTrue(fake.calls[0][1]['Authorization'].startswith('Basic '))
        self.assertIn('restrict_sr=on', fake.calls[1][0])
        self.assertEqual(fake.calls[1][1]['Authorization'], 'bearer T')
        thread = sources.reddit_thread('https://reddit.com/r/x/comments/ab1/q/', token='T', get=fake)
        self.assertEqual(thread['top_comments'], [{'score': 9, 'text': 'top'}])


class Ledger(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(ledger.check(cli.SAMPLE), [])

    def test_failures(self):
        self.assertIn('placeholders', ledger.check(ledger.TEMPLATE.format(question='q', date='d'))[0])
        all_high = cli.SAMPLE.replace('Confidence: low', 'Confidence: high').replace('Confidence: medium', 'Confidence: high')
        self.assertTrue(any('Every finding is "high"' in p for p in ledger.check(all_high)))
        one_kind = cli.SAMPLE.replace('Kind: paper', 'Kind: practitioner').replace('Kind: newsletter', 'Kind: practitioner')
        self.assertTrue(any('one kind' in p for p in ledger.check(one_kind)))
        bad = cli.SAMPLE.replace('Source: https://doi.org/10.0000/example', 'Source: a paper').replace('Confidence: medium', 'Confidence: certain')
        text = ' '.join(ledger.check(bad))
        self.assertIn('no source link', text)
        self.assertIn('high, medium or low', text)
        self.assertTrue(any('Missing section' in p for p in ledger.check('## Findings\n- x | Source: https://a | Kind: web | Confidence: low\n')))


class Cli(unittest.TestCase):
    def test_commands_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k: v for k, v in os.environ.items() if not k.startswith('REDDIT')}
            env['HOME'] = tmp
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-research'), *a], env=env, capture_output=True, text=True)
            self.assertEqual(run('doctor').returncode, 2)
            self.assertEqual(run('reddit', 'search', 'x').returncode, 2)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/bakery-ordering_ledger_practice_v1.md').returncode, 0)
            self.assertEqual(run('new', tmp + '/l.md', '--question', 'q').returncode, 0)
            self.assertEqual(run('check', tmp + '/l.md').returncode, 1)


if __name__ == '__main__':
    unittest.main()
