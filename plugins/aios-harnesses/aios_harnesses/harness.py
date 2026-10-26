"""One AIOS folder, four harnesses: inspect what each one reads, and keep them the same.

Claude Code, Codex and Cursor are inspected from their own files. Grok Bot runs
on its own computer, so it is checked from a probe answer the member pastes in.
Nothing here prints secret values: MCP env values are shown as names only.
"""
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from . import tomlmini

HARNESSES = ('claude', 'codex', 'cursor', 'grok')
LABEL = {'claude': 'Claude Code', 'codex': 'Codex', 'cursor': 'Cursor', 'grok': 'Grok Bot'}
OK, WARN, DIFF, ASK = 'OK', 'WARN', 'DIFF', 'ASK'
CANON_MCP = Path('.aios') / 'mcp.json'
GROK_REPORT = Path('.aios') / 'grok-bot.txt'
STATE = Path('.aios') / 'state.json'
BEGIN = '# aios-harnesses:begin (managed by `harness sync`; edit .aios/mcp.json instead)'
END = '# aios-harnesses:end'
DEFAULTS_BEGIN = '# aios-harnesses:defaults:begin'
DEFAULTS_END = '# aios-harnesses:defaults:end'
PHRASE_RE = re.compile(r'^Rules check phrase:\s*([a-z]+-[a-z]+-\d{2})\b', re.M)
REF_RE = re.compile(r'^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$')
WORDS_A = ('amber', 'cobalt', 'quiet', 'silver', 'brisk', 'mellow', 'copper', 'lunar')
WORDS_B = ('otter', 'heron', 'maple', 'falcon', 'harbour', 'willow', 'comet', 'badger')

AGENTS_TEMPLATE = """# AGENTS.md: the rules every harness reads in this folder

Keep this file short. Claude Code reads it through CLAUDE.md (`@AGENTS.md`).
Codex and Cursor read it directly. Grok Bot gets it pasted into its instructions.

## Who and what
- Business: (one line on who you are and what the business does).

## Folders
- (folder)/: (what goes in it).

## Never
- Never put passwords, API keys or tokens in this folder.
- Ask before deleting anything you did not create.

## Checks
- Before you start, say the check you will run. At the end, show its result.

Rules check phrase: {phrase} (used by /harness-check; do not edit)
"""


class Paths:
    """Where each harness keeps its files, honouring the harness's own env overrides."""

    def __init__(self, folder, home=None, env=None):
        env = os.environ if env is None else env
        self.env = env
        self.folder = Path(folder).expanduser().resolve()
        self.home = Path(home or env.get('HOME') or Path.home()).expanduser()
        ccd = env.get('CLAUDE_CONFIG_DIR')
        self.claude_dir = Path(ccd).expanduser() if ccd else self.home / '.claude'
        self.claude_json = (self.claude_dir / '.claude.json') if ccd else self.home / '.claude.json'
        self.codex_home = Path(env.get('CODEX_HOME') or self.home / '.codex').expanduser()
        self.cursor_home = self.home / '.cursor'
        self.agents_skills = self.home / '.agents' / 'skills'

    def show(self, path):
        """A short path for people: relative inside the AIOS folder, ~ inside the home folder."""
        path = str(path)
        folder = str(self.folder)
        if path.startswith(folder + os.sep):
            return path[len(folder) + 1:]
        for home in {str(self.home), str(self.home.resolve())}:
            if path == home or path.startswith(home + os.sep):
                return '~' + path[len(home):]
        return path

    def show_folder(self):
        for home in {str(self.home), str(self.home.resolve())}:
            if str(self.folder) == home or str(self.folder).startswith(home + os.sep):
                return '~' + str(self.folder)[len(home):]
        return str(self.folder)


# ---------------------------------------------------------------- small helpers

def read_text(path):
    try:
        return Path(path).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None


def read_json(path, problems=None):
    text = read_text(path)
    if text is None or not text.strip():
        return {}
    try:
        data = json.loads(text)
    except ValueError as exc:
        if problems is not None:
            problems.append('Could not read %s: %s' % (path, exc))
        return {}
    return data if isinstance(data, dict) else {}


def read_toml(path, problems=None):
    text = read_text(path)
    if text is None or not text.strip():
        return {}
    try:
        return tomlmini.loads(text)
    except (tomlmini.TomlError, ValueError, IndexError) as exc:
        if problems is not None:
            problems.append('Could not read %s: %s' % (path, exc))
        return {}


