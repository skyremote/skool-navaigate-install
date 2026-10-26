"""Optional Turso HTTP sync, with checked transactions and full content read-back.

The primary holds one atomic bundle per session/media item. Its completed hash
is written only after its message payload. No embedded replica or Turso CLI.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from . import db

REMOTE_SCHEMA = '''CREATE TABLE IF NOT EXISTS aios_brain_bundles_v1(
 ref TEXT PRIMARY KEY,payload TEXT NOT NULL,sha256 TEXT NOT NULL,updated REAL NOT NULL)'''


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def encode(value):
    if value is None:
        return {'type':'null'}
    if isinstance(value,int):
        return {'type':'integer','value':str(value)}
    if isinstance(value,float):
        return {'type':'float','value':value}
    return {'type':'text','value':str(value)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Turso redirect rejected; use the direct database URL')


class HTTP:
    def __init__(self,url,token):
        url = url.replace('libsql://','https://',1)
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.query or parsed.fragment:
            raise ValueError('Turso requires your own HTTPS or libsql database URL')
        self.url,self.token = url.rstrip('/')+'/v2/pipeline',token

    def post(self,request):
        try:
            req = urllib.request.Request(self.url,json.dumps({'baton':None,'requests':[request,{'type':'close'}]}).encode(),
                  {'Content-Type':'application/json','Authorization':'Bearer '+self.token},method='POST')
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=10) as response:
                data=json.load(response)
            result=data['results'][0]
            if result['type']!='ok':
                raise ValueError('request rejected')
            return result['response']['result']
        except urllib.error.HTTPError as exc:
            raise ValueError(f'Turso HTTP {exc.code}; no successful sync recorded') from None
        except Exception:
            # Header/transport exceptions can contain the raw bearer token.
            raise ValueError('Turso request failed; check the database URL, token and connection privately') from None

    @staticmethod
    def stmt(sql,args=()):
        return {'sql':sql,'args':[encode(a) for a in args]}

    def query(self,sql,args=()):
        result = self.post({'type':'execute','stmt':self.stmt(sql,args)})
        names = [c['name'] for c in result['cols']]
        def decode(cell):
            if cell['type']=='null':
                return None
            value = cell.get('value')
            return int(value) if cell['type']=='integer' else float(value) if cell['type']=='float' else value
        return [dict(zip(names,[decode(c) for c in row])) for row in result['rows']]

    def transaction(self,statements):
        steps = [{'stmt':self.stmt('BEGIN IMMEDIATE')}]
        for sql,args in statements:
            steps.append({'condition':{'type':'ok','step':len(steps)-1},'stmt':self.stmt(sql,args)})
        commit = len(steps)
        steps.append({'condition':{'type':'ok','step':commit-1},'stmt':self.stmt('COMMIT')})
        steps.append({'condition':{'type':'not','cond':{'type':'ok','step':commit}},'stmt':self.stmt('ROLLBACK')})
        result = self.post({'type':'batch','batch':{'steps':steps}})
        if any(result.get('step_errors',[])[:commit+1]) or len(result.get('step_results',[]))<=commit or result['step_results'][commit] is None:
            raise ValueError('Turso transaction did not commit; no successful sync recorded')


def verified(row):
    if row['sha256']=='pending' or sha(row['payload']) != row['sha256']:
        raise ValueError('Turso payload read-back failed')
    payload = json.loads(row['payload'])
    if payload['item']['ref'] != row['ref'] or payload['item']['updated'] != row['updated']:
        raise ValueError('Turso bundle identity read-back failed')
    # Never accept documents filed under a different ref.
    if any(d['ref'] != row['ref'] for d in payload['documents']):
        raise ValueError('Turso document identity mismatch')
    return payload


def headers(client):
    """Bound each response and never fetch a catalogue of transcript payloads."""
    found,last={},''
    while True:
        page=client.query('SELECT ref,updated,sha256 FROM aios_brain_bundles_v1 WHERE ref>? ORDER BY ref LIMIT 128',(last,))
        for row in page:
            found[row['ref']]=row
        if len(page)<128:
            return found
        last=page[-1]['ref']


def fetch_bundle(client,ref):
    rows=client.query('SELECT ref,updated,sha256,length(payload) AS chars FROM aios_brain_bundles_v1 WHERE ref=?',(ref,))
    if not rows:
        raise ValueError('Turso write missing on read-back')
    row=rows[0]
    parts=[]
    # Even one long session must not exceed the service response cap.
    for start in range(0,row['chars'],100000):
        chunk=client.query('SELECT substr(payload,?,?) AS part FROM aios_brain_bundles_v1 WHERE ref=? AND sha256=? AND updated=?',
                           (start+1,100000,ref,row['sha256'],row['updated']))
        if not chunk or not chunk[0]['part']:
            raise ValueError('Turso bundle changed during read-back; retry sync')
        parts.append(chunk[0]['part'])
    row['payload']=''.join(parts)
    verified(row)
    return row


def push(conn,client,ref):
    bundle=db.bundle(conn,ref)
    value=db.serialise(bundle)
    digest=sha(value)
    updated=bundle['item']['updated']
    client.transaction([
        ('INSERT OR IGNORE INTO aios_brain_bundles_v1 VALUES(?,?,?,?)',(ref,'','pending',0)),
        ('UPDATE aios_brain_bundles_v1 SET payload=?,sha256=\'pending\',updated=? WHERE ref=? AND updated<?',(value,updated,ref,updated)),
        ('UPDATE aios_brain_bundles_v1 SET sha256=? WHERE ref=? AND payload=? AND updated=?',(digest,ref,value,updated))])
    back=fetch_bundle(client,ref)
    if back['sha256']!=digest and back['updated']<=updated:
        raise ValueError('Turso hash differs after write')


def synchronise(conn,client):
    client.transaction([(REMOTE_SCHEMA,())])
    remote=headers(client)
    uploaded,downloaded=0,0
    for row in conn.execute('SELECT ref,updated FROM items').fetchall():
        other=remote.get(row['ref'])
        if not other or other['updated']<row['updated']:
            push(conn,client,row['ref'])
            uploaded+=1
    for ref,row in headers(client).items():
        local=conn.execute('SELECT updated FROM items WHERE ref=?',(ref,)).fetchone()
        if not local or local['updated']<row['updated']:
            fetched=fetch_bundle(client,ref)
            payload=verified(fetched)
            db.put_item(conn,payload['item'],payload['documents'])
            downloaded+=1
            # Redaction is enforced on incoming data too. Upgrade old unsafe bundles.
            if sha(db.serialise(db.bundle(conn,ref)))!=fetched['sha256']:
                with conn:
                    conn.execute('UPDATE items SET updated=? WHERE ref=?',(max(time.time(),fetched['updated']+0.000001),ref))
                push(conn,client,ref)
                uploaded+=1
        elif local['updated']==row['updated'] and sha(db.serialise(db.bundle(conn,ref)))!=row['sha256']:
            raise ValueError('Local and Turso content differ at the same version')
    return {'uploaded':uploaded,'downloaded':downloaded,'verified':True}


def health(conn,client):
    there=headers(client)
    have={row['ref']:sha(db.serialise(db.bundle(conn,row['ref']))) for row in conn.execute('SELECT ref FROM items')}
    mismatches=sorted(ref for ref in have.keys()|there.keys() if have.get(ref)!=there.get(ref,{}).get('sha256'))
    return {'healthy':not mismatches,'mismatched_refs':mismatches,'remote_items':len(there)}
