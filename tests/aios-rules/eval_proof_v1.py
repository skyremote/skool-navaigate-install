#!/usr/bin/env python3
"""Run the aios-rules eval suite once per case and write <out>/eval_v1.md (outside the repository).

Usage: python3 tests/aios-rules/eval_proof_v1.py --out <folder outside the repo>

Claude Code 2.1.310's `claude plugin eval` loads the plugin under test on its own, so a pack that
declares `"dependencies": ["aios"]` fails to load with `dependency-unsatisfied` and is never scored.
The two skills do not use the aios plugin at runtime, so this script evaluates a copy of the pack
whose only change is that the dependencies line is removed. Everything else is byte for byte the same.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / 'plugins' / 'aios-rules'
WORK = Path('/tmp/aios2-a-foundations/eval-copy/aios-rules')
HOME = Path('/tmp/aios2-sandbox-a-foundations-eval')


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='folder outside the repository for eval_v1.md and eval_v1.json')
    OUT = Path(ap.parse_args().out).expanduser().resolve()
    if OUT == REPO or REPO in OUT.parents:
        raise SystemExit('Build proof stays out of the repository: choose a folder outside it.')
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(PACK, WORK, ignore=shutil.ignore_patterns('results', '__pycache__'))
    manifest = WORK / '.claude-plugin' / 'plugin.json'
    data = json.loads(manifest.read_text())
    data.pop('dependencies', None)
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    HOME.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'))
    result = Path('/tmp/aios2-a-foundations/eval_v1.json')
    cmd = ['claude', 'plugin', 'eval', str(WORK), '--runs', '1', '--trust-plugin', '--no-publish',
           '--output-dir', '/tmp/aios2-a-foundations/eval_v1', '--json', str(result)]
    proc = subprocess.run(cmd, cwd=str(WORK), env=env, capture_output=True, text=True, timeout=3000)
    data = json.loads(result.read_text())
    rows, loaded = [], True
    for case in data['cases']:
        arms = case['arms']
        w, wo = arms.get('with', [{}])[0], arms.get('without', [{}])[0]
        graders = ', '.join('%s %s' % (g['name'], 'pass' if g['passed'] else 'fail') for g in w.get('graders', []))
        rows.append('| %s | %s | %s | %s | %s |' % (case['name'], w.get('score'), wo.get('score'),
                                                  case['aggregates'].get('delta'), graders))
        trace = w.get('tracePath')
        if trace and Path(trace).exists():
            for line in open(trace):
                event = json.loads(line)
                if event.get('subtype') == 'init' and event.get('plugin_errors'):
                    loaded = False
    agg = data['aggregates']
    lines = ['# aios-rules eval, v1', '',
             'One run per case, with a no-plugin baseline arm, Claude Code %s, model as configured for the account.' % data.get('claudeVersion'),
             'HOME was a sandbox (`/tmp/aios2-sandbox-a-foundations-eval`). The report stayed local (`--no-publish`).', '',
             '**Why a copy:** `claude plugin eval` does not load a pack\'s dependencies, so with `"dependencies": ["aios"]`',
             'the pack fails with `dependency-unsatisfied` and both arms score the same. The evaluated copy differs only',
             'in that line. Plugin loaded without errors in this run: %s.' % ('yes' if loaded else 'NO'), '',
             '```sh', ' '.join(cmd).replace(str(WORK), '<copy of plugins/aios-rules without dependencies>'), '```', '',
             '| Case | With pack | Without pack | Delta | With-pack graders |', '|---|---|---|---|---|'] + rows + ['',
             'Overall with pack: %s. Mean delta: %s. Cases passed: %s of %s. Cost: about $%.2f. Runner exit %d (it exits 1 when any case scores below 1.0).'
             % (agg.get('overallScore'), agg.get('meanDelta'), agg.get('casesPassed'), agg.get('casesTotal'),
                data.get('costUsd') or 0, proc.returncode), '',
             '`skill-fired` is a with-only indicator and is not part of the score.', '']
    OUT.mkdir(exist_ok=True)
    (OUT / 'eval_v1.md').write_text('\n'.join(lines))
    summary = {'aggregates': agg, 'claudeVersion': data.get('claudeVersion'), 'costUsd': data.get('costUsd'),
               'cases': [{'name': c['name'], 'aggregates': c['aggregates'],
                          'with_graders': [{'name': g['name'], 'passed': g['passed']} for g in c['arms'].get('with', [{}])[0].get('graders', [])]}
                         for c in data['cases']], 'plugin_loaded': loaded}
    (OUT / 'eval_v1.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
