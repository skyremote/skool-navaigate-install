"""Shared sandbox-install proof for stream D packs (aios-methods, aios-models, aios-ship).

Runs as a brand-new member: HOME, CLAUDE_CONFIG_DIR and CODEX_HOME all point into
/tmp/aios2-sandbox-d-methods-models-ship/<pack>. It copies this checkout into the sandbox,
applies the installer patch from plugins/aios-methods/INTEGRATION.md and adds the stream D
marketplace entries to the copy only. Nothing outside the sandbox is written.
Every command and its real output is written to $AIOS_PROOF_DIR/<pack>/sandbox_v1.md (outside the repo),
with the checkout path replaced by <checkout>.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Build evidence stays out of the repo (Daniel, 26 Oct 2026). Set AIOS_PROOF_DIR to your classroom's build-proof folder.
PROOF = Path(os.environ.get('AIOS_PROOF_DIR', '/tmp/aios-proof'))
BASE = Path('/tmp/aios2-sandbox-d-methods-models-ship')
STREAM_PACKS = ['aios-methods', 'aios-models', 'aios-ship']


class Sandbox:
    def __init__(self, pack):
        self.pack = pack
        self.home = BASE / pack
        if self.home.exists():
            shutil.move(str(self.home), str(self.home) + '-before-' + str(os.getpid()))
        self.home.mkdir(parents=True)
        self.checkout = self.home / 'skool-navaigate-install'
        self.lines = ['# Sandbox install proof v1: ' + pack, '',
                      'A new member on a clean machine. HOME=' + str(self.home) + ', CLAUDE_CONFIG_DIR=$HOME/.claude,',
                      'CODEX_HOME=$HOME/.codex. All data is fictional. The checkout is a copy of this branch inside the sandbox,',
                      'with the installer patch from `plugins/aios-methods/INTEGRATION.md` and the stream D marketplace entries applied',
                      'to the copy only. Commands and output below are real and unedited, apart from the checkout path shown as `<checkout>`.', '']
        self.failures = 0
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(('CLAUDE_CODE_', 'CLAUDECODE', 'CLAUDE_PLUGIN', 'CODEX_'))}
        self.env.update(HOME=str(self.home), CLAUDE_CONFIG_DIR=str(self.home / '.claude'), CODEX_HOME=str(self.home / '.codex'),
                        XDG_CONFIG_HOME=str(self.home / '.config'), XDG_DATA_HOME=str(self.home / '.local/share'),
                        XDG_CACHE_HOME=str(self.home / '.cache'), GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=str(self.home / '.gitconfig'),
                        PATH=str(self.home / '.local/bin') + os.pathsep + os.environ.get('PATH', ''))
        (self.home / '.gitconfig').write_text('[user]\n\tname = Acme Member\n\temail = member@example.com\n[init]\n\tdefaultBranch = main\n')

    def clean(self, text):
        text = text.replace(str(ROOT), '<checkout>')
        text = re.sub(r'/Users/[^/\s]+', '<your-home>', text)
        return re.sub(r'[\w.+-]+@(?!example\.com)[\w-]+\.[\w.]+', '<email>', text)

    def note(self, text):
        self.lines += [text, '']

    def run(self, command, cwd=None, expect=0, show=None, timeout=300):
        cwd = cwd or self.checkout
        result = subprocess.run(command, shell=True, cwd=cwd, env=self.env, text=True, capture_output=True, timeout=timeout)
        output = (result.stdout + result.stderr).rstrip()
        ok = result.returncode == expect if expect is not None else True
        if not ok:
            self.failures += 1
        shown = show or command
        where = '' if Path(cwd) == self.checkout else '  # in ' + str(Path(cwd)).replace(str(self.home), '$HOME')
        self.lines += ['```sh', '$ ' + self.clean(shown) + where, '```', '```text', self.clean(output) or '(no output)',
                       f'[exit {result.returncode}' + ('' if ok else f', expected {expect}') + ']', '```', '']
        return result

    def prepare_checkout(self):
        files = subprocess.run(['git', 'ls-files', '-co', '--exclude-standard'], cwd=ROOT, text=True,
                               capture_output=True, check=True).stdout.splitlines()
        for name in files:
            source = ROOT / name
            if source.is_file() and not name.startswith(('video/clips/', 'legacy/')):
                dest = self.checkout / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        doc = (ROOT / 'plugins/aios-methods/INTEGRATION.md').read_text()
        patch = doc.split('```diff\n', 1)[1].split('\n```', 1)[0] + '\n'
        subprocess.run(['patch', '-p1', '-s'], cwd=self.checkout, input=patch, text=True, check=True)
        market = self.checkout / '.claude-plugin/marketplace.json'
        data = json.loads(market.read_text())
        names = {p['name'] for p in data['plugins']}
        for pack in STREAM_PACKS:
            entry = self.checkout / 'plugins' / pack / 'MARKETPLACE_ENTRY.json'
            if entry.exists() and pack not in names:
                data['plugins'].append(json.loads(entry.read_text()))
        market.write_text(json.dumps(data, indent=2) + '\n')

    def install(self):
        self.note('## 1. Install in Claude Code')
        self.run('claude --version')
        self.run('claude plugin marketplace add ./', show='claude plugin marketplace add ./')
        self.run('claude plugin install aios@navaigate-aios')
        self.run('claude plugin install ' + self.pack + '@navaigate-aios')
        self.run('claude plugin list')
        self.run('claude plugin details ' + self.pack + '@navaigate-aios')
        self.note('## 2. Install for Codex and Cursor')
        self.run('./install.sh aios')
        self.run('./install.sh ' + self.pack)
        self.run('ls -l ~/.codex/skills ~/.cursor/skills ~/.agents/skills ~/.local/bin | sed "s#' + str(self.checkout) + '#<sandbox-checkout>#g"',
                 show='ls -l ~/.codex/skills ~/.cursor/skills ~/.agents/skills ~/.local/bin')
        self.note('## 3. The installer protects what is already there')
        self.run('./install.sh ' + self.pack, show='./install.sh ' + self.pack + '   # a second time is safe')

    def finish(self):
        verdict = 'PASS' if not self.failures else f'FAIL ({self.failures} step(s) did not exit as expected)'
        self.lines += ['## Result', '', verdict, '']
        out = PROOF / self.pack / 'sandbox_v1.md'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('\n'.join(self.lines))
        print(out, verdict)
        return 0 if not self.failures else 1


def main(pack, use):
    box = Sandbox(pack)
    box.prepare_checkout()
    box.install()
    use(box)
    return box.finish()


if __name__ == '__main__':
    sys.exit('Run the pack script, for example tests/aios-methods/sandbox_v1.py')