def atomic_write(path, text, mode=0o644):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def backup(path, log):
    path = Path(path)
    if path.exists():
        dest = path.with_name(path.name + '.backup-%d' % time.time_ns())
        shutil.copy2(str(path), str(dest))
        log.append('Backed up %s -> %s' % (path.name, dest.name))


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def meaningful_lines(text):
    """Lines a model would treat as rules: no blanks, no HTML comments."""
    text = re.sub(r'<!--.*?-->', '', text or '', flags=re.S)
    return [line.strip() for line in text.splitlines() if line.strip()]


def check_phrase(text):
    match = PHRASE_RE.search(text or '')
    return match.group(1) if match else None


def new_phrase(rng=None):
    rng = rng or random.SystemRandom()
    return '%s-%s-%02d' % (rng.choice(WORDS_A), rng.choice(WORDS_B), rng.randint(10, 99))


# ---------------------------------------------------------------- rules

def inspect_rules(p):
    """Return {harness: (status, summary, [problems])} for the rules each harness loads."""
    f = p.folder
    agents = f / 'AGENTS.md'
    agents_text = read_text(agents)
    out = {}
    if agents_text is None:
        missing = ('DIFF', 'no AGENTS.md', ['There is no AGENTS.md in %s. Run: harness setup' % p.show_folder()])
        return {'claude': missing, 'codex': missing, 'cursor': missing,
                'grok': (ASK, 'no AGENTS.md', [])}

    # Claude Code: CLAUDE.md wins over AGENTS.md, so it must be the one-line bridge.
    problems, warns = [], []
    claude_md = read_text(f / 'CLAUDE.md')
    if claude_md is None:
        summary = 'AGENTS.md'
    else:
        lines = meaningful_lines(claude_md)
        if lines == ['@AGENTS.md']:
            summary = 'bridge'
        elif '@AGENTS.md' in lines:
            summary = 'bridge + extra'
            problems.append('CLAUDE.md adds %d line(s) that only Claude Code reads. Move them into AGENTS.md and leave CLAUDE.md as the one line @AGENTS.md.' % (len(lines) - 1))
        else:
            summary = 'own CLAUDE.md'
            problems.append('CLAUDE.md does not contain @AGENTS.md, so Claude Code never reads AGENTS.md. Fold what you need into AGENTS.md, then make CLAUDE.md the one line @AGENTS.md.')
    if read_text(f / 'CLAUDE.local.md') is not None:
        problems.append('CLAUDE.local.md adds rules only Claude Code reads. Move them into AGENTS.md or delete the file.')
    rules_dir = f / '.claude' / 'rules'
    if rules_dir.is_dir() and any(rules_dir.glob('*.md')):
        warns.append('.claude/rules/ holds path rules only Claude Code reads. Fine for detail; keep must-follow rules in AGENTS.md.')
    if meaningful_lines(read_text(p.claude_dir / 'CLAUDE.md')):
        warns.append('%s adds personal rules to every Claude Code session.' % p.show(p.claude_dir / 'CLAUDE.md'))
    out['claude'] = ((DIFF if problems else (WARN if warns else OK)), summary, problems + warns)

    # Codex: AGENTS.override.md replaces AGENTS.md in the same folder.
    problems, warns = [], []
    summary = 'AGENTS.md'
    if read_text(f / 'AGENTS.override.md') is not None:
        summary = 'override file'
        problems.append('AGENTS.override.md makes Codex ignore AGENTS.md in this folder. Fold it into AGENTS.md and delete it.')
    for name in ('AGENTS.override.md', 'AGENTS.md'):
        if meaningful_lines(read_text(p.codex_home / name)):
            warns.append('%s adds personal rules to every Codex session.' % p.show(p.codex_home / name))
            break
    out['codex'] = ((DIFF if problems else (WARN if warns else OK)), summary, problems + warns)

    # Cursor: AGENTS.md plus any always-applied project rules.
    problems, warns = [], []
    summary = 'AGENTS.md'
    if read_text(f / '.cursorrules') is not None:
        summary = 'extra rules'
        problems.append('.cursorrules adds rules only Cursor reads. Move them into AGENTS.md and delete .cursorrules.')
    cursor_rules = f / '.cursor' / 'rules'
    if cursor_rules.is_dir():
        for rule in sorted(cursor_rules.glob('*.md*')):
            text = read_text(rule) or ''
            head = text.split('---', 2)[1] if text.startswith('---') and text.count('---') >= 2 else ''
            if re.search(r'^\s*alwaysApply:\s*true\s*$', head, re.M):
                summary = 'extra rules'
                problems.append('.cursor/rules/%s is always applied, so Cursor follows rules the others never see. Move what you need into AGENTS.md and delete the rule.' % rule.name)
            else:
                warns.append('.cursor/rules/%s loads only in Cursor, and only when it matches.' % rule.name)
    out['cursor'] = ((DIFF if problems else (WARN if warns else OK)), summary, problems + warns)
    out['grok'] = (ASK, 'paste AGENTS.md', [])
    return out


