"""The monthly rules audit: the budget check, /doctor prompt-audit and /skill-doctor, in one dated file.

Nothing in the member's rules is edited. Both slash commands run headless on the member's own
Claude Code sign-in (`claude -p`), with read-only tools. If a command is not available, the file
says so; it never invents a result.
"""
import datetime
import os
import shutil
import subprocess
from pathlib import Path

from . import check

UNAVAILABLE = ("isn't installed", 'is not installed', 'not available', "isn't available",
               'unknown command', 'unknown skill', 'no such command')
READ_ONLY = ['--allowedTools', 'Read,Glob,Grep', '--disallowedTools', 'Edit,Write,Bash,NotebookEdit']


def claude_binary():
    return os.environ.get('AIOS_RULES_CLAUDE') or shutil.which('claude')


def run_slash(command, folder, timeout):
    binary = claude_binary()
    if not binary:
        return 'not-run', 'Claude Code (`claude`) is not on PATH, so this step did not run.'
    try:
        proc = subprocess.run([binary, '-p', command] + READ_ONLY, cwd=str(folder),
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 'failed', 'Stopped after %d seconds with no result.' % timeout
    except OSError as exc:
        return 'failed', 'Could not start Claude Code: %s' % exc
    text = (proc.stdout or '').strip()
    if proc.returncode != 0:
        return 'failed', 'Exit %d.\n\n%s' % (proc.returncode, (text + '\n' + (proc.stderr or '')).strip())
    if not text:
        return 'failed', 'Claude Code returned nothing.'
    head = text[:400].lower()
    if any(marker in head for marker in UNAVAILABLE) and command.split()[0].lstrip('/') in head:
        return 'unavailable', text
    return 'ok', text


def next_name(out_dir, day):
    version = 1
    while (out_dir / ('%s_rules-audit_v%d.md' % (day, version))).exists():
        version += 1
    return out_dir / ('%s_rules-audit_v%d.md' % (day, version))


def audit(folder, out_dir=None, run_claude=True, timeout=900, today=None):
    folder = Path(folder).resolve()
    day = (today or datetime.date.today()).isoformat()
    out_dir = Path(out_dir) if out_dir else folder / '80_aios' / 'audits'
    if not out_dir.is_absolute():
        out_dir = folder / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    results = check.run(folder, ['claude', 'codex', 'cursor'])
    status = {'budget': 'over' if check.exit_code(results) else 'ok'}
    sections = [
        '# Rules audit, %s' % day, '',
        'Folder: `%s`. Nothing in your rules was changed by this audit.' % folder.name, '',
        '## 1. Always-loaded budget (aios-rules check)', '', '```text', check.render(results).rstrip(), '```', '',
    ]
    steps = [('2. Prompt audit (/doctor prompt-audit)', '/doctor prompt-audit', 'prompt_audit'),
             ('3. Skill usage (/skill-doctor)', '/skill-doctor', 'skill_doctor')]
    for title, command, key in steps:
        sections += ['## ' + title, '']
        if not run_claude:
            status[key] = 'skipped'
            sections += ['Skipped (--no-claude). Run `%s` in Claude Code and paste the report here.' % command, '']
            continue
        state, text = run_slash(command, folder, timeout)
        status[key] = state
        if state == 'ok':
            sections += [text, '']
        elif state == 'unavailable':
            sections += ['**Not available in this session.** Open Claude Code in a terminal on this machine, run '
                         '`%s`, and paste its report under this heading.' % command, '', '> ' + text.replace('\n', '\n> '), '']
        else:
            sections += ['**Did not complete (%s).** %s' % (state, text), '']
    sections += [
        '## 4. Decisions', '',
        '- [ ] Lines to cut from AGENTS.md (move detail to a skill or a path-scoped rule):',
        '- [ ] Skills to hide or turn off (from section 3):',
        '- [ ] Findings from section 2 to apply (ask Claude to apply only the ones you tick):',
        '- [ ] Next audit date:', '',
        'Status: budget %s; prompt audit %s; skill doctor %s.' % (
            status['budget'], status['prompt_audit'], status['skill_doctor']), '',
    ]
    path = next_name(out_dir, day)
    path.write_text('\n'.join(sections), encoding='utf-8')
    return path, status
