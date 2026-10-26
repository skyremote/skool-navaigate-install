"""Unit tests for the aios-bb pack against a fake bb CLI. Run: python3 -m unittest discover -s tests/aios-bb"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
FAKE = Path(__file__).resolve().parent / 'fake_bb.py'
sys.path.insert(0, str(ROOT / 'plugins/aios-bb'))
from aios_bb import cockpit as c  # noqa: E402
from aios_bb.cli import main  # noqa: E402


class Case(unittest.TestCase):
    kanban = False

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-bb-test-', dir='/tmp')
        base = Path(self.tmp.name).resolve()
        self.folder = base / 'acme-studio-aios'
        self.folder.mkdir()
        (self.folder / 'AGENTS.md').write_text('# Acme rules\n')
        self.state = base / 'bb-state.json'
        self.env = {'HOME': str(base), 'PATH': os.environ['PATH'], 'BB_CLI': str(FAKE),
                    'FAKE_BB_STATE': str(self.state), 'FAKE_BB_KANBAN': '1' if self.kanban else '0'}
        self.bb = c.Bb(env=self.env)

    def tearDown(self):
        self.tmp.cleanup()

    def state_data(self):
        return json.loads(self.state.read_text())

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.env, clear=False):
            os.environ.pop('BB_PROJECT_ID', None)
            os.environ.pop('BB_THREAD_ID', None)
            with redirect_stdout(out), redirect_stderr(err):
                code = main(['--folder', str(self.folder)] + list(argv))
        return code, out.getvalue(), err.getvalue()

    def prompt(self, text='Write the Acme Studio weekly report and check the totals.'):
        path = self.folder / 'brief.md'
        path.write_text(text)
        return path


class LaneTests(unittest.TestCase):
    def test_lane_names_and_aliases(self):
        self.assertEqual(c.lane_id('Review'), 'review')
        self.assertEqual(c.lane_id('in progress'), 'in-progress')
        self.assertEqual(c.lane_id('In_Progress'), 'in-progress')
        self.assertEqual(c.lane_id('doing'), 'in-progress')
        self.assertEqual(c.lane_id('todo'), 'backlog')
        with self.assertRaises(ValueError):
            c.lane_id('someday')


class SetupTests(Case):
    def test_setup_creates_project_and_four_sections(self):
        project, log = c.setup(self.bb, self.folder, 'Acme Studio AIOS')
        self.assertEqual(project['name'], 'Acme Studio AIOS')
        data = self.state_data()
        self.assertEqual([s['name'] for s in data['sections']], ['Backlog', 'In progress', 'Review', 'Done'])
        self.assertTrue(any('not a git repository' in line for line in log))

    def test_setup_is_idempotent(self):
        c.setup(self.bb, self.folder)
        project, log = c.setup(self.bb, self.folder)
        data = self.state_data()
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(len(data['sections']), 4)
        self.assertTrue(any('already points at this folder' in line for line in log))

    def test_dry_run_changes_nothing(self):
        _, log = c.setup(self.bb, self.folder, dry_run=True)
        data = self.state_data()
        self.assertEqual(data['projects'], [])
        self.assertEqual(data['sections'], [])
        self.assertTrue(log[0].startswith('Would create'))

    def test_missing_folder(self):
        with self.assertRaises(ValueError):
            c.setup(self.bb, self.folder / 'nope')

    def test_doctor(self):
        (self.folder / '.git').mkdir()
        rows = c.doctor(self.bb, self.folder)
        self.assertTrue(all(status != 'FAIL' for status, _ in rows))
        self.assertTrue(any('worktree' in msg for _, msg in rows))
        self.assertTrue(any('sidebar sections' in msg for _, msg in rows))

    def test_doctor_without_bb(self):
        bb = c.Bb(exe=str(self.folder / 'no-bb'), env=self.env)
        rows = c.doctor(bb, self.folder)
        self.assertEqual(rows[0][0], 'FAIL')
        self.assertIn('getbb.app', rows[0][1])


class SectionBoardTests(Case):
    def test_hand_card_today_close_with_sections(self):
        project, _ = c.setup(self.bb, self.folder)
        thread = c.hand(self.bb, project['id'], 'Acme weekly report', self.prompt(), 'codex')
        data = self.state_data()
        spawned = data['threads'][0]
        self.assertEqual(spawned['providerId'], 'codex')
        self.assertTrue(spawned['worktree'])
        sections = {s['id']: s['name'] for s in data['sections']}
        self.assertEqual(sections[spawned['sectionId']], 'In progress')
        msg = c.move_card(self.bb, thread['id'], 'review', 'Report ready')
        self.assertIn('Review section', msg)
        text, lanes = c.today(self.bb, project['id'])
        self.assertEqual([t['id'] for t in lanes['review']], [thread['id']])
        self.assertIn('Review (1)', text)
        c.move_card(self.bb, thread['id'], 'done')
        summary = c.close(self.bb, project['id'], archive_done=True)
        self.assertIn('Archived 1', summary)
        self.assertIsNotNone(self.state_data()['threads'][0]['archivedAt'])

    def test_card_by_title(self):
        project, _ = c.setup(self.bb, self.folder)
        thread = c.hand(self.bb, project['id'], 'Acme weekly report', self.prompt())
        c.move_card(self.bb, 'Acme weekly report', 'review')
        text, lanes = c.today(self.bb, project['id'])
        self.assertEqual([t['id'] for t in lanes['review']], [thread['id']])
        with self.assertRaises(ValueError):
            c.move_card(self.bb, 'No such thread', 'review')
        c.hand(self.bb, project['id'], 'Acme weekly report', self.prompt())
        with self.assertRaises(ValueError) as ctx:
            c.move_card(self.bb, 'Acme weekly report', 'done')
        self.assertIn('More than one', str(ctx.exception))

    def test_pending_interaction_shows_first(self):
        project, _ = c.setup(self.bb, self.folder)
        c.hand(self.bb, project['id'], 'Acme invoice run', self.prompt())
        data = self.state_data()
        data['threads'][0]['hasPendingInteraction'] = True
        self.state.write_text(json.dumps(data))
        text, _ = c.today(self.bb, project['id'])
        self.assertIn('Waiting on you now', text)
        self.assertLess(text.index('Waiting on you now'), text.index('Review ('))

    def test_hand_needs_a_prompt_file_and_known_provider(self):
        project, _ = c.setup(self.bb, self.folder)
        with self.assertRaises(ValueError):
            c.hand(self.bb, project['id'], 'x', self.folder / 'missing.md')
        with self.assertRaises(ValueError):
            c.hand(self.bb, project['id'], 'x', self.prompt(), 'grok')

    def test_plan_and_no_worktree_flags(self):
        project, _ = c.setup(self.bb, self.folder)
        c.hand(self.bb, project['id'], 'Acme plan', self.prompt(), 'claude', worktree=False, plan=True)
        spawned = self.state_data()['threads'][0]
        self.assertEqual(spawned['providerId'], 'claude-code')
        self.assertFalse(spawned['worktree'])
        self.assertTrue(spawned['plan'])

    def test_card_without_thread_outside_bb(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('BB_THREAD_ID', None)
            with self.assertRaises(ValueError):
                c.move_card(self.bb, None, 'review')

    def test_bb_error_message_is_readable(self):
        with self.assertRaises(c.BbError) as ctx:
            self.bb.json('thread', 'nonsense')
        self.assertIn('unknown command', str(ctx.exception))


class KanbanBoardTests(Case):
    kanban = True

    def test_kanban_plugin_is_used_when_present(self):
        project, _ = c.setup(self.bb, self.folder)
        thread = c.hand(self.bb, project['id'], 'Acme weekly report', self.prompt())
        self.assertIsNone(self.state_data()['threads'][0]['sectionId'])
        msg = c.move_card(self.bb, thread['id'], 'review', 'Ready for you')
        self.assertIn('kanban board', msg)
        data = self.state_data()
        self.assertEqual(data['cards'][-1], {'threadId': thread['id'], 'columnId': 'review', 'note': 'Ready for you', 'position': 0})
        text, lanes = c.today(self.bb, project['id'])
        self.assertEqual(lanes['review'][0]['note'], 'Ready for you')
        self.assertIn('Ready for you', text)

    def test_kanban_probe_is_cached(self):
        self.bb.has_kanban()
        self.bb.has_kanban()
        calls = [x for x in self.state_data()['calls'] if x[:1] == ['kanban']]
        self.assertEqual(len(calls), 1)


class CliTests(Case):
    def test_cli_round_trip(self):
        code, out, _ = self.cli('setup', '--name', 'Acme Studio AIOS')
        self.assertEqual(code, 0, out)
        self.assertIn('Created the bb project', out)
        code, out, _ = self.cli('hand', 'Acme weekly report', '--prompt-file', str(self.prompt()), '--provider', 'codex')
        self.assertEqual(code, 0, out)
        tid = self.state_data()['threads'][0]['id']
        code, out, _ = self.cli('card', 'review', '--thread', tid)
        self.assertEqual(code, 0)
        code, out, _ = self.cli('today')
        self.assertIn('Acme weekly report', out)
        code, out, _ = self.cli('close')
        self.assertIn('Still in Review (1)', out)
        code, out, _ = self.cli('doctor')
        self.assertIn('bb is running', out)

    def test_cli_without_project(self):
        code, out, err = self.cli('today')
        self.assertEqual(code, 2)
        self.assertIn('aios-bb setup', err)

    def test_bin_script_runs(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'plugins/aios-bb/bin/aios-bb'), '--version'],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn('2.0.0', proc.stdout)


if __name__ == '__main__':
    unittest.main()