# ---------------------------------------------------------------- skills

def skill_dirs(root, problems=None, show=str):
    """{name: real path} for every folder in root that holds a SKILL.md."""
    found = {}
    root = Path(root)
    if not root.is_dir():
        return found
    for child in sorted(root.iterdir()):
        if child.name.startswith('.') or child.name == 'synced':
            continue
        if child.is_symlink() and not child.exists():
            if problems is not None:
                problems.append('Broken skill link: %s' % show(child))
            continue
        if child.is_dir() and (child / 'SKILL.md').is_file():
            found[child.name] = str(child.resolve())
    return found


def skill_view(p, problems=None):
    """Which skill names each harness can see, from the folders its docs list."""
    f, h = p.folder, p.home
    sources = {
        'shared': [p.agents_skills, f / '.agents' / 'skills'],
        'claude': [p.claude_dir / 'skills', f / '.claude' / 'skills'],
        'codex': [p.agents_skills, f / '.agents' / 'skills'],
        'cursor': [p.agents_skills, h / '.cursor' / 'skills', p.claude_dir / 'skills', p.codex_home / 'skills',
                   f / '.agents' / 'skills', f / '.cursor' / 'skills', f / '.claude' / 'skills', f / '.codex' / 'skills'],
    }
    view = {}
    for key, roots in sources.items():
        names = {}
        for root in roots:
            for name, real in skill_dirs(root, problems if key == 'shared' or key == 'claude' else None, p.show).items():
                names.setdefault(name, real)
        view[key] = names
    return view


def inspect_skills(p):
    problems = []
    view = skill_view(p, problems)
    shared = set(view['shared'])
    out = {}
    for h in ('claude', 'codex', 'cursor'):
        seen = set(view[h])
        missing = sorted(shared - seen)
        issues = []
        if missing:
            issues.append('%s cannot see %d shared skill(s): %s. Fix: harness sync' % (LABEL[h], len(missing), ', '.join(missing)))
        status = DIFF if missing else OK
        out[h] = (status, '%d/%d' % (len(shared & seen), len(shared)), issues)
    # Skills outside the shared folder are seen by some harnesses and not others.
    outside = {}
    for h in ('claude', 'codex', 'cursor'):
        for name in set(view[h]) - shared:
            outside.setdefault(name, []).append(LABEL[h])
    notes = []
    for name in sorted(outside):
        who = outside[name]
        if len(who) < 3:
            notes.append('Skill "%s" lives outside ~/.agents/skills, so only %s see(s) it. Move it into ~/.agents/skills to share it.' % (name, ' and '.join(who)))
    for problem in problems:
        notes.append(problem)
    out['grok'] = (ASK, 'see its Skills page', [])
    return out, notes, len(shared)


# ---------------------------------------------------------------- MCP servers

def canonical_servers(p, problems=None):
    data = read_json(p.folder / CANON_MCP, problems)
    servers = data.get('mcpServers', {})
    return servers if isinstance(servers, dict) else {}


def signature(server):
    """What makes two MCP entries the same server: the command and args, or the URL."""
    if not isinstance(server, dict):
        return ('?',)
    if server.get('url'):
        return ('url', str(server['url']))
    args = server.get('args') or []
    return ('cmd', str(server.get('command', '')), tuple(str(a) for a in args))


def harness_servers(p, problems=None):
    """{harness: {name: server dict}} from each harness's own config files."""
    f = p.folder
    claude = {}
    cj = read_json(p.claude_json, problems)
    if isinstance(cj.get('mcpServers'), dict):
        claude.update(cj['mcpServers'])
    proj = (cj.get('projects') or {}).get(str(f)) or {}
    if isinstance(proj.get('mcpServers'), dict):
        claude.update(proj['mcpServers'])
    claude_project = read_json(f / '.mcp.json', problems).get('mcpServers') or {}
    claude.update(claude_project if isinstance(claude_project, dict) else {})

    codex = {}
    for path in (p.codex_home / 'config.toml', f / '.codex' / 'config.toml'):
        tables = read_toml(path, problems).get('mcp_servers') or {}
        if isinstance(tables, dict):
            codex.update(tables)

    cursor = {}
    for path in (p.cursor_home / 'mcp.json', f / '.cursor' / 'mcp.json'):
        servers = read_json(path, problems).get('mcpServers') or {}
        if isinstance(servers, dict):
            cursor.update(servers)
    return {'claude': claude, 'codex': codex, 'cursor': cursor}


