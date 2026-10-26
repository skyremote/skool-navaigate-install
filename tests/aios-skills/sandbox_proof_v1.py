#!/usr/bin/env python3
"""Install a stream C pack as a brand-new member in a throwaway HOME and record every command.

Usage: python3 tests/aios-skills/sandbox_proof_v1.py <pack> <steps.json> <out.md>

The repository is copied to /tmp with the INTEGRATION.md changes applied (the
installer patch and the marketplace entries), because shared files are merged by
the chief of staff, not by this stream. Nothing outside the sandbox is touched.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STREAM = 'c-skills-agents-verify'
SANDBOX = Path('/tmp/aios2-sandbox-' + STREAM)
COPY = Path('/tmp/aios2-' + STREAM + '/repo-copy')
PATCH = ROOT / 'plugins/aios-skills/INTEGRATION.md'
PACKS = ['aios-skills', 'aios-agents', 'aios-verify']


def prepare():
    if COPY.exists():
        shutil.rmtree(COPY)
    shutil.copytree(ROOT, COPY, ignore=shutil.ignore_patterns('.git', 'results', '__pycache__', '*.mp4', 'clips'))
    text = PATCH.read_text()
    diff = text.split('```diff\n', 1)[1].split('\n```', 1)[0] + '\n'
    subprocess.run(['patch', '-p1', '-s'], cwd=COPY, input=diff, text=True, check=True)
    market = COPY / '.claude-plugin/marketplace.json'
    data = json.loads(market.read_text())
    names = {p['name'] for p in data['plugins']}
    for pack in PACKS:
        entry = COPY / 'plugins' / pack / 'MARKETPLACE_ENTRY.json'
        if entry.exists() and pack not in names:
            data['plugins'].append(json.loads(entry.read_text()))
    market.write_text(json.dumps(data, indent=2) + '\n')
    subprocess.run(['git', 'init', '-q'], cwd=COPY, check=True)


def run(steps, fresh):
    if fresh and SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True, exist_ok=True)
    work = SANDBOX / 'acme-studio'
    work.mkdir(exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ('PATH', 'LANG', 'TERM', 'USER', 'SHELL',
           'ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'TMPDIR')}
    env.update(HOME=str(SANDBOX), CLAUDE_CONFIG_DIR=str(SANDBOX / '.claude'), CODEX_HOME=str(SANDBOX / '.codex'),
               PATH=str(SANDBOX / '.local/bin') + ':' + env.get('PATH', ''), AIOS_REPO=str(COPY))
    records = []
    for step in steps:
        cwd = {'repo': COPY, 'work': work}.get(step.get('cwd', 'work'), work)
        proc = subprocess.run(step['cmd'], shell=True, cwd=str(cwd), env=env, text=True, stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=step.get('timeout', 300))
        output = (proc.stdout + proc.stderr).replace(str(COPY), '<repo>').replace(str(SANDBOX), '$HOME')
        expect = step.get('expect')
        ok = proc.returncode == step.get('exit', 0) and (expect is None or expect in output)
        records.append((step, proc.returncode, output.rstrip(), ok))
    return records


def write(pack, records, out):
    lines = ['# Sandbox install proof v1: ' + pack, '',
             'A brand-new member home, `HOME=/tmp/aios2-sandbox-%s` (shown as `$HOME`), with no' % STREAM,
             'credentials copied in. The repository copy (`<repo>`) has the INTEGRATION.md installer',
             'patch and marketplace entries applied. Commands ran in order; each block shows the',
             'exit code and the real output.', '']
    passed = sum(1 for r in records if r[3])
    lines += ['Result: %d of %d steps as expected.' % (passed, len(records)), '']
    for step, code, output, ok in records:
        lines += ['## %s %s' % ('PASS' if ok else 'FAIL', step['title']), '',
                  '```sh', '$ ' + step['cmd'].replace(str(COPY), '<repo>'), '```', '```text',
                  output or '(no output)', '[exit %d]' % code, '```', '']
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text('\n'.join(lines))
    return passed == len(records)


def main():
    pack, steps_file, out = sys.argv[1], sys.argv[2], sys.argv[3]
    steps = json.loads(Path(steps_file).read_text())
    prepare()
    records = run(steps, fresh=os.environ.get('AIOS_SANDBOX_KEEP') != '1')
    ok = write(pack, records, out)
    for step, code, _, good in records:
        print('%s  [%d] %s' % ('PASS' if good else 'FAIL', code, step['title']))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
