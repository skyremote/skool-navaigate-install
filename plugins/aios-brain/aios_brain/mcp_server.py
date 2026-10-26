"""Small stdio MCP server. Stdlib only; no installation-time network fetches."""
import json
import sys
from . import config, db, media, search
from .errors import InputError
from .privacy import redact

TOOLS = [
 {'name':'brain_search','description':'Search your captured messages, digests and video captions using BM25 and recency. Returns refs for brain_read.',
  'inputSchema':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':50},'recency':{'type':'boolean'}},'required':['query'],'additionalProperties':False}},
 {'name':'brain_read','description':'Open a search ref. Long items return next_start; pass it as start for the next part.',
  'inputSchema':{'type':'object','properties':{'ref':{'type':'string'},'start':{'type':'integer','minimum':0},'max_chars':{'type':'integer','minimum':1,'maximum':60000}},'required':['ref'],'additionalProperties':False}},
 {'name':'brain_media_add','description':'Fetch and store one YouTube transcript. Tries free captions first; paid Supadata only with your own configured key. Does not digest automatically.',
  'inputSchema':{'type':'object','properties':{'url':{'type':'string'},'refresh':{'type':'boolean'}},'required':['url'],'additionalProperties':False}}
]


def call(name,args):
    tool = next((t for t in TOOLS if t['name']==name),None)
    if not tool or not isinstance(args,dict):
        raise ValueError('Unknown tool or invalid arguments')
    schema = tool['inputSchema']
    if set(args)-set(schema['properties']) or set(schema['required'])-set(args):
        raise ValueError('Missing or unknown arguments')
    types = {'string':str,'integer':int,'boolean':bool}
    for key,value in args.items():
        spec = schema['properties'][key]
        if type(value) is not types[spec['type']]:
            raise ValueError('Invalid argument type: '+key)
        if ('minimum' in spec and value<spec['minimum']) or ('maximum' in spec and value>spec['maximum']):
            raise ValueError('Argument out of range: '+key)
    with db.database() as conn:
        if name=='brain_search':
            return {'hits':search.search(conn,**args)}
        if name=='brain_read':
            return search.read(conn,**args)
        values=config.load()
        canonical,_=media.canonical_url(args['url'])
        scope = 'media:'+canonical
        try:
            result = media.add(conn,config=values,**args)
            db.clear_failure(conn,scope)
        except InputError:
            raise
        except (ValueError,OSError):
            db.failure(conn,scope,'media failed; retry after fixing its reported cause')
            raise
        result['sync'] = {'note':'Run brain sync to exchange data; recall stays local'}
        return result


def serve():
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            if not isinstance(request,dict):
                raise ValueError('Expected a JSON-RPC object')
            if 'id' not in request:
                continue
            method = request.get('method')
            if method=='initialize':
                asked = request.get('params',{}).get('protocolVersion')
                version = asked if asked in ('2024-11-05','2025-03-26','2025-06-18') else '2025-06-18'
                result = {'protocolVersion':version,'capabilities':{'tools':{}},'serverInfo':{'name':'aios-brain','version':'2.0.0'}}
            elif method=='ping':
                result = {}
            elif method=='tools/list':
                result = {'tools':TOOLS}
            elif method=='tools/call':
                params = request.get('params',{})
                try:
                    value = call(params.get('name'),params.get('arguments',{}))
                    result = {'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
                except Exception as exc:
                    result = {'isError':True,'content':[{'type':'text','text':redact(str(exc))}]}
            else:
                print(json.dumps({'jsonrpc':'2.0','id':request['id'],'error':{'code':-32601,'message':'Method not found'}}),flush=True)
                continue
            print(json.dumps({'jsonrpc':'2.0','id':request['id'],'result':result}),flush=True)
        except (ValueError,TypeError,KeyError):
            print(json.dumps({'jsonrpc':'2.0','id':request.get('id') if isinstance(request,dict) else None,
                              'error':{'code':-32700,'message':'Invalid JSON-RPC request'}}),flush=True)