def claude_approval(p, name):
    """Claude Code asks before it starts a project .mcp.json server. Return its state."""
    cj = read_json(p.claude_json)
    proj = (cj.get('projects') or {}).get(str(p.folder)) or {}
    settings = {}
    for path in (p.claude_dir / 'settings.json', p.folder / '.claude' / 'settings.json',
                 p.folder / '.claude' / 'settings.local.json'):
        settings.update(read_json(path))
    if name in (proj.get('disabledMcpjsonServers') or []) or name in (settings.get('disabledMcpjsonServers') or []):
        return 'rejected'
    if proj.get('enableAllProjectMcpServers') or settings.get('enableAllProjectMcpServers'):
        return 'approved'
    if name in (proj.get('enabledMcpjsonServers') or []) or name in (settings.get('enabledMcpjsonServers') or []):
        return 'approved'
    return 'pending'


def codex_trusted(p):
    cfg = read_toml(p.codex_home / 'config.toml')
    projects = cfg.get('projects') or {}
    entry = projects.get(str(p.folder)) or {}
    return isinstance(entry, dict) and entry.get('trust_level') == 'trusted'


def inspect_mcp(p):
    problems = []
    canon = canonical_servers(p, problems)
    found = harness_servers(p, problems)
    project_codex = read_toml(p.folder / '.codex' / 'config.toml').get('mcp_servers') or {}
    project_claude = read_json(p.folder / '.mcp.json').get('mcpServers') or {}
    out = {}
    notes = list(problems)
    for h in ('claude', 'codex', 'cursor'):
        have = found[h]
        issues, warns = [], []
        good = 0
        for name, server in sorted(canon.items()):
            if name not in have:
                issues.append('%s is missing MCP server "%s". Fix: harness sync' % (LABEL[h], name))
            elif signature(have[name]) != signature(server):
                issues.append('%s runs a different "%s" (%s) from .aios/mcp.json. Fix: harness sync' % (LABEL[h], name, describe(have[name])))
            elif h == 'codex' and have[name].get('enabled') is False:
                issues.append('Codex has "%s" switched off (enabled = false).' % name)
            else:
                good += 1
                if h == 'claude' and name in project_claude:
                    state = claude_approval(p, name)
                    if state == 'rejected':
                        issues.append('Claude Code was told not to run "%s". Run /mcp in Claude Code and enable it.' % name)
                    elif state == 'pending':
                        warns.append('Claude Code will ask you to approve "%s" the next time it opens this folder. Say yes.' % name)
                if h == 'codex' and name in project_codex and not codex_trusted(p):
                    warns.append('Codex reads .codex/config.toml only in a trusted folder. Trust this folder when Codex asks.')
        for name in sorted(set(have) - set(canon)):
            warns.append('%s also has "%s", which is not in .aios/mcp.json. Add it there to share it: harness mcp add %s ...' % (LABEL[h], name, name))
        status = DIFF if issues else (WARN if warns else OK)
        out[h] = (status, '%d/%d' % (good, len(canon)), issues + sorted(set(warns)))
    out['grok'] = (ASK, 'add in its settings', [])
    return out, notes, canon


def describe(server):
    sig = signature(server)
    if sig[0] == 'url':
        return sig[1]
    return ' '.join((sig[1],) + sig[2]).strip()


# ---------------------------------------------------------------- Grok Bot

def grok_probe(p):
    phrase = check_phrase(read_text(p.folder / 'AGENTS.md')) or '(run harness setup first)'
    return ('Answer in three short parts. RULES: the rules check phrase from the AIOS rules I gave you. '
            'MCP: the names of every MCP server or plugin you can use, one per line. '
            'SKILLS: the names of the skills you can use, one per line.'), phrase


def inspect_grok(p, canon, shared_skills):
    """Compare a pasted Grok Bot probe answer with the folder. Returns (rules, skills, mcp) rows."""
    text = read_text(p.folder / GROK_REPORT)
    if text is None:
        hint = ['Grok Bot: run `harness grok`, paste the probe into Grok Bot, save its answer as .aios/grok-bot.txt, then run the check again.']
        return (ASK, 'not checked', hint), (ASK, 'not checked', []), (ASK, 'not checked', [])
    low = text.lower()
    phrase = check_phrase(read_text(p.folder / 'AGENTS.md'))
    if phrase and phrase in low:
        rules = (OK, 'phrase matches', [])
    else:
        rules = (DIFF, 'phrase missing', ['Grok Bot did not give the rules check phrase. Paste AGENTS.md into its instructions again.'])
    missing = [n for n in sorted(canon) if n.lower() not in low]
    mcp = (DIFF if missing else OK, '%d/%d' % (len(canon) - len(missing), len(canon)),
           ['Grok Bot is missing MCP server "%s". Add it in Grok Bot (see harness grok).' % n for n in missing])
    have = [n for n in sorted(shared_skills) if n.lower() in low]
    skills = (OK if have or not shared_skills else WARN, '%d/%d named' % (len(have), len(shared_skills)),
              [] if have or not shared_skills else ['Grok Bot named none of your shared skills. That is normal: it uses its own plugins and skills.'])
    return rules, skills, mcp


