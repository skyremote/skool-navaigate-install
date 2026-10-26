"""Regression cases R01–R16 from the phase-1 audit and its reproduction scripts."""
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import tracemalloc
import unittest
from contextlib import redirect_stdout,redirect_stderr
from unittest.mock import patch

from test_brain import SandboxCase,FakePrimary,ROOT
from aios_brain import capture,config,db,digest,media,privacy,search,status,sync
from aios_brain.cli import main
from aios_brain.mcp_server import call
import install_pack as installer


class ReviewRegressions(SandboxCase):
    def cli(self,args):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err):
            code=main(args)
        return code,out.getvalue(),err.getvalue()

    def append(self,text='A new fictional turn'):
        with self.path().open('a') as stream:
            stream.write(json.dumps({'type':'user','sessionId':'fictional-claude','timestamp':'2026-10-26T10:05:00Z','message':{'role':'user','content':text}})+'\n')

    def test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration(self):
        skills=sorted((ROOT/'skills').iterdir())
        self.assertEqual(len(skills),28)
        for harness in ('.claude','.codex','.cursor','.agents'):
            folder=self.home/harness/'skills'
            folder.mkdir(parents=True)
            for skill in skills:
                (folder/skill.name).symlink_to(skill)
        marketplace=json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        legacy=next(p for p in marketplace['plugins'] if p['name']=='skool-navaigate-install')
        self.assertEqual(legacy['source'],'./')
        self.assertFalse((ROOT/'legacy/v1').exists())
        for harness in ('.claude','.codex','.cursor','.agents'):
            self.assertTrue(all((self.home/harness/'skills'/s.name/'SKILL.md').is_file() for s in skills))
        with self.assertRaisesRegex(ValueError,'guided move'):
            installer.install('aios')
        with redirect_stdout(io.StringIO()):
            installer.install('aios',migrate_v1=True)
        backups=list((self.home/'.local/share/aios/v1-backups').glob('*/*'))
        self.assertEqual(len(backups),3)
        self.assertTrue(all(p.is_symlink() and p.resolve()==ROOT/'skills/aios' for p in backups))
        self.assertEqual((self.home/'.claude/skills/aios').resolve(),ROOT/'skills/aios')
        for harness in ('.codex','.cursor','.agents'):
            self.assertEqual((self.home/harness/'skills/aios').resolve(),ROOT/'plugins/aios/skills/aios')
            self.assertTrue(all((self.home/harness/'skills'/s.name/'SKILL.md').is_file() for s in skills if s.name!='aios'))
        spec=importlib.util.spec_from_file_location('review_start',ROOT/'plugins/aios/scripts/status.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(module.inventory(home=self.home,cwd=self.home)['v1']['skills_by_harness']['claude'])

    def test_R02_active_append_gets_bounded_grace_not_permanent_green(self):
        self.fixtures();self.append()
        report=status.status(self.conn)
        self.assertTrue(report['healthy'],report)
        self.assertEqual(report['active_files'],[self.path().name])
        with self.conn:
            self.conn.execute('UPDATE health_pending SET since=?',(time.time()-capture.ACTIVE_GRACE_SECONDS-1,))
        os.utime(self.path(),None)  # Continued activity cannot restart the grace clock.
        report=status.status(self.conn)
        self.assertFalse(report['healthy'])
        self.assertIn(self.path().name,report['pending_files'])
        capture.capture(self.conn)
        self.assertTrue(status.status(self.conn)['healthy'])
        original=capture.fingerprint
        def busy(path):
            if path==self.path():
                raise capture.SessionChanged('Writer appended during inspection')
            return original(path)
        with patch.object(capture,'fingerprint',side_effect=busy):
            self.assertTrue(status.status(self.conn)['healthy'])
            with self.conn:
                self.conn.execute('UPDATE health_pending SET since=?',(time.time()-capture.ACTIVE_GRACE_SECONDS-1,))
            self.assertFalse(status.status(self.conn)['healthy'])

    def test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists(self):
        self.fixtures()
        self.assertEqual(self.cli(['digest','no-such-ref'])[0],1)
        self.assertEqual(self.cli(['media','add','https://youtube.com/playlist?list=abc'])[0],1)
        with self.assertRaises(ValueError):
            call('brain_media_add',{'url':'https://youtube.com/playlist?list=abc'})
        self.assertEqual(self.conn.execute('SELECT count(*) FROM failures').fetchone()[0],0)
        db.failure(self.conn,'sync','A fictional operational failure')
        self.assertEqual(self.cli(['failures','clear','--scope','sync'])[0],0)
        self.assertTrue(status.status(self.conn)['healthy'])

    def test_R03_moved_crashed_file_failure_clears(self):
        self.fixtures()
        broken=self.path().with_name('crashed.jsonl')
        broken.write_text('{"type":"user","message":{"role":"user","content":"Important decision"}}\n{')
        self.assertTrue(capture.capture(self.conn)['failures'])
        broken.rename(self.home/'saved-crashed.txt')
        self.assertTrue(status.status(self.conn)['healthy'])
        self.assertEqual(self.conn.execute('SELECT count(*) FROM failures').fetchone()[0],0)

    def test_R04_harness_overrides_and_empty_installed_harness(self):
        from sandbox_fixtures_v1 import write
        write(self.home)
        custom_claude=self.home/'alt-claude';custom_codex=self.home/'alt-codex'
        (self.home/'.claude').rename(custom_claude)
        (self.home/'.codex').rename(custom_codex)
        with patch.dict(os.environ,{'CLAUDE_CONFIG_DIR':str(custom_claude),'CODEX_HOME':str(custom_codex)}):
            self.assertEqual(capture.capture(self.conn)['captured'],3)
            self.assertTrue(status.status(self.conn)['healthy'])
        with tempfile.TemporaryDirectory(prefix='aios-empty-',dir='/tmp') as temp:
            other=Path(temp);(other/'custom-claude').mkdir()
            with patch.dict(os.environ,{'HOME':temp,'CLAUDE_CONFIG_DIR':str(other/'custom-claude'),'CODEX_HOME':'','PATH':'/usr/bin:/bin'}):
                with db.database(create=True) as conn:
                    report=status.status(conn)
                    self.assertFalse(report['healthy'])
                    self.assertTrue(any('claude: installed harness has zero' in p for p in report['problems']))

    def test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote(self):
        self.fixtures()
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        with patch.dict(os.environ,{'AIOS_BRAIN_TURSO_URL':'https://127.0.0.1:9','AIOS_BRAIN_TURSO_TOKEN':'fictional\nwrapped'}),patch.object(sync,'HTTP',side_effect=AssertionError('Recall must not connect')):
            self.assertTrue(call('brain_search',{'query':'Lighthouse'})['hits'])
            self.assertIn('2400',call('brain_read',{'ref':ref})['text'])
            self.assertEqual(self.cli(['search','Lighthouse'])[0],0)
            self.assertEqual(self.cli(['read',ref])[0],0)

    def test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks(self):
        self.fixtures()
        remote=FakePrimary()
        sync.synchronise(self.conn,remote)
        calls=[];query=remote.query
        def tracked(sql,args=()):
            calls.append(sql)
            return query(sql,args)
        remote.query=tracked
        self.assertEqual(sync.synchronise(self.conn,remote),{'uploaded':0,'downloaded':0,'verified':True})
        self.assertFalse(any('payload' in sql for sql in calls))
        self.assertTrue(sync.health(self.conn,remote)['healthy'])
        self.assertFalse(any('SELECT *' in sql for sql in calls))
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        value=db.bundle(self.conn,ref)
        value['item']['updated']+=100
        value['documents'][0]['body']='A long fictional passage. '*20000
        raw=db.serialise(value)
        with remote.conn:
            remote.conn.execute('UPDATE aios_brain_bundles_v1 SET payload=?,sha256=?,updated=? WHERE ref=?',(raw,sync.sha(raw),value['item']['updated'],ref))
        calls.clear()
        self.assertEqual(sync.synchronise(self.conn,remote)['downloaded'],1)
        self.assertGreater(sum('substr(payload' in sql for sql in calls),1)
        self.assertFalse(any('SELECT *' in sql for sql in calls))

    def test_R06_python39_toml_conflicts_and_crlf(self):
        exe=Path('/tmp/member/brain')
        cases=['[mcp_servers]\naios-brain.command="custom"\n','mcp_servers.aios-brain.command="custom"\n',
               '[[mcp_servers.aios-brain]]\ncommand="custom"\n']
        with patch.dict(sys.modules,{'tomllib':None}):
            for text in cases:
                with self.subTest(text=text),self.assertRaises(ValueError):
                    installer.codex_config(text,exe)
            block='[mcp_servers.aios-brain]\r\ncommand = "/tmp/member/brain"\r\nargs = ["mcp"]\r\n'
            self.assertEqual(installer.codex_config(block,exe),block)

    def test_R07_symlinked_config_sources_are_preserved(self):
        with redirect_stdout(io.StringIO()):
            installer.install('aios')
        for relative in ('.codex/config.toml','.cursor/mcp.json'):
            with self.subTest(relative=relative):
                dest=self.home/relative
                source=self.home/('source-'+dest.name)
                source.write_text('{}' if dest.suffix=='.json' else 'model="fictional"\n')
                dest.symlink_to(source)
                with self.assertRaisesRegex(ValueError,'Symlinked config preserved'):
                    installer.install('aios-brain')
                self.assertTrue(dest.is_symlink())
                self.assertEqual(dest.resolve(),source.resolve())
                self.assertEqual(source.read_text(),'{}' if dest.suffix=='.json' else 'model="fictional"\n')
                dest.unlink()  # Dispose only the test-created link between subcases.

    def test_R08_recapture_preserves_paid_digest_and_title(self):
        self.fixtures()
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        value=db.bundle(self.conn,ref)
        value['item'].update(title='Saved subscription digest',digest='{"summary":"Keep this summary"}')
        value['documents'].append({'id':ref+':digest','ref':ref,'kind':'digest','role':'digest','body':'Keep this summary','ts':value['item']['latest']})
        db.put_item(self.conn,value['item'],value['documents'])
        self.append();capture.capture(self.conn)
        value=db.bundle(self.conn,ref)
        self.assertEqual(value['item']['title'],'Saved subscription digest')
        self.assertIn('Keep this summary',value['item']['digest'])
        self.assertTrue(any(d['kind']=='digest' for d in value['documents']))

    def test_R09_idle_truncated_tail_recovers_valid_turns_only(self):
        self.fixtures()
        path=self.path().with_name('crashed.jsonl')
        path.write_text(json.dumps({'type':'user','sessionId':'crashed','timestamp':'2026-10-26T10:00:00Z','message':{'role':'user','content':'Important decision before the crash'}})+'\n{"partial":')
        old=time.time()-capture.CRASH_TAIL_SECONDS-10
        os.utime(path,(old,old))
        report=capture.capture(self.conn)
        self.assertFalse(report['failures'])
        self.assertTrue(report['warnings'])
        self.assertTrue(search.search(self.conn,'Important decision'))
        self.assertTrue(status.status(self.conn)['healthy'])
        valid=json.dumps({'type':'user','sessionId':'crashed','message':{'role':'user','content':'A decision before a split UTF8 tail'}}).encode()+b'\n'
        path.write_bytes(valid+b'{"message":"'+bytes([240,159]))
        os.utime(path,(old,old))
        self.assertFalse(capture.capture(self.conn)['failures'])
        self.assertTrue(search.search(self.conn,'split UTF8 tail'))
        path.write_text('{"bad":\n'+json.dumps({'type':'user','message':{'role':'user','content':'Never mark this complete'}})+'\n')
        os.utime(path,(old,old))
        self.assertTrue(capture.capture(self.conn)['failures'])
        self.assertFalse(search.search(self.conn,'Never mark this complete'))

    def test_R10_cursor_embedded_time_and_touch_do_not_change_messages(self):
        self.fixtures()
        path=self.home/'.cursor/projects/fictional/agent-transcripts/real-shape.jsonl'
        rows=[{'role':'user','message':{'content':[{'type':'text','text':'<timestamp>Monday, Aug 24, 2026, 7:45 AM (UTC+2)</timestamp>\n<user_query>Search brain for Buzz</user_query>'}]}},
              {'role':'assistant','message':{'content':[{'type':'text','text':'Looking it up.'}]}},{'type':'turn_ended','status':'success'}]
        path.write_text('\n'.join(json.dumps(row) for row in rows))
        capture.capture(self.conn)
        self.assertEqual(search.search(self.conn,'Buzz')[0]['timestamp'],1787550300)
        os.utime(path,(time.time()+60,time.time()+60))
        capture.capture(self.conn)
        self.assertTrue(status.status(self.conn)['healthy'])
        text=path.with_name('plain.txt');text.write_text('user:\nA navy page\nassistant:\nA cream page\n')
        capture.capture(self.conn);os.utime(text,(time.time()+60,time.time()+60))
        capture.capture(self.conn)
        self.assertTrue(status.status(self.conn)['healthy'])

    def test_R11_credentials_redacted_before_store_search_read_and_sync(self):
        self.fixtures()
        secrets=['sk-proj-'+('A1'*20),'ghp_'+('B2'*16),'eyJabcdefghi.abcdefghijkl.abcdefghijklm']
        body='Use navy paint. '+ ' '.join(secrets)+'\nTURSO_TOKEN=fictional-private-value\npassword: "fictional-password"\nWe should discuss password rotation.'
        self.append(body);capture.capture(self.conn)
        ref=search.search(self.conn,'navy paint')[0]['ref']
        text=search.read(self.conn,ref)['text']
        for secret in secrets+['fictional-private-value','fictional-password']:
            self.assertNotIn(secret,text)
        self.assertIn('[REDACTED]',text)
        self.assertIn('discuss password rotation',text)
        self.assertFalse(search.search(self.conn,'fictional private value'))
        remote=FakePrimary();sync.synchronise(self.conn,remote)
        payload=''.join(r['payload'] for r in remote.query('SELECT payload FROM aios_brain_bundles_v1'))
        self.assertTrue(all(secret not in payload for secret in secrets))
        # The same storage boundary covers transcripts and generated digests.
        value=db.bundle(self.conn,ref);value['documents'].append({'id':ref+':private','ref':ref,'kind':'digest','role':'digest','body':'api_key="'+secrets[0]+'"','ts':0})
        db.put_item(self.conn,value['item'],value['documents'])
        self.assertNotIn(secrets[0],db.serialise(db.bundle(self.conn,ref)))

    def test_R11_upgrade_scrubs_prior_local_rows_and_fts(self):
        self.fixtures()
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        secret='sk-proj-'+('C3'*20)
        with self.conn:
            self.conn.execute('UPDATE documents SET body=? WHERE ref=?',(secret,ref))
            self.conn.execute('UPDATE items SET digest=?,title=? WHERE ref=?',(json.dumps({'token':secret}),secret,ref))
            self.conn.execute("DELETE FROM meta WHERE key='redaction_version'")
        with db.database() as upgraded:
            value=db.bundle(upgraded,ref)
            self.assertNotIn(secret,db.serialise(value))
            json.loads(value['item']['digest'])
            self.assertFalse(search.search(upgraded,secret))

    def test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version(self):
        self.fixtures()
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        remote=FakePrimary();sync.synchronise(self.conn,remote)
        value=db.bundle(self.conn,ref)
        secret='ghp_'+('D4'*20)
        value['item']['updated']+=3600
        value['documents'][0]['body']='A captured key: '+secret
        raw=db.serialise(value)
        with remote.conn:
            remote.conn.execute('UPDATE aios_brain_bundles_v1 SET payload=?,sha256=?,updated=? WHERE ref=?',(raw,sync.sha(raw),value['item']['updated'],ref))
        sync.synchronise(self.conn,remote)
        self.assertNotIn(secret,db.serialise(db.bundle(self.conn,ref)))
        self.assertNotIn(secret,remote.query('SELECT payload FROM aios_brain_bundles_v1 WHERE ref=?',(ref,))[0]['payload'])
        self.assertTrue(sync.health(self.conn,remote)['healthy'])
        self.append('A turn after the future-version redaction')
        capture.capture(self.conn);sync.synchronise(self.conn,remote)
        self.assertIn('after the future-version',remote.query('SELECT payload FROM aios_brain_bundles_v1 WHERE ref=?',(ref,))[0]['payload'])

    def test_R12_malformed_token_and_header_exception_never_leak(self):
        bad='SECRETPART1\nSECRETPART2'
        with patch.dict(os.environ,{'AIOS_BRAIN_TURSO_URL':'https://127.0.0.1:9','AIOS_BRAIN_TURSO_TOKEN':bad}):
            code,out,err=self.cli(['sync'])
            self.assertEqual(code,1)
            self.assertNotIn('SECRETPART',out+err)
        client=sync.HTTP('https://example.turso.io','fictional-good')
        with patch('urllib.request.OpenerDirector.open',side_effect=ValueError('Invalid header b"Bearer SECRETPART1\\nSECRETPART2"')):
            with self.assertRaises(ValueError) as caught:
                client.query('SELECT 1')
        self.assertNotIn('SECRETPART',str(caught.exception))
        self.assertNotIn('SECRETPART',db.serialise(status.status(self.conn)))
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO failures VALUES('sync',?,?)",('Invalid header value b\'Bearer SECRETPART1\\nSECRETPART2\'',time.time()))
            self.conn.execute("DELETE FROM meta WHERE key='redaction_version'")
        with db.database() as upgraded:
            self.assertNotIn('SECRETPART',db.serialise(status.status(upgraded)))

    def test_R12_subprocesses_get_only_needed_credentials(self):
        self.fixtures()
        ref=search.search(self.conn,'Lighthouse')[0]['ref']
        login=subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True,'authMethod':'claude.ai'}),'')
        output=subprocess.CompletedProcess([],0,json.dumps({'result':json.dumps({'title':'Budget','summary':'Saved','questions':[],'atoms':[]})}),'')
        env={'AIOS_BRAIN_TURSO_TOKEN':'fictional-turso-secret','SUPADATA_API_KEY':'fictional-supadata-secret','ANTHROPIC_API_KEY':'fictional-api-secret'}
        with patch.dict(os.environ,env),patch.object(digest.shutil,'which',return_value='/tmp/claude'),patch.object(digest.subprocess,'run',side_effect=[login,output]) as run:
            digest.make(self.conn,ref)
            for item in run.call_args_list:
                self.assertTrue(set(env).isdisjoint(item.kwargs['env']))
        with patch.dict(os.environ,env),patch.object(media.shutil,'which',return_value='/tmp/yt-dlp'),patch.object(media.subprocess,'run',side_effect=subprocess.TimeoutExpired('yt-dlp',120)) as run:
            with self.assertRaises(subprocess.TimeoutExpired):
                media.captions('https://youtu.be/abcdefghijk')
            self.assertTrue(set(env).isdisjoint(run.call_args.kwargs['env']))

    def test_R13_retention_warning_arrives_before_custom_cleanup(self):
        self.fixtures()
        folder=capture.config_dirs()['claude'];(folder/'settings.json').write_text('{"cleanupPeriodDays":7}')
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO meta VALUES("last_capture",?)',(str(time.time()-5*86400),))
        report=status.status(self.conn)
        self.assertTrue(any('days left' in w and '7-day' in w for w in report['warnings']))
        self.assertTrue(any('retention is 7 days' in w for w in report['warnings']))

    def test_R14_unchanged_large_file_is_hashed_streaming_without_parsing(self):
        self.fixtures()
        path=self.path().with_name('large.jsonl')
        line=json.dumps({'type':'assistant','sessionId':'large','timestamp':'2026-10-26T10:00:00Z','message':{'role':'assistant','content':'x'*4096}})+'\n'
        with path.open('w') as stream:
            for _ in range(4096):
                stream.write(line)
        capture.capture(self.conn)
        tracemalloc.start()
        try:
            with patch.object(capture.Session,'turns',side_effect=AssertionError('Unchanged file must not be parsed')),patch.object(Path,'read_bytes',side_effect=AssertionError('No whole-file read')):
                self.assertTrue(status.status(self.conn)['healthy'])
            peak=tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertLess(peak,8*1024*1024)

    def test_R14_unknown_timestamps_still_skip_unchanged_cursor_json(self):
        self.fixtures()
        path=self.home/'.cursor/projects/fictional/agent-transcripts/no-clock.jsonl'
        path.write_text(json.dumps({'role':'user','message':{'content':'A message without any timestamp'}})+'\n')
        capture.capture(self.conn)
        with patch.object(capture.Session,'turns',side_effect=AssertionError('Unchanged clockless file must not be parsed')):
            self.assertTrue(status.status(self.conn)['healthy'])
            self.assertEqual(capture.capture(self.conn)['captured'],0)

    def test_R15_user_prompt_examples_survive_harness_scoped_cleaning(self):
        text='Rewrite my prompt: <instructions>Prepare the Q3 board pack</instructions> and keep <timestamp>yesterday</timestamp> as an example.\n[Thinking] is a heading in my document.'
        for source in capture.SOURCES:
            self.assertEqual(capture.clean(text,source),text)
        self.assertEqual(capture.clean('<system-reminder>Injected</system-reminder>Real task','claude'),'Real task')
        self.assertEqual(capture.clean('Answer\n[Tool call] Shell\nnoise','cursor',text_export=True),'Answer')

    def test_R16_concurrent_config_edit_aborts_without_losing_it(self):
        with redirect_stdout(io.StringIO()):
            installer.install('aios')
        codex=self.home/'.codex/config.toml';codex.write_text('model="initial"\n')
        cursor=self.home/'.cursor/mcp.json';cursor.write_text('{}')
        snapshot=installer.snapshot
        def competing(path):
            if path==cursor:
                codex.write_text('model="new concurrent choice"\n')
            return snapshot(path)
        with patch.object(installer,'snapshot',side_effect=competing),self.assertRaisesRegex(ValueError,'changed during install'):
            installer.install('aios-brain')
        self.assertEqual(codex.read_text(),'model="new concurrent choice"\n')
        self.assertEqual(cursor.read_text(),'{}')
        self.assertFalse((self.home/'.local/bin/brain').exists())
