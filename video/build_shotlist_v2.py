#!/usr/bin/env python3
"""Turn the recorded command inventory into an exact narration handoff."""
import json
from pathlib import Path

steps=json.loads(Path('video/steps_v2.json').read_text())
manifest={Path(r['file']).stem:r for r in json.loads(Path('video/clips/manifest_v2.json').read_text())}
views=[
 'The real Claude Code CLI adds the local checkout marketplace, then reports aios installed.',
 'The real CLI reports aios-brain installed and lists its unset optional Turso options.',
 'Three start-skill links appear for Codex, Cursor and shared agent skills.',
 'The brain skill, brain command and both MCP configuration entries are installed; PATH is set visibly.',
 'The local SQLite database is created, with local mode and no account needed shown.',
 'Three fictional session files are created for a repeatable sandbox-only demonstration.',
 'Three sessions and six fictional messages are captured, with network off, no failures and credential redaction applied before storage.',
 'The same capture reports zero changed sessions and three unchanged files, with no warnings.',
 'A BM25 search finds the fictional Lighthouse launch budget and returns a ref.',
 'The full ref from the search is typed, and the stored question and answer are shown.',
 'Healthy status, newest stored/session messages, active-session grace, per-harness counts, empty failures and the configured retention warning are held page by page.',
 'The real Claude Code plugin list shows both plugins, version 2.0.0 and enabled status.',
 'The real Codex CLI reads its sandbox configuration and lists the enabled brain stdio server.',
 'The actual sandbox Cursor MCP JSON is displayed in the terminal, without any secret values.',
 'The start plugin reports each harness separately, v1 migration choices and the next unconfirmed module; every page is held for reading.'
]
narration=[
 'Install the start plugin from the local review marketplace, then restart Claude Code and type /aios or /aios:aios.',
 'Add the brain pack when you want private memory of your work, then restart Claude Code to load its server.',
 'Link the start skill into Codex and Cursor, then restart those harnesses to load it.',
 'Add the brain skill and MCP server to Codex and Cursor, make its command available in your shell, then restart the harnesses.',
 'Create your own local brain without opening an account or adding an API key.',
 'For this training sandbox, create fictional chats so you can repeat the demonstration safely.',
 'Capture the text of your Claude Code, Codex and Cursor sessions into your local brain.',
 'Run capture again to confirm that unchanged session files are skipped.',
 'Search for words from a past task and keep the ref of the result you want to open.',
 'Read that exact result to see the saved messages rather than relying on a search excerpt.',
 'Check that stored messages match the session files, and remember to capture before old files are deleted.',
 'Check that Claude Code has installed and enabled both packs.',
 'Check that Codex can see the brain server in its own configuration.',
 'Check the Cursor server configuration while keeping credentials in your separate private environment file.',
 'Use the start plugin inventory to see which harness has each pack, review any v1 migration choice and choose the next module.'
]
lines=['# Setup tutorial shot list v2','',
 'Updated 26 October 2026: source material for later 3–10 minute landscape tutorials, made with /navmotion and narrated in Daniel’s voice. No raw-clip duration cap. One step per clip; full commands, real output and reading pauses.','',
 '## Before the first shot','',
 '- Start in the approved source checkout; the recording uses a physical scratch copy at /tmp/aios-video-checkout-v2 so no producing-machine paths appear on screen. This branch is not published, so do not show a GitHub 2.0 install until release approval.',
 '- These recordings use HOME=/tmp/aios-member-sandbox, CLAUDE_CONFIG_DIR=$HOME/.claude and CODEX_HOME=$HOME/.codex. Real member installs normally use the member’s own HOME.',
 '- Python 3.9+ with SQLite FTS5, Claude Code and (for its verification shot) Codex are already installed. No model login is needed for the local flow.',
 '- VHS runs in filename order. Its hidden set-up establishes the synthetic HOME, a clean prompt and a private recording cache; it is recording plumbing, not an unshown member installation step; commands and output are real and unaltered.',
 '- Clip 06 is an optional training demonstration: that helper refuses to write outside /tmp. Members capturing their own chats skip it after using the harnesses normally.',
 '- All output must be readable. Keep the command and its result together; extend a pause in the later edit whenever narration needs more time.','',
 '## Recorded steps','']
for index,step in enumerate(steps):
    row=manifest[step['name']]
    lines += ['### '+step['name'],'',
              '- Clip: `'+row['file']+'` — '+str(row['seconds'])+' seconds, 1920 x 1080.',
              '- Viewer sees: '+views[index],
              '- Narration: '+narration[index],'','Exact command'+('s' if len(step['commands'])>1 else '')+':','','```sh',*step['commands'],'```','']
lines += ['## Real screenshots and screens that need rebuilding','',
 '| Harness/view | Asset or plan | What it proves |',
 '|---|---|---|',
 '| Claude Code CLI | screens/12_claude-code-sandbox_v2.png | Real installed/enabled plugin inventory in the sandbox; not a successful authenticated skill call. |',
 '| Codex CLI | screens/13_codex-sandbox_v2.png | Real Codex recognition of the configured stdio server; direct MCP protocol/search is verified separately in the proof. |',
 '| Cursor configuration | screens/14_cursor-sandbox-config_v2.png | Real sandbox MCP JSON in a terminal. This is deliberately not labelled as Cursor’s GUI. |',
 '| Cursor MCP settings and chat UI | Rebuild as an explicitly labelled mock-up using only the sandbox configuration and fictional Juniper messages. | The available Cursor app is a running user instance; no isolated sandbox GUI was identified. Its existing workspace/settings were not opened under the brief’s private-config boundary. No live profile screenshot was saved. |',
 '| Claude Code /aios and /brain chat | Capture later after a member-owned sandbox subscription login, or use a labelled mock-up of the supplied skill and inventory output. | The isolated HOME is not logged in; model evals and authenticated chat are unverified. Do not substitute a real account screenshot. |',
 '| Codex remembered-chat response | Capture later in a signed-in isolated Codex profile, or use a labelled mock-up with only fictional content. | Installation and MCP configuration do not prove a model invoked the tools. |','',
 'The terminal screenshots are unaltered frames extracted from the real recordings. No generated interface is being passed off as a software screenshot. No mock-up is rendered in phase 1.','',
 '## Later tutorial edit','',
 'Suggested split: one installation tutorial (01–04 and 12–15), then one first-memory tutorial (05–11). Target 3–10 minutes for each after the clear explanation and Daniel’s narration are added. Let the member read and repeat each step; do not shorten the source merely to meet a clip cap.',
 '', 'For the read shot, copy the ref returned by your own search. The command above contains the actual ref captured in this sandbox; it is not a universal session identifier.',
 '', 'Optional Turso, paid transcripts and Haiku digests need separate account-aware tutorials after their live checks. Their local unit doubles are not software screen evidence.','']
Path('video/SHOTLIST_v2.md').write_text('\n'.join(lines))
print('Exact commands and narration outline written to video/SHOTLIST_v2.md')