def grok_instructions(p):
    canon = canonical_servers(p)
    probe, phrase = grok_probe(p)
    lines = ['Grok Bot setup (it runs on its own computer, so you add things in the app)', '',
             '1. Rules: open Grok Bot, then Customize, and paste the whole of AGENTS.md into its instructions.',
             '2. MCP servers: add each one below in Grok Bot (Customize, then MCPs, then add a custom server).',
             '   If your version has no form, ask Grok Bot in chat to "add a custom MCP server" with these values.']
    if not canon:
        lines.append('   (No servers in .aios/mcp.json yet. Add one with: harness mcp add <name> -- <command> [args])')
    for name, server in sorted(canon.items()):
        lines.append('   - Name: %s' % name)
        if server.get('url'):
            lines.append('     Type: remote (URL)   URL: %s' % server['url'])
            lines.append('     The URL must be reachable from the internet; localhost will not work.')
        else:
            lines.append('     Type: command (stdio)   Command: %s' % server.get('command', ''))
            lines.append('     Arguments: %s' % (' '.join(str(a) for a in server.get('args') or []) or 'none'))
            lines.append('     The command must exist on Grok Bot\'s computer, not only on your Mac.')
        env = server.get('env') or {}
        if env:
            lines.append('     Environment variables: %s (type the values in Grok Bot; never in a file)' % ', '.join(sorted(env)))
    lines += ['', '3. Check: paste this into a new Grok Bot chat:', '', '   ' + probe, '',
              '4. Save Grok Bot\'s whole answer as .aios/grok-bot.txt, then run: harness check',
              '   The rules check phrase it should give back is: %s' % phrase]
    return '\n'.join(lines)


# ---------------------------------------------------------------- live probes

LIVE_PROMPT = 'Reply with only the rules check phrase from the rules file you loaded for this folder. Nothing else.'


def live_commands():
    return {
        'claude': (['claude', '-p', LIVE_PROMPT], ['claude', 'mcp', 'list']),
        'codex': (['codex', 'exec', '--skip-git-repo-check', LIVE_PROMPT], ['codex', 'mcp', 'list']),
        'cursor': (['cursor-agent', '-p', LIVE_PROMPT, '--output-format', 'text'], ['cursor-agent', 'mcp', 'list']),
    }


def run_live(p, canon, runner=None, timeout=180):
    """Ask each installed harness CLI for the phrase and its MCP list. Costs one short prompt each."""
    runner = runner or subprocess.run
    phrase = check_phrase(read_text(p.folder / 'AGENTS.md'))
    results = {}
    for h, (ask, mcp) in live_commands().items():
        if not shutil.which(ask[0], path=p.env.get('PATH')):
            results[h] = (WARN, 'not installed', ['%s CLI (%s) is not on PATH, so it was not asked.' % (LABEL[h], ask[0])])
            continue
        issues = []
        try:
            said = runner(ask, cwd=str(p.folder), capture_output=True, text=True, timeout=timeout, env=dict(p.env))
            answer = (said.stdout or '') + (said.stderr or '')
            if said.returncode != 0:
                issues.append('%s did not answer (exit %d). Sign in, then try again.' % (LABEL[h], said.returncode))
            elif not phrase or phrase not in answer:
                issues.append('%s gave a different rules phrase, so it read a different rules file.' % LABEL[h])
            listed = runner(mcp, cwd=str(p.folder), capture_output=True, text=True, timeout=timeout, env=dict(p.env))
            text = (listed.stdout or '') + (listed.stderr or '')
            for name in sorted(canon):
                if name not in text:
                    issues.append('%s mcp list does not show "%s".' % (LABEL[h], name))
        except (OSError, subprocess.TimeoutExpired) as exc:
            issues.append('%s could not be asked: %s' % (LABEL[h], exc.__class__.__name__))
        results[h] = (DIFF if issues else OK, 'asked live', issues)
    return results


# ---------------------------------------------------------------- check

