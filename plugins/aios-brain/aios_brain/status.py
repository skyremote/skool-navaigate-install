"""Health measures the data and failures, never a last-ran heartbeat."""
import time
from . import capture, db


def status(conn):
    problems, pending, newest_file, newest_message = [],[],None,None
    device = db.device(conn)
    try:
        candidates = list(capture.files())
    except OSError:
        candidates = []
        problems.append('Cannot inspect session folders; check permissions')
    for source,path in candidates:
        try:
            raw,digest,modified = capture.snapshot(path)
            sid,messages = capture.parse(source,path,raw,modified)
            if sid is None:
                continue
            if newest_file is None or modified > newest_file['modified']:
                newest_file = {'name':path.name,'modified':modified}
            row = conn.execute('SELECT * FROM items WHERE device=? AND path=?',(device,str(path))).fetchone()
            expected_latest = max((m[2] for m in messages),default=None)
            if expected_latest is not None:
                newest_message = max(newest_message or 0,expected_latest)
            if row is None or row['file_hash'] != digest:
                pending.append(path.name)
                continue
            stored = conn.execute("SELECT role,body,ts FROM documents WHERE ref=? AND kind='message' ORDER BY id",(row['ref'],)).fetchall()
            if [tuple(d) for d in stored] != messages:
                problems.append(path.name+': stored messages differ from the session')
        except (OSError,ValueError,UnicodeError) as exc:
            problems.append(f'{path.name}: {exc}')
    failures = [dict(r) for r in conn.execute('SELECT * FROM failures ORDER BY at')]
    if pending:
        problems.append(f'{len(pending)} session file(s) not captured; run brain capture')
    stored_latest = conn.execute("SELECT max(ts) FROM documents d JOIN items i ON i.ref=d.ref WHERE kind='message' AND i.device=?",(device,)).fetchone()[0]
    all_latest = conn.execute("SELECT max(ts) FROM documents WHERE kind='message'").fetchone()[0]
    if newest_message and (stored_latest is None or stored_latest < newest_message):
        problems.append('Newest stored message is behind the newest session message')
    # Retention matters even if the last run returned zero.
    warnings = ['Claude Code deletes session files after 30 days. Capture regularly; keep your database off cloud-sync folders.']
    last_capture = conn.execute("SELECT value FROM meta WHERE key='last_capture'").fetchone()
    if not last_capture or time.time()-float(last_capture[0]) > 30*86400:
        warnings.append('No verified capture in the last 30 days. Session history may already be missing.')
    if not candidates:
        warnings.append('No session files found. This does not prove that any history has been captured.')
    return {'healthy':not problems and not failures,'session_files':len(candidates),
            'newest_session_file':newest_file,'newest_session_message':newest_message,
            'newest_stored_message':stored_latest,'newest_message_all_machines':all_latest,
            'pending_files':pending,'problems':problems,'failures':failures,'warnings':warnings}
