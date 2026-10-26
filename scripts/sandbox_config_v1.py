#!/usr/bin/env python3
"""Fictional pre-existing configuration for the member install proof."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('action',choices=['seed','verify'])
args = parser.parse_args()
home = Path.home()
if home.resolve()!=Path('/tmp/aios-member-sandbox').resolve():
    parser.error('This helper only runs in HOME=/tmp/aios-member-sandbox')
if args.action=='seed':
    for name in ('.codex','.cursor'):
        (home/name).mkdir(exist_ok=True)
    (home/'.codex/config.toml').write_text('[mcp_servers.fictional]\ncommand = "fictional-server"\n')
    (home/'.cursor/mcp.json').write_text(json.dumps({'mcpServers':{'fictional':{'command':'fictional-server'}}}))
    print('Seeded unrelated fictional MCP entries.')
else:
    text = (home/'.codex/config.toml').read_text()
    servers = json.loads((home/'.cursor/mcp.json').read_text())['mcpServers']
    assert '[mcp_servers.fictional]' in text
    assert 'aios-brain' in servers and 'fictional' in servers
    assert list((home/'.codex').glob('config.toml.backup-*'))
    assert list((home/'.cursor').glob('mcp.json.backup-*'))
    print('Both unrelated MCP entries and both backups verified.')
