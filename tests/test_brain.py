import importlib.util
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'plugins/aios-brain'),str(ROOT/'scripts')]
from aios_brain import capture, config, db, digest, media, search, status, sync
from aios_brain.cli import main
from aios_brain.mcp_server import call
from install_pack import codex_config
from sandbox_fixtures_v1 import write


class SandboxCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aios-test-',dir='/tmp')
        self.home = Path(self.tmp.name)
        self.env = patch.dict(os.environ,{'HOME':str(self.home),'AIOS_BRAIN_TURSO_URL':'','AIOS_BRAIN_TURSO_TOKEN':'',
                 'CLAUDE_PLUGIN_OPTION_TURSO_URL':'','CLAUDE_PLUGIN_OPTION_TURSO_TOKEN':'','SUPADATA_API_KEY':'','CLAUDE_CONFIG_DIR':'','CODEX_HOME':''})
        self.env.start()
        self.conn = db.connect(create=True)
    def tearDown(self):
        self.conn.close()
        self.env.stop()
        self.tmp.cleanup()
    def fixtures(self):
        write(self.home)
        return capture.capture(self.conn)
    def path(self):
        return self.home/'.claude/projects/fictional/fictional-claude.jsonl'



class BrainCase(SandboxCase):
    def test_all_harnesses_capture_and_unchanged(self):
        first = self.fixtures()
        self.assertEqual((first['captured'],first['messages']),(3,6))
        second = capture.capture(self.conn)
        self.assertEqual((second['captured'],second['unchanged']),(0,3))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM documents').fetchone()[0],6)

    def test_change_replaces_removed_messages_and_fts(self):
        self.fixtures()
        events = [json.loads(l) for l in self.path().read_text().splitlines()]
        events[1]['message']['content'][0]['text'] = 'The fictional Lighthouse launch budget is 3200 pounds.'
        self.path().write_text(''.join(json.dumps(e)+'\n' for e in events))
        changed = capture.capture(self.conn)
        self.assertEqual((changed['captured'],changed['unchanged']),(1,2))
        self.assertTrue(search.search(self.conn,'3200'))
        self.assertFalse(search.search(self.conn,'2400'))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM documents').fetchone()[0],6)

    def test_invalid_json_does_not_advance_hash(self):
        self.fixtures()
        before = self.conn.execute('SELECT file_hash FROM items WHERE source="claude"').fetchone()[0]
        with self.path().open('a') as f:
            f.write('{"partial":')
        result = capture.capture(self.conn)
        self.assertEqual(result['failures'],[])
        self.assertIn(self.path().name,result['active_files'])
        self.assertEqual(self.conn.execute('SELECT file_hash FROM items WHERE source="claude"').fetchone()[0],before)
        self.assertTrue(status.status(self.conn)['healthy'])
        old=time.time()-capture.CRASH_TAIL_SECONDS-1
        os.utime(self.path(),(old,old))
        self.assertFalse(status.status(self.conn)['healthy'])

    def test_failure_recovers_only_after_success(self):
        self.fixtures()
        raw = self.path().read_bytes()
        self.path().write_bytes(raw+b'{')
        capture.capture(self.conn)
        self.path().write_bytes(raw)
        capture.capture(self.conn)
        self.assertTrue(status.status(self.conn)['healthy'])

    def test_transaction_rolls_back_messages_and_hash(self):
        self.fixtures()
        value = db.bundle(self.conn,self.conn.execute('SELECT ref FROM items LIMIT 1').fetchone()[0])
        old = db.serialise(value)
        broken = [dict(d) for d in value['documents']]
        broken[1]['id'] = broken[0]['id']
        value['item']['file_hash'] = 'wrong'
        with self.assertRaises(sqlite3.IntegrityError):
            db.put_item(self.conn,value['item'],broken)
        self.assertEqual(db.serialise(db.bundle(self.conn,value['item']['ref'])),old)

    def test_harness_noise_and_tools_absent(self):
        self.fixtures()
        self.assertFalse(search.search(self.conn,'harness only needle'))
        self.assertFalse(search.search(self.conn,'tool only needle'))
        self.assertTrue(search.search(self.conn,'Lighthouse'))
        self.assertEqual(capture.clean('# AGENTS.md instructions\n<INSTRUCTIONS>noise</INSTRUCTIONS>actual task'),'actual task')

    def test_codex_first_meta_and_subagents(self):
        raw = '\n'.join(json.dumps(e) for e in [
            {'type':'session_meta','payload':{'id':'child','thread_source':'subagent'}},
            {'type':'session_meta','payload':{'id':'parent'}}]).encode()
        sid, messages = capture.parse('codex',Path('x.jsonl'),raw,0)
        self.assertIsNone(sid)
        raw = raw.replace(b'"thread_source": "subagent"',b'"thread_source": "cli"')
        sid,_ = capture.parse('codex',Path('x.jsonl'),raw,0)
        self.assertEqual(sid,'child')

    def test_cursor_text_export(self):
        sid,messages = capture.parse('cursor',Path('export.txt'),b'user:\nQuestion about a delivery\n\nassistant:\nDelivery is Friday\n',123)
        self.assertEqual(len(messages),2)
        self.assertEqual(messages[1][1],'Delivery is Friday')
        self.assertEqual(capture.clean('Useful answer\n[Tool call] Shell\nnoise-only-needle','cursor',text_export=True),'Useful answer')

    def test_status_pending_new_file_and_newest_message(self):
        write(self.home)
        report = status.status(self.conn)
        self.assertFalse(report['healthy'])
        self.assertEqual(len(report['pending_files']),3)
        self.assertIsNone(report['newest_stored_message'])
        capture.capture(self.conn)
        report = status.status(self.conn)
        self.assertTrue(report['healthy'])
        self.assertEqual(report['newest_session_message'],report['newest_stored_message'])

    def test_status_same_mtime_changed_file(self):
        self.fixtures()
        path = self.path()
        old = path.stat()
        path.write_text(path.read_text().replace('2400','3400'))
        os.utime(path,(old.st_atime,old.st_mtime))
        self.assertFalse(status.status(self.conn)['healthy'])

    def test_status_detects_missing_message_even_with_real_hash(self):
        self.fixtures()
        with self.conn:
            self.conn.execute('DELETE FROM documents WHERE id=(SELECT id FROM documents LIMIT 1)')
        self.assertFalse(status.status(self.conn)['healthy'])

    def test_status_does_not_treat_recent_heartbeat_as_health(self):
        self.fixtures()
        db.failure(self.conn,'sync','Read-back mismatch')
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO meta VALUES("last_capture",?)',(str(time.time()),))
        self.assertFalse(status.status(self.conn)['healthy'])

    def test_status_30_day_warning(self):
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO meta VALUES("last_capture",?)',(str(time.time()-31*86400),))
        self.assertTrue(any('No verified capture' in w for w in status.status(self.conn)['warnings']))

    def test_cli_status_exits_one_when_unhealthy(self):
        write(self.home)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(['status']),1)
            self.assertEqual(main(['capture']),0)
            self.assertEqual(main(['status']),0)

    def seed_rank(self):
        local = db.device(self.conn)
        for ref,body,ts in [('old','violet delivery parcel',time.time()-300*86400),
                            ('new','violet delivery parcel',time.time()),
                            ('unrelated','violet story flower',time.time())]:
            item = {'ref':ref,'source':'test','device':local,'file_hash':ref,'modified':ts,'latest':ts,'updated':ts,'title':'','path':None,'url':None,'digest':None}
            db.put_item(self.conn,item,[{'id':ref,'kind':'message','role':'user','body':body,'ts':ts}])

    def test_recency_breaks_equal_relevance_tie(self):
        self.seed_rank()
        hits = search.search(self.conn,'violet delivery')
        self.assertEqual([h['ref'] for h in hits],['new','old'])
        plain = search.search(self.conn,'violet delivery',recency=False)
        self.assertEqual(plain[0]['score'],plain[1]['score'])
        self.assertAlmostEqual(hits[0]['score']/hits[1]['score'],2/(1+2**-10),places=3)

    def test_bm25_strong_old_match_survives_recency(self):
        self.seed_rank()
        hits = search.search(self.conn,'delivery parcel')
        self.assertEqual({h['ref'] for h in hits},{'old','new'})
        self.assertFalse(search.search(self.conn,'unknownword'))

    def test_strong_old_bm25_match_beats_weak_recent_match(self):
        self.seed_rank()
        with self.conn:
            self.conn.execute('UPDATE documents SET body=? WHERE ref="old"', ('delivery ' * 60,))
            self.conn.execute('UPDATE documents SET body=? WHERE ref="new"', ('delivery '+'filler '*59,))
        hits = search.search(self.conn,'delivery')
        self.assertEqual(hits[0]['ref'],'old')

    def test_query_is_literal_and_limits_bounded(self):
        self.fixtures()
        self.assertFalse(search.search(self.conn,'Lighthouse OR fictional'))
        with self.assertRaises(ValueError):
            search.search(self.conn,'***')
        with self.assertRaises(ValueError):
            search.search(self.conn,'launch',half_life_days=0)

    def test_read_pagination_has_no_lost_text(self):
        self.fixtures()
        ref = search.search(self.conn,'Lighthouse')[0]['ref']
        all_text = search.read(self.conn,ref)['text']
        first = search.read(self.conn,ref,max_chars=10)
        second = search.read(self.conn,ref,start=first['next_start'])
        self.assertEqual(first['text']+second['text'],all_text)

    def test_local_mode_does_not_use_network(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('network forbidden')), patch('urllib.request.OpenerDirector.open',side_effect=AssertionError('network forbidden')):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(['init']),0)
                self.fixtures()
                self.assertEqual(main(['capture']),0)
                self.assertEqual(main(['status']),0)

    def test_config_half_pair_and_private_permissions(self):
        with patch.dict(os.environ,{'AIOS_BRAIN_TURSO_URL':'libsql://example.turso.io'}):
            with self.assertRaises(ValueError):
                config.load()
        path = self.home/'.config/aios-brain/env'
        path.parent.mkdir(parents=True)
        path.write_text('AIOS_BRAIN_TURSO_URL=libsql://example.turso.io\nAIOS_BRAIN_TURSO_TOKEN=fictional\n')
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            config.load()
        path.chmod(0o600)
        self.assertEqual(config.load()['AIOS_BRAIN_TURSO_TOKEN'],'fictional')

    def test_media_fallback_requires_own_key(self):
        with patch.object(media,'captions',side_effect=ValueError('no captions')),patch.object(media,'supadata') as paid:
            with self.assertRaises(ValueError):
                media.add(self.conn,'https://youtu.be/abcdefghijk',{})
            paid.assert_not_called()

    def test_media_capture_and_idempotency(self):
        with patch.object(media,'captions',return_value=('A fictional video about navy paint.','Paint guide')) as fetch:
            first = media.add(self.conn,'https://youtu.be/abcdefghijk',{})
            second = media.add(self.conn,'https://www.youtube.com/watch?v=abcdefghijk',{})
        self.assertTrue(first['stored'])
        self.assertFalse(second['stored'])
        self.assertEqual(fetch.call_count,1)
        self.assertTrue(search.search(self.conn,'navy paint'))
        self.assertEqual(first['digest'].split(';')[0],'off')

    def test_media_rejects_non_video_and_insecure_urls(self):
        for url in ['http://youtube.com/watch?v=abcdefghijk','https://example.com/watch?v=abcdefghijk','https://youtube.com/playlist?list=abc']:
            with self.assertRaises(ValueError):
                media.canonical_url(url)

    def test_digest_subscription_only_and_no_automatic_digest(self):
        self.fixtures()
        ref = self.conn.execute('SELECT ref FROM items LIMIT 1').fetchone()[0]
        login = subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True,'authMethod':'api_key'}),'')
        with patch.object(digest.shutil,'which',return_value='/tmp/claude'),patch.object(digest.subprocess,'run',return_value=login) as run:
            with self.assertRaises(ValueError):
                digest.make(self.conn,ref)
            self.assertEqual(run.call_count,1)

    def test_digest_validates_output_and_removes_api_credentials(self):
        self.fixtures()
        ref = search.search(self.conn,'Lighthouse')[0]['ref']
        login = subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True,'authMethod':'claude.ai'}),'')
        generated = {'title':'Lighthouse budget','summary':'Budget agreed.','questions':['What budget?'],'atoms':[{'kind':'decision','text':'2400 pounds'}]}
        result = subprocess.CompletedProcess([],0,json.dumps({'result':json.dumps(generated)}),'')
        with patch.dict(os.environ,{'ANTHROPIC_API_KEY':'fictional-secret'}),patch.object(digest.shutil,'which',return_value='/tmp/claude'),patch.object(digest.subprocess,'run',side_effect=[login,result]) as run:
            digest.make(self.conn,ref)
            self.assertNotIn('ANTHROPIC_API_KEY',run.call_args.kwargs['env'])
            self.assertIn('haiku',run.call_args.args[0])
        self.assertTrue(any(h['kind']=='digest' for h in search.search(self.conn,'budget')))

    def test_mcp_exact_schema_and_round_trip(self):
        self.fixtures()
        self.assertTrue(call('brain_search',{'query':'Lighthouse'})['hits'])
        for args in ({'query':'x','bogus':1},{'query':'x','limit':True},{'query':'x','limit':51}):
            with self.assertRaises(ValueError):
                call('brain_search',args)
        request = '\n'.join(json.dumps(v) for v in [
            {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}},
            {'jsonrpc':'2.0','method':'notifications/initialized'},
            {'jsonrpc':'2.0','id':2,'method':'tools/list'},
            {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'brain_search','arguments':{'query':'Lighthouse'}}}])+'\n'
        proc = subprocess.run([str(ROOT/'plugins/aios-brain/bin/brain'),'mcp'],input=request,text=True,capture_output=True)
        rows = [json.loads(l) for l in proc.stdout.splitlines()]
        self.assertEqual(proc.returncode,0)
        self.assertEqual(len(rows),3)
        self.assertEqual(len(rows[1]['result']['tools']),3)
        self.assertIn('Lighthouse',rows[2]['result']['content'][0]['text'])


