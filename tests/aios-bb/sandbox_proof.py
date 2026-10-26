#!/usr/bin/env python3
"""Install aios-bb as a brand-new member and drive a sandbox bb server, saving every command and output.

Needs a separate bb server for the sandbox (never the member's real one). Point BB_SANDBOX_CLI at a wrapper
that runs `bb` with BB_SERVER_URL set to that server. Run from the repository root:
  BB_SANDBOX_CLI=/tmp/aios2-bbsandbox/sbb python3 tests/aios-bb/sandbox_proof.py
Proof notes are build evidence and go to $AIOS_PROOF_DIR/aios-bb/ (default /tmp/aios2-proof), not the repo.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STREAM = 'b-bb'
HOME = Path('/tmp/aios2-sandbox-%s' % STREAM)
COPY = Path('/tmp/aios2-sandbox-%s-checkout' % STREAM)
REPORT = Path(os.environ.get('AIOS_PROOF_DIR', '/tmp/aios2-proof')) / 'aios-bb' / 'sandbox_v1.md'
FOLDER = HOME / 'acme-studio-aios'
SBB = os.environ.get('BB_SANDBOX_CLI', '/tmp/aios2-bbsandbox/sbb')

ENV = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'), CODEX_HOME=str(HOME / '.codex'),
           BB_CLI=SBB)
ENV['PATH'] = str(HOME / '.local/bin') + ':' + os.environ['PATH']
for key in ('BB_THREAD_ID', 'BB_PROJECT_ID', 'BB_ENVIRONMENT_ID', 'BB_THREAD_STORAGE', 'ANTHROPIC_API_KEY'):
    ENV.pop(key, None)

lines = ['# Sandbox install proof: aios-bb 2.0.0 (v1)', '',
         'A new member on a clean machine. HOME=/tmp/aios2-sandbox-b-bb (shown as `$HOME`). `bb` talks to a separate',
         'sandbox bb server (its own data folder and port), never the real one: `aios-bb` finds it through BB_CLI.',
         '`<checkout>` is a copy of this repository with the INTEGRATION.md changes applied. Every name is fictional.', '']
failed = []


def clean(text):
    for real, shown in ((str(COPY), '<checkout>'), (str(HOME), '$HOME'), ('/private$HOME', '$HOME'),
                        (SBB, '<sandbox-bb>'), (str(ROOT), '<repo>'), ('/private<checkout>', '<checkout>')):
        text = text.replace(real, shown)
    return text


def run(args, expect=0, cwd=None, title=None, env=None):
    proc = subprocess.run(args, cwd=str(cwd or COPY), env=env or ENV, text=True, capture_output=True, timeout=300)
    if title:
        lines.extend(['## ' + title, ''])
    out = '\n'.join(l.rstrip() for l in (proc.stdout + proc.stderr).splitlines())
    lines.extend(['```sh', clean(shlex.join(args)), '```', '```text', clean(out), '[exit %d]' % proc.returncode, '```', ''])
    REPORT.write_text('\n'.join(lines) + '\n')
    ok = expect is None or proc.returncode == expect
    print('%s -> exit %d %s' % (clean(shlex.join(args))[:90], proc.returncode, 'ok' if ok else 'UNEXPECTED'), flush=True)
    if not ok:
        failed.append(clean(shlex.join(args)))
    return proc


def prepare():
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    for path in (HOME, COPY):
        if path.exists():
            shutil.rmtree(path)
    HOME.mkdir(parents=True)
    shutil.copytree(ROOT, COPY, ignore=shutil.ignore_patterns('.git', 'results', '__pycache__', '*.mp4', '.bb'))
    subprocess.run(['git', 'apply', 'plugins/aios-harnesses/install_pack.patch'], cwd=str(COPY), check=True)
    market = json.loads((COPY / '.claude-plugin/marketplace.json').read_text())
    names = {p['name'] for p in market['plugins']}
    for pack in ('aios-harnesses', 'aios-bb'):
        entry = COPY / 'plugins' / pack / 'MARKETPLACE_ENTRY.json'
        if entry.exists() and pack not in names:
            market['plugins'].append(json.loads(entry.read_text()))
    (COPY / '.claude-plugin/marketplace.json').write_text(json.dumps(market, indent=2) + '\n')
    FOLDER.mkdir()
    (FOLDER / 'AGENTS.md').write_text('# Acme Studio AIOS\n\n- Business: Acme Studio, a fictional design studio.\n'
                                      '- Never put passwords or keys in this folder.\n')
    (FOLDER / 'CLAUDE.md').write_text('@AGENTS.md\n')
    git = ['git', '-c', 'user.name=Acme Member', '-c', 'user.email=member@acme.example']
    subprocess.run(['git', 'init', '-q'], cwd=str(FOLDER), check=True)
    subprocess.run(git + ['add', '-A'], cwd=str(FOLDER), check=True)
    subprocess.run(git + ['commit', '-qm', 'Start'], cwd=str(FOLDER), check=True)


def thread_id(name):
    data = json.loads(subprocess.run([SBB, 'thread', 'list', '--json'], capture_output=True, text=True, env=ENV).stdout)
    return [t['id'] for t in data if t.get('title') == name][0]


def main():
    prepare()
    run(['claude', 'plugin', 'validate', 'plugins/aios-bb', '--strict'], title='1. Validate the pack')
    run(['claude', 'plugin', 'marketplace', 'add', str(COPY)], title='2. Install in Claude Code')
    run(['claude', 'plugin', 'install', 'aios@navaigate-aios'])
    run(['claude', 'plugin', 'install', 'aios-bb@navaigate-aios'])
    run(['claude', 'plugin', 'list'])
    run(['./install.sh', 'aios'], title='3. Install for Codex and Cursor')
    run(['./install.sh', 'aios-bb'])
    run(['aios-bb', '--version'])
    run(['aios-bb', 'doctor'], cwd=FOLDER, title='4. Is bb ready for this folder?')
    run(['aios-bb', 'setup', '--dry-run', '--name', 'Acme Studio AIOS'], cwd=FOLDER, title='5. Create the bb project and the board')
    run(['aios-bb', 'setup', '--name', 'Acme Studio AIOS'], cwd=FOLDER)
    run(['aios-bb', 'setup', '--name', 'Acme Studio AIOS'], cwd=FOLDER)
    run([SBB, 'thread', 'section', 'list'], cwd=FOLDER)
    brief = FOLDER / 'brief.md'
    brief.write_text('Create the file notes/hello.md containing the one line "Acme Studio is set up in bb." '
                     'Check the file exists, then reply with the word DONE.\n')
    run(['aios-bb', 'hand', 'Acme hello note', '--prompt-file', str(brief), '--provider', 'codex'], cwd=FOLDER,
        title='6. Hand a job to a Codex thread in its own worktree')
    tid = thread_id('Acme hello note')
    run([SBB, 'thread', 'wait', tid, '--timeout', '240s'], cwd=FOLDER, expect=None)
    run([SBB, 'thread', 'show', tid], cwd=FOLDER, expect=None)
    run(['aios-bb', 'card', 'review', '--thread', tid, '--note', 'Note written'], cwd=FOLDER, title='7. Move the card to Review')
    run(['aios-bb', 'today'], cwd=FOLDER, title='8. Start of day')
    run(['aios-bb', 'card', 'done', '--thread', tid], cwd=FOLDER, title='9. Close the day')
    run(['aios-bb', 'close', '--archive-done'], cwd=FOLDER)
    lines.extend(['## Result', '', ('All commands gave the expected exit code.' if not failed else
                  'Unexpected exit codes: ' + '; '.join(failed)), ''])
    REPORT.write_text('\n'.join(lines) + '\n')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
