"""Optional Turso HTTP sync, with checked transactions and full content read-back.

The primary holds one atomic bundle per session/media item. Its completed hash
is written only after its message payload. No embedded replica or Turso CLI.
"""
import hashlib
import json
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
        req = urllib.request.Request(self.url,json.dumps({'baton':None,'requests':[request,{'type':'close'}]}).encode(),
              {'Content-Type':'application/json','Authorization':'Bearer '+self.token},method='POST')
        try:
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
                data = json.load(response)
            result = data['results'][0]
            if result['type'] != 'ok':
                raise ValueError('Turso rejected the request; check the database and token')
            return result['response']['result']
        except urllib.error.HTTPError as exc:
            raise ValueError(f'Turso HTTP {exc.code}; no successful sync recorded') from None
        except (OSError,KeyError,IndexError,TypeError,json.JSONDecodeError):
            raise ValueError('Turso response missing or unreadable; no successful sync recorded') from None

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


def synchronise(conn,client):
    client.transaction([(REMOTE_SCHEMA,())])
    remote = {r['ref']:r for r in client.query('SELECT * FROM aios_brain_bundles_v1')}
    uploaded,downloaded = 0,0
    for row in conn.execute('SELECT ref,updated FROM items').fetchall():
        ref = row['ref']
        if ref in remote and remote[ref]['updated'] >= row['updated']:
            continue
        value = db.serialise(db.bundle(conn,ref))
        digest = sha(value)
        # A failed write cannot leave the completed hash beside missing messages.
        client.transaction([
            ('INSERT OR IGNORE INTO aios_brain_bundles_v1 VALUES(?,?,?,?)',(ref,'','pending',0)),
            ('UPDATE aios_brain_bundles_v1 SET payload=?,sha256=\'pending\',updated=? WHERE ref=? AND updated<?',
             (value,row['updated'],ref,row['updated'])),
            ('UPDATE aios_brain_bundles_v1 SET sha256=? WHERE ref=? AND payload=? AND updated=?',
             (digest,ref,value,row['updated']))])
        back = client.query('SELECT * FROM aios_brain_bundles_v1 WHERE ref=?',(ref,))
        if not back:
            raise ValueError('Turso write missing on read-back')
        verified(back[0])
        if back[0]['sha256'] != digest and back[0]['updated'] <= row['updated']:
            raise ValueError('Turso hash differs after write')
        uploaded += 1
    for row in client.query('SELECT * FROM aios_brain_bundles_v1'):
        payload = verified(row)
        local = conn.execute('SELECT updated FROM items WHERE ref=?',(row['ref'],)).fetchone()
        if not local or local['updated'] < row['updated']:
            db.put_item(conn,payload['item'],payload['documents'])
            downloaded += 1
        elif local['updated'] == row['updated'] and sha(db.serialise(db.bundle(conn,row['ref']))) != row['sha256']:
            raise ValueError('Local and Turso content differ at the same version')
    return {'uploaded':uploaded,'downloaded':downloaded,'verified':True}


def health(conn,client):
    remote = client.query('SELECT * FROM aios_brain_bundles_v1')
    have = {r['ref']:sha(db.serialise(db.bundle(conn,r['ref']))) for r in conn.execute('SELECT ref FROM items')}
    there = {}
    for row in remote:
        verified(row)
        there[row['ref']] = row['sha256']
    mismatches = sorted(ref for ref in have.keys() | there.keys() if have.get(ref)!=there.get(ref))
    return {'healthy':not mismatches,'mismatched_refs':mismatches,'remote_items':len(remote)}
