#!/usr/bin/env python3
"""Record the audit reproductions without storing machine-specific paths."""
import os
from pathlib import Path
import shlex
import subprocess
import shutil
from proof_paths import portable

ROOT=Path(__file__).resolve().parents[1]
REPRO=Path('/tmp/aios-review-scripts')
commands=[['bash',str(REPRO/'runtime.sh'),str(ROOT)],
          ['bash',str(REPRO/'runtime2.sh'),str(ROOT)],
          ['bash',str(REPRO/'stale_failure.sh'),str(ROOT)],
          ['python3',str(REPRO/'cursor_jsonl.py'),str(ROOT)],
          ['python3',str(REPRO/'digest_loss.py'),str(ROOT)],
          ['python3',str(REPRO/'toml_cases.py'),str(ROOT)]]
lines=['# Audit reproductions v2','',
 'The review scripts run only against synthetic /tmp homes and the review checkout. Their diagnostics are preserved below; the named regression tests provide assertions for each finding.',
 'Machine-specific paths are represented by <worktree> and $HOME.',
 'The supplied cursor_jsonl.py script still labels its stored timestamp as file mtime; that diagnostic label is stale. The observed value now comes from the embedded Cursor timestamp. The final section deliberately shows failures against the unchanged baseline, separately from the passing current build.','']
env={'HOME':'/tmp/aios-review-runner-v2','PATH':'/usr/bin:/bin','TMPDIR':'/tmp','CLAUDE_CONFIG_DIR':'','CODEX_HOME':''}
for args in commands:
    if not Path(args[1]).exists():
        raise SystemExit('Review reproduction scripts are not present')
    proc=subprocess.run(args,env=env,cwd='/tmp',capture_output=True,text=True,timeout=60)
    lines+=['```sh',shlex.join(args),'```','```text',proc.stdout.rstrip(),proc.stderr.rstrip(),f'[exit {proc.returncode}]','```','']
modern=shutil.which('python3.14') or '/opt/homebrew/bin/python3.14'
if Path(modern).exists():
    args=[modern,str(REPRO/'toml_validate.py')]
    checked=subprocess.run(args,input=proc.stdout,env=env,capture_output=True,text=True,timeout=30)
    lines+=['## Independent TOML validation (Python 3.14)','', '```sh',shlex.join(args),'```','```text',checked.stdout.rstrip(),checked.stderr.rstrip(),f'[exit {checked.returncode}]','```','']
baseline=Path('/tmp/aios-review-baseline-v2.txt')
if baseline.exists():
    lines+=['## Baseline regression run','',
      'The 22 new regression tests were also run against the original ffddffb code in /tmp. Only the new test file and its import-only privacy helper were copied into that snapshot; the implementation stayed unchanged. The failures below demonstrate missing behaviour or missing new interfaces.','',
      '```text',baseline.read_text().rstrip(),'```','']
(ROOT/'proof/reproductions_v2.md').write_text(portable('\n'.join(lines))+'\n')
print('Audit reproduction evidence saved.')
