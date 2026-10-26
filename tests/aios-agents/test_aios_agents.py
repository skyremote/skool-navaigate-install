"""Unit tests for the aios-agents pack. Run from the repository root:
python3 -m unittest discover -s tests/aios-agents -v
"""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'plugins' / 'aios-agents'
sys.path.insert(0, str(PACK))

from aios_agents import brief, compare, crew  # noqa: E402
from aios_agents.cli import main  # noqa: E402

READY = """# Brief: supplier research

## Objective
Find the cheapest accounting software for a UK sole trader.
Done when: a table of exactly 3 tools, each with a monthly price and a link.

## Format
A markdown table, then at most 80 words.

## Context
Acme Studio is a sole trader in Leeds. VAT registered.

## Tools
Use: WebSearch, WebFetch, the vendors' own pricing pages
Avoid: review sites as the only source

## Boundaries
You own: the research and the table
Do not touch: any file on disk

## Stop
Stop when the table has 3 rows, or after 10 searches, and report what blocked you.
"""


def result(seconds=10, turns=2, cost=0.05, spawned=0, tokens=(100, 50, 1000, 2000), ok=True, models=True):
    data = {'type': 'result', 'subtype': 'success' if ok else 'error_max_turns', 'is_error': not ok,
            'duration_ms': seconds * 1000, 'num_turns': turns, 'total_cost_usd': cost,
            'usage': {'input_tokens': tokens[0], 'output_tokens': tokens[1],
                      'cache_creation_input_tokens': tokens[2], 'cache_read_input_tokens': tokens[3]},
            'subagent_stats': {'spawned': spawned}}
    if models:
        data['modelUsage'] = {'claude-sonnet-5-5': {'inputTokens': tokens[0], 'outputTokens': tokens[1],
                                                    'cacheCreationInputTokens': tokens[2],
                                                    'cacheReadInputTokens': tokens[3]},
                              'claude-haiku-5-5': {'inputTokens': 10, 'outputTokens': 5}}
    return data


class Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-agents-test-')
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        path = self.dir / name
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return path

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()


class BriefTests(unittest.TestCase):
    def test_ready_brief_passes(self):
        self.assertEqual(brief.check(READY), [])

    def test_template_is_not_ready_until_filled(self):
        problems = brief.check(brief.template())
        self.assertTrue(any('placeholders' in p for p in problems))

    def test_each_missing_section_is_named(self):
        for section in ('Objective', 'Format', 'Tools', 'Boundaries', 'Stop'):
            text = READY.replace('## %s\n' % section, '## Notes\n')
            self.assertIn('Missing section: ## %s' % section, brief.check(text), section)

    def test_empty_section(self):
        text = READY.replace('A markdown table, then at most 80 words.\n', '')
        self.assertIn('Section Format is empty', brief.check(text))

    def test_done_when_required_and_measurable(self):
        no_done = READY.replace('Done when: a table of exactly 3 tools, each with a monthly price and a link.\n', '')
        self.assertTrue(any('Done when' in p for p in brief.check(no_done)))
        vague = READY.replace('a table of exactly 3 tools, each with a monthly price and a link',
                              'it feels good')
        self.assertTrue(any('not measurable' in p for p in brief.check(vague)))

    def test_use_and_do_not_touch_lines(self):
        self.assertIn('Tools has no "Use:" line', brief.check(READY.replace('Use: ', 'Prefer ')))
        self.assertIn('Boundaries has no "Do not touch:" line',
                      brief.check(READY.replace('Do not touch: any file on disk', 'Leave files alone')))

    def test_stop_needs_condition(self):
        text = READY.replace('Stop when the table has 3 rows, or after 10 searches, and report what blocked you.',
                             'Report back.')
        self.assertTrue(any('Stop does not say' in p for p in brief.check(text)))

    def test_level_three_headings_count(self):
        self.assertEqual(brief.check(READY.replace('## ', '### ')), [])


class CompareTests(Temp):
    def test_summary_uses_model_usage_including_subagents(self):
        summary = compare.summary(result())
        self.assertEqual(summary['tokens'], 100 + 50 + 1000 + 2000 + 15)
        self.assertTrue(summary['ok'])

    def test_summary_falls_back_to_usage(self):
        self.assertEqual(compare.summary(result(models=False))['tokens'], 3150)

    def test_ratio_and_table(self):
        a = self.write('a.json', result(seconds=20, cost=0.10))
        b = self.write('b.json', result(seconds=50, cost=0.25, spawned=1, turns=5))
        out = compare.compare(a, b)
        rows = {row[0]: row for row in out['rows']}
        self.assertEqual(rows['reported time (s)'][3], 2.5)
        self.assertEqual(rows['sub-agents spawned'][1:], (0, 1, None))
        text = compare.format_table(out)
        self.assertIn('2.5x', text)
        self.assertIn('found a real problem', text)
        self.assertNotIn('Warning', text)
        self.assertIn('pass --wall', text)
        walled = compare.compare(a, b, wall=(25.0, 48.4))
        self.assertEqual(walled['rows'][0], ('wall clock (s)', 25.0, 48.4, 1.94))
        self.assertNotIn('pass --wall', compare.format_table(walled))

    def test_failed_run_is_flagged(self):
        a = self.write('a.json', result())
        b = self.write('b.json', result(ok=False))
        self.assertIn('Warning', compare.format_table(compare.compare(a, b)))

    def test_stream_json_and_list_inputs(self):
        lines = '\n'.join([json.dumps({'type': 'system'}), 'not json', json.dumps(result(seconds=7))])
        self.assertEqual(compare.summary(compare.load(self.write('s.jsonl', lines)))['seconds'], 7.0)
        listed = self.write('l.json', [{'type': 'assistant'}, result(seconds=9)])
        self.assertEqual(compare.summary(compare.load(listed))['seconds'], 9.0)

    def test_rejects_other_json(self):
        with self.assertRaises(compare.CompareError):
            compare.load(self.write('x.json', {'hello': 1}))

    def test_cli_compare_and_error(self):
        a = self.write('a.json', result())
        b = self.write('b.json', result(seconds=30))
        code, out, _ = self.run_cli('compare', str(a), str(b), '--labels', 'solo', 'reviewed')
        self.assertEqual(code, 0)
        self.assertIn('solo', out)
        code, out, _ = self.run_cli('compare', str(a), str(b), '--wall', '10', '20')
        self.assertIn('wall clock (s)', out)
        code, out, _ = self.run_cli('compare', str(a), str(b), '--json')
        self.assertEqual(json.loads(out)['second']['seconds'], 30.0)
        code, _, err = self.run_cli('compare', str(a), str(self.write('bad.json', '{}')))
        self.assertEqual(code, 1)
        self.assertIn('not a claude -p', err)


