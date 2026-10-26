#!/usr/bin/env python3
"""Install AIOS 2.0 packs for Codex and Cursor.

One command installs a pack and everything it depends on, in order. It plans every
pack first and writes nothing until every check passes. It preserves v1 links,
dotfiles symlinks, foreign skills and commands, and edits made by other programs.
Running it twice changes nothing the second time.
"""
import argparse
from contextlib import ExitStack
import fcntl
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL_DIRS=('.codex/skills','.cursor/skills','.agents/skills')
STATE='.local/share/aios'
# Claude Code hook events and their Cursor names. Events without a match are reported, never dropped silently.
CURSOR_EVENTS={'PreToolUse':'preToolUse','PostToolUse':'postToolUse','PostToolUseFailure':'postToolUseFailure',
               'UserPromptSubmit':'beforeSubmitPrompt','Stop':'stop','SubagentStart':'subagentStart',
               'SubagentStop':'subagentStop','SessionStart':'sessionStart','SessionEnd':'sessionEnd','PreCompact':'preCompact'}
CURSOR_TOOLS={'Bash':'Shell','Read':'Read','Write':'Write','Edit':'Write','MultiEdit':'Write','NotebookEdit':'Write',
              'Grep':'Grep','Glob':'Grep','Task':'Task','Agent':'Task'}
CODEX_EVENTS={'PreToolUse':'Before','PostToolUse':'After','PostToolUseFailure':'After a failed',
              'UserPromptSubmit':'When the member sends a prompt','Stop':'Before you finish a reply',
              'SessionStart':'At the start of each session','SessionEnd':'At the end of each session',
              'PreCompact':'Before the context is compacted','SubagentStart':'When a sub-agent starts',
              'SubagentStop':'When a sub-agent finishes','Notification':'When you need the member'}


