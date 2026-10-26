"""Unit tests for plugins/aios-methods. Standard library only; every repo lives in /tmp."""
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins/aios-methods'
sys.path.insert(0, str(PACK))
from aios_methods.cli import main, parse_glossary  # noqa: E402


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, text=True, capture_output=True).stdout


class InTemp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-methods-test-', dir='/tmp')
        self.base = Path(self.tmp.name)
        self.old = os.getcwd()
        self.env = {k: os.environ.get(k) for k in ('GIT_CONFIG_GLOBAL', 'GIT_CONFIG_NOSYSTEM')}
        os.environ['GIT_CONFIG_GLOBAL'] = str(self.base / 'gitconfig')
        os.environ['GIT_CONFIG_NOSYSTEM'] = '1'
        (self.base / 'gitconfig').write_text('[user]\n\tname = Acme Tester\n\temail = tester@example.com\n[init]\n\tdefaultBranch = main\n')

    def tearDown(self):
        os.chdir(self.old)
        for key, value in self.env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def make_repo(self):
        repo = self.base / 'acme-site'
        repo.mkdir()
        git(repo, 'init', '-q')
        (repo / 'README.md').write_text('Acme Studio\n')
        git(repo, 'add', '.')
        git(repo, 'commit', '-qm', 'start')
        os.chdir(repo)
        return repo


class WorktreeTests(InTemp):
    def test_new_list_done_round_trip(self):
        repo = self.make_repo()
        code, out, _ = run('worktree', 'new', 'invoice-export')
        self.assertEqual(code, 0, out)
        tree = self.base / 'acme-site-invoice-export'
        self.assertTrue((tree / 'README.md').exists())
        self.assertIn('work/invoice-export', git(repo, 'branch', '--list'))
        code, out, _ = run('worktree', 'list')
        self.assertIn('linked  clean', out)
        (tree / 'export.py').write_text('print("csv")\n')
        git(tree, 'add', '.')
        git(tree, 'commit', '-qm', 'export')
        code, _, err = run('worktree', 'done', 'invoice-export')
        self.assertEqual(code, 2)
        self.assertIn('not merged', err)
        git(repo, 'merge', '-q', 'work/invoice-export')
        code, out, _ = run('worktree', 'done', 'invoice-export')
        self.assertEqual(code, 0, out)
        self.assertFalse(tree.exists())
        self.assertNotIn('work/invoice-export', git(repo, 'branch', '--list'))

    def test_done_refuses_uncommitted_changes(self):
        self.make_repo()
        run('worktree', 'new', 'draft')
        (self.base / 'acme-site-draft' / 'notes.txt').write_text('half done\n')
        code, _, err = run('worktree', 'done', 'draft')
        self.assertEqual(code, 2)
        self.assertIn('Uncommitted changes', err)
        self.assertTrue((self.base / 'acme-site-draft' / 'notes.txt').exists())

    def test_new_refuses_existing_folder_and_bad_names(self):
        self.make_repo()
        (self.base / 'acme-site-taken').mkdir()
        code, _, err = run('worktree', 'new', 'taken')
        self.assertEqual(code, 2)
        self.assertIn('already exists', err)
        code, _, err = run('worktree', 'new', '../escape')
        self.assertEqual(code, 2)
        self.assertIn('lower-case', err)

    def test_new_from_inside_a_linked_worktree_uses_main_repo(self):
        self.make_repo()
        run('worktree', 'new', 'first')
        os.chdir(self.base / 'acme-site-first')
        code, out, _ = run('worktree', 'new', 'second')
        self.assertEqual(code, 0, out)
        self.assertTrue((self.base / 'acme-site-second').exists())

    def test_outside_git_is_refused(self):
        os.chdir(self.base)
        code, _, err = run('worktree', 'list')
        self.assertEqual(code, 2)
        self.assertIn('Not inside a git repository', err)


