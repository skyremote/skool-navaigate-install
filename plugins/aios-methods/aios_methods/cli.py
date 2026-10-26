"""aios-methods: safe git worktrees, a glossary, a spec and a loop file.

Standard library only. Every command refuses rather than overwrites.
Exit codes: 0 done, 1 a check found problems, 2 refused or bad input.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

NAME = re.compile(r'^[a-z0-9][a-z0-9-]{0,40}$')
TERM_LINE = re.compile(r'^- \*\*(?P<term>[^*]+)\*\*:\s*(?P<definition>.*)$')
BRANCH_PREFIX = 'work/'


class Refused(Exception):
    """A command stopped before it changed anything."""


def git(args, cwd=None, check=True):
    result = subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise Refused((result.stderr or result.stdout).strip() or 'git ' + ' '.join(args) + ' failed')
    return result


def repo_root(cwd=None):
    result = git(['rev-parse', '--show-toplevel'], cwd=cwd, check=False)
    if result.returncode != 0:
        raise Refused('Not inside a git repository. Run git init first, or cd into your project.')
    return Path(result.stdout.strip())


def main_root(cwd=None):
    """The main worktree, even when called from inside a linked worktree."""
    common = git(['rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=cwd).stdout.strip()
    return Path(common).parent


def check_name(name):
    if not NAME.match(name):
        raise Refused('Use a short lower-case name with letters, digits and dashes, for example add-invoice-export.')
    return name


def worktrees(cwd=None):
    out = git(['worktree', 'list', '--porcelain'], cwd=cwd).stdout
    items, item = [], {}
    for line in out.splitlines() + ['']:
        if not line:
            if item:
                items.append(item)
            item = {}
            continue
        key, _, value = line.partition(' ')
        item[key] = value or True
    for entry in items:
        branch = entry.get('branch', '')
        entry['branch'] = branch[len('refs/heads/'):] if isinstance(branch, str) and branch.startswith('refs/heads/') else ''
    return items


def is_dirty(path):
    return bool(git(['status', '--porcelain'], cwd=path).stdout.strip())


def worktree_new(args):
    name = check_name(args.name)
    root = main_root(repo_root())
    branch = BRANCH_PREFIX + name
    base = args.base or 'HEAD'
    target = Path(args.path).expanduser().resolve() if args.path else root.parent / (root.name + '-' + name)
    if target.exists():
        raise Refused('Folder already exists: ' + str(target) + '. Pick another name or remove that folder yourself.')
    if git(['rev-parse', '--verify', '--quiet', 'refs/heads/' + branch], cwd=root, check=False).returncode == 0:
        raise Refused('Branch ' + branch + ' already exists. Use aios-methods worktree list, or pick another name.')
    git(['rev-parse', '--verify', '--quiet', base + '^{commit}'], cwd=root)
    git(['worktree', 'add', '-b', branch, str(target), base], cwd=root)
    print('Created worktree ' + str(target))
    print('Branch ' + branch + ' (from ' + base + ')')
    print('Next: cd ' + shell_path(target) + ' and start your harness there (claude, codex or cursor-agent).')
    print('When it is merged: aios-methods worktree done ' + name)
    return 0


def shell_path(path):
    text = str(path)
    return "'" + text.replace("'", "'\\''") + "'" if re.search(r'[^\w@%+=:,./-]', text) else text


def worktree_list(args):
    root = main_root(repo_root())
    rows = worktrees(root)
    for entry in rows:
        path = Path(entry['worktree'])
        state = 'missing' if not path.exists() else ('changes' if is_dirty(path) else 'clean')
        label = 'main' if path == root else 'linked'
        print(f"{label:6}  {state:7}  {entry['branch'] or '(detached)':32}  {path}")
    return 0


def worktree_done(args):
    name = check_name(args.name)
    root = main_root(repo_root())
    branch = BRANCH_PREFIX + name
    match = [e for e in worktrees(root) if e['branch'] == branch]
    if not match:
        raise Refused('No worktree on branch ' + branch + '. See aios-methods worktree list.')
    path = Path(match[0]['worktree'])
    if path == root:
        raise Refused('That branch is checked out in your main folder. Switch it to another branch first.')
    if path.exists() and is_dirty(path):
        raise Refused('Uncommitted changes in ' + str(path) + '. Commit or discard them yourself first.')
    into = args.into or current_branch(root)
    merged = git(['merge-base', '--is-ancestor', branch, into], cwd=root, check=False).returncode == 0
    if not merged:
        raise Refused(branch + ' is not merged into ' + into + '. Merge it first (git merge ' + branch + '), or keep the worktree.')
    git(['worktree', 'remove', str(path)], cwd=root)
    print('Removed worktree ' + str(path))
    if args.keep_branch:
        print('Kept branch ' + branch)
    else:
        git(['branch', '-d', branch], cwd=root)
        print('Deleted merged branch ' + branch)
    return 0


def current_branch(root):
    name = git(['symbolic-ref', '--quiet', '--short', 'HEAD'], cwd=root, check=False).stdout.strip()
    if not name:
        raise Refused('Your main folder is on a detached HEAD. Pass --into <branch>.')
    return name


GLOSSARY_HEAD = """# Glossary

