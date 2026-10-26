#!/usr/bin/env python3
"""Install one pack, preserving v1 links, dotfiles symlinks and concurrent edits."""
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


def codex_config(text,executable):
    original=text
    normal=text.replace('\r\n','\n')
    if normal.startswith('\ufeff'):
        raise ValueError('TOML byte-order mark found; remove it manually before installing')
    for quoted in re.finditer(r'(?s)("""|\'\'\').*?\1',normal):
        if 'aios-brain' in quoted[0]:
            raise ValueError('aios-brain in a multiline TOML string; merge the MCP entry manually')
    block='[mcp_servers.aios-brain]\ncommand = '+json.dumps(str(executable))+'\nargs = ["mcp"]\n'
    if 'aios-brain' in normal:
        # Also covers dotted keys, array tables, inline objects and comments on 3.9.
        # Only our exact ordinary stanza is safe to recognise without a TOML parser.
        if normal.count(block.strip())!=1:
            raise ValueError('Existing custom aios-brain TOML preserved; merge it manually')
        remainder=normal.replace(block.strip(),'',1)
        if 'aios-brain' in remainder:
            raise ValueError('Other aios-brain TOML representation preserved; merge it manually')
        after=normal.split(block.strip(),1)[1]
        tail=after.lstrip('\n')
        if tail and not tail.startswith('[') and not tail.startswith('#'):
            raise ValueError('Custom aios-brain table fields preserved; merge them manually')
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
        if parsed.get('mcp_servers',{}).get('aios-brain')!={'command':str(executable),'args':['mcp']}:
            raise ValueError('MCP representation differs; merge it manually')
    return result


def snapshot(path):
    if path.is_symlink():
        raise ValueError('Symlinked config preserved; merge its dotfiles source manually: '+str(path))
    return path.read_bytes() if path.exists() else None


def check_current(path,expected):
    if path.is_symlink() or snapshot(path)!=expected:
        raise ValueError('Config changed during install; that file was not overwritten. Retry after the other writer stops: '+str(path))


def write_config(path,text,expected):
    check_current(path,expected)
    suffix=f'.backup-{time.time_ns()}'
    backup=path.with_name(path.name+suffix+('.absent' if expected is None else ''))
    with backup.open('xb') as stream:
        stream.write(expected if expected is not None else b'File did not exist before this install.\n')
    os.chmod(backup,0o600)
    check_current(path,expected)  # Includes edits during the backup itself.
    atomic_write(path,text)
    print('Configured '+os.path.relpath(path,Path.home())+'; backup '+backup.name)


def legacy_link(dest):
    return dest.is_symlink() and (ROOT/'skills') in dest.resolve().parents


def install(pack,migrate_v1=False):
    home=Path.home()
    plugin=ROOT/'plugins'/pack
    if not plugin.is_dir():
        raise ValueError('Unknown pack. Available: aios, aios-brain')
    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
        raise ValueError('aios-brain depends on aios 2.0. First review /aios, then run: ./install.sh aios')
    manifest=json.loads((plugin/'.claude-plugin/plugin.json').read_text())
    links=[]
    for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
        for source in sorted((plugin/'skills').iterdir()):
            dest=home/parent/source.name
            if dest.exists() or dest.is_symlink():
                if dest.is_symlink() and dest.resolve()==source.resolve():
                    continue
                if not (legacy_link(dest) and migrate_v1):
                    hint=' Ask /aios for a guided move; --migrate-v1 preserves the old link in a backup.' if legacy_link(dest) else ''
                    raise ValueError('Existing skill preserved: '+str(dest)+'.'+hint)
            links.append((source,dest))
    plans=[]
    if pack=='aios-brain':
        command=home/'.local/bin/brain'
        if command.exists() or command.is_symlink():
            if not command.is_symlink() or command.resolve()!=(plugin/'bin/brain').resolve():
                raise ValueError('Existing brain command preserved; move it aside manually')
        else:
            links.append((plugin/'bin/brain',command))
        codex=Path(os.environ.get('CODEX_HOME') or home/'.codex').expanduser()/'config.toml'
        old=snapshot(codex)
        plans.append((codex,codex_config(old.decode() if old is not None else '',command),old))
        cursor=home/'.cursor/mcp.json'
        old=snapshot(cursor)
        parsed=json.loads(old) if old is not None else {}
        if not isinstance(parsed,dict) or not isinstance(parsed.get('mcpServers',{}),dict):
            raise ValueError('Cursor MCP configuration must contain an object of servers')
        servers=parsed.setdefault('mcpServers',{})
        existing=servers.get('aios-brain',{})
        if not isinstance(existing,dict) or existing.get('command',str(command))!=str(command):
            raise ValueError('Existing custom Cursor brain server preserved; merge it manually')
        servers['aios-brain']=dict(existing,command=str(command),args=['mcp'])
        plans.append((cursor,json.dumps(parsed,indent=2)+'\n',old))
    with ExitStack() as stack:
        for path,_,_ in sorted(plans,key=lambda p:str(p[0])):
            path.parent.mkdir(parents=True,exist_ok=True)
            lock=stack.enter_context(path.with_name(path.name+'.aios-install.lock').open('a'))
            fcntl.flock(lock,fcntl.LOCK_EX)
        for path,_,expected in plans:
            check_current(path,expected)
        for path,text,expected in plans:
            write_config(path,text,expected)
    for source,dest in links:
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.is_symlink():
            # Only a reviewed v1 migration reaches here. Preserve, never unlink.
            backup=home/'.local/share/aios/v1-backups'/dest.parent.parent.name/(dest.name+'-'+str(time.time_ns()))
            backup.parent.mkdir(parents=True,exist_ok=True)
            dest.rename(backup)
            print('Preserved v1 link at '+str(backup.relative_to(home)))
        dest.symlink_to(source)
        print('Linked '+str(dest.relative_to(home)))
    receipt=home/'.local/share/aios/packs'/f'{pack}.json'
    atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')


def main():
    parser=argparse.ArgumentParser(description='Install one AIOS 2.0 pack; preserve existing configuration and v1 skills.')
    parser.add_argument('pack',choices=['aios','aios-brain'])
    parser.add_argument('--migrate-v1',action='store_true',help='After reviewing the guided move, preserve old v1 links in backups and link this pack')
    args=parser.parse_args()
    try:
        install(args.pack,args.migrate_v1)
    except (ValueError,OSError) as exc:
        print('Install stopped: '+str(exc),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
