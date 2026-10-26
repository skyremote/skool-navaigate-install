"""Data health, a bounded active-session grace window and early retention warnings."""
import hashlib
import json
from pathlib import Path
import math
import time
from . import capture, db
from .privacy import redact


def retention_days():
    settings=capture.config_dirs()['claude']/'settings.json'
    if settings.exists():
        try:
            value=json.loads(settings.read_text()).get('cleanupPeriodDays',30)
            if isinstance(value,(int,float)) and not isinstance(value,bool) and value>0:
                return float(value)
        except (ValueError,OSError,AttributeError):
            pass
    return 30.0


def within_grace(conn,path,modified):
    if modified<time.time()-capture.ACTIVE_GRACE_SECONDS:
        return False
    with conn:
        conn.execute('INSERT OR IGNORE INTO health_pending VALUES(?,?)',(str(path),min(time.time(),modified)))
    since=conn.execute('SELECT since FROM health_pending WHERE path=?',(str(path),)).fetchone()[0]
    return time.time()-since<capture.ACTIVE_GRACE_SECONDS


def status(conn):
    problems,pending,active,warnings=[],[],[],[]
    active_paths=set()
    newest_file,newest_message=None,None
    device=db.device(conn)
    db.prune_failures(conn)
    counts={source:0 for source in capture.SOURCES}
    try:
        candidates=list(capture.files())
    except OSError:
        candidates=[]
        problems.append('Cannot inspect session folders; check permissions')
    for source,path in candidates:
        counted=False
        try:
            digest,stat=capture.fingerprint(path)
            row=conn.execute('SELECT * FROM items WHERE device=? AND path=?',(device,str(path))).fetchone()
            cache=conn.execute('SELECT * FROM file_state WHERE path=?',(str(path),)).fetchone()
            if newest_file is None or stat.st_mtime>newest_file['modified']:
                newest_file={'name':path.name,'modified':stat.st_mtime}
            if row and cache and (cache['size'],cache['mtime_ns'],cache['file_hash'])==(stat.st_size,stat.st_mtime_ns,digest) and row['file_hash']==digest:
                counts[source]+=1
                counted=True
                if capture.message_hash(capture.stored_turns(conn,row['ref']))!=cache['message_hash']:
                    problems.append(path.name+': stored messages differ from the captured session; run brain capture')
                warnings.extend(json.loads(cache['warnings']))
                newest_message=max(newest_message or 0,row['latest'])
                with conn:
                    conn.execute('DELETE FROM health_pending WHERE path=?',(str(path),))
                continue
            session=capture.Session(source,path,stat.st_mtime)
            stored=iter(capture.stored_turns(conn,row['ref'])) if row else iter(())
            identical,prefix,incomplete=True,True,False
            turn_digest=hashlib.sha256()
            try:
                with (path.open(encoding='utf-8') if path.suffix=='.txt' else path.open('rb')) as stream:
                    for turn in session.turns(stream):
                        turn_digest.update(db.serialise(list(turn)).encode()+b'\n')
                        previous=next(stored,None)
                        if previous is None:
                            identical=False
                        elif previous!=turn:
                            prefix,identical=False,False
            except capture.IncompleteTail:
                incomplete,identical=True,False
            if next(stored,None) is not None:
                prefix,identical=False,False
            if session.subagent:
                continue
            counts[source]+=1
            counted=True
            newest_message=max(newest_message or 0,session.latest)
            warnings.extend(session.warnings)
            if path.stat().st_mtime_ns!=stat.st_mtime_ns or path.stat().st_size!=stat.st_size:
                raise capture.SessionChanged('Session changed during health check; retry')
            if row and row['file_hash']==digest and identical:
                capture.save_state(conn,path,row['ref'],stat,digest,turn_digest.hexdigest(),session.warnings)
                continue
            # Only a captured, append-only session can use the grace window.
            if row and prefix and within_grace(conn,path,stat.st_mtime):
                active.append(path.name)
                active_paths.add(str(path))
                continue
            if row and row['file_hash']==digest and not identical:
                problems.append(path.name+': stored messages differ from the session')
            else:
                pending.append(path.name)
            if incomplete:
                warnings.append(path.name+': incomplete final line; capture recovers valid turns after 5 minutes idle')
        except capture.SessionChanged:
            # A writer can append during the hash/parse itself. Keep the same
            # bounded clock; do not turn a busy captured session permanently red.
            row=conn.execute('SELECT * FROM items WHERE device=? AND path=?',(device,str(path))).fetchone()
            cache=conn.execute('SELECT * FROM file_state WHERE path=?',(str(path),)).fetchone()
            try:
                current=path.stat()
                eligible=row and cache and current.st_size>=cache['size'] and within_grace(conn,path,current.st_mtime)
            except OSError:
                eligible=False
            if not counted:
                counts[source]+=1
            if eligible:
                if newest_file is None or current.st_mtime>newest_file['modified']:
                    newest_file={'name':path.name,'modified':current.st_mtime}
                warnings.append(path.name+': changing during inspection; its newest message timestamp is unverified until capture')
                active.append(path.name)
                active_paths.add(str(path))
            else:
                pending.append(path.name)
        except (OSError,ValueError,UnicodeError) as exc:
            problems.append(redact(f'{path.name}: {exc}'))
    for source in capture.installed_sources():
        if counts[source]==0:
            problems.append(f'{source}: installed harness has zero session files in its configured folders; use the harness or check the folder override')
    if pending:
        problems.append(f'{len(pending)} session file(s) not captured; run brain capture')
    if active:
        warnings.append(f'{len(active)} active session file(s) changed after capture; grace window is {capture.ACTIVE_GRACE_SECONDS} seconds, then status fails until captured')
    failures=[dict(r) for r in conn.execute('SELECT * FROM failures ORDER BY at')
              if not (r['scope'].startswith('capture:') and r['scope'][8:] in active_paths)]
    stored_latest=conn.execute("SELECT max(ts) FROM documents d JOIN items i ON i.ref=d.ref WHERE kind='message' AND i.device=?",(device,)).fetchone()[0]
    all_latest=conn.execute("SELECT max(ts) FROM documents WHERE kind='message'").fetchone()[0]
    days=retention_days()
    warnings.append(f'Claude Code retention is {days:g} days. Capture regularly; keep the database off cloud-sync folders.')
    last=conn.execute("SELECT value FROM meta WHERE key='last_capture'").fetchone()
    if not last:
        warnings.append('No verified capture time recorded yet; run brain capture.')
    else:
        age=max(0,(time.time()-float(last[0]))/86400)
        if age>=days*2/3:
            remaining=max(0,math.floor(days-age))
            warnings.append(f'No verified capture for {age:.1f} days; about {remaining} days left before the {days:g}-day retention window expires.')
    return {'healthy':not problems and not failures,'session_files':sum(counts.values()),
            'files_by_harness':counts,'active_files':active,'active_grace_seconds':capture.ACTIVE_GRACE_SECONDS,
            'newest_session_file':newest_file,'newest_session_message':newest_message,
            'newest_stored_message':stored_latest,'newest_message_all_machines':all_latest,
            'pending_files':pending,'problems':problems,'failures':failures,'warnings':list(dict.fromkeys(warnings))}