One line per term. Use these words, exactly, in prompts, specs, code and commits.
Format: - **Term**: what it means here. Avoid: words that mean the same thing.

"""


def parse_glossary(text):
    terms, problems = [], []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith('- **'):
            continue
        found = TERM_LINE.match(line)
        if not found:
            problems.append(f'line {number}: use - **Term**: definition')
            continue
        term = found.group('term').strip()
        definition = found.group('definition').strip()
        if not definition:
            problems.append(f'line {number}: {term} has no definition')
        terms.append((term, definition, number))
    seen = {}
    for term, _, number in terms:
        key = term.casefold()
        if key in seen:
            problems.append(f'line {number}: {term} is already defined on line {seen[key]}')
        seen.setdefault(key, number)
    names = [t.casefold() for t, _, _ in terms]
    if names != sorted(names):
        problems.append('terms are not in alphabetical order')
    if not terms:
        problems.append('no terms yet: add one with aios-methods glossary add "Term" "definition"')
    return terms, problems


def glossary_init(args):
    path = Path(args.file)
    if path.exists():
        raise Refused(str(path) + ' already exists. Nothing changed.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(GLOSSARY_HEAD)
    print('Created ' + str(path))
    return 0


def glossary_add(args):
    path = Path(args.file)
    text = path.read_text() if path.exists() else GLOSSARY_HEAD
    term, definition = args.term.strip(), args.definition.strip()
    if not term or '*' in term or '\n' in term + definition:
        raise Refused('A term is one line of plain words.')
    if not definition:
        raise Refused('Give the term a definition.')
    terms, _ = parse_glossary(text)
    if any(t.casefold() == term.casefold() for t, _, _ in terms):
        raise Refused(term + ' is already in ' + str(path) + '. Edit that line instead.')
    line = '- **' + term + '**: ' + definition.rstrip('.') + '.'
    if args.avoid:
        line += ' Avoid: ' + args.avoid.strip() + '.'
    lines = text.splitlines()
    entries = [(i, TERM_LINE.match(l).group('term')) for i, l in enumerate(lines) if TERM_LINE.match(l)]
    index = len(lines)
    for i, existing in entries:
        if existing.casefold() > term.casefold():
            index = i
            break
    else:
        if entries:
            index = entries[-1][0] + 1
    lines.insert(index, line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines).rstrip('\n') + '\n')
    print('Added ' + term + ' to ' + str(path))
    return 0


def glossary_check(args):
    path = Path(args.file)
    if not path.exists():
        print('No ' + str(path) + '. Run aios-methods glossary init.')
        return 1
    terms, problems = parse_glossary(path.read_text())
    for problem in problems:
        print('Problem: ' + problem)
    print(f'{len(terms)} terms, {len(problems)} problems in {path}')
    return 1 if problems else 0


SPEC = """# {title}

## Goal
One or two sentences: what changes for the user when this is done.

## Who it is for

## Done when
Each line is a check the agent can run. Put the command in backticks.
- [ ] `replace-with-a-real-command`, for example `python3 -m unittest` or `npm test`

## Out of scope

## Decisions
Answers from the interview. One line each, newest last.

