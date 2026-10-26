import argparse
import json
import sqlite3
import subprocess
import sys
import time
from . import capture, config, db, digest, media, search, status, sync
from .errors import InputError
from .privacy import redact


def sync_if_configured(conn,values):
    if not values['AIOS_BRAIN_TURSO_URL']:
        return {'mode':'local','network':'off'}
    try:
        result = sync.synchronise(conn,sync.HTTP(values['AIOS_BRAIN_TURSO_URL'],values['AIOS_BRAIN_TURSO_TOKEN']))
        db.clear_failure(conn,'sync')
        return {'mode':'turso',**result}
    except (ValueError,OSError) as exc:
        db.failure(conn,'sync',str(exc))
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(prog='brain',description='Your private memory. Local by default.')
    commands = parser.add_subparsers(dest='command',required=True)
    commands.add_parser('init',help='Create your local SQLite file; no account needed')
    commands.add_parser('capture',help='Capture new or changed Claude Code, Codex and Cursor sessions')
    commands.add_parser('status',help='Check the data; exit 1 if capture or sync is unhealthy')
    commands.add_parser('sync',help='Exchange data with your own optional Turso database')
    find = commands.add_parser('search')
    find.add_argument('query')
    find.add_argument('--limit',type=int,default=8)
    find.add_argument('--no-recency',action='store_true')
    find.add_argument('--half-life-days',type=float,default=30)
    read = commands.add_parser('read')
    read.add_argument('ref')
    read.add_argument('--start',type=int,default=0)
    read.add_argument('--max-chars',type=int,default=12000)
    summarise = commands.add_parser('digest',help='Opt into Haiku on your own Claude subscription')
    summarise.add_argument('ref')
    medias = commands.add_parser('media').add_subparsers(dest='action',required=True)
    add = medias.add_parser('add')
    add.add_argument('url')
    add.add_argument('--refresh',action='store_true')
    failures=commands.add_parser('failures',help='List or acknowledge operational failures; never deletes data')
    actions=failures.add_subparsers(dest='failure_action',required=True)
    actions.add_parser('list')
    clear=actions.add_parser('clear')
    group=clear.add_mutually_exclusive_group(required=True)
    group.add_argument('--scope')
    group.add_argument('--all',action='store_true')
    commands.add_parser('mcp',help='Run the stdio MCP server')
    args = parser.parse_args(argv)
    if args.command=='mcp':
        from .mcp_server import serve
        serve()
        return 0
    try:
        values = config.load() if args.command not in ('search','read','failures') else {}
        with db.database(create=args.command=='init') as conn:
            code = 0
            if args.command=='init':
                result = {'initialised':True,'database':str(db.data_path()),'mode':'turso configured; run brain sync' if values['AIOS_BRAIN_TURSO_URL'] else 'local; no account needed'}
            elif args.command=='capture':
                result = capture.capture(conn)
                if result['failures']:
                    code = 1
                elif result['captured'] or result['unchanged']:
                    with conn:
                        conn.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('last_capture',str(time.time())))
                result['sync'] = sync_if_configured(conn,values)
            elif args.command=='search':
                result = {'hits':search.search(conn,args.query,args.limit,not args.no_recency,args.half_life_days)}
            elif args.command=='read':
                result = search.read(conn,args.ref,args.start,args.max_chars)
            elif args.command=='status':
                result = status.status(conn)
                result['mode'] = 'local'
                if values['AIOS_BRAIN_TURSO_URL']:
                    result['mode'] = 'turso'
                    try:
                        result['sync'] = sync.health(conn,sync.HTTP(values['AIOS_BRAIN_TURSO_URL'],values['AIOS_BRAIN_TURSO_TOKEN']))
                        result['healthy'] = result['healthy'] and result['sync']['healthy']
                    except (ValueError,OSError):
                        result['healthy'] = False
                        result['problems'].append('Turso health check failed; run brain sync and check your configuration')
                code = 0 if result['healthy'] else 1
            elif args.command=='sync':
                result = sync_if_configured(conn,values)
            elif args.command=='failures':
                db.prune_failures(conn)
                if args.failure_action=='clear':
                    with conn:
                        cur=conn.execute('DELETE FROM failures' if args.all else 'DELETE FROM failures WHERE scope=?',() if args.all else (args.scope,))
                    result={'acknowledged':cur.rowcount,'note':'Session and remote health are still checked; no captured data was deleted'}
                else:
                    result={'failures':[dict(row) for row in conn.execute('SELECT * FROM failures ORDER BY at')]}
            elif args.command in ('media','digest'):
                if args.command=='digest':
                    db.bundle(conn,args.ref)
                    scope='digest:'+args.ref
                else:
                    scope='media:'+media.canonical_url(args.url)[0]
                try:
                    result = digest.make(conn,args.ref) if args.command=='digest' else media.add(conn,args.url,values,args.refresh)
                    db.clear_failure(conn,scope)
                except InputError:
                    raise
                except (ValueError,OSError,subprocess.TimeoutExpired):
                    db.failure(conn,scope,args.command+' failed; retry the same command after fixing its reported cause')
                    raise
                result['sync'] = {'note':'Run brain sync to exchange data'}
            print(json.dumps(result,ensure_ascii=False,indent=2))
            return code
    except (ValueError,OSError,sqlite3.Error,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'error':redact(str(exc))},ensure_ascii=False),file=sys.stderr)
        return 1