def atomic_write(path,text):
    if path.is_symlink():
        raise ValueError('Symlinked file preserved; edit its dotfiles source manually: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=str(path.parent))
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write(text)
        os.chmod(name,0o600)
        os.replace(name,path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def codex_config(text,executable,name='aios-brain',args=('mcp',)):
    """Add one MCP server table to Codex's config.toml, or confirm our exact table is already there."""
    original=text
    normal=text.replace('\r\n','\n')
    if normal.startswith('﻿'):
        raise ValueError('TOML byte-order mark found; remove it manually before installing')
    for quoted in re.finditer(r'(?s)("""|\'\'\').*?\1',normal):
        if name in quoted[0]:
            raise ValueError(name+' in a multiline TOML string; merge the MCP entry manually')
    block='[mcp_servers.'+name+']\ncommand = '+json.dumps(str(executable))+'\nargs = '+json.dumps(list(args))+'\n'
    if name in normal:
        # Also covers dotted keys, array tables, inline objects and comments on 3.9.
        # Only our exact ordinary stanza is safe to recognise without a TOML parser.
        if normal.count(block.strip())!=1:
            raise ValueError('Existing custom '+name+' TOML preserved; merge it manually')
        remainder=normal.replace(block.strip(),'',1)
        if name in remainder:
            raise ValueError('Other '+name+' TOML representation preserved; merge it manually')
        after=normal.split(block.strip(),1)[1]
        tail=after.lstrip('\n')
        if tail and not tail.startswith('[') and not tail.startswith('#'):
            raise ValueError('Custom '+name+' table fields preserved; merge them manually')
        result=original
    else:
        newline='\r\n' if '\r\n' in original else '\n'
        result=original.rstrip()+newline*2+block.replace('\n',newline)
    try:
        import tomllib
    except ImportError:
        pass  # The conservative guard above applies on Python 3.9/3.10 too.
    else:
        tomllib.loads(normal)
        parsed=tomllib.loads(result)
        if parsed.get('mcp_servers',{}).get(name)!={'command':str(executable),'args':list(args)}:
            raise ValueError('MCP representation differs; merge it manually')
    return result


def cursor_mcp(text,servers):
    parsed=json.loads(text) if text and text.strip() else {}
    if not isinstance(parsed,dict) or not isinstance(parsed.get('mcpServers',{}),dict):
        raise ValueError('Cursor MCP configuration must contain an object of servers')
    current=parsed.setdefault('mcpServers',{})
    for name,(command,args) in servers.items():
        existing=current.get(name,{})
        if not isinstance(existing,dict) or existing.get('command',str(command))!=str(command):
            raise ValueError('Existing custom Cursor '+name+' server preserved; merge it manually')
        current[name]=dict(existing,command=str(command),args=list(args))
    return json.dumps(parsed,indent=2)+'\n'


def cursor_matcher(matcher):
    """Translate a Claude Code tool matcher into Cursor tool types. None means it cannot be translated."""
    if matcher in (None,'','*'):
        return ''
    names=[]
    for part in matcher.split('|'):
        part=part.strip()
        if part.startswith('mcp__'):
            names.append('MCP:'+part.split('__')[-1])
        elif part in CURSOR_TOOLS:
            names.append(CURSOR_TOOLS[part])
        else:
            return None
    return '|'.join(dict.fromkeys(names))


def pack_hooks(plugin):
    """Read a pack's Claude Code hooks file. Returns (events, [(event, matcher, hook)])."""
    path=plugin/'hooks/hooks.json'
    if not path.is_file():
        return []
    data=json.loads(path.read_text())
    found=[]
    for event,groups in (data.get('hooks') or {}).items():
        for group in groups or []:
            for hook in group.get('hooks') or []:
                found.append((event,group.get('matcher',''),hook))
    return found


def substitute(text,plugin):
    return str(text).replace('${CLAUDE_PLUGIN_ROOT}',str(plugin)).replace('$CLAUDE_PLUGIN_ROOT',str(plugin))


def cursor_hooks(text,plugin):
    """Merge a pack's hooks into ~/.cursor/hooks.json. Existing entries always stay. Returns (text, notes)."""
    parsed=json.loads(text) if text and text.strip() else {}
    if not isinstance(parsed,dict) or not isinstance(parsed.get('hooks',{}),dict):
        raise ValueError('Cursor hooks.json must hold an object of hooks; merge it manually')
    parsed.setdefault('version',1)
    hooks=parsed.setdefault('hooks',{})
    notes=[]
    for event,matcher,hook in pack_hooks(plugin):
        target=CURSOR_EVENTS.get(event)
        if hook.get('type','command')!='command':
            notes.append('Cursor: '+event+' '+hook.get('type','')+' hook not added; Cursor runs command hooks only from this installer')
            continue
        if not target:
            notes.append('Cursor: no '+event+' event; that hook is not added')
            continue
        if event=='Stop':
            notes.append('Cursor: its stop hook cannot block a reply; the '+event+' hook reports only')
        translated=cursor_matcher(matcher) if event in ('PreToolUse','PostToolUse','PostToolUseFailure') else ''
        if translated is None:
            notes.append('Cursor: matcher '+matcher+' has no Cursor tool name; that hook is not added')
            continue
        entry={'command':'AIOS_HARNESS=cursor '+substitute(hook['command'],plugin)}
        if translated:
            entry['matcher']=translated
        if hook.get('timeout'):
            entry['timeout']=hook['timeout']
        entries=hooks.setdefault(target,[])
        if not isinstance(entries,list):
            raise ValueError('Cursor hooks.json '+target+' is not a list; merge it manually')
        if not any(isinstance(e,dict) and e.get('command')==entry['command'] and e.get('matcher','')==entry.get('matcher','') for e in entries):
            entries.append(entry)
    return json.dumps(parsed,indent=2)+'\n',notes


def codex_rules(plugin,name):
    """The written rules for Codex, which does not run Claude Code plugin hooks."""
    rules_file=plugin/'hooks/RULES.md'
    if rules_file.is_file():
        lines=[l.rstrip() for l in rules_file.read_text().splitlines() if l.strip()]
    else:
        about=json.loads((plugin/'hooks/hooks.json').read_text()).get('description') if (plugin/'hooks/hooks.json').is_file() else None
        lines=['- What the hooks do: '+about] if about else []
        for event,matcher,hook in pack_hooks(plugin):
            when=CODEX_EVENTS.get(event,'On '+event)
            if event in ('PreToolUse','PostToolUse','PostToolUseFailure'):
                when+=' '+(matcher or 'any tool')+' tool call'
            lines.append('- '+when+', run `'+substitute(hook.get('command',''),plugin)+'` and follow what it reports.')
    if not lines:
        return ''
    return '\n'.join(['<!-- aios-hooks:'+name+' start -->','## '+name+' rules (written down, not enforced)',
                      'In Claude Code these rules run as hooks. Codex does not run them, so nothing checks them here. Follow them yourself.',
                      *lines,'<!-- aios-hooks:'+name+' end -->'])


def agents_block(text,name,block):
    start,end='<!-- aios-hooks:'+name+' start -->','<!-- aios-hooks:'+name+' end -->'
    if text.count(start)>1 or text.count(start)!=text.count(end):
        raise ValueError('AGENTS.md has a broken '+name+' rules block; fix it manually')
    if start in text:
        before,rest=text.split(start,1)
        after=rest.split(end,1)[1]
        return before+block+after
    return (text.rstrip()+'\n\n' if text.strip() else '')+block+'\n'


def snapshot(path):
    if path.is_symlink():
        raise ValueError('Symlinked config preserved; merge its dotfiles source manually: '+str(path))
    return path.read_bytes() if path.exists() else None


def check_current(path,expected):
    if path.is_symlink() or snapshot(path)!=expected:
        raise ValueError('Config changed during install; that file was not overwritten. Retry after the other writer stops: '+str(path))


def write_config(path,text,expected):
    check_current(path,expected)
    if expected is not None and expected==text.encode():
        return False
    suffix=f'.backup-{time.time_ns()}'
    backup=path.with_name(path.name+suffix+('.absent' if expected is None else ''))
    with backup.open('xb') as stream:
        stream.write(expected if expected is not None else b'File did not exist before this install.\n')
    os.chmod(backup,0o600)
    check_current(path,expected)  # Includes edits during the backup itself.
    atomic_write(path,text)
    print('Configured '+os.path.relpath(path,Path.home())+'; backup '+backup.name)
    return True


def legacy_link(dest):
    return dest.is_symlink() and (ROOT/'skills') in dest.resolve().parents


def other_checkout(dest,source):
    """The root of another copy of this repository when dest links to the same file there, else None."""
    if not dest.is_symlink():
        return None
    target=dest.resolve()
    for parent in target.parents:
        market=parent/'.claude-plugin/marketplace.json'
        if market.is_file():
            try:
                same=json.loads(market.read_text()).get('name')==json.loads((ROOT/'.claude-plugin/marketplace.json').read_text()).get('name')
            except (OSError,ValueError):
                return None
            if not same or parent==ROOT or target.relative_to(parent)!=source.resolve().relative_to(ROOT):
                return None
            return parent
    return None


def other_checkout_hint(pack,dest,other):
    return ('Existing link preserved: '+str(dest)+'. It points into another copy of this repository: '+str(other)+
            '. Install from that copy with: aios-guide install '+pack+'. Or move AIOS to this copy: ./install.sh '+pack+' --use-this-checkout')


def available_packs():
    return sorted(p.name for p in (ROOT/'plugins').iterdir() if (p/'.claude-plugin/plugin.json').is_file())


def manifest(pack):
    path=ROOT/'plugins'/pack/'.claude-plugin/plugin.json'
    if not path.is_file():
        raise ValueError('Unknown pack '+pack+'. Available: '+', '.join(available_packs()))
    return json.loads(path.read_text())


def dependencies(data):
    names=[]
    for dep in data.get('dependencies') or []:
        name=dep.get('name') if isinstance(dep,dict) else dep
        names.append(str(name).split('@',1)[0])
    return names


def dependency_order(packs,read=None):
    """Dependencies first, each pack once. A cycle or an unknown pack stops the install before any write."""
    read=read or manifest
    order,state=[],{}
    def visit(pack,trail):
        if state.get(pack)=='done':
            return
        if state.get(pack)=='visiting':
            cycle=trail[trail.index(pack):]+[pack]
            raise ValueError('Dependency cycle: '+' -> '.join(cycle))
        state[pack]='visiting'
        for dep in dependencies(read(pack)):
            visit(dep,trail+[pack])
        state[pack]='done'
        order.append(pack)
    for pack in packs:
        visit(pack,[])
    return order


def mcp_servers(plugin,home):
    """Command-based MCP servers from a pack's .mcp.json, pointed at the linked command in ~/.local/bin."""
    path=plugin/'.mcp.json'
    if not path.is_file():
        return {},[]
    servers,notes={},[]
    for name,server in (json.loads(path.read_text()).get('mcpServers') or {}).items():
        command=str(server.get('command',''))
        if not command:
            notes.append('MCP server '+name+' has no command (URL servers need a manual entry)')
            continue
        if command.startswith('${CLAUDE_PLUGIN_ROOT}/bin/'):
            command=str(home/'.local/bin'/command.rsplit('/',1)[1])
        else:
            command=substitute(command,plugin)
        servers[name]=(command,[substitute(a,plugin) for a in server.get('args',[])])
        if server.get('env'):
            notes.append('MCP server '+name+': set its settings ('+', '.join(sorted(server['env']))+') in your shell for Codex and Cursor')
    return servers,notes


class Plan:
    def __init__(self):
        self.links=[]       # (source, dest)
        self.configs={}     # path -> [original bytes or None, current text]
        self.notes=[]
        self.packs=[]

    def config(self,path):
        if path not in self.configs:
            old=snapshot(path)
            self.configs[path]=[old,old.decode() if old is not None else '']
        return self.configs[path][1]

    def update(self,path,text):
        self.configs[path][1]=text


def plan_pack(pack,plan,home,migrate_v1,planned,use_this_checkout=False):
    plugin=ROOT/'plugins'/pack
    data=manifest(pack)
    for dep in dependencies(data):
        if dep not in planned and not installed(dep,home):
            raise ValueError(pack+' depends on '+dep+'. First run: ./install.sh '+dep)
    skills=sorted(p for p in (plugin/'skills').iterdir() if (p/'SKILL.md').is_file()) if (plugin/'skills').is_dir() else []
    for parent in SKILL_DIRS:
        for source in skills:
            dest=home/parent/source.name
            if dest.exists() or dest.is_symlink():
                if dest.is_symlink() and dest.resolve()==source.resolve():
                    continue
                other=other_checkout(dest,source)
                if other is not None:
                    if not use_this_checkout:
                        raise ValueError(other_checkout_hint(pack,dest,other))
                    plan.links.append((source,dest))
                    continue
                if not (legacy_link(dest) and migrate_v1):
                    hint=' Ask /aios for a guided move; --migrate-v1 preserves the old link in a backup.' if legacy_link(dest) else ''
                    raise ValueError('Existing skill preserved: '+str(dest)+'.'+hint)
            plan.links.append((source,dest))
    tools=sorted(p for p in (plugin/'bin').iterdir() if p.is_file() and os.access(p,os.X_OK)) if (plugin/'bin').is_dir() else []
    for source in tools:
        command=home/'.local/bin'/source.name
        if command.exists() or command.is_symlink():
            if command.is_symlink() and command.resolve()==source.resolve():
                continue
            other=other_checkout(command,source)
            if other is None:
                raise ValueError('Existing '+source.name+' command preserved; move it aside manually')
            if not use_this_checkout:
                raise ValueError(other_checkout_hint(pack,command,other))
        plan.links.append((source,command))
    servers,notes=mcp_servers(plugin,home)
    plan.notes.extend(notes)
    if servers:
        codex=Path(os.environ.get('CODEX_HOME') or home/'.codex').expanduser()/'config.toml'
        text=plan.config(codex)
        for name,(command,args) in servers.items():
            text=codex_config(text,command,name,args)
        plan.update(codex,text)
        cursor=home/'.cursor/mcp.json'
        plan.update(cursor,cursor_mcp(plan.config(cursor),servers))
    if pack_hooks(plugin):
        cursor=home/'.cursor/hooks.json'
        text,notes=cursor_hooks(plan.config(cursor),plugin)
        plan.update(cursor,text)
        plan.notes.extend(notes)
        block=codex_rules(plugin,pack)
        if block:
            agents=Path(os.environ.get('CODEX_HOME') or home/'.codex').expanduser()/'AGENTS.md'
            plan.update(agents,agents_block(plan.config(agents),pack,block))
            plan.notes.append('Codex: '+pack+' hooks are written into '+os.path.relpath(agents,home)+' as rules. Codex does not enforce them.')
    plan.packs.append((pack,data,[s.name for s in skills],[t.name for t in tools],sorted(servers),bool(pack_hooks(plugin))))


def installed(pack,home):
    receipt=home/STATE/'packs'/(pack+'.json')
    return receipt.is_file() and not check(pack,home,quiet=True)


def install(pack,migrate_v1=False,dry_run=False,use_this_checkout=False):
    """Install a pack and its dependencies. Returns the packs in install order."""
    home=Path.home()
    order=dependency_order([pack])
    plan=Plan()
    for name in order:
        plan_pack(name,plan,home,migrate_v1,set(order[:order.index(name)]),use_this_checkout)
    if dry_run:
        for source,dest in plan.links:
            print('Would link '+str(dest.relative_to(home)))
        for path,(old,text) in sorted(plan.configs.items()):
            if old is None or old!=text.encode():
                print('Would configure '+os.path.relpath(path,home))
        for note in plan.notes:
            print('Note: '+note)
        return order
    with ExitStack() as stack:
        paths=sorted(plan.configs,key=str)
        for path in paths:
            path.parent.mkdir(parents=True,exist_ok=True)
            lock=stack.enter_context(path.with_name(path.name+'.aios-install.lock').open('a'))
            fcntl.flock(lock,fcntl.LOCK_EX)
        for path in paths:
            check_current(path,plan.configs[path][0])
        for path in paths:
            old,text=plan.configs[path]
            write_config(path,text,old)
    for source,dest in plan.links:
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.is_symlink():
            # Only a reviewed v1 migration or --use-this-checkout reaches here. Preserve, never unlink.
            kind='v1' if legacy_link(dest) else 'checkout'
            backup=home/STATE/(kind+'-backups')/dest.parent.parent.name/(dest.name+'-'+str(time.time_ns()))
            backup.parent.mkdir(parents=True,exist_ok=True)
            dest.rename(backup)
            print('Preserved '+('v1' if kind=='v1' else 'the other copy\'s')+' link at '+str(backup.relative_to(home)))
        dest.symlink_to(source)
        print('Linked '+str(dest.relative_to(home)))
    for name,data,skills,tools,servers,hooks in plan.packs:
        receipt=home/STATE/'packs'/(name+'.json')
        body=json.dumps({'name':name,'version':data['version'],'root':str(ROOT/'plugins'/name),'harnesses':['codex','cursor','agents'],
                         'skills':skills,'bin':tools,'mcp_servers':servers,'hooks':hooks,'dependencies':dependencies(data)},indent=2)+'\n'
        if not receipt.is_file() or receipt.read_text()!=body:
            atomic_write(receipt,body)
    record_checkout(home)
    for note in dict.fromkeys(plan.notes):
        print('Note: '+note)
    names=', '.join(p[0]+' '+p[1]['version'] for p in plan.packs)
    print('Installed '+names+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for pack commands.')
    return order


def record_checkout(home):
    path=home/STATE/'checkout.json'
    current=json.loads(path.read_text()).get('root') if path.is_file() else None
    if current!=str(ROOT):
        atomic_write(path,json.dumps({'root':str(ROOT),'install':str(ROOT/'install.sh')},indent=2)+'\n')
        print('Recorded this checkout for /aios: '+str(ROOT))


def check(pack,home=None,quiet=False):
    """The installer's own proof for Codex and Cursor. Returns a list of problems; empty means installed."""
    home=Path(home or Path.home())
    plugin=ROOT/'plugins'/pack
    problems=[]
    receipt=home/STATE/'packs'/(pack+'.json')
    data=manifest(pack)
    if not receipt.is_file():
        problems.append('no install receipt for '+pack)
    elif json.loads(receipt.read_text()).get('version')!=data['version']:
        problems.append('receipt version differs from '+data['version']+'; run ./install.sh '+pack)
    for parent in SKILL_DIRS:
        for source in sorted((plugin/'skills').iterdir()) if (plugin/'skills').is_dir() else []:
            dest=home/parent/source.name
            if not ((dest/'SKILL.md').is_file() and dest.resolve()==source.resolve()):
                problems.append('skill '+source.name+' not linked in ~/'+parent)
    for source in sorted((plugin/'bin').iterdir()) if (plugin/'bin').is_dir() else []:
        command=home/'.local/bin'/source.name
        if os.access(source,os.X_OK) and not (command.is_symlink() and command.resolve()==source.resolve()):
            problems.append('command '+source.name+' not linked in ~/.local/bin')
    servers,_=mcp_servers(plugin,home)
    if servers:
        codex=Path(os.environ.get('CODEX_HOME') or home/'.codex').expanduser()/'config.toml'
        cursor=home/'.cursor/mcp.json'
        for name in servers:
            if not codex.is_file() or '[mcp_servers.'+name+']' not in codex.read_text():
                problems.append('MCP server '+name+' missing from Codex config.toml')
            try:
                present=name in json.loads(cursor.read_text()).get('mcpServers',{})
            except (ValueError,OSError):
                present=False
            if not present:
                problems.append('MCP server '+name+' missing from ~/.cursor/mcp.json')
    if pack_hooks(plugin):
        try:
            want,_=cursor_hooks('',plugin)
            have=json.loads((home/'.cursor/hooks.json').read_text()).get('hooks',{})
            for event,entries in json.loads(want)['hooks'].items():
                for entry in entries:
                    if entry not in have.get(event,[]):
                        problems.append('Cursor hook for '+event+' missing from ~/.cursor/hooks.json')
        except (ValueError,OSError):
            problems.append('Cursor hooks.json unreadable')
        agents=Path(os.environ.get('CODEX_HOME') or home/'.codex').expanduser()/'AGENTS.md'
        if codex_rules(plugin,pack) and (not agents.is_file() or codex_rules(plugin,pack) not in agents.read_text()):
            problems.append('Codex written rules for '+pack+' missing from AGENTS.md')
    if not quiet:
        for problem in problems:
            print('FAIL '+problem)
        print(('OK ' if not problems else 'NOT INSTALLED ')+pack+' '+data['version'])
    return problems


def main(argv=None):
    parser=argparse.ArgumentParser(description='Install an AIOS 2.0 pack and its dependencies for Codex and Cursor. Claude Code configuration is never changed.')
    parser.add_argument('pack',nargs='?',help='pack name, for example aios-brain or aios-complete')
    parser.add_argument('--migrate-v1',action='store_true',help='After reviewing the guided move, preserve old v1 links in backups and link this pack')
    parser.add_argument('--use-this-checkout',action='store_true',help='Move links that point into another copy of this repository to this copy (the old links are kept in a backup)')
    parser.add_argument('--dry-run',action='store_true',help='Show what would change and write nothing')
    parser.add_argument('--check',action='store_true',help='Prove the pack is installed for Codex and Cursor')
    parser.add_argument('--list',action='store_true',help='List the packs in this checkout')
    parser.add_argument('--where',action='store_true',help='Print this checkout path')
    args=parser.parse_args(argv)
    try:
        if args.where:
            print(ROOT)
            return 0
        if args.list or not args.pack:
            for name in available_packs():
                print(name+' '+manifest(name)['version'])
            return 0
        if args.check:
            return 1 if check(args.pack) else 0
        install(args.pack,args.migrate_v1,args.dry_run,args.use_this_checkout)
    except (ValueError,OSError) as exc:
        print('Install stopped: '+str(exc),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