## Open questions
- Replace this line with the first question, or write None.
"""


def section(text, title):
    found = re.search(r'^## ' + re.escape(title) + r'\s*$(?P<body>.*?)(?=^## |\Z)', text, re.M | re.S)
    return found.group('body') if found else None


def spec_new(args):
    slug = check_name(args.slug)
    path = Path(args.dir) / (slug + '.md')
    if path.exists():
        raise Refused(str(path) + ' already exists. Nothing changed.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SPEC.format(title=slug.replace('-', ' ').capitalize()))
    print('Created ' + str(path))
    return 0


def spec_check(args):
    path = Path(args.file)
    if not path.exists():
        print('No ' + str(path))
        return 1
    text = path.read_text()
    problems = []
    goal = section(text, 'Goal')
    if goal is None or not re.sub(r'One or two sentences:.*', '', goal).strip():
        problems.append('Goal is empty')
    done = section(text, 'Done when') or ''
    real = [line for line in done.splitlines() if line.strip().startswith('- ')
            and re.search(r'`[^`]+`', line) and 'replace-with-a-real-command' not in line]
    if not real:
        problems.append('Done when has no runnable check: add a line with a command in backticks')
    questions = section(text, 'Open questions')
    if questions is None:
        problems.append('Open questions section is missing')
    else:
        open_lines = [l for l in questions.splitlines() if l.strip().startswith('- ')
                      and not re.match(r'^-\s*(none\.?|replace this line.*)$', l.strip(), re.I)]
        if any('replace this line' in l.lower() for l in questions.splitlines()):
            problems.append('Open questions still holds the template line: answer it or write None')
        if open_lines:
            problems.append(f'{len(open_lines)} open question(s): answer them before you build')
    for problem in problems:
        print('Problem: ' + problem)
    print(f'{len(real)} runnable check(s), {len(problems)} problem(s) in {path}')
    return 1 if problems else 0


LOOP = """# Default /loop prompt for this project

Each run, do one small unit of work and prove it:

1. Read the spec in docs/specs/ and pick the first unchecked line under "Done when".
2. Make the smallest change that could tick it.
3. Run that line's command. Paste the real output.
4. If it passes, tick the box and commit with a one-line message.
5. If it fails twice on the same line, stop and tell me what you tried.
6. When every box is ticked, say "All checks pass" and stop the loop.

Never push, deploy or delete files from a loop.
"""


def loop_init(args):
    path = Path(args.file)
    if path.exists():
        raise Refused(str(path) + ' already exists. Nothing changed.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(LOOP)
    print('Created ' + str(path))
    print('In Claude Code, type /loop on its own to run it, or /loop 10m to run it every ten minutes.')
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog='aios-methods', description='Working methods: worktrees, glossary, spec and loop files.')
    groups = parser.add_subparsers(dest='group', required=True)

    tree = groups.add_parser('worktree', help='Parallel work in a separate folder and branch').add_subparsers(dest='action', required=True)
    new = tree.add_parser('new', help='Create ../<repo>-<name> on branch work/<name>')
    new.add_argument('name')
    new.add_argument('--base', help='Start from this branch or commit (default: HEAD)')
    new.add_argument('--path', help='Folder to create (default: beside your repo)')
    new.set_defaults(run=worktree_new)
    tree.add_parser('list', help='Show every worktree and whether it has changes').set_defaults(run=worktree_list)
    done = tree.add_parser('done', help='Remove a merged, clean worktree and its branch')
    done.add_argument('name')
    done.add_argument('--into', help='Branch it must be merged into (default: the main folder\'s branch)')
    done.add_argument('--keep-branch', action='store_true')
    done.set_defaults(run=worktree_done)

    gloss = groups.add_parser('glossary', help='One shared word list for you and the agent').add_subparsers(dest='action', required=True)
    for action, run in (('init', glossary_init), ('check', glossary_check)):
        cmd = gloss.add_parser(action)
        cmd.add_argument('--file', default='GLOSSARY.md')
        cmd.set_defaults(run=run)
    add = gloss.add_parser('add')
    add.add_argument('term')
    add.add_argument('definition')
    add.add_argument('--avoid', help='Words people use for the same thing')
    add.add_argument('--file', default='GLOSSARY.md')
    add.set_defaults(run=glossary_add)

    spec = groups.add_parser('spec', help='A short spec with runnable checks').add_subparsers(dest='action', required=True)
    snew = spec.add_parser('new')
    snew.add_argument('slug')
    snew.add_argument('--dir', default='docs/specs')
    snew.set_defaults(run=spec_new)
    scheck = spec.add_parser('check')
    scheck.add_argument('file')
    scheck.set_defaults(run=spec_check)

    loop = groups.add_parser('loop', help='A default prompt for bare /loop').add_subparsers(dest='action', required=True)
    linit = loop.add_parser('init')
    linit.add_argument('--file', default='.claude/loop.md')
    linit.set_defaults(run=loop_init)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except Refused as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 2
