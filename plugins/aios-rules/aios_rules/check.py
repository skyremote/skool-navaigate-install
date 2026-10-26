"""Count what each harness loads into every session, and flag anything over budget.

Token counts are approximate: characters divided by four, rounded up. The aim is a
fast, honest signal that runs anywhere with Python 3.9 and no network.
"""
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

from . import frontmatter

DEFAULTS = {
    'file_lines_target': 150,   # the pack's own target for one rules file
    'file_lines_max': 200,      # Anthropic: target under 200 lines per CLAUDE.md
    'total_lines_max': 300,     # everything always loaded, added together
    'total_tokens_max': 4000,   # approximate tokens, everything always loaded
    'skill_listing_tokens_max': 2000,  # about 1% of a 200k window
}
SKILL_DESCRIPTION_CAP = 1536    # Claude Code truncates description + when_to_use here
MEMORY_LINES = 200              # auto memory: first 200 lines or 25 KB load
MEMORY_BYTES = 25 * 1024
CODEX_MAX_BYTES = 32 * 1024     # Codex project_doc_max_bytes default
IMPORT_DEPTH = 4                # Claude Code: imports recurse up to four hops

IMPORT = re.compile(r'(?<![\w`@])@((?:[^\s`\\]|\\ )+)')


def approx_tokens(chars):
    return int(math.ceil(chars / 4.0))


