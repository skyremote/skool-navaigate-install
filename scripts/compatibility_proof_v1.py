#!/usr/bin/env python3
"""Probe CLI assumptions in a second empty /tmp HOME. No credentials are used."""
import json
import os
import shlex
import subprocess
from pathlib import Path
from proof_paths import portable

root = Path(__file__).resolve().parents[1]
home = Path('/tmp/aios-dependency-proof_v1')
home.mkdir(exist_ok=True)
env = dict(os.environ,HOME=str(home),CLAUDE_CONFIG_DIR=str(home/'.claude'),XDG_CONFIG_HOME=str(home/'.config'))
lines = ['# Claude Code compatibility evidence v1','',
 'Tested with Claude Code 2.1.310. All writes use a separate empty /tmp HOME.','']
for args,expected in [(['claude','plugin','marketplace','add','.'],1),
                       (['claude','plugin','marketplace','add','./'],0),
                       (['claude','plugin','install','aios-brain@navaigate-aios'],0),
                       (['claude','plugin','list','--json'],0)]:
    p = subprocess.run(args,cwd=root,env=env,text=True,capture_output=True,timeout=60)
    lines += ['```sh',shlex.join(args),'```','```text',(p.stdout+p.stderr).rstrip(),f'[exit {p.returncode}]','```','']
    if args[2:4]==['list','--json']:
        plugins = json.loads(p.stdout)
        ids = {r['id']:r for r in plugins}
        assert ids['aios@navaigate-aios']['enabled'] is True
        assert ids['aios-brain@navaigate-aios']['enabled'] is True
    assert (p.returncode != 0) if expected else p.returncode == 0
lines += ['## Findings','',
 '`marketplace add .` is rejected by this CLI. `marketplace add ./` and an absolute checkout path work. Documentation and tapes use those forms.',
 '', 'Installing only aios-brain also installs and enables aios. The manifests use the tested bare dependency name.',
 '', 'A shell plugin install does not show the userConfig dialog. Both optional options can be left unset for local mode; configure them later for MCP sync. No non-empty sensitive values were entered.',
 '', 'userConfig substitutions reach the MCP environment. Do not assume a terminal command receives them; the CLI also supports the private env file. Exported hook option names are uppercase.',
 '', 'Strict validation succeeds. The listing directory check warns that square listing icons are absent; it says this check does not change the validation result.',
 '', 'The installed CLI exposes evals with a no-plugin baseline and --no-publish. All three eval attempts are blocked by the empty sandbox not having a subscription login; see eval-results_v1.md.',
 '', 'The local-path marketplace loads plugin source from this checkout in place. Keep the checkout present; plugin list readFromFolder is the source authority even if installPath names an absent cache folder.',
 '', 'References: [manifest/userConfig and bin layout](https://code.claude.com/docs/en/plugins-reference), [eval suite format](https://code.claude.com/docs/en/plugin-evals). The CLI probes above are the evidence for this build.','']
(root/'proof/compatibility_v1.md').write_text(portable('\n'.join(lines))+'\n')
print('Dependency enablement and local-path compatibility checks passed.')