def check(p, live=False, runner=None):
    rules = inspect_rules(p)
    skills, skill_notes, shared_count = inspect_skills(p)
    mcp, mcp_notes, canon = inspect_mcp(p)
    shared_names = set(skill_view(p)['shared'])
    rules['grok'], skills['grok'], mcp['grok'] = inspect_grok(p, canon, shared_names)
    rows = [('Rules (AGENTS.md)', rules), ('Skills (%d shared)' % shared_count, skills),
            ('MCP servers (%d)' % len(canon), mcp)]
    if live:
        rows.append(('Live answer', run_live(p, canon, runner)))
    differs, warnings = [], []
    for _title, row in rows:
        for h in HARNESSES:
            if h not in row:
                continue
            status, _summary, issues = row[h]
            for issue in issues:
                (differs if status == DIFF else warnings).append(issue)
    warnings.extend(skill_notes + mcp_notes)
    return {'folder': p.show_folder(), 'rows': rows, 'differs': dedupe(differs), 'warnings': dedupe(warnings)}


def dedupe(items):
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def render(report):
    width = 22
    col = 18
    lines = ['AIOS harness check   folder: %s' % report['folder'], '',
             ' ' * width + ''.join(LABEL[h].ljust(col) for h in HARNESSES)]
    for title, row in report['rows']:
        cells = []
        for h in HARNESSES:
            if h in row:
                status, summary, _ = row[h]
                cells.append(('%s %s' % (status, summary))[:col - 1].ljust(col))
            else:
                cells.append(''.ljust(col))
        lines.append(title.ljust(width) + ''.join(cells))
    lines.append('')
    if report['differs']:
        lines.append('What differs')
        for i, item in enumerate(report['differs'], 1):
            lines.append('%d. %s' % (i, item))
        lines.append('')
    if report['warnings']:
        lines.append('Worth knowing')
        for item in report['warnings']:
            lines.append('- ' + item)
        lines.append('')
    n = len(report['differs'])
    lines.append('Result: %s' % ('all harnesses match.' if n == 0 else '%d difference%s. Fix them, then run the check again.' % (n, '' if n == 1 else 's')))
    return '\n'.join(lines)


def report_json(report):
    rows = {}
    for title, row in report['rows']:
        rows[title] = {LABEL[h]: {'status': v[0], 'summary': v[1], 'issues': v[2]} for h, v in row.items()}
    return {'folder': report['folder'], 'rows': rows, 'differs': report['differs'],
            'warnings': report['warnings'], 'ok': not report['differs']}


# ---------------------------------------------------------------- sync (writers)

def translate_env(env, style):
    """Canonical env: literal values or ${NAME} references. Return (env, forwarded names)."""
    literal, forwarded = {}, []
    for key, value in sorted((env or {}).items()):
        ref = REF_RE.match(str(value))
        if ref:
            if style == 'claude':
                literal[key] = '${%s}' % ref.group(1)
            elif style == 'cursor':
                literal[key] = '${env:%s}' % ref.group(1)
            else:
                forwarded.append(ref.group(1) if ref.group(1) == key else key)
                if ref.group(1) != key:
                    literal[key] = str(value)
        else:
            literal[key] = str(value)
    return literal, forwarded


def json_entry(server, style):
    if server.get('url'):
        entry = {'url': server['url']}
        if style == 'claude':
            entry['type'] = 'http'
        return entry
    entry = {'command': server.get('command', ''), 'args': [str(a) for a in server.get('args') or []]}
    env, _ = translate_env(server.get('env'), style)
    if env:
        entry['env'] = env
    return entry


def codex_block(canon):
    lines = [BEGIN]
    for name, server in sorted(canon.items()):
        lines.append('[mcp_servers.%s]' % (name if re.match(r'^[A-Za-z0-9_-]+$', name) else json.dumps(name)))
        if server.get('url'):
            lines.append('url = %s' % tomlmini.dumps_string(server['url']))
        else:
            lines.append('command = %s' % tomlmini.dumps_string(server.get('command', '')))
            lines.append('args = %s' % tomlmini.dumps_array(server.get('args') or []))
            env, forwarded = translate_env(server.get('env'), 'codex')
            if env:
                lines.append('env = { %s }' % ', '.join('%s = %s' % (json.dumps(k), tomlmini.dumps_string(v)) for k, v in env.items()))
            if forwarded:
                lines.append('env_vars = %s' % tomlmini.dumps_array(forwarded))
        lines.append('')
    lines.append(END)
    return '\n'.join(lines) + '\n'