def read(path):
    try:
        return Path(path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None


def count_lines(text):
    if not text:
        return 0
    return text.count('\n') + (0 if text.endswith('\n') else 1)


class Tally:
    """Collects every loaded item and the flags raised against it."""

    def __init__(self, harness, project, home, budgets):
        self.harness = harness
        self.project = project
        self.home = home
        self.budgets = budgets
        self.items = []
        self.flags = []
        self.notes = []
        self.seen = set()

    def show(self, path):
        path = str(path)
        project, home = str(self.project), str(self.home)
        if path == project or path.startswith(project + os.sep):
            return '.' + path[len(project):] if path != project else '.'
        if path == home or path.startswith(home + os.sep):
            return '~' + path[len(home):]
        return path

    def add(self, path, text, kind, loaded='always', parent=None):
        real = os.path.realpath(str(path))
        if loaded == 'always':
            if real in self.seen:
                return None
            self.seen.add(real)
        item = {
            'path': self.show(path), 'kind': kind, 'loaded': loaded,
            'lines': count_lines(text), 'chars': len(text),
            'tokens': approx_tokens(len(text)),
        }
        if parent:
            item['imported_by'] = self.show(parent)
        self.items.append(item)
        return item

    def flag(self, level, path, message):
        self.flags.append({'level': level, 'path': self.show(path) if path else '', 'message': message})

    def result(self):
        always = [i for i in self.items if i['loaded'] == 'always']
        instructions = [i for i in always if i['kind'] != 'skill-listing']
        listing = [i for i in always if i['kind'] == 'skill-listing']
        totals = {
            'lines': sum(i['lines'] for i in instructions),
            'tokens': sum(i['tokens'] for i in instructions),
            'skill_listing_tokens': sum(i['tokens'] for i in listing),
            'files': len(instructions),
        }
        b = self.budgets
        if totals['lines'] > b['total_lines_max']:
            self.flag('over', None, 'Always-loaded instructions are %d lines, over the %d-line budget.'
                      % (totals['lines'], b['total_lines_max']))
        if totals['tokens'] > b['total_tokens_max']:
            self.flag('over', None, 'Always-loaded instructions are about %d tokens, over the %d-token budget.'
                      % (totals['tokens'], b['total_tokens_max']))
        if totals['skill_listing_tokens'] > b['skill_listing_tokens_max']:
            self.flag('warn', None, 'Skill descriptions are about %d tokens; Claude Code may cut the least-used ones.'
                      ' Run /skill-doctor.' % totals['skill_listing_tokens'])
        over = [f for f in self.flags if f['level'] == 'over']
        return {
            'harness': self.harness, 'project': str(self.project), 'budgets': b,
            'items': self.items, 'totals': totals, 'flags': self.flags, 'notes': self.notes,
            'status': 'over' if over else ('warn' if self.flags else 'ok'),
        }


def file_flags(tally, path, text, label):
    lines = count_lines(text)
    b = tally.budgets
    if re.search(r'\{\{[A-Z_]', text or ''):
        tally.flag('warn', path, '%s still has {{...}} placeholders. Fill them in or delete those lines.' % label)
    if lines > b['file_lines_max']:
        tally.flag('over', path, '%s is %d lines, over the %d-line limit. Move detail into skills or path-scoped rules.'
                   % (label, lines, b['file_lines_max']))
    elif lines > b['file_lines_target']:
        tally.flag('warn', path, '%s is %d lines, over the %d-line target.' % (label, lines, b['file_lines_target']))


def strip_code(text):
    """Blank out fenced blocks and inline code so their @words are not imports."""
    out, fence = [], None
    for line in text.split('\n'):
        marker = line.lstrip()[:3]
        if fence is None and marker in ('```', '~~~'):
            fence = marker
            out.append('')
            continue
        if fence is not None:
            if line.lstrip().startswith(fence):
                fence = None
            out.append('')
            continue
        out.append(re.sub(r'`[^`]*`', '', line))
    return '\n'.join(out)


def resolve_import(raw, base, home):
    raw = raw.replace('\\ ', ' ')
    candidates = [raw]
    trimmed = raw.rstrip('.,;:)!?')
    if trimmed != raw:
        candidates.append(trimmed)
    for candidate in candidates:
        if candidate.startswith('~/'):
            path = Path(home) / candidate[2:]
        elif candidate.startswith('/'):
            path = Path(candidate)
        else:
            path = Path(base) / candidate
        if path.is_file():
            return path, candidate
    return None, trimmed


def load_with_imports(tally, path, kind, depth=0, parent=None):
    text = read(path)
    if text is None:
        return
    item = tally.add(path, text, kind if depth == 0 else 'import', parent=parent)
    if item is None:
        return
    file_flags(tally, path, text, 'This file')
    if depth >= IMPORT_DEPTH:
        if IMPORT.search(strip_code(text)):
            tally.flag('warn', path, 'Imports stop after four hops; deeper @imports here do not load.')
        return
    for match in IMPORT.finditer(strip_code(text)):
        target, shown = resolve_import(match.group(1), Path(path).parent, tally.home)
        if target is None:
            if '/' in shown or '.' in shown:
                tally.flag('warn', path, 'Import @%s points to a file that does not exist.' % shown)
            continue
        load_with_imports(tally, target, kind, depth + 1, parent=path)


def chain(project, stop=None):
    """Directories from the filesystem root (or `stop`) down to the project."""
    project = Path(project).resolve()
    parts = [project] + list(project.parents)
    parts.reverse()
    if stop is not None:
        stop = Path(stop).resolve()
        parts = [p for p in parts if p == stop or stop in p.parents]
    return parts


def git_root(project):
    try:
        out = subprocess.run(['git', '-C', str(project), 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return Path(out.stdout.strip()).resolve()


def git_common_root(project):
    """The main checkout of a repository, so worktrees share one auto-memory folder."""
    try:
        out = subprocess.run(['git', '-C', str(project), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    common = Path(out.stdout.strip())
    return common.parent.resolve() if common.name == '.git' else None


def rule_files(rules):
    rules = Path(rules)
    if not rules.is_dir():
        return []
    return sorted(p for p in rules.rglob('*.md') if p.is_file())


def add_rules(tally, rules, scope):
    """Rules without `paths` load in every session; scoped rules load on demand."""
    for path in rule_files(rules):
        text = read(path) or ''
        block, body = frontmatter.split(text)
        paths = frontmatter.as_list(frontmatter.parse(block).get('paths'))
        if block is not None and not paths and 'paths' in (block or ''):
            tally.flag('warn', path, 'The paths field is empty or did not parse, so this rule loads in every session.')
        if paths:
            item = tally.add(path, body, scope + '-rule', loaded='on-demand')
            item['paths'] = paths
        else:
            tally.add(path, body, scope + '-rule')
            file_flags(tally, path, body, 'This rule')


def settings_overrides(config, project):
    overrides = {}
    for path in (Path(config) / 'settings.json', Path(project) / '.claude' / 'settings.json',
                 Path(project) / '.claude' / 'settings.local.json'):
        text = read(path)
        if not text:
            continue
        try:
            data = json.loads(text)
        except ValueError:
            continue
        if isinstance(data, dict) and isinstance(data.get('skillOverrides'), dict):
            overrides.update(data['skillOverrides'])
    return overrides


def add_skill_listing(tally, folders, overrides):
    for folder in folders:
        skills = Path(folder)
        if not skills.is_dir():
            continue
        for skill in sorted(skills.glob('*/SKILL.md')):
            meta = frontmatter.parse(frontmatter.split(read(skill) or '')[0])
            name = meta.get('name') or skill.parent.name
            state = overrides.get(name, 'on')
            if str(meta.get('disable-model-invocation', '')).lower() == 'true' or state in ('off', 'user-invocable-only'):
                continue
            listing = '- %s' % name
            if state != 'name-only':
                text = ' '.join(str(meta.get(k, '')) for k in ('description', 'when_to_use')).strip()
                if len(text) > SKILL_DESCRIPTION_CAP:
                    tally.flag('warn', skill, 'Skill description is %d characters; Claude Code cuts it at %d.'
                               % (len(text), SKILL_DESCRIPTION_CAP))
                    text = text[:SKILL_DESCRIPTION_CAP]
                listing += ': ' + text
            tally.add(skill, listing + '\n', 'skill-listing')


def memory_folder_name(path):
    return re.sub(r'[^A-Za-z0-9]', '-', str(path))


def check_claude(project, home, budgets, env=None):
    env = os.environ if env is None else env
    config = Path(env.get('CLAUDE_CONFIG_DIR') or Path(home) / '.claude')
    tally = Tally('claude', project, home, budgets)
    for managed in (Path('/Library/Application Support/ClaudeCode/CLAUDE.md'), Path('/etc/claude-code/CLAUDE.md')):
        if managed.is_file():
            load_with_imports(tally, managed, 'managed')
    if (config / 'CLAUDE.md').is_file():
        load_with_imports(tally, config / 'CLAUDE.md', 'user')
    add_rules(tally, config / 'rules', 'user')
    dirs = chain(project)
    names = ('CLAUDE.md', '.claude/CLAUDE.md', 'CLAUDE.local.md')
    user_file = os.path.realpath(str(config / 'CLAUDE.md'))

    def project_file(path):
        # Your ~/.claude/CLAUDE.md sits in the chain when you work under ~, but it is the
        # user file: it loads anyway and never stops Claude Code reading AGENTS.md.
        return path.is_file() and os.path.realpath(str(path)) != user_file

    has_claude = any(project_file(d / n) for d in dirs for n in names)
    for d in dirs:
        if has_claude:
            for n in names:
                if project_file(d / n):
                    load_with_imports(tally, d / n, 'local' if n == 'CLAUDE.local.md' else 'project')
        else:
            for n in ('AGENTS.md', '.claude/AGENTS.md'):
                if (d / n).is_file():
                    load_with_imports(tally, d / n, 'agents')
    root = git_root(project) or Path(project).resolve()
    for d in chain(project, stop=root):
        if d != Path(home).resolve():
            add_rules(tally, d / '.claude' / 'rules', 'project')
    if not has_claude and not any((d / 'AGENTS.md').is_file() for d in dirs):
        tally.flag('warn', None, 'No CLAUDE.md or AGENTS.md found from this folder up. Run: aios-rules init')
    elif has_claude and (Path(project) / 'AGENTS.md').is_file():
        bridge = read(Path(project) / 'CLAUDE.md') or ''
        if not IMPORT.search(strip_code(bridge)) or 'AGENTS.md' not in strip_code(bridge):
            tally.flag('warn', Path(project) / 'CLAUDE.md',
                       'CLAUDE.md does not import AGENTS.md, so Claude Code skips AGENTS.md. Add the line @AGENTS.md.')
    memory_root = git_common_root(project) or root
    memory = config / 'projects' / memory_folder_name(memory_root) / 'memory' / 'MEMORY.md'
    text = read(memory)
    if text is not None:
        loaded = '\n'.join(text.split('\n')[:MEMORY_LINES])
        loaded = loaded.encode('utf-8')[:MEMORY_BYTES].decode('utf-8', 'ignore')
        tally.add(memory, loaded, 'auto-memory')
        if count_lines(text) > MEMORY_LINES or len(text.encode('utf-8')) > MEMORY_BYTES:
            tally.flag('warn', memory, 'MEMORY.md is past 200 lines or 25 KB; the rest does not load.')
    add_skill_listing(tally, [config / 'skills', Path(project) / '.claude' / 'skills'],
                      settings_overrides(config, project))
    tally.notes.append('Plugin skills, MCP tool names and the system prompt are not counted. Run /context in a session for the full picture.')
    return tally.result()


def check_codex(project, home, budgets, env=None):
    env = os.environ if env is None else env
    codex_home = Path(env.get('CODEX_HOME') or Path(home) / '.codex')
    tally = Tally('codex', project, home, budgets)
    total = 0
    for name in ('AGENTS.override.md', 'AGENTS.md'):
        if (codex_home / name).is_file():
            text = read(codex_home / name) or ''
            tally.add(codex_home / name, text, 'user')
            file_flags(tally, codex_home / name, text, 'This file')
            break
    root = git_root(project) or Path(project).resolve()
    for d in chain(project, stop=root):
        for name in ('AGENTS.override.md', 'AGENTS.md'):
            path = d / name
            if path.is_file():
                text = read(path) or ''
                total += len(text.encode('utf-8'))
                tally.add(path, text, 'agents')
                file_flags(tally, path, text, 'This file')
                break
    if total > CODEX_MAX_BYTES:
        tally.flag('over', None, 'Project AGENTS.md files total %d bytes; Codex stops reading at %d.' % (total, CODEX_MAX_BYTES))
    if total == 0:
        tally.flag('warn', None, 'Codex finds no AGENTS.md between the repository root and this folder.')
    tally.notes.append('Codex does not expand @imports and does not read CLAUDE.md or .claude/rules/.')
    return tally.result()


def check_cursor(project, home, budgets, env=None):
    tally = Tally('cursor', project, home, budgets)
    project = Path(project).resolve()
    for name in ('AGENTS.md', '.cursorrules'):
        if (project / name).is_file():
            text = read(project / name) or ''
            tally.add(project / name, text, 'agents' if name == 'AGENTS.md' else 'legacy-rules')
            file_flags(tally, project / name, text, 'This file')
    rules = project / '.cursor' / 'rules'
    if rules.is_dir():
        for path in sorted(p for p in rules.rglob('*') if p.suffix in ('.mdc', '.md') and p.is_file()):
            text = read(path) or ''
            block, body = frontmatter.split(text)
            meta = frontmatter.parse(block)
            if str(meta.get('alwaysApply', '')).lower() == 'true':
                tally.add(path, body, 'cursor-rule')
                file_flags(tally, path, body, 'This rule')
            else:
                item = tally.add(path, body, 'cursor-rule', loaded='on-demand')
                item['paths'] = frontmatter.as_list(meta.get('globs'))
    if not (project / 'AGENTS.md').is_file():
        tally.flag('warn', None, 'Cursor finds no AGENTS.md in this folder.')
    tally.notes.append('Cursor user rules live in its settings, not in files, so they are not counted.')
    return tally.result()


CHECKS = {'claude': check_claude, 'codex': check_codex, 'cursor': check_cursor}


def run(project, harnesses, budgets=None, home=None, env=None):
    budgets = dict(DEFAULTS, **(budgets or {}))
    home = Path(home or os.path.expanduser('~')).resolve()
    project = Path(project).resolve()
    return [CHECKS[h](project, home, budgets, env) for h in harnesses]


def render(results):
    lines = []
    for r in results:
        t = r['totals']
        lines.append('%s: %s' % (r['harness'].upper().replace('CLAUDE', 'CLAUDE CODE'), r['status'].upper()))
        lines.append('  Always loaded: %d files, %d lines, about %d tokens (budget %d lines, %d tokens).'
                     % (t['files'], t['lines'], t['tokens'], r['budgets']['total_lines_max'], r['budgets']['total_tokens_max']))
        for item in r['items']:
            if item['loaded'] == 'always' and item['kind'] != 'skill-listing':
                via = '  (via %s)' % item['imported_by'] if 'imported_by' in item else ''
                lines.append('    %5d lines  %6d tokens  %-13s %s%s' % (item['lines'], item['tokens'], item['kind'], item['path'], via))
        listing = [i for i in r['items'] if i['kind'] == 'skill-listing']
        if listing:
            lines.append('  Skill listing: %d skills, about %d tokens.' % (len(listing), t['skill_listing_tokens']))
        demand = [i for i in r['items'] if i['loaded'] == 'on-demand']
        if demand:
            lines.append('  On demand (loads only for matching files):')
            for item in demand:
                lines.append('    %5d lines  %6d tokens  %s  paths: %s' % (item['lines'], item['tokens'], item['path'], ', '.join(item.get('paths', []))))
        for f in r['flags']:
            where = (' ' + f['path'] + ':') if f['path'] else ''
            lines.append('  %s%s %s' % ('OVER' if f['level'] == 'over' else 'WARN', where, f['message']))
        for note in r['notes']:
            lines.append('  Note: ' + note)
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def exit_code(results):
    return 1 if any(r['status'] == 'over' for r in results) else 0


def main(args):
    harnesses = ['claude', 'codex', 'cursor'] if args.harness == 'all' else [args.harness]
    budgets = {}
    for key in DEFAULTS:
        value = getattr(args, key, None)
        if value is not None:
            budgets[key] = value
    results = run(args.dir, harnesses, budgets)
    if args.json:
        sys.stdout.write(json.dumps(results, indent=2) + '\n')
    else:
        sys.stdout.write(render(results))
    return exit_code(results)
