#!/usr/bin/env python3
"""Install aios-harnesses as a brand-new member in a throwaway HOME and save every command and output.

Run from the repository root: python3 tests/aios-harnesses/sandbox_proof.py
It copies the checkout to /tmp, applies the INTEGRATION.md changes to the copy only, and never touches
the real ~/.claude, ~/.codex or ~/.cursor. Paths in the saved proof are shown as <checkout> and $HOME.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STREAM = 'b-harnesses'
HOME = Path('/tmp/aios2-sandbox-%s' % STREAM)
COPY = Path('/tmp/aios2-sandbox-%s-checkout' % STREAM)
# Proof notes are build evidence, kept out of the repo. Set AIOS_PROOF_DIR to choose where they go.
REPORT = Path(os.environ.get('AIOS_PROOF_DIR', '/tmp/aios2-proof')) / 'aios-harnesses' / 'sandbox_v1.md'
FOLDER = HOME / 'acme-studio-aios'

ENV = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'), CODEX_HOME=str(HOME / '.codex'),
           XDG_CONFIG_HOME=str(HOME / '.config'), XDG_DATA_HOME=str(HOME / '.local/share'))
ENV['PATH'] = str(HOME / '.local/bin') + ':' + os.environ['PATH']
for key in ('CURSOR_CONFIG_DIR', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'BB_THREAD_ID', 'BB_PROJECT_ID'):
    ENV.pop(key, None)

lines = ['# Sandbox install proof: aios-harnesses 2.0.0 (v1)', '',
         'A new member on a clean machine. HOME=/tmp/aios2-sandbox-b-harnesses (shown as `$HOME`), with',
         'CLAUDE_CONFIG_DIR=$HOME/.claude and CODEX_HOME=$HOME/.codex. `<checkout>` is a copy of this repository with',
         'the INTEGRATION.md changes applied (marketplace entries and the install_pack.py patch).',
         'Every name is fictional. No real member data, account or token is used.', '']
failed = []


def clean(text):
    for real, shown in ((str(COPY), '<checkout>'), (str(HOME), '$HOME'), ('/private$HOME', '$HOME'),
                        (str(ROOT), '<repo>'), ('/private<checkout>', '<checkout>')):
        text = text.replace(real, shown)
    return text


def run(args, expect=0, cwd=None, title=None, shell=False):
    proc = subprocess.run(args, cwd=str(cwd or COPY), env=ENV, text=True, capture_output=True, timeout=180, shell=shell)
    shown = args if shell else shlex.join(args)
    if title:
        lines.extend(['## ' + title, ''])
    out = '\n'.join(l.rstrip() for l in (proc.stdout + proc.stderr).splitlines())
    lines.extend(['```sh', clean(shown), '```', '```text', clean(out), '[exit %d]' % proc.returncode, '```', ''])
    REPORT.write_text('\n'.join(lines) + '\n')
    status = 'ok' if expect is None or proc.returncode == expect else 'UNEXPECTED (wanted %d)' % expect
    print('%s -> exit %d %s' % (clean(shown)[:90], proc.returncode, status), flush=True)
    if expect is not None and proc.returncode != expect:
        failed.append(clean(shown))
    return proc


def prepare():
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    for path in (HOME, COPY):
        if path.exists():
            shutil.rmtree(path)
    HOME.mkdir(parents=True)
    shutil.copytree(ROOT, COPY, ignore=shutil.ignore_patterns('.git', 'results', '__pycache__', '*.mp4', 'clips', '.bb'))
    subprocess.run(['git', 'apply', 'plugins/aios-harnesses/install_pack.patch'], cwd=str(COPY), check=True)
    market = json.loads((COPY / '.claude-plugin/marketplace.json').read_text())
    names = {p['name'] for p in market['plugins']}
    for pack in ('aios-harnesses', 'aios-bb'):
        entry_path = COPY / 'plugins' / pack / 'MARKETPLACE_ENTRY.json'
        if entry_path.exists() and pack not in names:
            market['plugins'].append(json.loads(entry_path.read_text()))
    (COPY / '.claude-plugin/marketplace.json').write_text(json.dumps(market, indent=2) + '\n')


def fixtures():
    skill = HOME / '.agents/skills/acme-weekly-report'
    skill.mkdir(parents=True)
    (skill / 'SKILL.md').write_text('---\nname: acme-weekly-report\ndescription: Build the Acme Studio weekly report from the sales sheet.\n---\n\nBuild the report, then check the totals match the sheet.\n')
    FOLDER.mkdir()


def main():
    prepare()
    run(['claude', '--version'], title='1. The tools on this machine')
    run(['codex', '--version'])
    run(['cursor-agent', '--version'])
    run(['claude', 'plugin', 'validate', 'plugins/aios-harnesses', '--strict'], title='2. Validate the pack')
    run(['claude', 'plugin', 'validate', '.claude-plugin/marketplace.json', '--strict'])
    run(['claude', 'plugin', 'marketplace', 'add', str(COPY)], title='3. Install in Claude Code')
    run(['claude', 'plugin', 'install', 'aios@navaigate-aios'])
    run(['claude', 'plugin', 'install', 'aios-harnesses@navaigate-aios'])
    run(['claude', 'plugin', 'list'])
    run(['./install.sh', 'aios-harnesses'], expect=1, title='4. Install for Codex and Cursor (aios must come first)')
    run(['./install.sh', 'aios'])
    run(['./install.sh', 'aios-harnesses'])
    run(['ls', '-l', str(HOME / '.agents/skills'), str(HOME / '.local/bin')], shell=False)
    run(['harness', '--version'])
    fixtures()
    run(['harness', 'check'], expect=1, cwd=FOLDER, title='5. First check on an empty folder (expected to differ)')
    run(['harness', 'setup', '--dry-run'], cwd=FOLDER, title='6. Set up the folder')
    run(['harness', 'setup'], cwd=FOLDER)
    run(['cat', 'CLAUDE.md'], cwd=FOLDER)
    run(['harness', 'mcp', 'add', 'acme-notes', '--env', 'ACME_NOTES_TOKEN=${ACME_NOTES_TOKEN}', '--', 'npx', '-y', '@acme/notes-mcp'],
        cwd=FOLDER, title='7. One MCP server for every harness')
    run(['harness', 'mcp', 'add', 'leaky', '--env', 'ACME_API_KEY=abcd1234efgh5678', '--', 'npx', 'leaky'], expect=2, cwd=FOLDER)
    run(['cat', '.codex/config.toml'], cwd=FOLDER)
    run(['harness', 'check'], cwd=FOLDER, title='8. Check: every harness matches')
    run(['claude', 'mcp', 'list'], cwd=FOLDER, title='9. Ask the real harness CLIs what they load')
    run(['cursor-agent', 'mcp', 'list'], cwd=FOLDER, expect=None)
    # A member answers yes when Codex asks to trust the folder; this is the line Codex writes.
    with open(HOME / '.codex/config.toml', 'a') as cfg:
        cfg.write('\n[projects.%s]\ntrust_level = "trusted"\n' % json.dumps(str(FOLDER.resolve())))
    run(['codex', 'mcp', 'list'], cwd=FOLDER, expect=None)
    (FOLDER / '.cursorrules').write_text('- Use American spelling.\n')
    (FOLDER / '.codex/config.toml').unlink()
    run(['harness', 'check'], expect=1, cwd=FOLDER, title='10. A deliberate mismatch: an old .cursorrules and a lost Codex config')
    (FOLDER / '.cursorrules').unlink()
    run(['harness', 'sync'], cwd=FOLDER, title='11. Fix it and check again')
    run(['harness', 'check'], cwd=FOLDER)
    run(['harness', 'grok'], cwd=FOLDER, title='12. Grok Bot')
    phrase = [l for l in (FOLDER / 'AGENTS.md').read_text().splitlines() if l.startswith('Rules check phrase:')][0].split()[3]
    (FOLDER / '.aios/grok-bot.txt').write_text('RULES: %s\nMCP:\nacme-notes\nweb-search\nSKILLS:\nacme-weekly-report\n' % phrase)
    run(['harness', 'check'], cwd=FOLDER)
    run(['harness', 'defaults', '--apply'], cwd=FOLDER, title='13. Model and effort defaults')
    run(['harness', 'check', '--json'], cwd=FOLDER, title='14. The same check as JSON')
    lines.extend(['## Result', '', ('All commands gave the expected exit code.' if not failed else
                  'Unexpected exit codes: ' + '; '.join(failed)), ''])
    REPORT.write_text('\n'.join(lines) + '\n')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
