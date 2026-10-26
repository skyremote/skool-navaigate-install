"""A small stdio MCP server, so Claude Code passes the member's Granola key from the plugin settings."""
import json
import sys

from . import __version__, granola

TOOLS = [
    {'name': 'meetings_list', 'description': 'List recent Granola meetings (date, title, id). Optional title filter.',
     'inputSchema': {'type': 'object', 'properties': {'n': {'type': 'integer', 'default': 25},
                                                      'query': {'type': 'string'}}}},
    {'name': 'meetings_transcript', 'description': 'The words said in one Granola meeting, as labelled turns.',
     'inputSchema': {'type': 'object', 'required': ['id'], 'properties': {'id': {'type': 'string'},
                                                                          'me': {'type': 'string', 'default': 'Me'}}}},
]


def call(name, args, key=None, get=None):
    key = key or granola.api_key()
    get = get or granola.fetch
    if name == 'meetings_list':
        notes = granola.list_notes(int(args.get('n') or 25), key, get=get)
        query = (args.get('query') or '').lower()
        rows = ['%s  %s  [%s]' % (granola.date_of(n), granola.title_of(n), n.get('id', ''))
                for n in notes if query in granola.title_of(n).lower()]
        return '\n'.join(rows) or 'No meetings matched.'
    if name == 'meetings_transcript':
        n = granola.note(args['id'], key, transcript=True, get=get)
        return granola.transcript_text(n, me=args.get('me') or 'Me') or 'This meeting has no transcript yet.'
    raise ValueError('Unknown tool ' + name)


def handle(request):
    method = request.get('method')
    if method == 'initialize':
        version = request.get('params', {}).get('protocolVersion') or '2025-06-18'
        return {'protocolVersion': version, 'capabilities': {'tools': {}},
                'serverInfo': {'name': 'tools-meetings', 'version': __version__}}
    if method == 'tools/list':
        return {'tools': TOOLS}
    if method == 'tools/call':
        params = request.get('params', {})
        try:
            text, error = call(params.get('name'), params.get('arguments') or {}), False
        except Exception as problem:  # report to the agent, keep serving
            text, error = str(problem), True
        return {'content': [{'type': 'text', 'text': text}], 'isError': error}
    if method == 'ping':
        return {}
    return None


def serve(stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        if 'id' not in request:
            continue  # a notification
        result = handle(request)
        if result is None:
            reply = {'jsonrpc': '2.0', 'id': request['id'], 'error': {'code': -32601, 'message': 'Method not found'}}
        else:
            reply = {'jsonrpc': '2.0', 'id': request['id'], 'result': result}
        stdout.write(json.dumps(reply) + '\n')
        stdout.flush()
    return 0
