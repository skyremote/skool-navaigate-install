#!/usr/bin/env python3
"""Keep the marketplace, the aios catalogue and the aios-complete bundle in step.

Run after merging a stream:   python3 scripts/build_catalogue.py --merge-entries
Check in CI (writes nothing): python3 scripts/build_catalogue.py --check

1. --merge-entries copies every plugins/<pack>/MARKETPLACE_ENTRY.json into marketplace.json.
2. Each marketplace entry gets metadata.module (1 to 12).
3. aios-complete depends on aios, aios-brain and every core pack (modules 2 to 11) in the marketplace.
4. plugins/aios/catalogue.json is generated from marketplace.json and each pack's plugin.json.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKETPLACE='navaigate-aios'
LEGACY='skool-navaigate-install'
BUNDLE='aios-complete'
SKOOL='https://www.skool.com/navaigate/classroom'
MODULES=['Start here','Your folders and your rules','The harnesses','bb as the cockpit','Memory you own',
         'Skills that earn their place','Agents without sprawl','Make it verifiable','Working methods',
         'Models, effort and cost','Ship it to others','The shelf']
KNOWN={'aios':1,'aios-rules':2,'aios-harnesses':3,'aios-bb':4,'aios-brain':5,'aios-skills':6,'aios-agents':7,
       'aios-verify':8,'aios-methods':9,'aios-models':10,'aios-ship':11}
# Words a member might use for a capability, mapped to the pack that provides it.
CAPABILITIES={'aios-rules':['rules','agents.md','folders','claude.md'],'aios-harnesses':['harness','codex','cursor','grok','mcp list'],
              'aios-bb':['bb','board','kanban','cockpit','threads'],'aios-brain':['brain','memory','remember','search my chats','sync','turso'],
              'aios-skills':['skill','skills','evals'],'aios-agents':['agent','agents','sub-agent','crew','delegate'],
              'aios-verify':['verify','tests','review','hooks'],'aios-methods':['loop','worktree','interview','methods','grill'],
              'aios-models':['model','models','effort','cost','usage'],'aios-ship':['ship','package','publish','plugin'],
              'shelf-video':['video','captions','filler'],'shelf-decks':['deck','slides','powerpoint','presentation'],
              'shelf-invoices':['invoice','invoices','billing'],
              'aios-complete':['everything','whole framework','the whole aios','complete','all packs','all of it']}


class CatalogueError(ValueError):
    pass


def load(path):
    return json.loads(path.read_text())


def dump(data):
    return json.dumps(data,indent=2,ensure_ascii=False)+'\n'


def module_of(entry,manifest):
    for source in (entry.get('metadata') or {},manifest.get('metadata') or {}):
        if isinstance(source.get('module'),int):
            return source['module']
    name=entry['name']
    if name in KNOWN:
        return KNOWN[name]
    found=re.search(r'\bModule (\d{1,2})\b',entry.get('description','')+' '+manifest.get('description',''))
    if found:
        return int(found.group(1))
    if name.startswith('shelf-') or entry.get('description','').lower().startswith('the shelf'):
        return 12
    raise CatalogueError('No module number for '+name+': add "metadata": {"module": N} to its MARKETPLACE_ENTRY.json')


def entry_order(entry):
    name=entry['name']
    if name==LEGACY:
        return (0,0,name)
    if name==BUNDLE:
        return (2,0,name)
    return (1,(entry.get('metadata') or {}).get('module',99),name)


def build(root=ROOT,merge_entries=False):
    """Return {path: text} for every generated file. Raises CatalogueError on any disagreement."""
    market_path=root/'.claude-plugin/marketplace.json'
    market=load(market_path)
    entries={e['name']:e for e in market['plugins']}
    staged=sorted(p for p in (root/'plugins').glob('*/MARKETPLACE_ENTRY.json'))
    for path in staged:
        entry=load(path)
        if entry.get('source')!='./plugins/'+path.parent.name:
            raise CatalogueError(str(path.relative_to(root))+' source must be ./plugins/'+path.parent.name)
        if entry['name'] not in entries:
            if not merge_entries:
                raise CatalogueError(entry['name']+' has a MARKETPLACE_ENTRY.json but no marketplace entry: run build_catalogue.py --merge-entries')
            entries[entry['name']]=entry
        elif merge_entries:
            merged=dict(entries[entry['name']]);merged.update(entry)
            entries[entry['name']]=merged
        elif any(entries[entry['name']].get(k)!=v for k,v in entry.items() if k!='metadata'):
            raise CatalogueError(entry['name']+': marketplace entry differs from its MARKETPLACE_ENTRY.json: run build_catalogue.py --merge-entries')
    manifests={}
    for name,entry in entries.items():
        source=root/entry['source']
        path=source/'.claude-plugin/plugin.json'
        if not path.is_file():
            raise CatalogueError(name+': no plugin.json at '+entry['source'])
        manifest=load(path)
        manifests[name]=(source,manifest)
        if manifest.get('name')!=name:
            raise CatalogueError(name+': plugin.json says its name is '+str(manifest.get('name')))
        if entry.get('version')!=manifest.get('version'):
            raise CatalogueError(name+': marketplace version '+str(entry.get('version'))+' differs from plugin.json '+str(manifest.get('version')))
        if name not in (LEGACY,BUNDLE):
            meta=dict(entry.get('metadata') or {});meta['module']=module_of(entry,manifest)
            entry['metadata']=meta
    for folder in sorted((root/'plugins').iterdir()):
        if (folder/'.claude-plugin/plugin.json').is_file() and not any(Path(root/e['source']).resolve()==folder.resolve() for e in entries.values()):
            raise CatalogueError('plugins/'+folder.name+' is not in marketplace.json')
    # The bundle: every pack on the core path, modules 1 to 11. The shelf stays optional.
    core=sorted((n for n,e in entries.items() if n not in (LEGACY,BUNDLE) and (e.get('metadata') or {}).get('module',99)<=11),
                key=lambda n:(entries[n]['metadata']['module'],n))
    out={}
    if BUNDLE in entries:
        bundle_path=manifests[BUNDLE][0]/'.claude-plugin/plugin.json'
        bundle=manifests[BUNDLE][1]
        if bundle.get('dependencies')!=core:
            bundle=dict(bundle,dependencies=core)
            manifests[BUNDLE]=(manifests[BUNDLE][0],bundle)
        out[bundle_path]=dump(bundle)
    market=dict(market,plugins=sorted(entries.values(),key=entry_order))
    out[market_path]=dump(market)
    packs=[]
    for entry in market['plugins']:
        name=entry['name']
        source,manifest=manifests[name]
        packs.append(describe(name,entry,source,manifest,root))
    catalogue={'about':'Generated by scripts/build_catalogue.py from .claude-plugin/marketplace.json and each plugin.json. Do not edit.',
               'marketplace':market['name'],'version':market.get('metadata',{}).get('version'),
               'install':{'claude_code':'claude plugin install <pack>@'+market['name'],'codex_cursor':'./install.sh <pack>'},
               'modules':[{'number':i+1,'title':t,'lesson':SKOOL,
                           'packs':[p['name'] for p in packs if p['module']==i+1]} for i,t in enumerate(MODULES)],
               'packs':packs}
    out[root/'plugins/aios/catalogue.json']=dump(catalogue)
    return out


def describe(name,entry,source,manifest,root):
    def names(folder,suffix=None):
        path=source/folder
        if not path.is_dir():
            return []
        if suffix:
            return sorted(p.stem for p in path.iterdir() if p.suffix==suffix)
        return sorted(p.name for p in path.iterdir() if (p/'SKILL.md').is_file())
    hooks_file=source/'hooks/hooks.json'
    hooks=sorted((load(hooks_file).get('hooks') or {}).keys()) if hooks_file.is_file() and name!=LEGACY else []
    mcp_file=source/'.mcp.json'
    mcp=sorted((load(mcp_file).get('mcpServers') or {}).keys()) if mcp_file.is_file() and name!=LEGACY else []
    config=manifest.get('userConfig') or {}
    kind='legacy' if name==LEGACY else 'bundle' if name==BUNDLE else 'start' if name=='aios' else \
         'shelf' if entry['metadata']['module']==12 else 'core'
    tools=sorted(p.name for p in (source/'bin').iterdir() if p.is_file()) if (source/'bin').is_dir() and name!=LEGACY else []
    return {'name':name,'kind':kind,'module':(entry.get('metadata') or {}).get('module'),
            'version':manifest['version'],'description':entry.get('description',manifest.get('description','')),
            'source':entry['source'],'dependencies':[d if isinstance(d,str) else d.get('name') for d in manifest.get('dependencies',[])],
            'skills':names('skills') if name!=LEGACY else [],'agents':names('agents','.md'),'commands':names('commands','.md'),
            'bin':tools,'hooks':hooks,'mcp_servers':mcp,
            'user_config':[{'key':k,'sensitive':bool(v.get('sensitive')),'required':bool(v.get('required'))} for k,v in sorted(config.items())],
            'tour':(source/'TOUR.md').is_file() and name!=LEGACY,
            'capabilities':CAPABILITIES.get(name,[])}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--merge-entries',action='store_true',help='copy every MARKETPLACE_ENTRY.json into marketplace.json')
    parser.add_argument('--check',action='store_true',help='write nothing; exit 1 if any generated file is out of date')
    args=parser.parse_args(argv)
    try:
        out=build(merge_entries=args.merge_entries)
    except CatalogueError as exc:
        print('Catalogue error: '+str(exc),file=sys.stderr)
        return 1
    stale=[p for p,t in out.items() if not p.is_file() or p.read_text()!=t]
    if args.check:
        for path in stale:
            print('Out of date: '+str(path.relative_to(ROOT)),file=sys.stderr)
        return 1 if stale else 0
    for path in stale:
        path.write_text(out[path])
        print('Wrote '+str(path.relative_to(ROOT)))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
