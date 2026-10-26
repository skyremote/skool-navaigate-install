"""ship-pack: scaffold, check, version and list a Claude Code plugin ("pack") you can give to others.

Standard library only. It never overwrites an existing file or folder.
Exit codes: 0 done, 1 check found errors, 2 refused or bad input.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

from . import templates

NAME = re.compile(r'^[a-z0-9][a-z0-9-]{1,40}$')
SEMVER = re.compile(r'^\d+\.\d+\.\d+$')
TODO = 'TODO(ship-pack)'
SECRET_PATTERNS = [
    ('an Anthropic or OpenAI style key', re.compile(r'sk-[A-Za-z0-9_-]{20,}')),
    ('a JWT or OAuth token', re.compile(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+')),
    ('a GitHub token', re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}')),
    ('an AWS access key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('a Slack token', re.compile(r'xox[abprs]-[A-Za-z0-9-]{10,}')),
    ('a private key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
]
HOME_PATH = re.compile(r'(/Users/|/home/)(?!<|\$|you\b|your|member\b|example\b)[A-Za-z0-9._-]+/')
SECRET_KEY_NAME = re.compile(r'(token|secret|password|api_?key|apikey|credential)', re.I)
SKIP_DIRS = {'.git', '__pycache__', 'results', 'node_modules', '.venv'}


class Refused(Exception):
    """Stopped before changing anything."""


def check_name(name):
    if not NAME.match(name):
        raise Refused('Use a short lower-case name with letters, digits and dashes, for example invoice-builder.')
    return name


def write_new(path, text, mode=None):
    if path.exists():
        raise Refused(str(path) + ' already exists. Nothing changed.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if mode:
        path.chmod(mode)


def frontmatter(text):
    if not text.startswith('---\n'):
        return None, text
    end = text.find('\n---', 4)
    if end < 0:
        return None, text
    data = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(':')
        if sep and not line.startswith((' ', '\t')):
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data, text[end + 4:]


def scaffold(target, name, description, skill, author, depends, skill_source=None):
    if target.exists():
        raise Refused(str(target) + ' already exists. Pick another name or folder.')
    today = datetime.date.today().isoformat()
    manifest = {'name': name, 'version': '0.1.0', 'description': description, 'author': {'name': author}, 'license': 'MIT'}
    if depends:
        manifest['dependencies'] = depends
    files = {
        '.claude-plugin/plugin.json': json.dumps(manifest, indent=2) + '\n',
        'README.md': templates.README.format(name=name, description=description, skill=skill),
        'CHANGELOG.md': templates.CHANGELOG.format(version='0.1.0', date=today, note='First version.'),
        'MARKETPLACE_ENTRY.json': json.dumps({'name': name, 'source': './' + name, 'version': '0.1.0',
                                              'description': description}, indent=2) + '\n',
        'tests/test_pack.py': templates.TEST_PACK,
        '.gitignore': 'evals/results/\n__pycache__/\n*.pyc\n.env\n.env.*\n',
    }
    for case, (prompt, pattern) in templates.EVAL_CASES.items():
        files[f'evals/{case}/prompt.md'] = prompt.format(todo=TODO)
        files[f'evals/{case}/graders/result.md'] = templates.REGEX_GRADER.format(pattern=pattern.format(todo=TODO))
        files[f'evals/{case}/graders/skill-fired.md'] = templates.SKILL_GRADER.format(skill=skill)
    if skill_source is None:
        files[f'skills/{skill}/SKILL.md'] = templates.SKILL.format(skill=skill, todo=TODO)
    staged = Path(str(target) + '.ship-pack-tmp')
    if staged.exists():
        raise Refused(str(staged) + ' is left over from an earlier run. Remove it yourself, then try again.')
    try:
        for rel, text in files.items():
            write_new(staged / rel, text)
        write_new(staged / 'install.sh', templates.INSTALL_SH.format(name=name), mode=0o755)
        if skill_source is not None:
            shutil.copytree(skill_source, staged / 'skills' / skill, ignore=shutil.ignore_patterns(*SKIP_DIRS))
        staged.rename(target)
    except BaseException:
        if staged.exists():
            shutil.rmtree(staged)
        raise
    return target


def cmd_new(args):
    name = check_name(args.name)
    skill = check_name(args.skill or name)
    description = args.description or f'{TODO}: one or two sentences on what {name} does and when to use it.'
    target = scaffold(Path(args.dir) / name, name, description, skill, args.author, args.depends)
    print('Created ' + str(target))
    print_next(target)
    return 0


def cmd_from_skill(args):
    source = Path(args.skill_dir).expanduser()
    skill_md = source / 'SKILL.md'
    if not skill_md.is_file():
        raise Refused('No SKILL.md in ' + str(source) + '. Point at the folder that holds it.')
    meta, _ = frontmatter(skill_md.read_text())
    if not meta or not meta.get('name') or not meta.get('description'):
        raise Refused('SKILL.md needs frontmatter with name and description first.')
    skill = check_name(meta['name'])
    problems = scan_tree(source)
    if problems:
        for problem in problems:
            print('Problem: ' + problem, file=sys.stderr)
        raise Refused('Fix those in the skill before you package it, because the pack will be public.')
    name = check_name(args.name or skill)
    target = scaffold(Path(args.dir) / name, name, meta['description'], skill, args.author, args.depends, skill_source=source)
    print('Packaged skill ' + skill + ' as ' + str(target))
    print_next(target)
    return 0


def print_next(target):
    print('Next:')
    print('  1. Fill every ' + TODO + ' line (the eval prompts and graders, and the skill if new).')
    print('  2. ship-pack check ' + str(target))
    print('  3. python3 -m unittest discover ' + str(target / 'tests'))
    print('  4. claude plugin validate ' + str(target) + ' --strict')
    print('  5. claude plugin eval ' + str(target) + ' --runs 1')


def files_in(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


def scan_tree(root):
    problems = []
    for path in sorted(files_in(root)):
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(root)
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                problems.append(f'{rel}: looks like {label}. Move it to userConfig with "sensitive": true')
        if HOME_PATH.search(text):
            problems.append(f'{rel}: contains a personal home path. Use $HOME or ~ instead')
    return problems


def check_pack(root):
    errors, warnings = [], []
    manifest_path = root / '.claude-plugin/plugin.json'
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as exc:
        return ['.claude-plugin/plugin.json is missing or not valid JSON (' + str(exc).split(':')[0] + ')'], []
    name, version = manifest.get('name', ''), manifest.get('version', '')
    if not NAME.match(str(name)):
        errors.append('plugin.json name must be lower-case letters, digits and dashes')
    elif name != root.name:
        warnings.append(f'plugin.json name "{name}" differs from the folder name "{root.name}"')
    if not SEMVER.match(str(version)):
        errors.append('plugin.json version must look like 1.2.3')
    description = str(manifest.get('description', ''))
    if not description:
        errors.append('plugin.json needs a description')
    if not isinstance(manifest.get('author'), dict) or not manifest['author'].get('name'):
        warnings.append('plugin.json has no author name')
    for key, spec in (manifest.get('userConfig') or {}).items():
        if SECRET_KEY_NAME.search(key) and not (isinstance(spec, dict) and spec.get('sensitive') is True):
            errors.append(f'userConfig "{key}" looks like a secret: add "sensitive": true so it is kept in the keychain')
    skills = sorted((root / 'skills').glob('*/SKILL.md')) if (root / 'skills').is_dir() else []
    if not skills:
        errors.append('no skills: add skills/<name>/SKILL.md')
    for skill in skills:
        rel = skill.relative_to(root)
        text = skill.read_text()
        meta, body = frontmatter(text)
        if not meta or not meta.get('name') or not meta.get('description'):
            errors.append(f'{rel}: needs frontmatter with name and description')
            continue
        if meta['name'] != skill.parent.name:
            errors.append(f'{rel}: name "{meta["name"]}" must match its folder "{skill.parent.name}"')
        if len(text.splitlines()) >= 500:
            errors.append(f'{rel}: {len(text.splitlines())} lines; keep SKILL.md under 500 and move detail to references/')
        if len(meta['description']) > 1024:
            errors.append(f'{rel}: description is over 1,024 characters')
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', meta['description'].strip()) if s]
        if len(sentences) > 2:
            warnings.append(f'{rel}: description has {len(sentences)} sentences; one or two is easier to trigger')
    cases = sorted(p.parent for p in (root / 'evals').glob('*/prompt.md')) if (root / 'evals').is_dir() else []
    if len(cases) < 3:
        errors.append(f'{len(cases)} eval case(s); write at least three in evals/<case>/prompt.md')
    for case in cases:
        if not list((case / 'graders').glob('*.md')):
            errors.append(f'evals/{case.name}: no graders in graders/')
    for path in sorted(files_in(root)):
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        if TODO in text:
            errors.append(f'{path.relative_to(root)}: still has {TODO} placeholders')
    errors += scan_tree(root)
    entry_path = root / 'MARKETPLACE_ENTRY.json'
    if entry_path.exists():
        try:
            entry = json.loads(entry_path.read_text())
            if entry.get('version') and entry['version'] != version:
                errors.append(f'MARKETPLACE_ENTRY.json version {entry["version"]} does not match plugin.json {version}')
        except ValueError:
            errors.append('MARKETPLACE_ENTRY.json is not valid JSON')
    for tool in (root / 'bin').iterdir() if (root / 'bin').is_dir() else []:
        if tool.is_file() and not os.access(tool, os.X_OK):
            errors.append(f'bin/{tool.name} is not executable: chmod +x bin/{tool.name}')
    if (root / 'CLAUDE.md').exists():
        warnings.append('CLAUDE.md at the plugin root is not loaded; put instructions in a skill')
    readme = (root / 'README.md').read_text() if (root / 'README.md').exists() else ''
    if '/plugin install' not in readme and 'claude plugin install' not in readme:
        warnings.append('README.md has no install line for Claude Code')
    changelog = (root / 'CHANGELOG.md').read_text() if (root / 'CHANGELOG.md').exists() else ''
    if '## ' + str(version) not in changelog:
        warnings.append(f'CHANGELOG.md has no "## {version}" entry')
    if not (root / 'tests').is_dir():
        warnings.append('no tests/ folder')
    return errors, warnings


def cmd_check(args):
    root = Path(args.pack).resolve()
    errors, warnings = check_pack(root)
    for error in errors:
        print('Error: ' + error)
    for warning in warnings:
        print('Warning: ' + warning)
    print(f'{root.name}: {len(errors)} error(s), {len(warnings)} warning(s)')
    if not errors:
        print('Next: claude plugin validate ' + args.pack + ' --strict')
    return 1 if errors else 0


def bump_version(version, part):
    major, minor, patch = (int(x) for x in version.split('.'))
    if part == 'major':
        return f'{major + 1}.0.0'
    if part == 'minor':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


def cmd_bump(args):
    root = Path(args.pack)
    manifest_path = root / '.claude-plugin/plugin.json'
    manifest = json.loads(manifest_path.read_text())
    old = manifest.get('version', '')
    if not SEMVER.match(old):
        raise Refused('plugin.json version "' + old + '" is not 1.2.3, so it cannot be bumped.')
    if not args.note.strip():
        raise Refused('Say what changed with --note, because members read the changelog.')
    new = bump_version(old, args.part)
    manifest['version'] = new
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    entry_path = root / 'MARKETPLACE_ENTRY.json'
    if entry_path.exists():
        entry = json.loads(entry_path.read_text())
        entry['version'] = new
        entry_path.write_text(json.dumps(entry, indent=2) + '\n')
    changelog = root / 'CHANGELOG.md'
    text = changelog.read_text() if changelog.exists() else '# Changelog\n'
    head, _, rest = text.partition('\n## ')
    entry = templates.CHANGELOG_ENTRY.format(version=new, date=datetime.date.today().isoformat(), note=args.note.strip())
    changelog.write_text(head.rstrip('\n') + '\n\n' + entry + ('\n## ' + rest if rest else ''))
    print(f'{manifest["name"]}: {old} -> {new}')
    print('Members get it with: claude plugin marketplace update <your-marketplace>, then claude plugin update '
          + manifest['name'] + '@<your-marketplace>')
    return 0


def cmd_marketplace(args):
    root = Path(args.pack)
    manifest = json.loads((root / '.claude-plugin/plugin.json').read_text())
    path = Path(args.file)
    if path.exists():
        market = json.loads(path.read_text())
    else:
        if not args.name or not args.owner:
            raise Refused(str(path) + ' does not exist yet: pass --name and --owner to create it.')
        market = {'name': check_name(args.name), 'owner': {'name': args.owner},
                  'metadata': {'description': args.description or 'Plugins from ' + args.owner + '.'}, 'plugins': []}
    source = args.source or './' + os.path.relpath(root.resolve(), path.resolve().parent.parent)
    entry = {'name': manifest['name'], 'source': source, 'version': manifest['version'],
             'description': manifest.get('description', '')}
    plugins = [p for p in market.get('plugins', []) if p.get('name') != manifest['name']]
    action = 'Updated' if len(plugins) != len(market.get('plugins', [])) else 'Added'
    plugins.append(entry)
    market['plugins'] = plugins
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(market, indent=2) + '\n')
    print(f'{action} {manifest["name"]} {manifest["version"]} in {path} (source {source})')
    print('Check it: claude plugin validate ' + str(path.parent.parent))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog='ship-pack', description='Make a pack (a Claude Code plugin) you can give to others.')
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('new', help='Scaffold a new pack with a skill, three evals, tests and an installer')
    new.add_argument('name')
    new.add_argument('--skill', help='First skill name (default: the pack name)')
    new.add_argument('--description')
    new.add_argument('--dir', default='.')
    frm = sub.add_parser('from-skill', help='Turn an existing skill folder into a pack')
    frm.add_argument('skill_dir')
    frm.add_argument('--name', help='Pack name (default: the skill name)')
    frm.add_argument('--dir', default='.')
    for cmd in (new, frm):
        cmd.add_argument('--author', default='your-name')
        cmd.add_argument('--depends', action='append', default=[], help='Another plugin this one needs (repeatable)')
    new.set_defaults(run=cmd_new)
    frm.set_defaults(run=cmd_from_skill)
    chk = sub.add_parser('check', help='Check a pack before you share it (no network)')
    chk.add_argument('pack')
    chk.set_defaults(run=cmd_check)
    bump = sub.add_parser('bump', help='Raise the version in plugin.json, the marketplace entry and the changelog')
    bump.add_argument('pack')
    bump.add_argument('part', choices=['patch', 'minor', 'major'])
    bump.add_argument('--note', required=True, help='One line on what changed')
    bump.set_defaults(run=cmd_bump)
    market = sub.add_parser('marketplace', help='Add or update this pack in a marketplace.json')
    market.add_argument('pack')
    market.add_argument('--file', default='.claude-plugin/marketplace.json')
    market.add_argument('--name', help='Marketplace name, when creating the file')
    market.add_argument('--owner', help='Owner name, when creating the file')
    market.add_argument('--description', help='Marketplace description, when creating the file')
    market.add_argument('--source', help='Source path in the marketplace (default: relative path to the pack)')
    market.set_defaults(run=cmd_marketplace)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except Refused as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 2