class FakePrimary:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
    def __del__(self):
        self.conn.close()
    def transaction(self,statements):
        with self.conn:
            for sql,args in statements:
                self.conn.execute(sql,args)
    def query(self,sql,args=()):
        return [dict(r) for r in self.conn.execute(sql,args)]


class SyncTests(SandboxCase):
    def test_two_machines_exchange_and_verify_actual_contents(self):
        self.fixtures()
        remote = FakePrimary()
        self.assertEqual(sync.synchronise(self.conn,remote)['uploaded'],3)
        self.assertTrue(sync.health(self.conn,remote)['healthy'])
        with self.conn:
            self.conn.execute('DELETE FROM items')
        self.assertFalse(sync.health(self.conn,remote)['healthy'])
        self.assertEqual(sync.synchronise(self.conn,remote)['downloaded'],3)
        self.assertTrue(search.search(self.conn,'Lighthouse'))
        self.assertTrue(sync.health(self.conn,remote)['healthy'])

    def test_readback_failure_surfaces_despite_successful_write(self):
        self.fixtures()
        remote = FakePrimary()
        real = remote.query
        def corrupt(sql,args=()):
            rows = real(sql,args)
            if 'WHERE ref=' in sql and rows:
                rows[0]['sha256']='a lying success marker'
            return rows
        remote.query = corrupt
        with self.assertRaisesRegex(ValueError,'read-back'):
            sync.synchronise(self.conn,remote)

    def test_transport_never_forwards_a_token_on_redirect(self):
        with self.assertRaisesRegex(ValueError,'redirect rejected'):
            sync.NoRedirect().redirect_request(None,None,302,'redirect',{},'https://other.example')

    def test_http_200_error_is_not_success_and_token_not_printed(self):
        http = sync.HTTP('libsql://example.turso.io','fictional-secret')
        response = io.BytesIO(json.dumps({'results':[{'type':'error','error':{'message':'fictional-secret'}}]}).encode())
        with patch('urllib.request.OpenerDirector.open',return_value=response):
            with self.assertRaises(ValueError) as error:
                http.query('SELECT 1')
        self.assertNotIn('fictional-secret',str(error.exception))

    def test_transaction_missing_commit_rejected(self):
        http = sync.HTTP('https://example.turso.io','fictional')
        with patch.object(http,'post',return_value={'step_results':[{},None,None],'step_errors':[None,{'message':'denied'}]}):
            with self.assertRaisesRegex(ValueError,'did not commit'):
                http.transaction([('SELECT 1',())])