def strip_block(text, begin, end):
    pattern = re.compile(r'(?ms)^' + re.escape(begin) + r'.*?^' + re.escape(end) + r'[^\n]*\n?')
    return pattern.sub('', text)


def merge_codex(text, canon):
    """Replace our managed block at the end of a Codex TOML file; refuse clashes outside it."""
    outside = strip_block(text or '', BEGIN, END)
    theirs = (tomlmini.loads(outside).get('mcp_servers') or {}) if outside.strip() else {}
    clashes = sorted(set(theirs) & set(canon))
    if clashes:
        raise ValueError('.codex/config.toml already defines %s outside the managed block. Delete those tables, then run harness sync.' % ', '.join(clashes))
    body = outside.rstrip()
    result = (body + '\n\n' if body else '') + codex_block(canon)
    tomlmini.loads(result)
    return result


def merge_json(path, canon, style, removed=()):
    data = read_json(path)
    servers = data.get('mcpServers')
    if not isinstance(servers, dict):
        servers = {}
    for name in removed:
        servers.pop(name, None)
    for name, server in canon.items():
        servers[name] = json_entry(server, style)
    data['mcpServers'] = servers
    return json.dumps(data, indent=2) + '\n'


def link_skills(src_root, dest_root, log, conflicts, show=str):
    for name, real in skill_dirs(src_root).items():
        dest = Path(dest_root) / name
        if dest.is_symlink():
            if not dest.exists() or str(dest.resolve()) != real:
                if not dest.exists():
                    dest.unlink()
                else:
                    conflicts.append('%s already links somewhere else. Left alone.' % show(dest))
                    continue
            else:
                continue
        elif dest.exists():
            conflicts.append('%s is a real folder, not a link. Left alone: move it into the shared folder yourself.' % show(dest))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(Path(src_root) / name)
        log.append('Linked %s -> %s' % (show(dest), show(Path(src_root) / name)))


def sync(p, dry_run=False, removed=()):
    """Make every harness see the shared skills and the MCP list in .aios/mcp.json."""
    log, conflicts = [], []
    canon = canonical_servers(p)
    plans = []
    plans.append((p.folder / '.mcp.json', merge_json(p.folder / '.mcp.json', canon, 'claude', removed)))
    plans.append((p.folder / '.cursor' / 'mcp.json', merge_json(p.folder / '.cursor' / 'mcp.json', canon, 'cursor', removed)))
    codex_path = p.folder / '.codex' / 'config.toml'
    try:
        plans.append((codex_path, merge_codex(read_text(codex_path), canon)))
    except (ValueError, tomlmini.TomlError) as exc:
        conflicts.append(str(exc))
    state = read_json(p.folder / STATE)
    written = state.setdefault('written', {})
    for path, text in plans:
        current = read_text(path)
        if current == text:
            continue
        if dry_run:
            log.append('Would write %s' % p.show(path))
            continue
        key = str(path.relative_to(p.folder))
        if current is not None and written.get(key) != digest(current):
            backup(path, log)  # someone else wrote it last: keep their copy
        atomic_write(path, text)
        written[key] = digest(text)
        log.append('Wrote %s' % p.show(path))
    if not dry_run and plans:
        atomic_write(p.folder / STATE, json.dumps(state, indent=2) + '\n')
    if dry_run:
        for name in skill_dirs(p.agents_skills):
            if not (p.claude_dir / 'skills' / name).exists():
                log.append('Would link %s into Claude Code' % name)
    else:
        link_skills(p.agents_skills, p.claude_dir / 'skills', log, conflicts, p.show)
        link_skills(p.folder / '.agents' / 'skills', p.folder / '.claude' / 'skills', log, conflicts, p.show)
    return log, conflicts


def setup(p, dry_run=False, rng=None):
    log, notes = [], []
    agents = p.folder / 'AGENTS.md'
    text = read_text(agents)
    if text is None:
        if not dry_run:
            atomic_write(agents, AGENTS_TEMPLATE.format(phrase=new_phrase(rng)))
        log.append(('Would create' if dry_run else 'Created') + ' AGENTS.md (fill in the brackets)')
    elif not check_phrase(text):
        if not dry_run:
            backup(agents, log)
            atomic_write(agents, text.rstrip() + '\n\nRules check phrase: %s (used by /harness-check; do not edit)\n' % new_phrase(rng))
        log.append(('Would add' if dry_run else 'Added') + ' a rules check phrase to the end of AGENTS.md')
    claude_md = read_text(p.folder / 'CLAUDE.md')
    if claude_md is None:
        if not dry_run:
            atomic_write(p.folder / 'CLAUDE.md', '@AGENTS.md\n')
        log.append(('Would create' if dry_run else 'Created') + ' CLAUDE.md with the one line @AGENTS.md')
    elif meaningful_lines(claude_md) != ['@AGENTS.md']:
        notes.append('CLAUDE.md has its own text. It was not changed. Fold it into AGENTS.md, then make CLAUDE.md the one line @AGENTS.md.')
    if not (p.folder / CANON_MCP).exists():
        if not dry_run:
            atomic_write(p.folder / CANON_MCP, json.dumps({'mcpServers': {}}, indent=2) + '\n')
        log.append(('Would create' if dry_run else 'Created') + ' .aios/mcp.json (your one list of MCP servers)')
    if not dry_run:
        p.agents_skills.mkdir(parents=True, exist_ok=True)
    more, conflicts = sync(p, dry_run)
    return log + more, notes + conflicts


