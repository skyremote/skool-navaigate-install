"""Unit tests for tools-tasks. Local only."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-tasks'
sys.path.insert(0, str(PACK))

from tools_tasks import cli, tasks  # noqa: E402


class Check(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(tasks.check(tasks.SAMPLE), [])

    def test_failures(self):
        self.assertIn('placeholders', tasks.check(tasks.TEMPLATE.format(title='t', source='s'))[0])
        self.assertEqual(tasks.check('no tasks'), ['No tasks under "## Tasks".'])
        text = ' '.join(tasks.check('## Tasks\n- Working on the website | Owner: Sam\n'
                                    '- Look into pricing | Owner: | Due: Friday | Done when: x\n'))
        for expected in ('Start with a verb', 'No due date', 'No "Done when"', 'Too vague', 'No owner', 'YYYY-MM-DD'):
            self.assertIn(expected, text)


class Today(unittest.TestCase):
    def test_order_limit_and_groups(self):
        picked, overdue = tasks.today(cli.SAMPLE_OPEN, on='2026-10-26')
        self.assertEqual([t['name'] for t in picked], ['Send the page layout to Northwind', 'Invoice Contoso for October',
                                                       'Book the photographer'])
        self.assertEqual(sorted(overdue), ['Contoso', 'Northwind'])
        self.assertNotIn('Renew the domain', [t['name'] for t in picked])
        picked, _ = tasks.today(cli.SAMPLE_OPEN, on='2026-10-26', limit=10)
        self.assertEqual(picked[-1]['name'], 'Update the website footer')

    def test_priority_breaks_ties(self):
        rows = [{'name': 'b', 'due': '2026-10-26', 'priority': 3}, {'name': 'a', 'due': '2026-10-26', 'priority': 1}]
        self.assertEqual([t['name'] for t in tasks.today(rows, on='2026-10-26')[0]], ['a', 'b'])


class Cli(unittest.TestCase):
    def test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-tasks'), *a], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/northwind_tasks_v1.md').returncode, 0)
            out = run('today', tmp + '/open-tasks_v1.json', '--on', '2026-10-26')
            self.assertEqual(out.returncode, 0)
            self.assertIn('3. Book the photographer', out.stdout)
            self.assertEqual(run('new', tmp + '/n.md', '--title', 't').returncode, 0)
            self.assertEqual(run('check', tmp + '/n.md').returncode, 1)
            Path(tmp, 'bad.json').write_text('{')
            self.assertEqual(run('today', tmp + '/bad.json').returncode, 1)

    def test_mcp_is_clickups_own(self):
        server = json.loads((PACK / '.mcp.json').read_text())['mcpServers']['clickup']
        self.assertEqual(server, {'type': 'http', 'url': 'https://mcp.clickup.com/mcp'})


if __name__ == '__main__':
    unittest.main()
