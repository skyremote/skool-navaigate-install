"""Fetch YouTube captions, using a paid fallback only with the user's own key."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import textwrap
import time
import urllib.parse
import urllib.request
from pathlib import Path
from . import db


def canonical_url(url):
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or '').lower()
    if parsed.scheme != 'https' or parsed.username:
        raise ValueError('Use an HTTPS YouTube video URL')
    if host in ('youtube.com','www.youtube.com','m.youtube.com'):
        video = urllib.parse.parse_qs(parsed.query).get('v',[''])[0]
        if parsed.path.startswith(('/shorts/','/embed/')):
            video = parsed.path.split('/')[2]
    elif host == 'youtu.be':
        video = parsed.path.strip('/')
    else:
        raise ValueError('Phase 1 supports YouTube video URLs')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video):
        raise ValueError('Use one YouTube video URL, not a channel or playlist')
    return 'https://www.youtube.com/watch?v='+video,video


def captions(url):
    binary = shutil.which('yt-dlp')
    if not binary:
        raise ValueError('yt-dlp is not installed. Install yt-dlp, or set your own SUPADATA_API_KEY.')
    with tempfile.TemporaryDirectory(prefix='aios-captions-') as folder:
        proc = subprocess.run([binary,'--ignore-config','--skip-download','--no-playlist','--write-subs',
            '--write-auto-subs','--sub-langs','en.*,en','--sub-format','json3','--dump-single-json',
            '-o',str(Path(folder)/'video.%(ext)s'),'--',url],capture_output=True,text=True,timeout=120)
        paths = sorted(Path(folder).glob('*.json3'))
        # Read the caption output as well as checking the exit code.
        if proc.returncode or not paths:
            raise ValueError('yt-dlp returned no readable English captions')
        data = json.loads(paths[0].read_text())
        lines, previous = [],''
        for event in data.get('events',[]):
            text = ''.join(s.get('utf8','') for s in event.get('segs',[])).strip()
            if text and text != previous:
                lines.append(text)
                previous = text
        body = re.sub(r'\s+',' ',' '.join(lines)).strip()
        if not body:
            raise ValueError('Caption file has no words')
        meta = json.loads(proc.stdout)
        return body,meta.get('title') or 'YouTube video'


def supadata(url,key):
    def get(path):
        req = urllib.request.Request('https://api.supadata.ai/v1'+path,headers={'x-api-key':key})
        try:
            with urllib.request.urlopen(req,timeout=30) as response:
                return json.load(response)
        except (OSError,ValueError):
            raise ValueError('Supadata request failed; check your own key and quota') from None
    result = get('/transcript?'+urllib.parse.urlencode({'url':url,'text':'true','lang':'en'}))
    if result.get('jobId'):
        job = urllib.parse.quote(str(result['jobId']),safe='')
        for _ in range(20):
            time.sleep(3)
            result = get('/transcript/'+job)
            if result.get('status') in ('failed','error'):
                raise ValueError('Supadata could not transcribe this video')
            if result.get('content'):
                break
    content = result.get('content')
    if isinstance(content,list):
        content = ' '.join(str(p.get('text','')) for p in content)
    if not isinstance(content,str) or not content.strip():
        raise ValueError('Supadata returned no transcript')
    return content.strip(),'YouTube video'


def add(conn,url,config,refresh=False):
    url,video = canonical_url(url)
    ref = 'youtube:'+video
    old = conn.execute('SELECT ref FROM items WHERE ref=?',(ref,)).fetchone()
    if old and not refresh:
        return {'ref':ref,'stored':False,'note':'Already captured; use brain read '+ref}
    try:
        body,title = captions(url)
        via = 'yt-dlp'
    except (ValueError,OSError,subprocess.TimeoutExpired):
        key = config.get('SUPADATA_API_KEY')
        if not key:
            raise ValueError('Free captions unavailable. Install yt-dlp or set your own SUPADATA_API_KEY to opt into paid transcription.') from None
        body,title = supadata(url,key)
        via = 'supadata'
    now = time.time()
    item = {'ref':ref,'source':'youtube','device':db.device(conn),'path':None,
            'file_hash':hashlib.sha256(body.encode()).hexdigest(),'modified':now,'latest':now,
            'updated':now,'title':title,'url':url,'digest':None}
    # Small chunks make search hits useful without cutting up the stored transcript.
    chunks = textwrap.wrap(body,width=1800,break_long_words=False,break_on_hyphens=False)
    documents = [{'id':f'{ref}:{i:08d}','ref':ref,'kind':'transcript','role':'transcript','body':p,'ts':now} for i,p in enumerate(chunks)]
    db.put_item(conn,item,documents)
    return {'ref':ref,'stored':True,'via':via,'title':title,'characters':len(body),'digest':'off; run brain digest '+ref+' to opt in'}
