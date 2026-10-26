#!/usr/bin/env python3
"""Run the real install/CLI flow with every command, output and exit code saved."""
import json
import os
import shlex
import subprocess
from pathlib import Path
from proof_paths import portable

ROOT = Path(__file__).resolve().parents[1]
HOME = Path('/tmp/aios-member-sandbox')
ENV = dict(os.environ,HOME=str(HOME),CLAUDE_CONFIG_DIR=str(HOME/'.claude'),
           XDG_CONFIG_HOME=str(HOME/'.config'),XDG_DATA_HOME=str(HOME/'.local/share'))
ENV['PATH'] = str(HOME/'.local/bin')+':'+ENV['PATH']
# Prevent inherited harness overrides from pointing at a real config folder.
ENV['CODEX_HOME'] = str(HOME/'.codex')
ENV.pop('CURSOR_CONFIG_DIR',None)
ENV.pop('AIOS_BRAIN_TURSO_URL',None)
ENV.pop('AIOS_BRAIN_TURSO_TOKEN',None)
ENV.pop('CLAUDE_PLUGIN_OPTION_TURSO_URL',None)
ENV.pop('CLAUDE_PLUGIN_OPTION_TURSO_TOKEN',None)
ENV.pop('SUPADATA_API_KEY',None)
ENV['TMPDIR']='/tmp'
HOME.mkdir(parents=True,exist_ok=True)
REPORT = ROOT/'.evidence/sandbox-run_v2.md'
lines = ['# Sandbox member install proof v2','',
         'Paths are normalised as <worktree> and $HOME for portability. All commands use HOME=/tmp/aios-member-sandbox and CLAUDE_CONFIG_DIR=$HOME/.claude.',
         'The working directory is the review checkout. Fixtures are fictional. No real member data or tokens are used.','']
failed = []


def run(args,expect=0):
    if args[0]=='brain':
        args=[str(HOME/'.local/bin/brain'),*args[1:]]
    proc = subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    command = shlex.join(args)
    lines.extend(['```sh',command,'```','```text','\n'.join(line.rstrip() for line in (proc.stdout+proc.stderr).splitlines()),f'[exit {proc.returncode}]','```',''])
    REPORT.write_text(portable('\n'.join(lines))+'\n')
    print(command+' -> exit '+str(proc.returncode),flush=True)
    if proc.returncode != expect:
        failed.append(command)
        lines.extend(['FAILED: unexpected exit; stopped before any dependent command.',''])
        REPORT.write_text(portable('\n'.join(lines))+'\n')
        raise SystemExit(1)
    return proc


run(['claude','--version'])
run(['claude','plugin','validate','plugins/aios','--strict'])
run(['claude','plugin','validate','./','--strict'])
run(['claude','plugin','validate','plugins/aios-brain','--strict'])
run(['claude','plugin','validate','.claude-plugin/marketplace.json','--strict'])
run(['claude','plugin','marketplace','add',str(ROOT)])
run(['claude','plugin','install','aios@navaigate-aios'])
run(['claude','plugin','install','aios-brain@navaigate-aios'])
run(['claude','plugin','list','--json'])
# Existing fictional entries prove both config merges preserve other servers.
run(['python3','scripts/sandbox_config_v1.py','seed'])
run(['./install.sh','aios'])
run(['./install.sh','aios-brain'])
run(['python3','scripts/sandbox_fixtures_v1.py','--home',str(HOME)])
run(['brain','init'])
run(['brain','status'],expect=1)
run(['brain','capture'])
run(['brain','capture'])
hits = run(['brain','search','Lighthouse budget'])
try:
    ref = json.loads(hits.stdout)['hits'][0]['ref']
    run(['brain','read',ref])
except (ValueError,KeyError,IndexError):
    failed.append('No Lighthouse search hit')
run(['brain','status'])
run(['python3','plugins/aios/scripts/status.py'])
run(['python3','scripts/sandbox_config_v1.py','verify'])
run(['python3','scripts/sandbox_mcp_v1.py'])
run(['codex','--version'])
run(['codex','mcp','list'])
lines.extend(['## Result','',('PASS: all expected exit codes, search/read and backup assertions passed.' if not failed else 'FAIL: '+', '.join(failed)),
              '', 'This proves installation and the local CLI flow. Harness reload and live remote Turso/paid media/subscription digest use are separate checks.',''])
REPORT.write_text(portable('\n'.join(lines))+'\n')
raise SystemExit(bool(failed))
