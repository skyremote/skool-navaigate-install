#!/usr/bin/env python3
"""aios-guide: the member's path through the twelve modules, in any harness.

  aios-guide next                 what is installed and the one next step
  aios-guide list                 every pack, its module and whether it is installed
  aios-guide find <words>         which pack gives a capability ("set up my brain")
  aios-guide install <pack|N>     install a pack (and its dependencies), then prove it
  aios-guide verify <pack>        prove a pack is installed and its hooks are active
  aios-guide learn <N|pack>       walk a module's tour, one step at a time
  aios-guide progress --complete N   record a module the member confirms is done
  aios-guide where                the checkout and catalogue this command uses
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import status  # noqa: E402

PLUGIN=HERE.parent
MARKET='navaigate-aios'


def home():
    return Path.home()


def state_dir():
    return home()/'.local/share/aios'


def cat():
    return status.catalogue()


def packs():
    return {p['name']:p for p in cat()['packs'] if p['kind']!='legacy'}


def harness(explicit=None):
    if explicit:
        return explicit
    if os.environ.get('CLAUDECODE') or os.environ.get('CLAUDE_PLUGIN_ROOT'):
        return 'claude'
    return 'codex-cursor'


def checkout():
    """The repository checkout that install.sh recorded, or the one this file lives in."""
    record=state_dir()/'checkout.json'
    if record.is_file():
        try:
            root=Path(json.loads(record.read_text())['root'])
            if (root/'install.sh').is_file():
                return root
        except (ValueError,KeyError,OSError):
            pass
    root=PLUGIN.parents[1]
    return root if (root/'install.sh').is_file() and (root/'.claude-plugin/marketplace.json').is_file() else None


def claude_dir():
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or home()/'.claude')


def claude_roots(pack):
    roots=[]
    def load(path):
        try:
            return json.loads(path.read_text())
        except (ValueError,OSError):
            return {}
    entries=load(claude_dir()/'plugins/installed_plugins.json').get('plugins',{}).get(pack+'@'+MARKET,[])
    if isinstance(entries,dict):
        entries=[entries]
    roots+= [Path(e['installPath']) for e in entries if e.get('installPath')]
    market=load(claude_dir()/'plugins/known_marketplaces.json').get(MARKET,{}).get('installLocation')
    if market:
        roots.append(Path(market)/'plugins'/pack)
    return roots


def pack_root(pack):
    """Where a pack's files are on this machine: Claude Code's copy, the marketplace clone or the checkout."""
    candidates=claude_roots(pack)
    root=checkout()
    if root:
        candidates.append(root/'plugins'/pack)
    candidates.append(PLUGIN.parent/pack)
    for path in candidates:
        if (path/'.claude-plugin/plugin.json').is_file():
            return path
    return None


def resolve(target):
    """A pack name, a module number or capability words -> pack name."""
    table=packs()
    target=str(target).strip()
    if target in table:
        return target
    if target.isdigit():
        number=int(target)
        found=[p['name'] for p in table.values() if p['module']==number and p['kind'] in ('start','core')]
        if found:
            return found[0]
        if number==12:
            raise SystemExit('Module 12 is the shelf. Choose one: '+', '.join(n for n,p in table.items() if p['kind']=='shelf'))
        raise SystemExit('Module '+target+' has no pack yet. Its lesson is on Skool: '+cat()['modules'][number-1]['lesson'])
    hits=find(target)
    if not hits:
        raise SystemExit('No pack matches "'+target+'". Run: aios-guide list')
    return hits[0][1]


def find(words):
    text=words.lower()
    scores=[]
    for name,pack in packs().items():
        score=sum(3 for c in pack['capabilities'] if re.search(r'\b'+re.escape(c)+r'\b',text))
        if pack['kind']!='bundle':
            score+=sum(1 for w in re.findall(r'[a-z]{4,}',text) if w in pack['description'].lower())
        if score:
            scores.append((score,name))
    return sorted(scores,key=lambda s:(-s[0],s[1]))


def installed_here(name,report=None):
    report=report or status.inventory()
    for entry in report['packs']:
        if entry['pack']==name:
            h=entry['harnesses']
            return {'claude':bool(h['claude']['installed']),'codex':h['codex']['skills_present'],'cursor':h['cursor']['skills_present']}
    return {'claude':False,'codex':False,'cursor':False}


def install_command(name,where):
    if where=='claude':
        return 'claude plugin install '+name+'@'+MARKET
    root=checkout()
    return (str(root/'install.sh') if root else './install.sh')+' '+name


def cmd_next(args):
    report=status.inventory()
    where=harness(args.harness)
    number=report['next_module']
    lines=['Harness: '+('Claude Code' if where=='claude' else 'Codex or Cursor')]
    have=[e['pack'] for e in report['packs']]
    lines.append('Installed packs: '+(', '.join(have) if have else 'none yet'))
    if report['v1']['marketplace_plugin_installed'] or any(report['v1']['skills_by_harness'].values()):
        lines.append('v1 skills found: they keep working, with fixes only until '+report['v1']['support_until']+'.')
    if not number:
        lines.append('Every module is confirmed. Pick a shelf pack: aios-guide list')
    else:
        module=cat()['modules'][number-1]
        lines.append('Next module: '+str(number)+'. '+module['title'])
        names=module['packs']
        if names:
            name=names[0]
            done=installed_here(name,report)
            ready=done['claude'] if where=='claude' else (done['codex'] or done['cursor'])
            lines.append('Its pack: '+name+(' (installed)' if ready else ' (not installed)'))
            lines.append('Next step: '+('aios-guide learn '+str(number) if ready else install_command(name,where)))
        else:
            lines.append('Its pack is still being built. The lesson is on Skool: '+module['lesson'])
    print('\n'.join(lines))
    return 0


def cmd_list(args):
    report=status.inventory()
    for p in cat()['packs']:
        if p['kind']=='legacy':
            continue
        done=installed_here(p['name'],report)
        flags=[k for k,v in done.items() if v]
        module='-' if p['module'] is None else str(p['module'])
        print(f"{module:>2}  {p['name']:<16} {p['kind']:<6} {'installed: '+', '.join(flags) if flags else 'not installed'}")
        print('    '+p['description'])
    missing=[m for m in cat()['modules'] if not m['packs']]
    if missing:
        print('Still being built: '+', '.join(str(m['number'])+'. '+m['title'] for m in missing))
    return 0


def cmd_find(args):
    hits=find(' '.join(args.words))
    if not hits:
        print('No pack matches. Run: aios-guide list')
        return 1
    for score,name in hits[:3]:
        p=packs()[name]
        print(name+' (module '+str(p['module'])+'): '+p['description'])
    return 0


def run(command,**kw):
    print('$ '+' '.join(command),flush=True)
    proc=subprocess.run(command,text=True,capture_output=True,**kw)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc


def verify_claude(name):
    claude=shutil.which('claude')
    if not claude:
        print('Unverified: the claude command is not on PATH.')
        return 1
    proc=run([claude,'plugin','details',name])
    if proc.returncode!=0:
        return 1
    expect=packs()[name]
    text=proc.stdout
    problems=[]
    for label,want in (('Skills',len(expect['skills'])),('Hooks',None),('MCP servers',len(expect['mcp_servers']))):
        found=re.search(r'^\s*'+label+r' \((\d+)\)',text,re.M)
        have=int(found.group(1)) if found else None
        if label=='Hooks':
            if expect['hooks'] and not have:
                problems.append('hooks are not active')
        elif have is not None and have<want:
            problems.append(label.lower()+': '+str(have)+' of '+str(want))
    for dep in expect['dependencies']:
        if run([claude,'plugin','details',dep]).returncode!=0:
            problems.append('dependency '+dep+' is not installed')
    if problems:
        print('FAIL '+name+': '+'; '.join(problems))
        return 1
    print('OK '+name+' is installed in Claude Code'+(' and its hooks are active' if expect['hooks'] else '')+'.')
    return 0


def verify_checkout(name):
    root=checkout()
    if not root:
        print('Unverified: no checkout recorded. Run install.sh from your clone of the repository first.')
        return 1
    return run([str(root/'install.sh'),name,'--check']).returncode


def cmd_install(args):
    name=resolve(' '.join(args.target))
    where=harness(args.harness)
    if where=='claude':
        claude=shutil.which('claude')
        if not claude:
            print('The claude command is not on PATH. Run this yourself: '+install_command(name,where))
            return 1
        proc=run([claude,'plugin','install',name+'@'+MARKET])
        if proc.returncode!=0:
            print('Install failed. If the marketplace is missing, run: claude plugin marketplace add skyremote/skool-navaigate-install')
            return proc.returncode
        code=verify_claude(name)
        print('Now type /reload-plugins in this session to load '+name+'.')
        return code
    root=checkout()
    if not root:
        print('No checkout recorded. Clone the repository, then run ./install.sh '+name+' from it.')
        return 1
    proc=run([str(root/'install.sh'),name])
    if proc.returncode!=0:
        return proc.returncode
    code=verify_checkout(name)
    print('Restart Codex or Cursor to load '+name+'.')
    return code


def cmd_verify(args):
    name=resolve(args.pack)
    return verify_claude(name) if harness(args.harness)=='claude' else verify_checkout(name)


STEP=re.compile(r'^## Step (\d+)\.\s*(.*)$',re.M)


def parse_tour(text):
    """TOUR.md -> intro, steps [{number,title,do,command,see,check}], outro."""
    marks=list(STEP.finditer(text))
    intro=text[:marks[0].start()] if marks else text
    steps=[]
    outro=''
    for i,mark in enumerate(marks):
        end=marks[i+1].start() if i+1<len(marks) else len(text)
        body=text[mark.end():end]
        later=re.search(r'^## ',body,re.M)
        if later:
            outro=body[later.start():]
            body=body[:later.start()]
        step={'number':int(mark.group(1)),'title':mark.group(2).strip()}
        for key,label in (('do','Do'),('command','Command'),('see','You should see'),('check','Check')):
            found=re.search(r'^- '+re.escape(label)+r':\s*(.*)$',body,re.M)
            step[key]=found.group(1).strip() if found else ''
        steps.append(step)
    return intro.strip(),steps,outro.strip()


def learn_state(name):
    return state_dir()/'learn'/(name+'.json')


def cmd_learn(args):
    name=resolve(args.target)
    p=packs()[name]
    module=cat()['modules'][p['module']-1] if p['module'] else None
    lesson=module['lesson'] if module else cat()['modules'][-1]['lesson']
    path=learn_state(name)
    done=set(json.loads(path.read_text()).get('done',[])) if path.is_file() else set()
    if args.reset:
        done=set()
    root=pack_root(name)
    tour=root/'TOUR.md' if root else None
    if not tour or not tour.is_file():
        print('Module '+str(p['module'])+': '+(module['title'] if module else name))
        print('This pack has no tour yet. Follow the Skool lesson: '+lesson)
        if p['skills']:
            print('Its skills: '+', '.join('/'+s for s in p['skills']))
        if not root:
            print('The pack is not on this machine yet. Install it first: aios-guide install '+name)
        return 0
    intro,steps,outro=parse_tour(tour.read_text())
    numbers=[s['number'] for s in steps]
    if args.done is not None:
        if args.done not in numbers:
            raise SystemExit('No step '+str(args.done)+' in this tour.')
        done.add(args.done)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'pack':name,'done':sorted(done),'steps':len(steps)})+'\n')
    pick=args.step or next((n for n in numbers if n not in done),None)
    print('Module '+str(p['module'])+': '+(module['title'] if module else name)+' ('+str(len(done))+' of '+str(len(steps))+' steps checked)')
    print('Lesson: '+lesson)
    if pick is None:
        print('Every step is checked.')
        if outro:
            print(outro)
        print('If the member confirms the module is finished, run: aios-guide progress --complete '+str(p['module']))
        return 0
    if not done and not args.step:
        print(intro)
    step=next(s for s in steps if s['number']==pick)
    print('')
    print('Step '+str(step['number'])+' of '+str(len(steps))+'. '+step['title'])
    for key,label in (('do','Do'),('command','Command'),('see','You should see'),('check','Check')):
        if step[key]:
            print(label+': '+step[key])
    print('')
    print('When the check passes, run: aios-guide learn '+str(p['module'] or name)+' --done '+str(step['number']))
    return 0


def cmd_progress(args):
    path=state_dir()/'progress.json'
    data=json.loads(path.read_text()) if path.is_file() else {}
    done=set(n for n in data.get('completed_modules',[]) if type(n) is int)
    if args.complete:
        if not 1<=args.complete<=12:
            raise SystemExit('Modules run from 1 to 12.')
        done.add(args.complete)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'completed_modules':sorted(done)})+'\n')
    print('Confirmed modules: '+(', '.join(map(str,sorted(done))) if done else 'none'))
    return 0


def cmd_where(args):
    root=checkout()
    print('Catalogue: '+str(status.CATALOGUE))
    print('Checkout: '+(str(root) if root else 'none recorded (Claude Code installs need none)'))
    print('Harness: '+harness(args.harness))
    return 0


def main(argv=None):
    parser=argparse.ArgumentParser(prog='aios-guide',description='Your path through the AIOS modules.')
    parser.add_argument('--harness',choices=['claude','codex','cursor','codex-cursor'],help='which harness is asking (default: detect)')
    sub=parser.add_subparsers(dest='command')
    sub.add_parser('next')
    sub.add_parser('list')
    sub.add_parser('where')
    f=sub.add_parser('find');f.add_argument('words',nargs='+')
    i=sub.add_parser('install');i.add_argument('target',nargs='+')
    v=sub.add_parser('verify');v.add_argument('pack')
    l=sub.add_parser('learn');l.add_argument('target')
    l.add_argument('--step',type=int);l.add_argument('--done',type=int);l.add_argument('--reset',action='store_true')
    g=sub.add_parser('progress');g.add_argument('--complete',type=int)
    args=parser.parse_args(argv)
    if args.harness in ('codex','cursor'):
        args.harness='codex-cursor'
    handlers={'next':cmd_next,'list':cmd_list,'find':cmd_find,'install':cmd_install,'verify':cmd_verify,
              'learn':cmd_learn,'progress':cmd_progress,'where':cmd_where,None:cmd_next}
    return handlers[args.command](args)


if __name__=='__main__':
    raise SystemExit(main())
