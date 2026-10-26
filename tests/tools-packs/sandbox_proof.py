#!/usr/bin/env python3
"""Sandbox install proof for one tools pack, as a brand-new member.

It copies this checkout to /tmp, adds every tools pack's MARKETPLACE_ENTRY.json to the marketplace (the only
shared-file change), then installs the pack with HOME=/tmp/aios2-sandbox-tools/<pack> in Claude Code and for
Codex and Cursor, and runs the pack's own steps from tests/<pack>/sandbox_steps.py. Every command, its output and
its exit code go to $AIOS2_PROOF_DIR/<pack>/sandbox_v1.md (build evidence is course material, kept out of Git).
Nothing touches the real ~/.claude, ~/.codex or ~/.cursor. It pauses while the 1-minute load average is above 60.

Usage: AIOS2_PROOF_DIR=<folder> python3 tests/tools-packs/sandbox_proof.py tools-meetings
"""
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = Path('/tmp/aios2-sandbox-tools')
PROOF = Path(os.environ.get('AIOS2_PROOF_DIR') or '/tmp/aios2-tool-packs/proof')


def load_too_high(limit=60.0):
    """Ruled 26 October 2026: run one sandbox at a time, and pause only while the 1-minute load average is above 60."""
    return os.getloadavg()[0] > limit


def prepare_checkout(checkout):
    if checkout.exists():
        shutil.rmtree(checkout)
    subprocess.run(['rsync', '-a', '--exclude', '.git', '--exclude', 'excalidraw.log', '--exclude', '__pycache__',
                    str(REPO) + '/', str(checkout) + '/'], check=True)
    market = checkout / '.claude-plugin/marketplace.json'
    data = json.loads(market.read_text())
    names = {p['name'] for p in data['plugins']}
    for entry in sorted((checkout / 'plugins').glob('tools-*/MARKETPLACE_ENTRY.json')):
        item = json.loads(entry.read_text())
        if item['name'] not in names:
            data['plugins'].append(item)
    market.write_text(json.dumps(data, indent=2) + '\n')


def environment(home):
    env = dict(os.environ, HOME=str(home), CLAUDE_CONFIG_DIR=str(home / '.claude'), CODEX_HOME=str(home / '.codex'),
               XDG_CONFIG_HOME=str(home / '.config'), XDG_DATA_HOME=str(home / '.local/share'),
               XDG_CACHE_HOME=str(home / '.cache'))
    for key in list(env):
        if key.startswith('CLAUDE_PLUGIN_') or key in ('CURSOR_CONFIG_DIR', 'AIOS_CONFIG_DIR') or key.endswith('_API_KEY'):
            env.pop(key, None)
    # Tools that find their sign-in through the account's home folder, not $HOME, get the member's folder too.
    env['NOTEBOOKLM_HOME'] = str(home / '.notebooklm')
    env['PATH'] = ':'.join([str(home / '.local/bin'), env['PATH']])
    return env


class Report:
    def __init__(self, pack, home, checkout):
        self.pack, self.home, self.checkout = pack, home, checkout
        self.file = PROOF / pack / 'sandbox_v1.md'
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.lines = ['# Sandbox install proof: ' + pack + ' (v1)', '',
                      'A brand-new member: HOME=' + str(home) + ', CLAUDE_CONFIG_DIR=$HOME/.claude, CODEX_HOME=$HOME/.codex.',
                      'No API keys are set (every *_API_KEY variable is removed). The checkout is a copy at',
                      str(checkout) + ' with the tools packs\' MARKETPLACE_ENTRY.json files added to the marketplace.',
                      'All sample data is fictional (Acme Studio, Northwind Bakery). Long outputs keep their last 40 lines.', '']
        self.failed = []
        self.env = environment(home)

    def run(self, args, expect=0, cwd=None, timeout=600, note='', stdin=None):
        proc = subprocess.run([str(a) for a in args], cwd=str(cwd or self.checkout), env=self.env, text=True,
                              capture_output=True, timeout=timeout, input=stdin)
        out = (proc.stdout + proc.stderr).replace(str(Path.home()), '$REAL_HOME').splitlines()
        if len(out) > 40:
            out = ['[... %d lines trimmed ...]' % (len(out) - 40)] + out[-40:]
        if note:
            self.lines.append(note)
        self.lines += ['```sh', shlex.join(str(a) for a in args), '```', '```text'] + [x.rstrip() for x in out] + [
            '[exit %d%s]' % (proc.returncode, '' if expect is None or proc.returncode == expect else ', EXPECTED %d' % expect), '```', '']
        self.file.write_text('\n'.join(self.lines) + '\n')
        print(shlex.join(str(a) for a in args)[:120] + ' -> exit ' + str(proc.returncode), flush=True)
        if expect is not None and proc.returncode != expect:
            self.failed.append(shlex.join(str(a) for a in args))
        return proc

    def finish(self):
        self.lines += ['## Result', '', 'All commands matched their expected exit codes.' if not self.failed else
                       'Unexpected exit codes:\n' + '\n'.join('- `' + c + '`' for c in self.failed)]
        self.file.write_text('\n'.join(self.lines) + '\n')
        return 1 if self.failed else 0


def common(r, pack):
    r.run(['claude', '--version'])
    r.run(['claude', 'plugin', 'validate', 'plugins/' + pack, '--strict'])
    r.run(['claude', 'plugin', 'validate', '.claude-plugin/marketplace.json', '--strict'])
    r.run(['claude', 'plugin', 'marketplace', 'add', r.checkout])
    r.run(['claude', 'plugin', 'install', 'aios@navaigate-aios'])
    r.run(['claude', 'plugin', 'install', pack + '@navaigate-aios'])
    r.run(['claude', 'plugin', 'list'])
    r.run(['./install.sh', pack], note='Codex and Cursor: one command installs the pack and the start plugin it needs.')
    r.run(['./install.sh', pack], note='A second install changes nothing.')
    r.run(['./install.sh', pack, '--check'])
    r.run(['ls', '-go', r.home / '.codex/skills', r.home / '.cursor/skills', r.home / '.agents/skills'])
    if (r.home / '.local/bin').is_dir():
        r.run(['ls', '-go', r.home / '.local/bin'])


def main():
    pack = sys.argv[1]
    while load_too_high():
        print('Load average above 60; waiting a minute.', flush=True)
        time.sleep(60)
    home, checkout = BASE / pack, BASE / (pack + '-checkout')
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True)
    prepare_checkout(checkout)
    r = Report(pack, home, checkout)
    common(r, pack)
    steps = REPO / 'tests' / pack / 'sandbox_steps.py'
    if steps.exists():
        spec = importlib.util.spec_from_file_location('sandbox_steps_' + pack.replace('-', '_'), steps)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.run(r, home, home / 'Work')
    return r.finish()


if __name__ == '__main__':
    raise SystemExit(main())
