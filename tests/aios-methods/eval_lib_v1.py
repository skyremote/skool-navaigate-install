"""Run a stream D pack's three eval cases once each, with a no-plugin baseline.

claude plugin eval (2.1.310) does not load a path-target plugin whose manifest lists
"dependencies": ["aios"], because the bare name cannot be resolved inside the eval
sandbox: the with-arm then runs with no plugin at all. So this runner evaluates a copy
in /tmp with only the dependencies key removed. The skills, evals and bin are unchanged.
Results go to $AIOS_PROOF_DIR/<pack>/eval_<version>.json and .md, outside the repo.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SANDBOX = Path('/tmp/aios2-sandbox-d-methods-models-ship/eval-home')


def main(pack, version='v1'):
    work = Path('/tmp/aios2-d-methods-models-ship/eval-copy') / pack
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(ROOT / 'plugins' / pack, work, ignore=shutil.ignore_patterns('results', '__pycache__'))
    manifest = work / '.claude-plugin/plugin.json'
    data = json.loads(manifest.read_text())
    data.pop('dependencies', None)
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    SANDBOX.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('CLAUDE_CODE_', 'CLAUDECODE', 'CLAUDE_PLUGIN'))}
    env.update(HOME=str(SANDBOX), CLAUDE_CONFIG_DIR=str(SANDBOX / '.claude'))
    out = Path(os.environ.get('AIOS_PROOF_DIR', '/tmp/aios-proof')) / pack  # build evidence stays out of the repo
    out.mkdir(parents=True, exist_ok=True)
    raw = Path('/tmp/aios2-d-methods-models-ship') / (pack + '-eval_' + version + '.json')
    args = ['claude', 'plugin', 'eval', str(work), '--runs', '1', '--trust-plugin', '--no-publish', '--json', str(raw)]
    result = subprocess.run(args, env=env, text=True, capture_output=True, timeout=3600)
    data = json.loads(raw.read_text())
    text = json.dumps(data, indent=2).replace(str(ROOT), '<checkout>')
    (out / ('eval_' + version + '.json')).write_text(text + '\n')
    lines = ['# Eval results ' + version + ': ' + pack, '',
             'One run per case, with a no-plugin baseline arm (`--runs 1`, ablation with-without), Claude Code '
             + data.get('claudeVersion', '?') + ', ' + data.get('startedAt', '') + '.',
             'Evaluated a /tmp copy with only `dependencies` removed, because `claude plugin eval` cannot load a path plugin',
             'whose bare-name dependency (`aios`) is not resolvable in its sandbox. Skills, evals and bin are unchanged.', '',
             '```sh', 'claude plugin eval <copy-of>/plugins/' + pack + ' --runs 1 --trust-plugin --no-publish --json <file>', '```', '',
             '| Case | With pack | Without (baseline) | Skill fired | Graders failed with the pack |', '|---|---|---|---|---|']
    for case in data.get('cases', []):
        arms = case.get('arms', {})
        w = arms.get('with', [{}])[0]
        wo = arms.get('without', [{}])[0]
        fired = [g['passed'] for g in w.get('graders', []) if g['name'] == 'skill-fired']
        failed = [g['name'] for g in w.get('graders', []) if g.get('scored', True) and not g['passed']]
        err = (' (error: ' + w['error'] + ')') if w.get('error') else ''
        lines.append(f"| {case['name']} | {w.get('score')}{err} | {wo.get('score')} | {fired[0] if fired else 'n/a'} | {', '.join(failed) or 'none'} |")
    agg = data.get('aggregates', {})
    lines += ['', f"Overall with the pack: {agg.get('overallScore')}. Mean delta against the baseline: {agg.get('meanDelta')}.",
              f"Exit code {result.returncode} (1 means at least one case scored below the threshold of 1.0).", '']
    (out / ('eval_' + version + '.md')).write_text('\n'.join(lines))
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
