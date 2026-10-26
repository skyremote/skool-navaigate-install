"""tools-reverse: explain how shipped software works with REA, inside a scope you are allowed to work in, with evidence for every claim."""
import argparse
import shutil
import sys
from pathlib import Path

from . import __version__, report

SETUP = 'npx rea-agents setup   (needs Node.js; choose your agents, review the plan, approve it, restart your agent)'


def rea_skill(home=None):
    home = Path(home or Path.home())
    return any((home / d / 'reverse-engineer-anything/SKILL.md').is_file() for d in ('.claude/skills', '.agents/skills', '.codex/skills', '.cursor/skills'))


def doctor(_args):
    print('tools-reverse ' + __version__)
    node = shutil.which('npx')
    print('Node.js (npx): ' + ('found' if node else 'not found. Install Node.js LTS from nodejs.org first'))
    rea = shutil.which('rea')
    print('rea command: ' + ('installed' if rea else 'not installed (optional: npm install --global rea-agents)'))
    skill = rea_skill()
    print("REA's own skill and MCP registration: " + ('skill found' if skill else 'not set up. ' + SETUP))
    print('Native apps also need an engine REA supports (Ghidra, IDA or Hopper); websites and JavaScript apps do not.')
    return 0 if node and skill else 2


def new(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting %s. Use a new _v2 name.' % out)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.SCOPE.format(target=args.target, question=args.question))
    print('Wrote a scope and findings file: %s. Fill in whose it is and the basis before any analysis.' % out)
    return 0


def check(args):
    problems = report.check(Path(args.file).expanduser().read_text())
    if problems:
        print('FAIL: %d problem(s)' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: a scope you may work in, and every finding has evidence and a status.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'acme-calculator_investigation_v1.md'
    path.write_text(report.SAMPLE)
    print('A practice investigation (fictional): %s\nNext: tools-reverse check %s' % (path, path))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-reverse', description=__doc__)
    p.add_argument('--version', action='version', version='tools-reverse ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help="Node.js and REA's own setup").set_defaults(run=doctor)
    s = sub.add_parser('new', help='a scope and findings file')
    s.add_argument('out')
    s.add_argument('--target', required=True)
    s.add_argument('--question', required=True)
    s.set_defaults(run=new)
    s = sub.add_parser('check', help='check the scope and the findings')
    s.add_argument('file')
    s.set_defaults(run=check)
    s = sub.add_parser('sample', help='a practice investigation')
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
