#!/usr/bin/env python3
"""Sandbox install proof for shelf-decks 2.0.1, as a brand-new member.

Copies this checkout to /tmp, adds the pack's MARKETPLACE_ENTRY.json to the copy's marketplace (no other shared
file is patched), then installs and runs the pack with HOME=/tmp/aios2-sandbox-shelf-decks. Every command, its
output and its exit code go to $AIOS2_PROOF_DIR/shelf-decks/sandbox_v2.md (build evidence lives with the course,
outside the repo). Nothing touches the real ~/.claude, ~/.codex or ~/.cursor.

Usage: AIOS2_PROOF_DIR=<classroom>/aios-2/build-proof python3 tests/shelf-decks/sandbox_proof.py
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

PACK = 'shelf-decks'
REPO = Path(__file__).resolve().parents[2]
CHECKOUT = Path('/tmp/aios2-shelf-decks-v2/checkout')
HOME = Path('/tmp/aios2-sandbox-shelf-decks')
PROOF = Path(os.environ.get('AIOS2_PROOF_DIR') or Path.home() / 'NAS_Local/150_Navbot_Classroom/aios-2/build-proof')
WORK = HOME / 'Decks'
REAL_HOME = str(Path.home())


def prepare_checkout():
    if CHECKOUT.exists():
        shutil.rmtree(CHECKOUT)
    subprocess.run(['rsync', '-a', '--exclude', '.git', '--exclude', 'node_modules', '--exclude', 'video/clips',
                    str(REPO) + '/', str(CHECKOUT) + '/'], check=True)
    market = CHECKOUT / '.claude-plugin/marketplace.json'
    data = json.loads(market.read_text())
    entry = json.loads((CHECKOUT / 'plugins' / PACK / 'MARKETPLACE_ENTRY.json').read_text())
    data['plugins'] = [p for p in data['plugins'] if p['name'] != PACK] + [entry]
    market.write_text(json.dumps(data, indent=2) + '\n')


def environment():
    env = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'), CODEX_HOME=str(HOME / '.codex'),
               XDG_CONFIG_HOME=str(HOME / '.config'), XDG_DATA_HOME=str(HOME / '.local/share'),
               XDG_CACHE_HOME=str(HOME / '.cache'), npm_config_cache=str(HOME / '.npm'))
    for key in ('CURSOR_CONFIG_DIR', 'AIOS_CONFIG_DIR', 'CLAUDE_PLUGIN_ROOT', 'CLAUDE_PLUGIN_DATA', 'SHELF_DECKS_HOME',
                'SHELF_DECKS_DATA', 'SHELF_DECKS_BRAND', 'NODE_PATH'):
        env.pop(key, None)
    env['PATH'] = ':'.join([str(HOME / '.local/bin'), env['PATH']])
    return env


class Report:
    def __init__(self):
        self.file = PROOF / PACK / 'sandbox_v2.md'
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.lines = ['# Sandbox install proof: shelf-decks 2.0.1 (v2)', '',
                      'A brand-new member: HOME=' + str(HOME) + ', CLAUDE_CONFIG_DIR=$HOME/.claude, CODEX_HOME=$HOME/.codex.',
                      'The checkout is a copy at ' + str(CHECKOUT) + ' with the pack\'s MARKETPLACE_ENTRY.json added to',
                      'the marketplace (the only shared-file change, see INTEGRATION.md). All deck data is fictional',
                      '(Northwind Bakery, Acme Studio). Long outputs are trimmed to their last 40 lines.', '']
        self.failed = []
        self.env = environment()

    def run(self, args, expect=0, cwd=None, timeout=1800, note=''):
        proc = subprocess.run([str(a) for a in args], cwd=str(cwd or CHECKOUT), env=self.env, text=True,
                              capture_output=True, timeout=timeout)
        out = (proc.stdout + proc.stderr).replace(REAL_HOME, '$REAL_HOME').splitlines()
        if len(out) > 40:
            out = ['[... %d lines trimmed ...]' % (len(out) - 40)] + out[-40:]
        command = shlex.join(str(a) for a in args).replace(REAL_HOME, '$REAL_HOME')
        if note:
            self.lines.append(note)
        self.lines += ['```sh', command, '```', '```text'] + [x.rstrip() for x in out] + [
            '[exit %d%s]' % (proc.returncode, '' if proc.returncode == expect else ', EXPECTED %d' % expect), '```', '']
        self.file.write_text('\n'.join(self.lines) + '\n')
        print(command + ' -> exit ' + str(proc.returncode), flush=True)
        if proc.returncode != expect:
            self.failed.append(command)
        return proc

    def finish(self):
        self.lines += ['## Result', '', 'All commands matched their expected exit codes.' if not self.failed else
                       'Unexpected exit codes:\n' + '\n'.join('- `' + c + '`' for c in self.failed)]
        self.file.write_text('\n'.join(self.lines) + '\n')
        return 1 if self.failed else 0


def main():
    if HOME.exists():
        shutil.rmtree(HOME)
    HOME.mkdir(parents=True)
    WORK.mkdir(parents=True)
    prepare_checkout()
    r = Report()
    r.run(['claude', '--version'])
    r.run(['claude', 'plugin', 'validate', 'plugins/' + PACK, '--strict'])
    r.run(['claude', 'plugin', 'validate', '.claude-plugin/marketplace.json', '--strict'])
    r.run(['claude', 'plugin', 'marketplace', 'add', CHECKOUT])
    r.run(['claude', 'plugin', 'install', 'aios@navaigate-aios'])
    r.run(['claude', 'plugin', 'install', PACK + '@navaigate-aios'])
    r.run(['claude', 'plugin', 'list'])
    cached = sorted((HOME / '.claude/plugins/cache').glob('*/' + PACK + '/*/bin/shelf-decks'))
    if cached:
        r.run([cached[-1], '--version'], note='Claude Code: the command from the installed plugin cache.')
    r.run(['./install.sh', PACK], note='Codex and Cursor: the installer puts the start plugin `aios` in first, then the pack.')
    r.run(['./install.sh', PACK, '--check'])
    r.run(['ls', '-go', HOME / '.codex/skills', HOME / '.agents/skills', HOME / '.local/bin'])
    r.run(['shelf-decks', '--version'])
    r.run(['shelf-decks', 'check'], expect=1, note='Before setup the Node packages are missing, and check says how to fix it.')
    r.run(['shelf-decks', 'setup'], note='Installs pptxgenjs, puppeteer-core and pdf-lib into $HOME/.local/share/shelf-decks.')
    r.run(['shelf-decks', 'check'])
    r.run(['shelf-decks', 'sample', WORK / 'northwind'])
    r.run(['shelf-decks', 'render', WORK / 'northwind/deck.js', '--pdf'])
    r.run(['shelf-decks', 'shots', WORK / 'northwind/Northwind_Second_Shop_v1.html'])
    r.run(['shelf-decks', 'render', WORK / 'northwind/deck.js', '--html-only'], note='A second render is a new version; v1 stays.')
    r.run(['ls', '-go', WORK / 'northwind', WORK / 'northwind/images'])
    r.run(['shelf-decks', 'pdf', WORK / 'northwind/Northwind_Second_Shop_v1.html'], expect=1,
          note='The PDF is never overwritten.')
    r.run(['shelf-decks', 'init', '--name', 'Acme Studio', '--accent', 'C2410C', '--ink', '1C1917', '--bg', 'FAF7F2',
           '--display', 'Fraunces', '--body', 'Inter', '--image-style', 'warm documentary photography, no text in the image'])
    r.run(['cat', HOME / '.config/shelf-decks/brand.json'])
    r.run(['shelf-decks', 'new', WORK / 'acme-q3'])
    r.run(['shelf-decks', 'render', WORK / 'acme-q3/deck.js'])
    r.run(['shelf-decks', 'brand'])
    return r.finish()


if __name__ == '__main__':
    raise SystemExit(main())