def mcp_add(p, name, command=None, args=(), url=None, env=None):
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9_-]*$', name):
        raise ValueError('Use letters, numbers, - and _ for the server name.')
    env = env or {}
    for key, value in env.items():
        if not REF_RE.match(value) and looks_secret(key, value):
            raise ValueError('%s looks like a secret. Put it in your shell as %s and write --env %s=${%s} instead.' % (key, key, key, key))
    data = read_json(p.folder / CANON_MCP)
    servers = data.setdefault('mcpServers', {})
    entry = {'url': url} if url else {'command': command, 'args': list(args)}
    if env:
        entry['env'] = dict(env)
    servers[name] = entry
    atomic_write(p.folder / CANON_MCP, json.dumps(data, indent=2) + '\n')
    return sync(p)


def mcp_remove(p, name):
    data = read_json(p.folder / CANON_MCP)
    servers = data.get('mcpServers') or {}
    if name not in servers:
        raise ValueError('"%s" is not in .aios/mcp.json.' % name)
    del servers[name]
    atomic_write(p.folder / CANON_MCP, json.dumps(data, indent=2) + '\n')
    return sync(p, removed=(name,))


def looks_secret(key, value):
    return bool(re.search(r'(KEY|TOKEN|SECRET|PASSWORD|AUTH)', key.upper())) and len(value) >= 8


# ---------------------------------------------------------------- defaults

RECOMMENDED = {
    'claude': ('your plan\'s default model', 'medium'),
    'codex': ('Codex\'s default model', 'medium'),
    'cursor': ('pick per job', 'set in the model picker'),
}


def defaults(p):
    claude = {}
    for path in (p.claude_dir / 'settings.json', p.folder / '.claude' / 'settings.json'):
        claude.update(read_json(path))
    codex = {}
    for path in (p.codex_home / 'config.toml', p.folder / '.codex' / 'config.toml'):
        codex.update({k: v for k, v in read_toml(path).items() if not isinstance(v, dict)})
    cursor = read_json(p.cursor_home / 'cli-config.json')
    model = cursor.get('model') if isinstance(cursor.get('model'), dict) else {}
    return [
        ('claude', claude.get('model', '(default)'), claude.get('effortLevel', '(default: medium)'), 'settings.json'),
        ('codex', codex.get('model', '(default)'), codex.get('model_reasoning_effort', '(default)'), 'config.toml'),
        ('cursor', model.get('modelId', '(default)'), '(in the model picker)', 'model picker'),
        ('grok', '(Grok)', '(set in the app)', 'app settings'),
    ]


def apply_defaults(p, effort='medium'):
    log = []
    settings_path = p.folder / '.claude' / 'settings.json'
    data = read_json(settings_path)
    if data.get('effortLevel') != effort:
        backup(settings_path, log)
        data['effortLevel'] = effort
        atomic_write(settings_path, json.dumps(data, indent=2) + '\n')
        log.append('Set effortLevel = %s in .claude/settings.json' % effort)
    codex_path = p.folder / '.codex' / 'config.toml'
    text = read_text(codex_path) or ''
    rest = strip_block(text, DEFAULTS_BEGIN, DEFAULTS_END)
    if re.search(r'^\s*model_reasoning_effort\s*=', rest.split('\n[', 1)[0], re.M):
        log.append('Left .codex/config.toml alone: it already sets model_reasoning_effort.')
    else:
        block = '%s\nmodel_reasoning_effort = %s\n%s\n' % (DEFAULTS_BEGIN, json.dumps(effort), DEFAULTS_END)
        new = block + rest.lstrip('\n')
        if new != text:
            tomlmini.loads(new)
            backup(codex_path, log)
            atomic_write(codex_path, new)
            log.append('Set model_reasoning_effort = %s in .codex/config.toml' % effort)
    return log