class GlossaryTests(InTemp):
    def test_init_add_sorted_and_check(self):
        os.chdir(self.base)
        self.assertEqual(run('glossary', 'init')[0], 0)
        self.assertEqual(run('glossary', 'init')[0], 2)
        run('glossary', 'add', 'Retainer', 'a monthly fee for a fixed number of days')
        run('glossary', 'add', 'Client', 'a business that pays us', '--avoid', 'customer, account')
        text = (self.base / 'GLOSSARY.md').read_text()
        self.assertLess(text.index('**Client**'), text.index('**Retainer**'))
        self.assertIn('Avoid: customer, account.', text)
        code, out, _ = run('glossary', 'check')
        self.assertEqual(code, 0, out)
        self.assertIn('2 terms, 0 problems', out)
        self.assertEqual(run('glossary', 'add', 'client', 'duplicate')[0], 2)

    def test_check_finds_duplicates_order_and_empty(self):
        _, problems = parse_glossary('- **Zebra**: last\n- **Apple**:\n- **apple**: again\n- **Bad line\n')
        joined = ' | '.join(problems)
        self.assertIn('Apple has no definition', joined)
        self.assertIn('already defined', joined)
        self.assertIn('alphabetical', joined)
        self.assertIn('use - **Term**', joined)

    def test_empty_glossary_fails(self):
        os.chdir(self.base)
        run('glossary', 'init')
        self.assertEqual(run('glossary', 'check')[0], 1)


class SpecAndLoopTests(InTemp):
    def test_template_fails_until_filled(self):
        os.chdir(self.base)
        self.assertEqual(run('spec', 'new', 'invoice-export')[0], 0)
        path = self.base / 'docs/specs/invoice-export.md'
        code, out, _ = run('spec', 'check', str(path))
        self.assertEqual(code, 1)
        self.assertIn('Goal is empty', out)
        self.assertIn('no runnable check', out)
        self.assertIn('template line', out)
        path.write_text('# Invoice export\n\n## Goal\nExport each month\'s invoices as one CSV.\n\n'
                        '## Done when\n- [ ] `python3 -m unittest tests/test_export.py`\n\n'
                        '## Open questions\n- Which currency for Swiss clients?\n')
        code, out, _ = run('spec', 'check', str(path))
        self.assertEqual(code, 1)
        self.assertIn('1 open question', out)
        path.write_text(path.read_text().replace('- Which currency for Swiss clients?', '- None'))
        code, out, _ = run('spec', 'check', str(path))
        self.assertEqual(code, 0, out)
        self.assertIn('1 runnable check(s), 0 problem(s)', out)

    def test_loop_init_writes_once(self):
        os.chdir(self.base)
        code, out, _ = run('loop', 'init')
        self.assertEqual(code, 0)
        text = (self.base / '.claude/loop.md').read_text()
        self.assertIn('Run that line\'s command', text)
        self.assertIn('Never push, deploy or delete', text)
        self.assertEqual(run('loop', 'init')[0], 2)


class PackShapeTests(unittest.TestCase):
    def test_skills_are_short_with_frontmatter(self):
        for skill in sorted((PACK / 'skills').glob('*/SKILL.md')):
            text = skill.read_text()
            self.assertTrue(text.startswith('---\nname: '), skill)
            self.assertLess(len(text.splitlines()), 500, skill)

    def test_wrapper_runs(self):
        result = subprocess.run([str(PACK / 'bin/aios-methods'), '--help'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('worktree', result.stdout)

    def test_three_eval_cases(self):
        cases = [p for p in (PACK / 'evals').iterdir() if (p / 'prompt.md').exists()]
        self.assertGreaterEqual(len(cases), 3)
        for case in cases:
            self.assertTrue(list((case / 'graders').glob('*.md')), case)



class TourAndManifest(unittest.TestCase):
    def test_tour_is_short_and_manifest_has_module(self):
        import json as _json
        pack = Path(__file__).resolve().parents[2] / 'plugins/aios-methods'
        tour = (pack / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('## Step 1', tour)
        manifest = _json.loads((pack / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['dependencies'], ['aios'])
        self.assertIsInstance(manifest['metadata']['module'], int)


if __name__ == '__main__':
    unittest.main()
