"""tools-images: images and AI video on your own Higgsfield account, with shot-by-shot prompts checked before credits are spent."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__, prompts

CLI_INSTALL = 'curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh'
SKILLS_INSTALL = 'npx skills add higgsfield-ai/skills   (or in Claude Code: /plugin marketplace add higgsfield-ai/skills)'


def skills_installed(home=None):
    home = Path(home or Path.home())
    dirs = [home / d for d in ('.claude/skills', '.agents/skills', '.codex/skills', '.cursor/skills')]
    if any((d / 'higgsfield-generate/SKILL.md').is_file() for d in dirs):
        return True
    cache = home / '.claude/plugins/cache'
    return cache.is_dir() and any(cache.glob('*/higgsfield*/*/skills/higgsfield-generate/SKILL.md'))


def doctor(_args):
    print('tools-images ' + __version__)
    code = 0
    cli = shutil.which('higgsfield')
    if not cli:
        print('Higgsfield CLI: not installed. ' + CLI_INSTALL)
        code = 2
    else:
        status = subprocess.run([cli, 'account', 'status'], capture_output=True, text=True, timeout=60)
        signed_in = status.returncode == 0
        print('Higgsfield CLI: installed, ' + ('signed in' if signed_in else 'not signed in. Run: higgsfield auth login'))
        code = code or (0 if signed_in else 2)
    print("Higgsfield's own skills: " + ('installed' if skills_installed() else 'not installed. ' + SKILLS_INSTALL))
    return code


def check(args):
    problems = prompts.check_video(Path(args.prompt).expanduser().read_text(), args.seconds)
    if problems:
        print('FAIL: %d thing(s) to fix before you spend credits' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: four sections, shots back to back, one signature shot. Ready to generate.')
    return 0


def do_log(args):
    entry = prompts.log(args.folder, args.prompt, args.model, args.job, args.result, args.note or '')
    print('Logged %s on %s in %s' % (entry['prompt_file'], entry['model'], Path(args.folder) / 'manifest_v1.jsonl'))
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'northwind-cake_video-prompt_v1.txt'
    path.write_text(prompts.SAMPLE)
    print('A practice 10-second video prompt (fictional Northwind Bakery): %s' % path)
    print('Next: tools-images check %s --seconds 10' % path)
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-images', description=__doc__)
    p.add_argument('--version', action='version', version='tools-images ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help="the Higgsfield CLI, sign-in and Higgsfield's skills").set_defaults(run=doctor)
    s = sub.add_parser('check', help='check a shot-by-shot video prompt before generating')
    s.add_argument('prompt')
    s.add_argument('--seconds', type=int, help='the target length')
    s.set_defaults(run=check)
    s = sub.add_parser('log', help='record a generation in the folder manifest')
    s.add_argument('folder')
    s.add_argument('--prompt', required=True)
    s.add_argument('--model', required=True)
    s.add_argument('--job', default='')
    s.add_argument('--result', default='')
    s.add_argument('--note')
    s.set_defaults(run=do_log)
    s = sub.add_parser('sample', help='a practice video prompt')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print('The Higgsfield CLI did not answer. Check your connection and try again.', file=sys.stderr)
        return 2