class InstallerTests(unittest.TestCase):
    def test_foreign_skill_is_preserved_and_brain_needs_real_start_pack(self):
        with tempfile.TemporaryDirectory(prefix='aios-foreign-',dir='/tmp') as temp:
            home = Path(temp)
            existing = home/'.codex/skills/aios'
            existing.mkdir(parents=True)
            (existing/'SKILL.md').write_text('Member-owned skill')
            env = dict(os.environ,HOME=temp,CODEX_HOME=str(home/'.codex'),CLAUDE_CONFIG_DIR=str(home/'.claude'))
            for pack in ['aios','aios-brain']:
                proc = subprocess.run([str(ROOT/'install.sh'),pack],env=env,text=True,capture_output=True)
                self.assertEqual(proc.returncode,1)
            self.assertEqual((existing/'SKILL.md').read_text(),'Member-owned skill')
            self.assertFalse((home/'.cursor').exists())

    def test_toml_unrelated_entries_preserved(self):
        original = 'model = "fictional"\n\n[mcp_servers.other]\ncommand = "other"\n\n[features]\nfoo = true\n'
        result = codex_config(original,Path('/tmp/member/brain'))
        self.assertTrue(result.startswith(original.rstrip()))
        self.assertEqual(result.count('[mcp_servers.aios-brain]'),1)
        second = codex_config(result,Path('/tmp/member/brain'))
        self.assertEqual(second.count('[mcp_servers.aios-brain]'),1)
        self.assertIn('[mcp_servers.other]\ncommand = "other"',second)
        self.assertIn('[features]\nfoo = true',second)

    def test_existing_arrays_after_our_table_are_preserved(self):
        original = codex_config('',Path('/tmp/member/brain'))
        original += '\n[[unrelated]]\nname = "keep me"\n'
        self.assertEqual(codex_config(original,Path('/tmp/member/brain')),original)
        with self.assertRaises(ValueError):
            codex_config('[mcp_servers.aios-brain]\ncommand="custom"\n',Path('/tmp/member/brain'))

    def test_sandbox_install_backup_and_no_other_skill_links(self):
        with tempfile.TemporaryDirectory(prefix='aios-install-',dir='/tmp') as temp:
            home = Path(temp)
            (home/'.codex').mkdir()
            (home/'.cursor').mkdir()
            toml = 'model = "fictional"\n[mcp_servers.other]\ncommand="other"\n'
            cursor = {'mcpServers':{'other':{'command':'other'}},'unrelated':True}
            (home/'.codex/config.toml').write_text(toml)
            (home/'.cursor/mcp.json').write_text(json.dumps(cursor))
            env = dict(os.environ,HOME=temp,CODEX_HOME=str(home/'.codex'),CLAUDE_CONFIG_DIR=str(home/'.claude'))
            for pack in ['aios','aios-brain','aios-brain']:
                proc = subprocess.run([str(ROOT/'install.sh'),pack],env=env,text=True,capture_output=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
            for harness in ['.codex','.cursor','.agents']:
                self.assertEqual(sorted(p.name for p in (home/harness/'skills').iterdir()),['aios','brain'])
            self.assertFalse((home/'.claude').exists())
            self.assertEqual(json.loads((home/'.cursor/mcp.json').read_text())['mcpServers']['other'],cursor['mcpServers']['other'])
            self.assertTrue(any(p.read_text()==toml for p in (home/'.codex').glob('config.toml.backup-*')))
            # 2.0 installs are idempotent: the repeat run finds nothing to change, so it writes no second backup.
            self.assertEqual(len(list((home/'.cursor').glob('mcp.json.backup-*'))),1)


class StartStatusTests(unittest.TestCase):
    def test_inventory_reports_each_harness_without_completing_lessons(self):
        spec = importlib.util.spec_from_file_location('start_status',ROOT/'plugins/aios/scripts/status.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix='aios-status-',dir='/tmp') as temp:
            home = Path(temp)
            (home/'.claude/plugins').mkdir(parents=True)
            plugin = ROOT/'plugins/aios'
            (home/'.claude/plugins/installed_plugins.json').write_text(json.dumps({'plugins':{'aios@navaigate-aios':[{'installPath':str(plugin)}]}}))
            (home/'.claude/settings.json').write_text(json.dumps({'enabledPlugins':{'aios@navaigate-aios':False}}))
            skill = home/'.codex/skills/aios'
            skill.parent.mkdir(parents=True)
            skill.symlink_to(plugin/'skills/aios')
            report = module.inventory(home=home,cwd=home)
            found = next(p for p in report['packs'] if p['pack']=='aios')['harnesses']
            self.assertFalse(found['claude']['enabled'])
            self.assertTrue(found['claude']['files_present'])
            self.assertTrue(found['codex']['skills_present'])
            self.assertFalse(found['cursor']['skills_present'])
            self.assertEqual(report['next_module'],1)
            path = home/'.local/share/aios/progress.json'
            path.parent.mkdir(parents=True)
            path.write_text('{"completed_modules":[1,2,3,4]}')
            self.assertEqual(module.inventory(home=home,cwd=home)['next_module'],5)


if __name__=='__main__':
    unittest.main()