class ResultTests(Temp):
    def test_result_prints_reply_and_subagents(self):
        data = result(spawned=1)
        data['result'] = 'All 7 tests pass. The reviewer found one real bug.'
        data['subagent_stats']['by_type'] = {'aios-agents:code-reviewer': 1}
        code, out, _ = self.run_cli('result', str(self.write('r.json', data)))
        self.assertEqual(code, 0)
        self.assertIn('aios-agents:code-reviewer (1)', out)
        self.assertIn('one real bug', out)
        code, out, _ = self.run_cli('result', str(self.write('n.json', result())))
        self.assertIn('Sub-agents used: none', out)


class CliBriefTests(Temp):
    def test_new_prints_and_writes_without_overwrite(self):
        code, out, _ = self.run_cli('brief', 'new')
        self.assertEqual(code, 0)
        self.assertIn('## Objective', out)
        target = self.dir / 'briefs' / 'job_v1.md'
        self.assertEqual(self.run_cli('brief', 'new', '--out', str(target))[0], 0)
        self.assertTrue(target.exists())
        code, _, err = self.run_cli('brief', 'new', '--out', str(target))
        self.assertEqual(code, 1)
        self.assertIn('already exists', err)

    def test_check_exit_codes_and_json(self):
        good = self.write('good.md', READY)
        code, out, _ = self.run_cli('brief', 'check', str(good))
        self.assertEqual((code, out.split(':')[0]), (0, 'READY'))
        code, out, _ = self.run_cli('brief', 'check', str(self.write('bad.md', '# nothing')), '--json')
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)['ok'])


class CrewTests(unittest.TestCase):
    def test_three_read_only_agents_without_claude_md(self):
        agents = crew.crew(PACK / 'agents')
        self.assertEqual([a['name'] for a in agents], ['code-reviewer', 'design-critic', 'researcher'])
        for agent in agents:
            self.assertTrue(agent['read_only'], agent['name'])
            self.assertTrue(agent['omit_claude_md'], agent['name'])
            self.assertEqual(agent['model'], 'sonnet')
        reviewer = agents[0]
        self.assertEqual(reviewer['tools'], 'Read, Grep, Glob')

    def test_no_agent_can_edit_or_run_shell(self):
        for path in (PACK / 'agents').glob('*.md'):
            tools = crew.frontmatter(path.read_text())['tools']
            for forbidden in ('Edit', 'Write', 'Bash', 'NotebookEdit', 'Agent'):
                self.assertNotIn(forbidden, tools.split(', '), path.name)

    def test_cli_crew(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(['crew']), 0)
        self.assertIn('code-reviewer', out.getvalue())


class PackTests(unittest.TestCase):
    def test_manifest_and_marketplace_entry(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual((data['name'], data['version'], data['dependencies']), ('aios-agents', '2.0.0', ['aios']))
        self.assertEqual(data['author']['name'], 'skyremote')
        entry = json.loads((PACK / 'MARKETPLACE_ENTRY.json').read_text())
        self.assertEqual(entry['source'], './plugins/aios-agents')

    def test_skills_short(self):
        for skill in PACK.glob('skills/*/SKILL.md'):
            lines = skill.read_text().splitlines()
            self.assertLess(len(lines), 500)
            description = next(l for l in lines if l.startswith('description:'))
            self.assertLessEqual(description.count('. ') + 1, 2, skill)

    def test_three_eval_cases_load_aios_too(self):
        prompts = sorted((PACK / 'evals').glob('*/prompt.md'))
        self.assertEqual(len(prompts), 3)
        for prompt in prompts:
            self.assertIn('"../../../aios"', prompt.read_text())

    def test_bin_runs_through_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'aios-agent'
            link.symlink_to(PACK / 'bin/aios-agent')
            proc = subprocess.run([str(link), '--version'], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('2.0.0', proc.stdout)



class TourAndModuleTests(unittest.TestCase):
    def test_module_number_and_tour(self):
        data = json.loads((PACK / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(data['metadata'], {'module': 7})
        self.assertEqual(data['dependencies'], ['aios'])
        tour = (PACK / 'TOUR.md').read_text()
        self.assertLess(len(tour.splitlines()), 150)
        self.assertIn('/aios learn 7', tour)
        for label in ('**Do:**', '**Command:**', '**They should see:**', '**Check:**'):
            self.assertIn(label, tour)


if __name__ == '__main__':
    unittest.main()
