#!/usr/bin/env python3
"""Sandbox proof for the AIOS 2.0 core, as a new member, in Claude Code, Codex and Cursor.

  python3 tests/core/sandbox_proof.py --repo <checkout> --out <folder outside the repo>

The checkout should hold the packs to prove (for aios-complete, a merge of every stream).
Every command runs with HOME=/tmp/aios2-sandbox-core (or --home). Each command, its
output and its exit code go into <out>/sandbox_v1.md. Fixtures are fictional.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve()
REPO_OF_SCRIPT=HERE.parents[2]
CORE=['aios','aios-rules','aios-harnesses','aios-bb','aios-brain','aios-skills','aios-agents','aios-verify',
      'aios-methods','aios-models','aios-ship']


class Proof:
    def __init__(self,repo,home,out):
        self.repo,self.home,self.out=repo,home,out
        self.lines=['# AIOS 2.0 core: sandbox proof v1','',
                    'HOME is the sandbox folder. Paths are shown as `$HOME` and `<repo>`. Fixtures are fictional.','']
        self.failed=[]
        env=dict(os.environ,HOME=str(home),CLAUDE_CONFIG_DIR=str(home/'.claude'),CODEX_HOME=str(home/'.codex'),
                 XDG_CONFIG_HOME=str(home/'.config'),XDG_DATA_HOME=str(home/'.local/share'),TMPDIR='/tmp')
        for key in ('CLAUDECODE','CLAUDE_CODE_ENTRYPOINT','CLAUDE_PLUGIN_ROOT','CLAUDE_PLUGIN_DATA','CURSOR_CONFIG_DIR',
                    'AIOS_BRAIN_TURSO_URL','AIOS_BRAIN_TURSO_TOKEN','SUPADATA_API_KEY','CLAUDE_CODE_SESSION_ID'):
            env.pop(key,None)
        env['PATH']=str(home/'.local/bin')+':'+env['PATH']
        self.env=env

    def portable(self,text):
        return text.replace(str(self.repo),'<repo>').replace(str(self.home),'$HOME').replace('/private$HOME','$HOME')

    def heading(self,text):
        self.lines.extend(['## '+text,''])

    def note(self,text):
        self.lines.extend([text,''])

    def save(self):
        self.out.mkdir(parents=True,exist_ok=True)
        (self.out/'sandbox_v1.md').write_text(self.portable('\n'.join(self.lines))+'\n')

    def run(self,args,expect=0,timeout=300,keep=60,must=None,must_not=None,label=None):
        proc=subprocess.run(args,cwd=str(self.home),env=self.env,text=True,capture_output=True,timeout=timeout)
        text=(proc.stdout+proc.stderr).rstrip()
        shown=text.splitlines()
        if len(shown)>keep:
            shown=shown[:keep]+['... ('+str(len(text.splitlines())-keep)+' more lines)']
        ok=(expect is None or proc.returncode==expect)
        problems=[]
        if not ok:
            problems.append('exit '+str(proc.returncode)+', expected '+str(expect))
        for pattern in must or []:
            if not re.search(pattern,text,re.M):
                problems.append('missing: '+pattern)
        for pattern in must_not or []:
            if re.search(pattern,text,re.M):
                problems.append('unexpected: '+pattern)
        self.lines.extend(['```sh',shlex.join(args),'```','```text',*[l.rstrip() for l in shown],'[exit '+str(proc.returncode)+']','```'])
        if problems:
            self.failed.append((label or shlex.join(args))+': '+'; '.join(problems))
            self.lines.append('**FAIL:** '+'; '.join(problems))
        else:
            self.lines.append('PASS'+(': '+label if label else ''))
        self.lines.append('')
        self.save()
        print(('PASS ' if not problems else 'FAIL ')+(label or shlex.join(args)[:100]),flush=True)
        return proc


def claude_installed(proof):
    data=json.loads(proof.run(['claude','plugin','list','--json'],keep=5,label='list installed plugins').stdout or '[]')
    items=data if isinstance(data,list) else data.get('plugins',data.get('installed',[]))
    names=set()
    for item in items:
        name=item.get('id') or item.get('name') or ''
        names.add(name.split('@')[0])
    return names


def claude_code(proof):
    p=proof
    p.heading('Claude Code')
    p.run(['claude','--version'])
    p.run(['claude','plugin','marketplace','add',str(p.repo)],label='add the local marketplace')
    p.run(['claude','plugin','install','aios@navaigate-aios'],must=[r'Successfully installed plugin: aios@navaigate-aios'],label='install aios')
    p.run(['claude','plugin','details','aios'],must=[r'Skills \(1\)'],label='aios is installed with its skill')
    p.note('A new headless session stands in for `/reload-plugins`: each `claude -p` loads the installed plugins fresh.')
    p.run(['claude','-p','/aios set up my brain. I confirm: install it now and show me the proof.','--allowedTools','Bash',
           '--model','claude-sonnet-5-5'],timeout=600,must=[r'(?i)reload-plugins'],label='/aios installs aios-brain on request')
    installed=claude_installed(p)
    if 'aios-brain' not in installed:
        p.failed.append('aios-brain not installed by /aios');p.note('**FAIL:** aios-brain is not installed.')
    p.run(['claude','plugin','details','aios-brain'],must=[r'MCP servers \(1\)',r'Skills \(1\)'],label='aios-brain proof: skill and MCP server')
    p.run(['claude','-p','/aios install the whole framework with aios-complete. I confirm: install it now and show me the proof.',
           '--allowedTools','Bash','--model','claude-sonnet-5-5'],timeout=900,label='/aios installs aios-complete')
    installed=claude_installed(p)
    missing=[n for n in CORE+['aios-complete'] if n not in installed]
    shelf=[n for n in installed if n.startswith('shelf-')]
    p.note('Installed after aios-complete: '+', '.join(sorted(installed))+'.')
    if missing:
        p.failed.append('aios-complete left out: '+', '.join(missing));p.note('**FAIL:** missing '+', '.join(missing))
    if shelf:
        p.failed.append('shelf packs installed by the bundle: '+', '.join(shelf));p.note('**FAIL:** shelf packs installed: '+', '.join(shelf))
    p.run(['claude','plugin','details','aios-verify'],must=[r'Hooks \([1-9]'],label='aios-verify hooks are active in Claude Code')
    p.run([str(p.repo/'plugins/aios/bin/aios-guide'),'--harness','claude','verify','aios-verify'],must=[r'^OK aios-verify .*hooks are active'],
          label='aios-guide verify (Claude Code)')
    p.run(['claude','-p','/aios learn 3','--allowedTools','Bash','--model','claude-sonnet-5-5'],timeout=600,
          must=[r'(?i)step 1'],label='/aios learn 3 teaches step 1 of the harnesses tour')


def codex_cursor(proof):
    p=proof
    p.heading('Codex and Cursor (one installer)')
    # Fictional member files that must survive every install.
    (p.home/'.codex').mkdir(parents=True,exist_ok=True)
    (p.home/'.cursor').mkdir(parents=True,exist_ok=True)
    (p.home/'.codex/config.toml').write_text('model = "fictional"\n[mcp_servers.acme-notes]\ncommand = "acme-notes"\n')
    (p.home/'.codex/AGENTS.md').write_text('# Acme Studio rules\n- Use British English.\n')
    (p.home/'.cursor/hooks.json').write_text(json.dumps({'version':1,'hooks':{'afterFileEdit':[{'command':'./hooks/acme-format.sh'}]}},indent=2)+'\n')
    (p.home/'.cursor/mcp.json').write_text(json.dumps({'mcpServers':{'acme-notes':{'command':'acme-notes'}}},indent=2)+'\n')
    p.note('Seeded fictional member files: a Codex MCP server and AGENTS.md rule, a Cursor hook and MCP server.')
    install=str(p.repo/'install.sh')
    p.run([install,'aios'],must=[r'Recorded this checkout',r'Installed aios 2\.0\.0'],label='install aios (records the checkout)')
    guide=str(p.home/'.local/bin/aios-guide')
    p.run([guide,'--harness','codex','next'],must=[r'Next module: 1\. Start here'],label='aios-guide next')
    p.run([guide,'--harness','codex','find','set','up','my','brain'],must=[r'^aios-brain'],label='find a pack by capability')
    p.run([guide,'--harness','codex','install','aios-brain'],must=[r'^OK aios-brain'],label='aios-guide installs aios-brain and proves it')
    p.run([guide,'--harness','codex','install','aios-complete'],must=[r'^OK aios-complete'],label='aios-guide installs aios-complete')
    p.run([install,'aios-complete'],must_not=[r'^Linked',r'^Configured'],label='second run changes nothing')
    for pack in CORE+['aios-complete']:
        p.run([install,pack,'--check'],keep=3,must=[r'^OK '+re.escape(pack)],label=pack+' --check')
    hooks=json.loads((p.home/'.cursor/hooks.json').read_text())
    p.lines.extend(['Cursor `~/.cursor/hooks.json` after the installs:','```json',json.dumps(hooks,indent=2),'```',''])
    if hooks['hooks'].get('afterFileEdit')!=[{'command':'./hooks/acme-format.sh'}]:
        p.failed.append('member Cursor hook lost')
    if not any('aios-verify guard' in e.get('command','') and e.get('matcher')=='Shell' for e in hooks['hooks'].get('preToolUse',[])):
        p.failed.append('aios-verify guard not merged into Cursor preToolUse')
    backups=sorted(x.name for x in (p.home/'.cursor').glob('*.backup-*'))
    p.note('Cursor backups: '+', '.join(re.sub(r'\d{6,}','<time>',b) for b in backups)+'.')
    agents=(p.home/'.codex/AGENTS.md').read_text()
    p.lines.extend(['Codex `~/.codex/AGENTS.md` after the installs:','```markdown',agents.rstrip(),'```',''])
    if not agents.startswith('# Acme Studio rules\n- Use British English.') or 'not enforced' not in agents:
        p.failed.append('Codex AGENTS.md rules block wrong')
    p.run(['codex','--version'])
    p.run(['codex','mcp','list'],must=[r'aios-brain',r'acme-notes'],label='Codex sees the brain MCP server and keeps the member one')
    prompt=p.run(['codex','debug','prompt-input','hello'],keep=0,label='Codex prompt input (what Codex would send the model)')
    text=prompt.stdout
    for name in ('aios','brain','harness-check','verify-setup'):
        hit=re.search(r'\b'+re.escape(name)+r'\b',text) is not None
        p.note('Codex prompt lists skill `'+name+'`: '+('yes' if hit else 'no'))
        if not hit:
            p.failed.append('Codex prompt does not list skill '+name)
    hit='aios-hooks:aios-verify' in text or 'written down, not enforced' in text
    p.note('Codex prompt carries the written aios-verify rules: '+('yes' if hit else 'no'))
    if not hit:
        p.failed.append('Codex prompt does not carry the aios-verify rules')
    p.run([guide,'--harness','codex','learn','3'],must=[r'Step 1 of \d+\.'],label='aios-guide learn 3 in Codex and Cursor')
    p.run(['cursor-agent','--version'])
    p.run(['cursor-agent','mcp','list'],expect=None,label='Cursor MCP list (needs a Cursor login to show status)')
    p.note('Cursor and Codex model sessions were not run: the sandbox has no Cursor or Codex login, and copying the '
           'owner\'s tokens into the sandbox could rotate and break the real logins.')


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--repo',type=Path,default=REPO_OF_SCRIPT)
    parser.add_argument('--home',type=Path,default=Path('/tmp/aios2-sandbox-core'))
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--only',choices=['claude','codex-cursor'])
    args=parser.parse_args()
    repo,out=args.repo.resolve(),args.out.resolve()
    if repo in out.parents or out==repo or REPO_OF_SCRIPT in out.parents:
        raise SystemExit('Proof notes stay out of the repository: choose --out outside it.')
    proof=Proof(repo,args.home,out)
    args.home.mkdir(parents=True,exist_ok=True)
    proof.note('Checkout: `'+subprocess.run(['git','-C',str(repo),'log','--oneline','-1'],text=True,capture_output=True).stdout.strip()+'`')
    if args.only in (None,'claude'):
        claude_code(proof)
    if args.only in (None,'codex-cursor'):
        codex_cursor(proof)
    proof.heading('Result')
    proof.note('PASS: every check passed.' if not proof.failed else 'FAIL:\n'+'\n'.join('- '+f for f in proof.failed))
    proof.save()
    print('Report: '+str(out/'sandbox_v1.md'))
    raise SystemExit(1 if proof.failed else 0)


if __name__=='__main__':
    main()
