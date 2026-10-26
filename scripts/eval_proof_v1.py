#!/usr/bin/env python3
"""Run all three advice eval cases, keeping authentication failures explicit."""
import json
import os
import shlex
import subprocess
from pathlib import Path
from proof_paths import portable

root = Path(__file__).resolve().parents[1]
home = Path('/tmp/aios-member-sandbox')
env = dict(os.environ,HOME=str(home),CLAUDE_CONFIG_DIR=str(home/'.claude'))
rows = []
lines = ['# Plugin eval results v1','',
 'Real claude plugin eval attempts, with a no-plugin baseline requested and publishing disabled.',
 'The sandbox uses HOME=/tmp/aios-member-sandbox. No credentials were copied from a real harness.','']
for case in ['local-setup','silent-failure','media-privacy']:
    output = root/'proof'/f'eval-{case}_v1.json'
    args = ['claude','plugin','eval','plugins/aios-brain','--case',case,'--runs','1',
            '--trust-plugin','--no-publish','--output-dir',f'/tmp/aios-eval-{case}_v1','--json',str(output)]
    p = subprocess.run(args,cwd=root,env=env,text=True,capture_output=True,timeout=300)
    data = json.loads(portable(output.read_text())) if output.exists() else {}
    if output.exists():
        output.write_text(portable(json.dumps(data,indent=2))+'\n')
    cases = data.get('cases',[])
    errors = [r.get('error') for c in cases for runs in c.get('arms',{}).values() for r in runs if r.get('error')]
    row = {'case':case,'exit':p.returncode,'partial':data.get('partial'),
           'reason':data.get('partialReason'),'errors':errors,
           'runner_overall_score':data.get('aggregates',{}).get('overallScore'),
           'valid_model_score':None if data.get('partial') else data.get('aggregates',{}).get('overallScore')}
    rows.append(row)
    lines += ['```sh',shlex.join(args),'```','```text',(p.stdout+p.stderr).rstrip(),f'[exit {p.returncode}]','```','']
lines += ['## Scores','', '| Case | With plugin | No-plugin baseline | Valid result |', '|---|---|---|---|']
for row in rows:
    if row['partial']:
        lines.append('| '+row['case']+' | Unscored | Not reached | '+str(row['reason'])+' |')
    else:
        lines.append('| '+row['case']+' | '+str(row['valid_model_score'])+' | See raw report | Completed |')
lines += ['', 'The runner records zero on the aborted first arm and exits 2, but this is an authentication failure, not a measured plugin quality score. No valid WITH/WITHOUT delta exists.',
 '', 'Next action: sign in to the member sandbox with its own Claude subscription, then rerun the three-case suite with --no-publish. The final acceptance run should use the default three runs per arm.',
 '', 'The cases cover local setup commands/storage/health, detecting a misleading heartbeat and 30-day retention, and free-caption/paid-transcription/digest opt-in boundaries. Skill invocation is an indicator; output regexes score both arms.',
 '', 'Unit and integration checks exercise the implementation independently; they do not replace model evals.','']
(root/'.evidence/eval-results_v1.md').write_text(portable('\n'.join(lines))+'\n')
(root/'.evidence/eval-summary_v1.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
