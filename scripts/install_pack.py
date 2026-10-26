#!/usr/bin/env python3
"""Install exactly one pack for Codex and Cursor, preserving user configuration."""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def atomic_write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name = tempfile.mkstemp(prefix='.'+path.name+'-',dir=str(path.parent))
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write(text)
        os.chmod(name,0o600)
        os.replace(name,path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def codex_config(text,executable):
    # Keep every unrelated byte. Refuse unusual overlapping representations
    # rather than risk editing a table we cannot identify unambiguously.
    section = re.compile(r'^[ \t]*\[([^\]\n]+)\][ \t]*(?:#.*)?$',re.M)
    matches = list(section.finditer(text))
    target = None
    for index,match in enumerate(matches):
        name = re.sub(r'[\s\"\']','',match.group(1))
        if name == 'mcp_servers.aios-brain':
            target = (match.start(),matches[index+1].start() if index+1<len(matches) else len(text))
        elif name.startswith('mcp_servers.aios-brain.'):
            raise ValueError('Existing nested aios-brain MCP configuration; merge it manually')
    if re.search(r'^\s*(?:[\"\']?mcp_servers[\"\']?)\s*=',text,re.M):
        raise ValueError('Inline mcp_servers table found; use a normal TOML table before installing')
    if re.search(r'^\s*[\"\']?aios-brain[\"\']?\s*=',text,re.M):
        raise ValueError('Inline aios-brain table found; merge it manually')
    block = '[mcp_servers.aios-brain]\ncommand = '+json.dumps(str(executable))+'\nargs = ["mcp"]\n'
    if target:
        # Match our exact managed stanza before returning the original file unchanged.
        # Any custom env, comments or nested/array tables require an explicit manual merge.
        tail = text[target[0]:]
        next_header = re.search(r'(?m)^[ \t]*\[',tail[tail.find('\n')+1:])
        end = tail.find('\n')+1+next_header.start() if next_header else len(tail)
        if tail[:end].strip() != block.strip():
            raise ValueError('Existing custom aios-brain MCP table preserved; merge it manually')
        return text
    result = text.rstrip()+'\n\n'+block
    try:
        import tomllib
    except ImportError:
        # Python 3.9/3.10: the edit is deliberately limited to an ordinary table.
        pass
    else:
        tomllib.loads(text)
        tomllib.loads(result)
    return result


def install(pack):
    home = Path.home()
    plugin = ROOT/'plugins'/pack
    if not plugin.is_dir():
        raise ValueError('Unknown pack. Available: aios, aios-brain')
    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
        raise ValueError('aios-brain depends on aios. First run: ./install.sh aios')
    manifest = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
    links = []
    for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
        for source in sorted((plugin/'skills').iterdir()):
            dest = home/parent/source.name
            if dest.exists() or dest.is_symlink():
                if not dest.is_symlink() or ROOT not in dest.resolve().parents:
                    raise ValueError('Existing skill preserved: '+str(dest)+'. Move it aside yourself before opting into 2.0.')
            links.append((source,dest))
    configs = []
    if pack=='aios-brain':
        command = home/'.local/bin/brain'
        if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
            raise ValueError('Existing brain executable preserved; move it aside before opting into this pack')
        links.append((plugin/'bin/brain',command))
        codex = home/'.codex/config.toml'
        old = codex.read_text() if codex.exists() else ''
        configs.append((codex,codex_config(old,command)))
        cursor = home/'.cursor/mcp.json'
        parsed = json.loads(cursor.read_text()) if cursor.exists() else {}
        if not isinstance(parsed,dict) or not isinstance(parsed.get('mcpServers',{}),dict):
            raise ValueError('Cursor MCP configuration must contain an object of servers')
        servers = parsed.setdefault('mcpServers',{})
        existing = servers.get('aios-brain',{})
        if not isinstance(existing,dict) or existing.get('command',str(command))!=str(command):
            raise ValueError('Existing custom Cursor aios-brain server preserved; merge it manually')
        servers['aios-brain'] = dict(existing,command=str(command),args=['mcp'])
        configs.append((cursor,json.dumps(parsed,indent=2)+'\n'))
    # All conflicts and both config files have been checked before the first write.
    for path,content in configs:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():
            backup = path.with_name(path.name+f'.backup-{time.time_ns()}')
            shutil.copy2(path,backup)
            os.chmod(backup,0o600)
            print('Backed up '+str(path.relative_to(home))+' -> '+backup.name)
        else:
            # Keep an explicit record of the absent pre-install file too.
            backup = path.with_name(path.name+f'.backup-{time.time_ns()}.absent')
            atomic_write(backup,'File did not exist before this install.\n')
        atomic_write(path,content)
        print('Configured '+str(path.relative_to(home)))
    for source,dest in links:
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.is_symlink():
            dest.unlink()
        dest.symlink_to(source)
        print('Linked '+str(dest.relative_to(home)))
    receipt = home/'.local/share/aios/packs'/f'{pack}.json'
    atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')


def main():
    parser = argparse.ArgumentParser(description='Install one AIOS 2.0 pack for Codex and Cursor. No Claude config is changed.')
    parser.add_argument('pack',choices=['aios','aios-brain'])
    args = parser.parse_args()
    try:
        install(args.pack)
    except (ValueError,OSError) as exc:
        print('Install stopped: '+str(exc),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
