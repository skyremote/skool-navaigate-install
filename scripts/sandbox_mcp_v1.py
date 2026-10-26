#!/usr/bin/env python3
"""Talk to the installed stdio server using fictional captured content."""
import json
import subprocess
from pathlib import Path

home = Path.home()
assert home.resolve()==Path('/tmp/aios-member-sandbox').resolve()
server = json.loads((home/'.cursor/mcp.json').read_text())['mcpServers']['aios-brain']
command = [server['command'],*server['args']]
requests = [
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'sandbox-proof','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list'},
 {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'brain_search','arguments':{'query':'Juniper navy'}}}]
p = subprocess.run(command,input=''.join(json.dumps(r)+'\n' for r in requests),text=True,capture_output=True,check=True)
print('Server command: '+json.dumps(command))
print(p.stdout.rstrip())
rows = [json.loads(line) for line in p.stdout.splitlines()]
assert len(rows)==3
assert {t['name'] for t in rows[1]['result']['tools']}=={'brain_search','brain_read','brain_media_add'}
assert json.loads(rows[2]['result']['content'][0]['text'])['hits']
print('MCP handshake, inventory and fictional search verified through the installed server command.')
