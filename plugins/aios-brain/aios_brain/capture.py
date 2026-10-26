"""Incremental, stable-file capture of human turns, without harness scaffolding."""
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from . import db

SOURCES = ('claude','codex','cursor')
BLOCKS = re.compile(r'<(system-reminder|environment_context|INSTRUCTIONS|instructions|command-name|'
                    r'command-message|command-args|local-command-stdout|local-command-stderr|'
                    r'user-prompt-submit-hook|bash-stdout|bash-stderr|timestamp)>.*?</\1>', re.S | re.I)


def clean(text):
    query = re.search(r'<user_query>(.*?)</user_query>',text,re.S)
    if query:
        text = query.group(1)
    if text.lstrip().startswith('# AGENTS.md instructions'):
        # Instructions can share a turn with the user's real question.
        end = text.rfind('</INSTRUCTIONS>')
        text = text[end + len('</INSTRUCTIONS>'):] if end >= 0 else ''
    text = BLOCKS.sub('',text)
    text = re.split(r'(?m)^\[(?:Tool call|Tool result|Thinking)\]',text,maxsplit=1)[0]
    text = re.sub(r'^Caveat: The messages below were generated.*$', '',text,flags=re.M)
    return text.strip()


def text_blocks(value):
    if isinstance(value,str):
        return value
    if not isinstance(value,list):
        return ''
    return '\n'.join(v.get('text','') for v in value if isinstance(v,dict)
                     and v.get('type') in ('text','input_text','output_text'))


def epoch(value, fallback):
    if isinstance(value,(float,int)):
        return value / 1000 if value > 10**11 else float(value)
    if isinstance(value,str):
        try:
            parsed = datetime.fromisoformat(value.replace('Z','+00:00'))
            return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).timestamp()
        except ValueError:
            pass
    return fallback


def roots():
    home = Path.home()
    return {'claude':[home/'.claude/projects'],
            'codex':[home/'.codex/sessions',home/'.codex/archived_sessions'],
            'cursor':[home/'.cursor/projects']}


def files():
    for source, dirs in roots().items():
        for root in dirs:
            if not root.exists():
                continue
            for path in sorted(root.rglob('*')):
                if not path.is_file() or path.suffix not in ('.jsonl','.txt'):
                    continue
                if source != 'cursor' and path.suffix != '.jsonl':
                    continue
                if source == 'cursor' and 'agent-transcripts' not in path.parts:
                    continue
                if 'subagents' in path.parts or path.name.startswith('agent-'):
                    continue
                yield source,path


def snapshot(path):
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_mtime_ns,before.st_size) != (after.st_mtime_ns,after.st_size):
        raise ValueError('Session changed during capture; retry brain capture')
    return raw,hashlib.sha256(raw).hexdigest(),after.st_mtime


def parse(source, path, raw, modified):
    messages, sid, meta_seen = [],path.stem,False
    text = raw.decode('utf-8')  # Damaged UTF-8 must not get a completed file hash.
    if source == 'cursor' and path.suffix == '.txt':
        for role,body in re.findall(r'(?ms)^(user|assistant):\s*\n(.*?)(?=^(?:user|assistant):\s*\n|\Z)',text):
            body = clean(body)
            if body:
                messages.append((role,body,modified))
        if text.strip() and not messages:
            raise ValueError('Unrecognised Cursor transcript; export as JSONL or role-labelled text')
        return sid,messages
    for n,line in enumerate(text.splitlines(),1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event,dict):
                raise ValueError('Expected an object')
        except ValueError as exc:
            raise ValueError(f'Malformed session JSON at line {n}; retry after the writer finishes') from exc
        msg = None
        ts = epoch(event.get('timestamp'),modified)
        if source == 'codex':
            payload = event.get('payload') or {}
            if not isinstance(payload,dict):
                raise ValueError(f'Malformed Codex event at line {n}')
            if event.get('type') == 'session_meta' and not meta_seen:
                meta_seen = True
                origin = payload.get('source') or {}
                if payload.get('thread_source') == 'subagent' or (
                    isinstance(origin,dict) and 'subagent' in origin):
                    return None,[]
                sid = payload.get('id') or sid
            elif event.get('type') == 'response_item' and payload.get('type') == 'message':
                if payload.get('channel') == 'analysis':
                    continue
                msg = payload
        elif source == 'claude':
            if event.get('isSidechain'):
                continue
            if not meta_seen and event.get('sessionId'):
                sid,meta_seen = event['sessionId'],True
            msg = event.get('message')
        else:
            if event.get('role') in ('user','assistant'):
                nested = event.get('message') or {}
                if not isinstance(nested,dict):
                    raise ValueError(f'Malformed Cursor event at line {n}')
                msg = {'role':event['role'],'content':nested.get('content',event.get('content'))}
        if isinstance(msg,dict) and msg.get('role') in ('user','assistant'):
            body = clean(text_blocks(msg.get('content')))
            if body:
                messages.append((msg['role'],body,ts))
    return str(sid),messages


def capture(conn):
    result = {'captured':0,'unchanged':0,'messages':0,'skipped_subagents':0,'failures':[]}
    local = db.device(conn)
    try:
        candidates = list(files())
    except OSError:
        db.failure(conn,'discovery','Cannot read a session folder; check permissions')
        raise ValueError('Cannot read a session folder; check permissions')
    db.clear_failure(conn,'discovery')
    for source,path in candidates:
        scope = 'capture:' + str(path)
        try:
            raw,digest,modified = snapshot(path)
            old = conn.execute('SELECT * FROM items WHERE device=? AND path=?',(local,str(path))).fetchone()
            if old and old['file_hash'] == digest:
                result['unchanged'] += 1
                db.clear_failure(conn,scope)
                continue
            sid,messages = parse(source,path,raw,modified)
            if sid is None:
                result['skipped_subagents'] += 1
                db.clear_failure(conn,scope)
                continue
            ref = f'{source}:{local}:{sid}'
            if old and old['ref'] != ref:
                raise ValueError('Session identity changed in place; preserve the old file and investigate')
            duplicate = conn.execute('SELECT path FROM items WHERE ref=?',(ref,)).fetchone()
            if duplicate and duplicate['path'] != str(path) and Path(duplicate['path']).exists():
                # An archived and live copy may coexist; never let an older copy overwrite.
                if old is None:
                    raise ValueError('Duplicate session identity in two files; keep one session copy')
            docs = [{'id':f'{ref}:{n:08d}','kind':'message','role':role,'body':body,'ts':ts}
                    for n,(role,body,ts) in enumerate(messages)]
            item = {'ref':ref,'source':source,'device':local,'path':str(path),'file_hash':digest,
                    'modified':modified,'latest':max((m[2] for m in messages),default=modified),
                    'updated':time.time(),'title':'','url':None,'digest':None}
            db.put_item(conn,item,docs)
            db.clear_failure(conn,scope)
            result['captured'] += 1
            result['messages'] += len(messages)
        except (OSError,ValueError,UnicodeError) as exc:
            error = f'{path.name}: {exc}'
            db.failure(conn,scope,error)
            result['failures'].append(error)
    return result
