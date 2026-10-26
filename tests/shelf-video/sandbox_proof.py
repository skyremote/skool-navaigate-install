#!/usr/bin/env python3
"""Sandbox install proof for the shelf packs, as a brand-new member.

It copies this checkout to /tmp, applies the shared-file changes written in each pack's INTEGRATION.md
(the marketplace entries and the installer's pack list), then installs and runs the pack with
HOME=/tmp/aios2-sandbox-e-shelf. Every command, its output and its exit code go into
$AIOS2_PROOF_DIR/<pack>/sandbox_v1.md (outside the repo: build evidence is course material). Nothing touches the real ~/.claude, ~/.codex or ~/.cursor.

Usage: python3 tests/shelf-video/sandbox_proof.py shelf-video|shelf-decks|shelf-invoices
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECKOUT = Path('/tmp/aios2-e-shelf/checkout')
HOME = Path('/tmp/aios2-sandbox-e-shelf')
# Build evidence is course material, not repo content: it goes beside the lessons, outside Git.
PROOF = Path(os.environ.get('AIOS2_PROOF_DIR') or Path.home() / 'NAS_Local/150_Navbot_Classroom/aios-2/build-proof')
WORK = HOME / 'Work'


def prepare_checkout():
    if CHECKOUT.exists():
        shutil.rmtree(CHECKOUT)
    subprocess.run(['rsync', '-a', '--exclude', '.git', '--exclude', 'video/clips', '--exclude', 'excalidraw.log',
                    str(REPO) + '/', str(CHECKOUT) + '/'], check=True)
    market = CHECKOUT / '.claude-plugin/marketplace.json'
    data = json.loads(market.read_text())
    names = {p['name'] for p in data['plugins']}
    for entry in sorted((CHECKOUT / 'plugins').glob('*/MARKETPLACE_ENTRY.json')):
        item = json.loads(entry.read_text())
        if item['name'] not in names:
            data['plugins'].append(item)
    market.write_text(json.dumps(data, indent=2) + '\n')
    diff = REPO / 'plugins/shelf-video/install_pack.diff'
    subprocess.run(['patch', '-p0', '-s', str(CHECKOUT / 'scripts/install_pack.py'), str(diff)], check=True)


def environment():
    env = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'), CODEX_HOME=str(HOME / '.codex'),
               XDG_CONFIG_HOME=str(HOME / '.config'), XDG_DATA_HOME=str(HOME / '.local/share'),
               XDG_CACHE_HOME=str(HOME / '.cache'))
    for key in ('CURSOR_CONFIG_DIR', 'AIOS_CONFIG_DIR', 'CLAUDE_PLUGIN_ROOT'):
        env.pop(key, None)
    # The member's Python packages and the Whisper CLI are tools, like FFmpeg on PATH: reuse the
    # ones already installed on this Mac (read-only) instead of downloading PyTorch again.
    env['PYTHONUSERBASE'] = subprocess.run(['python3', '-m', 'site', '--user-base'], capture_output=True,
                                           text=True).stdout.strip()
    whisper = shutil.which('whisper')
    extra = [str(Path(whisper).parent)] if whisper else []
    env['PATH'] = ':'.join([str(HOME / '.local/bin')] + extra + [env['PATH']])
    return env


class Report:
    def __init__(self, pack):
        self.pack = pack
        self.file = PROOF / pack / 'sandbox_v1.md'
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.lines = ['# Sandbox install proof: ' + pack + ' (v1)', '',
                      'A brand-new member: HOME=' + str(HOME) + ', CLAUDE_CONFIG_DIR=$HOME/.claude, CODEX_HOME=$HOME/.codex.',
                      'The checkout is a copy at ' + str(CHECKOUT) + ' with the INTEGRATION.md changes applied',
                      '(marketplace entries and the installer pack list). All sample data is fictional (Acme Studio).',
                      'Long outputs are trimmed to their last 40 lines.', '']
        self.failed = []
        self.env = environment()

    def run(self, args, expect=0, cwd=None, timeout=900, note=''):
        proc = subprocess.run([str(a) for a in args], cwd=str(cwd or CHECKOUT), env=self.env, text=True,
                              capture_output=True, timeout=timeout)
        out = (proc.stdout + proc.stderr).replace(str(Path.home()), '$REAL_HOME').splitlines()
        if len(out) > 40:
            out = ['[... %d lines trimmed ...]' % (len(out) - 40)] + out[-40:]
        command = shlex.join(str(a) for a in args)
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


def common(r, pack):
    r.run(['claude', '--version'])
    r.run(['claude', 'plugin', 'validate', 'plugins/' + pack, '--strict'])
    r.run(['claude', 'plugin', 'validate', '.claude-plugin/marketplace.json', '--strict'])
    r.run(['claude', 'plugin', 'marketplace', 'add', CHECKOUT])
    r.run(['claude', 'plugin', 'install', 'aios@navaigate-aios'])
    r.run(['claude', 'plugin', 'install', pack + '@navaigate-aios'])
    r.run(['claude', 'plugin', 'list'])
    r.run(['./install.sh', pack], expect=1, note='Codex and Cursor: a pack refuses to install before the start plugin.')
    r.run(['./install.sh', 'aios'])
    r.run(['./install.sh', pack])
    r.run(['./install.sh', pack], note='A second install is safe: it relinks our own links only.')
    r.run(['ls', '-go', HOME / '.codex/skills', HOME / '.cursor/skills', HOME / '.agents/skills', HOME / '.local/bin'])
    r.run(['cat', HOME / '.local/share/aios/packs' / (pack + '.json')])


def video(r):
    whisper_cache = Path.home() / '.cache/whisper/small.en.pt'
    cache = HOME / '.cache/whisper'
    cache.mkdir(parents=True, exist_ok=True)
    if whisper_cache.exists() and not (cache / 'small.en.pt').exists():
        # Reuse the already-downloaded open model file instead of a second 460 MB download.
        (cache / 'small.en.pt').symlink_to(whisper_cache)
    WORK.mkdir(parents=True, exist_ok=True)
    r.run(['python3', '-m', 'pip', 'install', '--user', '--disable-pip-version-check', 'Pillow'],
          note='The tools step from the README. Pillow is already present for this Python, so pip only confirms it.')
    r.run(['whisper', '--help'], note='openai-whisper is installed (MIT). Only the help header is shown.')
    r.run(['ffmpeg', '-version'])
    r.run(['shelf-video', '--version'])
    r.run(['shelf-video', 'settings'])
    r.run(['shelf-video', 'sample', '--out', WORK / 'sam_acme_v1.mp4'])
    r.run(['shelf-video', 'init', WORK / 'sam_acme_v1.mp4'])
    project = WORK / 'sam_acme_v1_EDIT_v1'
    r.run(['shelf-video', 'transcribe', '--project', project])
    r.run(['cat', project / 'transcript/words_v1.txt'])
    r.run(['shelf-video', 'plan', '--project', project, '--show'])
    r.run(['shelf-video', 'render', '--project', project], expect=1, note='Render refuses until the member approves.')
    r.run(['shelf-video', 'approve', '--project', project], expect=1, note='Approval needs the member\'s --yes.')
    r.run(['shelf-video', 'approve', '--project', project, '--yes', '--note', 'Sandbox member approved after reading the plan'],
          note='The sandbox member has read the plan above and approves it.')
    r.run(['shelf-video', 'render', '--project', project])
    r.run(['shelf-video', 'verify', '--project', project])
    r.run(['cat', project / 'exports/edit_v1/captions.srt'])
    r.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,width,height',
           '-of', 'compact', project / 'exports/edit_v1/edited.mp4'])


def main():
    pack = sys.argv[1] if len(sys.argv) > 1 else 'shelf-video'
    if HOME.exists():
        shutil.rmtree(HOME)
    HOME.mkdir(parents=True)
    prepare_checkout()
    r = Report(pack)
    common(r, pack)
    steps = {'shelf-video': video}
    extra = REPO / 'tests' / pack / 'sandbox_steps.py'
    if pack in steps:
        steps[pack](r)
    elif extra.exists():
        sys.path.insert(0, str(extra.parent))
        import sandbox_steps
        sandbox_steps.run(r, HOME, WORK)
    return r.finish()


if __name__ == '__main__':
    raise SystemExit(main())
