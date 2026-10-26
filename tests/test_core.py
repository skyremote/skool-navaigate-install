"""AIOS 2.0 core: catalogue, dependency order, cycles, idempotent installs, hook merges, the guide and release tags."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout,redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'plugins/aios/scripts')]
import build_catalogue  # noqa: E402
import install_pack as installer  # noqa: E402


def quiet(fn,*args,**kw):
    with redirect_stdout(io.StringIO()) as out,redirect_stderr(io.StringIO()):
        result=fn(*args,**kw)
    return result,out.getvalue()


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')


def make_pack(root,name,deps=(),skills=(),bin_tools=(),hooks=None,rules=None,mcp=None,entry=True,module=None):
    folder=root/'plugins'/name
    data={'name':name,'version':'2.0.0','description':'Fictional '+name+' pack.','author':{'name':'skyremote'}}
    if deps:
        data['dependencies']=list(deps)
    write_json(folder/'.claude-plugin/plugin.json',data)
    for skill in skills:
        (folder/'skills'/skill).mkdir(parents=True)
        (folder/'skills'/skill/'SKILL.md').write_text('---\nname: '+skill+'\ndescription: Fictional.\n---\nBody.\n')
    for tool in bin_tools:
        path=folder/'bin'/tool
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('#!/bin/sh\necho '+tool+'\n')
        path.chmod(0o755)
    if hooks is not None:
        write_json(folder/'hooks/hooks.json',{'hooks':hooks})
    if rules:
        (folder/'hooks/RULES.md').write_text(rules)
    if mcp:
        write_json(folder/'.mcp.json',{'mcpServers':mcp})
    if entry:
        item={'name':name,'source':'./plugins/'+name,'version':'2.0.0','description':'Fictional '+name+' pack.'}
        if module:
            item['metadata']={'module':module}
        write_json(folder/'MARKETPLACE_ENTRY.json',item)
    return folder


class Fixture(unittest.TestCase):
    """A fictional repository and a fictional member home, both under /tmp."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='aios-core-',dir='/tmp')
        base=Path(self.tmp.name)
        self.root=base/'repo'
        self.home=base/'home'
        self.home.mkdir()
        (self.root/'skills').mkdir(parents=True)
        write_json(self.root/'.claude-plugin/marketplace.json',{'name':'navaigate-aios','owner':{'name':'Acme'},
                   'metadata':{'version':'2.0.0'},'plugins':[]})
        self.env=patch.dict(os.environ,{'HOME':str(self.home),'CODEX_HOME':'','CLAUDE_CONFIG_DIR':''})
        self.env.start()
        self.root_patch=patch.object(installer,'ROOT',self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.env.stop()
        self.tmp.cleanup()


class DependencyOrder(unittest.TestCase):
    def order(self,graph,packs):
        return installer.dependency_order(packs,read=lambda p:{'dependencies':graph[p]})

    def test_dependencies_come_first_and_each_pack_once(self):
        graph={'aios':[],'brain':['aios'],'rules':['aios'],'complete':['aios','brain','rules']}
        self.assertEqual(self.order(graph,['complete']),['aios','brain','rules','complete'])

    def test_diamond_installs_shared_dependency_once(self):
        graph={'aios':[],'a':['aios'],'b':['aios'],'top':['a','b']}
        order=self.order(graph,['top'])
        self.assertEqual(order.count('aios'),1)
        self.assertLess(order.index('aios'),order.index('a'))

    def test_cycle_is_named_and_stops(self):
        graph={'aios':[],'a':['b'],'b':['c'],'c':['a']}
        with self.assertRaisesRegex(ValueError,'Dependency cycle: a -> b -> c -> a'):
            self.order(graph,['a'])

    def test_self_cycle(self):
        with self.assertRaisesRegex(ValueError,'cycle: a -> a'):
            self.order({'a':['a']},['a'])

    def test_object_and_marketplace_qualified_dependencies(self):
        self.assertEqual(installer.dependencies({'dependencies':[{'name':'aios','version':'^2.0'},'aios-brain@navaigate-aios']}),
                         ['aios','aios-brain'])

    def test_real_repository_order(self):
        order=installer.dependency_order(['aios-complete'])
        self.assertEqual(order[0],'aios')
        self.assertEqual(order[-1],'aios-complete')
        self.assertEqual(len(order),len(set(order)))


class Catalogue(unittest.TestCase):
    def test_committed_files_match_the_generator(self):
        out=build_catalogue.build()
        for path,text in out.items():
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertEqual(path.read_text(),text,'Run: python3 scripts/build_catalogue.py')

    def test_catalogue_lists_every_marketplace_plugin(self):
        market=json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        catalogue=json.loads((ROOT/'plugins/aios/catalogue.json').read_text())
        self.assertEqual([p['name'] for p in market['plugins']],[p['name'] for p in catalogue['packs']])
        for entry,pack in zip(market['plugins'],catalogue['packs']):
            self.assertEqual(entry['version'],pack['version'])

    def test_aios_has_no_dependencies_and_every_other_pack_needs_it(self):
        catalogue=json.loads((ROOT/'plugins/aios/catalogue.json').read_text())
        for pack in catalogue['packs']:
            if pack['name']=='aios':
                self.assertEqual(pack['dependencies'],[])
            elif pack['kind']!='legacy':
                self.assertIn('aios',installer.dependency_order([pack['name']]))

    def test_bundle_holds_every_core_pack_and_no_shelf_pack(self):
        catalogue=json.loads((ROOT/'plugins/aios/catalogue.json').read_text())
        bundle=next(p for p in catalogue['packs'] if p['name']=='aios-complete')
        core=[p['name'] for p in catalogue['packs'] if p['kind'] in ('start','core')]
        self.assertEqual(sorted(bundle['dependencies']),sorted(core))
        self.assertIn('aios-brain',bundle['dependencies'])
        self.assertFalse([p for p in catalogue['packs'] if p['kind']=='shelf' and p['name'] in bundle['dependencies']])


class CatalogueFixture(Fixture):
    def market(self):
        return json.loads((self.root/'.claude-plugin/marketplace.json').read_text())

    def setup_packs(self):
        make_pack(self.root,'aios',skills=['aios'])
        make_pack(self.root,'aios-brain',deps=['aios'],skills=['brain'],mcp={'aios-brain':{'command':'${CLAUDE_PLUGIN_ROOT}/bin/brain','args':['mcp']}})
        make_pack(self.root,'aios-rules',deps=['aios'],skills=['rules'],
                  hooks={'PreToolUse':[{'matcher':'Bash','hooks':[{'type':'command','command':'echo'}]}]})
        make_pack(self.root,'shelf-video',deps=['aios'],skills=['shelf-video'])
        make_pack(self.root,'aios-complete',deps=['aios'],entry=False)
        (self.root/'plugins/aios-complete/.claude-plugin').mkdir(exist_ok=True)
        market=self.market()
        market['plugins'].append({'name':'aios-complete','source':'./plugins/aios-complete','version':'2.0.0','description':'Bundle.'})
        write_json(self.root/'.claude-plugin/marketplace.json',market)

    def apply(self,merge=True):
        out=build_catalogue.build(self.root,merge_entries=merge)
        for path,text in out.items():
            path.write_text(text)
        return out

    def test_unmerged_entry_fails_until_merged(self):
        self.setup_packs()
        with self.assertRaisesRegex(build_catalogue.CatalogueError,'no marketplace entry'):
            build_catalogue.build(self.root)
        self.apply()
        self.assertEqual(build_catalogue.build(self.root),{p:p.read_text() for p in build_catalogue.build(self.root)})

    def test_merge_adds_modules_order_and_bundle_dependencies(self):
        self.setup_packs()
        self.apply()
        names=[p['name'] for p in self.market()['plugins']]
        self.assertEqual(names,['aios','aios-rules','aios-brain','shelf-video','aios-complete'])
        modules={p['name']:p.get('metadata',{}).get('module') for p in self.market()['plugins']}
        self.assertEqual(modules,{'aios':1,'aios-rules':2,'aios-brain':5,'shelf-video':12,'aios-complete':None})
        bundle=json.loads((self.root/'plugins/aios-complete/.claude-plugin/plugin.json').read_text())
        self.assertEqual(bundle['dependencies'],['aios','aios-rules','aios-brain'])
        catalogue=json.loads((self.root/'plugins/aios/catalogue.json').read_text())
        rules=next(p for p in catalogue['packs'] if p['name']=='aios-rules')
        self.assertEqual(rules['hooks'],['PreToolUse'])
        brain=next(p for p in catalogue['packs'] if p['name']=='aios-brain')
        self.assertEqual(brain['mcp_servers'],['aios-brain'])
        self.assertEqual([m['packs'] for m in catalogue['modules'] if m['number']==12],[['shelf-video']])

    def test_version_disagreement_fails(self):
        self.setup_packs()
        self.apply()
        market=self.market()
        market['plugins'][1]['version']='2.0.1'
        write_json(self.root/'.claude-plugin/marketplace.json',market)
        with self.assertRaisesRegex(build_catalogue.CatalogueError,'differs'):
            build_catalogue.build(self.root)

    def test_plugin_folder_missing_from_marketplace_fails(self):
        self.setup_packs()
        self.apply()
        make_pack(self.root,'aios-orphan',deps=['aios'],entry=False)
        with self.assertRaisesRegex(build_catalogue.CatalogueError,'aios-orphan is not in marketplace'):
            build_catalogue.build(self.root)

    def test_unknown_module_needs_explicit_number(self):
        self.setup_packs()
        make_pack(self.root,'mystery',deps=['aios'])
        with self.assertRaisesRegex(build_catalogue.CatalogueError,'No module number for mystery'):
            build_catalogue.build(self.root,merge_entries=True)
        make_pack(self.root,'mystery2',deps=['aios'],module=7)
        (self.root/'plugins/mystery/MARKETPLACE_ENTRY.json').write_text(json.dumps({'name':'mystery','source':'./plugins/mystery','version':'2.0.0','description':'Module 4. Fictional.'}))
        self.apply()
        modules={p['name']:p['metadata']['module'] for p in self.market()['plugins'] if p.get('metadata')}
        self.assertEqual((modules['mystery'],modules['mystery2']),(4,7))

    def test_check_mode_reports_stale_file(self):
        self.setup_packs()
        self.apply()
        out=build_catalogue.build(self.root)
        catalogue=self.root/'plugins/aios/catalogue.json'
        catalogue.write_text('{}\n')
        self.assertNotEqual(out[catalogue],catalogue.read_text())


class Installs(Fixture):
    def packs(self,with_hooks=False):
        make_pack(self.root,'aios',skills=['aios'],bin_tools=['aios-guide'])
        hooks=None
        if with_hooks:
            hooks={'PreToolUse':[{'matcher':'Bash','hooks':[{'type':'command','command':'${CLAUDE_PLUGIN_ROOT}/bin/guard','timeout':5}]}],
                   'Stop':[{'hooks':[{'type':'command','command':'${CLAUDE_PLUGIN_ROOT}/bin/guard stop'}]}],
                   'Notification':[{'hooks':[{'type':'command','command':'say done'}]}]}
        make_pack(self.root,'aios-verify',deps=['aios'],skills=['verify-setup'],bin_tools=['guard'],hooks=hooks)
        make_pack(self.root,'aios-brain',deps=['aios'],skills=['brain'],bin_tools=['brain'],
                  mcp={'aios-brain':{'command':'${CLAUDE_PLUGIN_ROOT}/bin/brain','args':['mcp'],'env':{'TOKEN':'${user_config.t}'}}})
        make_pack(self.root,'aios-complete',deps=['aios','aios-verify','aios-brain'])

    def snapshot_home(self):
        files={}
        for path in sorted(self.home.rglob('*')):
            if path.is_symlink():
                files[str(path.relative_to(self.home))]='->'+os.readlink(path)
            elif path.is_file():
                files[str(path.relative_to(self.home))]=path.read_bytes()
        return files

    def test_dependencies_install_first_from_an_empty_home(self):
        self.packs()
        order,_=quiet(installer.install,'aios-brain')
        self.assertEqual(order,['aios','aios-brain'])
        for harness in ('.codex','.cursor','.agents'):
            self.assertEqual(sorted(p.name for p in (self.home/harness/'skills').iterdir()),['aios','brain'])
        self.assertTrue((self.home/'.local/bin/aios-guide').is_symlink())
        self.assertEqual(installer.check('aios-brain',quiet=True),[])

    def test_bundle_installs_every_dependency_and_checks(self):
        self.packs()
        order,out=quiet(installer.install,'aios-complete')
        self.assertEqual(order[0],'aios');self.assertEqual(order[-1],'aios-complete')
        self.assertIn('Installed aios 2.0.0, aios-verify 2.0.0, aios-brain 2.0.0, aios-complete 2.0.0',out)
        for pack in order:
            self.assertEqual(installer.check(pack,quiet=True),[],pack)

    def test_second_run_changes_nothing(self):
        self.packs(with_hooks=True)
        quiet(installer.install,'aios-complete')
        before=self.snapshot_home()
        _,out=quiet(installer.install,'aios-complete')
        self.assertEqual(self.snapshot_home(),before)
        self.assertNotIn('Linked',out)
        self.assertNotIn('Configured',out)

    def test_records_the_checkout_once(self):
        self.packs()
        _,out=quiet(installer.install,'aios')
        record=json.loads((self.home/'.local/share/aios/checkout.json').read_text())
        self.assertEqual(record['root'],str(self.root))
        self.assertIn('Recorded this checkout',out)
        _,out=quiet(installer.install,'aios')
        self.assertNotIn('Recorded',out)

    def test_conflict_in_a_dependency_writes_nothing(self):
        self.packs()
        foreign=self.home/'.local/bin/brain'
        foreign.parent.mkdir(parents=True)
        foreign.write_text('member tool')
        with self.assertRaisesRegex(ValueError,'Existing brain command preserved'):
            quiet(installer.install,'aios-complete')
        self.assertEqual(foreign.read_text(),'member tool')
        self.assertFalse((self.home/'.codex').exists())
        self.assertFalse((self.home/'.cursor').exists())
        self.assertFalse((self.home/'.local/share/aios').exists())

    def test_check_fails_when_a_link_is_removed(self):
        self.packs()
        quiet(installer.install,'aios-verify')
        (self.home/'.cursor/skills/verify-setup').unlink()
        problems=installer.check('aios-verify',quiet=True)
        self.assertEqual(problems,['skill verify-setup not linked in ~/.cursor/skills'])
        self.assertEqual(quiet(installer.main,['aios-verify','--check'])[0],1)
        quiet(installer.install,'aios-verify')
        self.assertEqual(quiet(installer.main,['aios-verify','--check'])[0],0)

    def test_dry_run_writes_nothing(self):
        self.packs(with_hooks=True)
        _,out=quiet(installer.install,'aios-complete',dry_run=True)
        self.assertIn('Would link .codex/skills/aios',out)
        self.assertIn('Would configure .cursor/hooks.json',out)
        self.assertEqual(self.snapshot_home(),{})

    def test_generic_mcp_server_uses_linked_command_and_reports_settings(self):
        self.packs()
        _,out=quiet(installer.install,'aios-brain')
        codex=(self.home/'.codex/config.toml').read_text()
        self.assertIn('[mcp_servers.aios-brain]\ncommand = "'+str(self.home/'.local/bin/brain')+'"',codex)
        cursor=json.loads((self.home/'.cursor/mcp.json').read_text())
        self.assertEqual(cursor['mcpServers']['aios-brain']['command'],str(self.home/'.local/bin/brain'))
        self.assertIn('set its settings (TOKEN) in your shell',out)

    def test_unknown_pack_lists_available(self):
        self.packs()
        with self.assertRaisesRegex(ValueError,'Unknown pack nope. Available: aios, aios-brain'):
            installer.install('nope')


class Hooks(Installs):
    def cursor(self):
        return json.loads((self.home/'.cursor/hooks.json').read_text())

    def test_cursor_merge_keeps_existing_entries_and_backs_up(self):
        self.packs(with_hooks=True)
        existing={'version':1,'hooks':{'preToolUse':[{'command':'./hooks/member.sh','matcher':'Shell'}],'afterFileEdit':[{'command':'fmt'}]}}
        write_json(self.home/'.cursor/hooks.json',existing)
        original=(self.home/'.cursor/hooks.json').read_bytes()
        _,out=quiet(installer.install,'aios-verify')
        merged=self.cursor()
        guard=str(self.root/'plugins/aios-verify/bin/guard')
        self.assertEqual(merged['hooks']['afterFileEdit'],[{'command':'fmt'}])
        self.assertEqual(merged['hooks']['preToolUse'][0],{'command':'./hooks/member.sh','matcher':'Shell'})
        self.assertEqual(merged['hooks']['preToolUse'][1],{'command':'AIOS_HARNESS=cursor '+guard,'matcher':'Shell','timeout':5})
        self.assertEqual(merged['hooks']['stop'],[{'command':'AIOS_HARNESS=cursor '+guard+' stop'}])
        backups=list((self.home/'.cursor').glob('hooks.json.backup-*'))
        self.assertEqual([b.read_bytes() for b in backups],[original])
        self.assertIn('Cursor: no Notification event',out)

    def test_cursor_merge_is_idempotent(self):
        self.packs(with_hooks=True)
        quiet(installer.install,'aios-verify')
        first=self.cursor()
        quiet(installer.install,'aios-verify')
        self.assertEqual(self.cursor(),first)
        self.assertEqual(len(first['hooks']['preToolUse']),1)

    def test_symlinked_cursor_hooks_are_preserved(self):
        self.packs(with_hooks=True)
        source=self.home/'dotfiles-hooks.json'
        source.write_text('{"version":1,"hooks":{}}')
        (self.home/'.cursor').mkdir()
        (self.home/'.cursor/hooks.json').symlink_to(source)
        with self.assertRaisesRegex(ValueError,'Symlinked config preserved'):
            quiet(installer.install,'aios-verify')
        self.assertEqual(source.read_text(),'{"version":1,"hooks":{}}')

    def test_invalid_cursor_hooks_stop_the_install(self):
        self.packs(with_hooks=True)
        write_json(self.home/'.cursor/hooks.json',{'version':1,'hooks':[]})
        with self.assertRaisesRegex(ValueError,'merge it manually'):
            quiet(installer.install,'aios-verify')

    def test_matcher_translation(self):
        self.assertEqual(installer.cursor_matcher('Bash'),'Shell')
        self.assertEqual(installer.cursor_matcher('Edit|Write|MultiEdit'),'Write')
        self.assertEqual(installer.cursor_matcher('mcp__brain__search'),'MCP:search')
        self.assertEqual(installer.cursor_matcher(''),'')
        self.assertIsNone(installer.cursor_matcher('WebFetch'))

    def test_codex_gets_written_rules_marked_not_enforced(self):
        self.packs(with_hooks=True)
        agents=self.home/'.codex/AGENTS.md'
        agents.parent.mkdir(parents=True)
        agents.write_text('# My rules\n- Use British English.\n')
        _,out=quiet(installer.install,'aios-verify')
        text=agents.read_text()
        self.assertTrue(text.startswith('# My rules\n- Use British English.\n'))
        self.assertIn('<!-- aios-hooks:aios-verify start -->',text)
        self.assertIn('not enforced',text)
        self.assertIn('Before Bash tool call, run `'+str(self.root/'plugins/aios-verify/bin/guard')+'`',text)
        self.assertIn('Codex does not enforce them',out)
        quiet(installer.install,'aios-verify')
        self.assertEqual(agents.read_text(),text)

    def test_codex_rules_file_wins_and_updates_in_place(self):
        self.packs(with_hooks=True)
        rules=self.root/'plugins/aios-verify/hooks/RULES.md'
        rules.write_text('- Run the tests before you say a change is done.\n')
        quiet(installer.install,'aios-verify')
        agents=self.home/'.codex/AGENTS.md'
        self.assertIn('- Run the tests before you say a change is done.',agents.read_text())
        rules.write_text('- Run the tests and show the result.\n')
        agents.write_text(agents.read_text()+'\n- A member rule added later.\n')
        quiet(installer.install,'aios-verify')
        text=agents.read_text()
        self.assertIn('- Run the tests and show the result.',text)
        self.assertNotIn('before you say a change is done',text)
        self.assertIn('- A member rule added later.',text)
        self.assertEqual(text.count('aios-hooks:aios-verify start'),1)

    def test_check_notices_a_removed_cursor_hook(self):
        self.packs(with_hooks=True)
        quiet(installer.install,'aios-verify')
        data=self.cursor();data['hooks']['stop']=[]
        write_json(self.home/'.cursor/hooks.json',data)
        self.assertIn('Cursor hook for stop missing from ~/.cursor/hooks.json',installer.check('aios-verify',quiet=True))


class Guide(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='aios-guide-',dir='/tmp')
        self.home=Path(self.tmp.name)
        self.env=patch.dict(os.environ,{'HOME':str(self.home),'CODEX_HOME':'','CLAUDE_CONFIG_DIR':'','CLAUDECODE':'','CLAUDE_PLUGIN_ROOT':''})
        self.env.start()
        import guide
        self.guide=guide

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def run_guide(self,*args):
        out=io.StringIO()
        with redirect_stdout(out),redirect_stderr(io.StringIO()):
            code=self.guide.main(list(args))
        return code,out.getvalue()

    def test_capability_words_find_the_pack(self):
        self.assertEqual(self.guide.resolve('set up my brain'),'aios-brain')
        self.assertEqual(self.guide.resolve('5'),'aios-brain')
        self.assertEqual(self.guide.resolve('install the whole framework'),'aios-complete')

    def test_tour_parsing(self):
        intro,steps,outro=self.guide.parse_tour((ROOT/'plugins/aios/TOUR.md').read_text())
        self.assertTrue(intro.startswith('# Tour: module 1'))
        self.assertEqual([s['number'] for s in steps],[1,2,3,4,5,6])
        self.assertEqual(steps[0]['command'],'`aios-guide next`')
        self.assertTrue(all(s['do'] and s['command'] and s['see'] and s['check'] for s in steps))
        self.assertTrue(outro.startswith('## Keep going'))

    def test_learn_walks_one_step_at_a_time(self):
        code,out=self.run_guide('--harness','codex','learn','1')
        self.assertEqual(code,0)
        self.assertIn('Step 1 of 6. See where you start',out)
        self.assertIn('Lesson: https://www.skool.com/',out)
        code,out=self.run_guide('--harness','codex','learn','1','--done','1')
        self.assertIn('(1 of 6 steps checked)',out)
        self.assertIn('Step 2 of 6',out)
        for n in range(2,7):
            code,out=self.run_guide('--harness','codex','learn','1','--done',str(n))
        self.assertIn('Every step is checked.',out)
        self.assertIn('aios-guide progress --complete 1',out)
        self.assertFalse((self.home/'.local/share/aios/progress.json').exists())

    def test_learn_without_a_tour_points_to_the_lesson(self):
        code,out=self.run_guide('--harness','codex','learn','aios-brain')
        self.assertEqual(code,0)
        self.assertIn('Follow the Skool lesson',out)

    def test_progress_only_on_request(self):
        code,out=self.run_guide('progress','--complete','1')
        self.assertIn('Confirmed modules: 1',out)
        code,out=self.run_guide('--harness','codex','next')
        self.assertIn('Next module: 2.',out)

    def test_next_on_an_empty_machine(self):
        code,out=self.run_guide('--harness','codex','next')
        self.assertIn('Installed packs: none yet',out)
        self.assertIn('Next module: 1. Start here',out)
        self.assertIn('install.sh aios',out)

    def test_status_reads_names_from_the_catalogue(self):
        import status
        self.assertNotIn('aios-skills-kit',status.PACKS)
        self.assertNotIn('aios-ship-it',status.PACKS)
        self.assertEqual(status.inventory(home=self.home,cwd=self.home)['available_packs'],status.PACKS)

    def test_member_skill_with_the_same_name_is_not_ours(self):
        import status
        own=self.home/'.codex/skills/aios'
        own.mkdir(parents=True)
        (own/'SKILL.md').write_text('A member skill')
        report=status.inventory(home=self.home,cwd=self.home)
        self.assertEqual(report['packs'],[])


class ReleaseTags(unittest.TestCase):
    def test_tags_only_untagged_packs_with_a_fake_claude(self):
        with tempfile.TemporaryDirectory(prefix='aios-release-',dir='/tmp') as temp:
            clone=Path(temp)/'repo'
            subprocess.run(['git','clone','-q','--no-hardlinks',str(ROOT),str(clone)],check=True)
            # The working tree may hold uncommitted work: copy what the script reads over the clone.
            for rel in ('scripts','.claude-plugin','plugins'):
                shutil.copytree(str(ROOT/rel),str(clone/rel),dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
            subprocess.run(['git','-C',str(clone),'remote','remove','origin'],check=True)
            subprocess.run(['git','-C',str(clone),'tag','aios--v2.0.0'],check=True)
            log=Path(temp)/'calls.txt'
            fake=Path(temp)/'claude'
            fake.write_text('#!/bin/sh\necho "$PWD $*" >> '+str(log)+'\n')
            fake.chmod(0o755)
            proc=subprocess.run(['bash',str(clone/'scripts/release_tags.sh'),'--dry-run'],env=dict(os.environ,CLAUDE_BIN=str(fake)),
                                text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn('skip aios--v2.0.0 (already tagged)',proc.stdout)
            calls=log.read_text().splitlines()
            self.assertTrue(all(c.endswith('plugin tag --dry-run .') for c in calls))
            tagged={Path(c.split(' ')[0]).name for c in calls}
            self.assertIn('aios-brain',tagged)
            self.assertIn('aios-complete',tagged)
            self.assertNotIn('aios',tagged)
            bad=subprocess.run(['bash',str(clone/'scripts/release_tags.sh'),'--force'],env=dict(os.environ,CLAUDE_BIN=str(fake)),
                               text=True,capture_output=True)
            self.assertEqual(bad.returncode,2)


if __name__=='__main__':
    unittest.main()
