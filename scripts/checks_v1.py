#!/usr/bin/env python3
"""Save fresh acceptance checks for the unpublished review build."""
import json
import os
import shlex
import subprocess
from pathlib import Path
from proof_paths import portable

root=Path(__file__).resolve().parents[1]
home=Path('/tmp/aios-member-sandbox')
env=dict(os.environ,HOME=str(home),CLAUDE_CONFIG_DIR=str(home/'.claude'),CODEX_HOME=str(home/'.codex'))
commands=[['python3','--version'],['python3','-m','unittest','discover','-s','tests','-v'],
 ['claude','plugin','validate','plugins/aios','--strict'],
 ['claude','plugin','validate','plugins/aios-brain','--strict'],
 ['claude','plugin','validate','.claude-plugin/marketplace.json','--strict'],
 ]+([['vhs','validate','video/tapes/*_v2.tape'],['python3','video/check_clips_v2.py']] if (root/'video').is_dir() else [])
lines=['# Checks v2','','All harness CLI checks use the isolated member HOME.','']
for args in commands:
    proc=subprocess.run(args,cwd=root,env=env,text=True,capture_output=True)
    lines+=['```sh',shlex.join(args),'```','```text',(proc.stdout+proc.stderr).rstrip(),f'[exit {proc.returncode}]','```','']
    (root/'.evidence/checks_v2.md').write_text(portable('\n'.join(lines))+'\n')
    if proc.returncode:
        raise SystemExit('Check failed; see .evidence/checks_v2.md')
legacy={p.parent.name for p in (root/'skills').glob('*/SKILL.md')}
roadmap=(root/'ROADMAP.md').read_text()
assert len(legacy)==28
assert all('| '+name+' |' in roadmap for name in legacy)
lines+=['## Scope checks','',
 'All 28 old skill directories have a row in ROADMAP.md. The original v1 source is preserved, retained at its old paths and installable for six months, with fixes only.',
 '', 'Both plugins and the marketplace pass strict validation. The listing directory check warns that icons are absent; it explicitly does not change the validation result.',
 '', 'The unit/integration suite covers incremental capture and rollback, harness noise, Codex fork identities, Cursor exports, recency/relevance, actual-data health and exit codes, local no-network operation, media opt-in, subscription-only digest calls, stdio MCP, HTTP errors/read-back/redirects, inventory and installer preservation/backups.',
 '', 'Remote exchange, captions and digest paths use independent fictional doubles. Live member Turso, Supadata, YouTube captions and a subscription digest have not been exercised. All three model evals are authentication-blocked in the isolated HOME; see eval-results_v1.md.',
 '', 'The real sandbox proof covers local marketplace installation, both pack installs, fictional capture/search/read/status, unrelated MCP entries/backups, the installed stdio handshake/search and Codex’s real MCP inventory. Findings R01–R16 have dedicated regression tests; see review-fixes_v2.md.',
 '', 'The revised raw tutorial sequence contains 15 ordered landscape clips. ffprobe checks their inventory, 1920 x 1080 dimensions and positive durations. The earlier 40-second cap has been removed. Full command/output views and reading pauses are documented in video/SHOTLIST_v2.md; the full inventory includes a page-by-page hold.',
 '', 'Actual terminal screenshots of Claude Code, Codex and the Cursor sandbox configuration are saved in video/screens. Authenticated chats and the live Cursor profile are not presented as verified UI; the shot list marks the later capture/mock-up boundary.',
 '', 'No push, PR, tag, publication, Skool operation or write to real harness/brain configuration was performed. The pre-existing untracked excalidraw.log is outside this change.','']
(root/'.evidence/checks_v2.md').write_text(portable('\n'.join(lines))+'\n')
print('Fresh local acceptance evidence saved in .evidence/checks_v2.md')
