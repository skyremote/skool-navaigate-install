#!/usr/bin/env python3
"""Read-only pack inventory. Installed, enabled and running are different facts."""
import json
import shutil
from pathlib import Path

PACKS = ['aios','aios-rules','aios-harnesses','aios-bb','aios-brain','aios-skills-kit',
         'aios-agents','aios-verify','aios-methods','aios-models','aios-ship-it',
         'aios-video','aios-decks','aios-invoices','aios-voice','aios-design','aios-research','aios-content']
MODULES = ['Start here','Your folders and your rules','The harnesses','bb as the cockpit',
           'Memory you own','Skills that earn their place','Agents without sprawl','Make it verifiable',
           'Working methods','Models, effort and cost','Ship it to others','The shelf']


def inventory(home=None,cwd=None):
    home,cwd = Path(home or Path.home()),Path(cwd or Path.cwd())
    errors = []
    def load(path,default):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text())
        except (ValueError,OSError):
            errors.append('Cannot read '+str(path.relative_to(home)))
            return default
    registry = load(home/'.claude/plugins/installed_plugins.json',{}).get('plugins',{})
    enabled = load(home/'.claude/settings.json',{}).get('enabledPlugins',{})
    # Project and local settings can change effective enablement.
    for path in (cwd/'.claude/settings.json',cwd/'.claude/settings.local.json'):
        if path.exists():
            try:
                enabled.update(json.loads(path.read_text()).get('enabledPlugins',{}))
            except (ValueError,OSError):
                errors.append('Cannot read project plugin settings')
    result = []
    for pack in PACKS:
        entries = registry.get(pack+'@navaigate-aios',[])
        if isinstance(entries,dict):
            entries = [entries]
        paths = [Path(e['installPath']) for e in entries if e.get('installPath')]
        available = [p for p in paths if p.is_dir()]
        # Local-path marketplace plugins can load in place.
        markets = load(home/'.claude/plugins/known_marketplaces.json',{})
        if entries and not available:
            directory = markets.get('navaigate-aios',{}).get('installLocation')
            if directory and (Path(directory)/'plugins'/pack).is_dir():
                available = [Path(directory)/'plugins'/pack]
        skill = 'brain' if pack=='aios-brain' else 'aios' if pack=='aios' else None
        harnesses = {'claude':{'installed':bool(entries),'files_present':bool(available),
                             'enabled':enabled.get(pack+'@navaigate-aios','unknown')}}
        for harness in ('codex','cursor','agents'):
            root = home/('.'+harness)/'skills'
            receipt = load(home/'.local/share/aios/packs'/f'{pack}.json',{})
            expected = Path(receipt.get('root',''))/'skills'
            names = [p.name for p in expected.iterdir() if (p/'SKILL.md').is_file()] if receipt and expected.is_dir() else ([skill] if skill else [])
            found = bool(names) and all((root/n/'SKILL.md').is_file() and (not receipt or (root/n).resolve()==(expected/n).resolve()) for n in names)
            harnesses[harness] = {'skills_present':found,'receipt_version':receipt.get('version') if found else None}
        if any(v.get('installed') or v.get('skills_present') for v in harnesses.values()):
            result.append({'pack':pack,'harnesses':harnesses})
    progress = load(home/'.local/share/aios/progress.json',{}).get('completed_modules',[])
    completed = {n for n in progress if type(n) is int and 1<=n<=12}
    next_module = next((n for n in range(1,13) if n not in completed),None)
    return {'packs':result,'harness_commands':{h:bool(shutil.which(h)) for h in ('claude','codex','cursor')},
            'rules_present':(cwd/'AGENTS.md').is_file(),'next_module':next_module,
            'next_title':MODULES[next_module-1] if next_module else 'Choose one shelf tool',
            'progress_basis':'Only member-confirmed modules in ~/.local/share/aios/progress.json count. Installed does not mean completed.',
            'available_packs':['aios','aios-brain'],'errors':errors}


if __name__=='__main__':
    print(json.dumps(inventory(),indent=2))
