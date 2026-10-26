"""bb as the cockpit: a project for the AIOS folder, a four-lane board, and the daily loop.

Everything goes through the member's own `bb` CLI (`--json` everywhere), so this works on any Mac
that runs bb, with or without a kanban plugin. With a plugin that adds `bb kanban`, cards move on
its board. Without one, the four lanes are bb sidebar sections with the same names.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

LANES = (('backlog', 'Backlog'), ('in-progress', 'In progress'), ('review', 'Review'), ('done', 'Done'))
LANE_NAMES = dict(LANES)
ALIASES = {'todo': 'backlog', 'doing': 'in-progress', 'progress': 'in-progress', 'inprogress': 'in-progress',
           'check': 'review', 'closed': 'done', 'finished': 'done'}
PROVIDERS = {'claude': 'claude-code', 'claude-code': 'claude-code', 'codex': 'codex'}


class BbError(RuntimeError):
    pass


class Bb:
    """A thin wrapper over the bb CLI. `runner` is swapped in tests."""

    def __init__(self, exe=None, runner=None, env=None):
        self.env = dict(os.environ if env is None else env)
        self.exe = exe or self.env.get('BB_CLI') or shutil.which('bb', path=self.env.get('PATH')) or 'bb'
        self.runner = runner or subprocess.run

    def raw(self, *args, check=True):
        try:
            proc = self.runner([self.exe] + list(args), capture_output=True, text=True, timeout=120, env=self.env)
        except FileNotFoundError:
            raise BbError('The bb command was not found. Install bb from getbb.app, then in bb run: bb settings cli-command install')
        except subprocess.TimeoutExpired:
            raise BbError('bb did not answer within two minutes. Is the bb app running?')
        if check and proc.returncode != 0:
            message = (proc.stdout or '').strip()
            try:
                message = json.loads(message)['error']['message']
            except (ValueError, KeyError, TypeError):
                message = (message or proc.stderr or '').strip()
            raise BbError('bb %s failed: %s' % (' '.join(args[:3]), message[:300]))
        return proc

    def json(self, *args):
        proc = self.raw(*(list(args) + ['--json']))
        try:
            return json.loads(proc.stdout or 'null')
        except ValueError:
            raise BbError('bb %s did not return JSON' % ' '.join(args[:3]))

    def has_kanban(self):
        if getattr(self, '_kanban', None) is None:
            self._kanban = self._probe_kanban()
        return self._kanban

    def _probe_kanban(self):
        try:
            proc = self.raw('kanban', '--help', check=False)
        except BbError:
            return False
        return proc.returncode == 0 and 'kanban' in (proc.stdout or '').lower() and 'Unknown command' not in (proc.stdout + proc.stderr)


def lane_id(name):
    key = name.strip().lower().replace(' ', '-').replace('_', '-')
    key = ALIASES.get(key.replace('-', ''), ALIASES.get(key, key))
    if key not in LANE_NAMES:
        raise ValueError('Use one of: backlog, in-progress, review, done.')
    return key


# ---------------------------------------------------------------- doctor

def doctor(bb, folder):
    """Return a list of (status, message). Status is OK, WARN or FAIL."""
    rows = []
    try:
        status = bb.json('status')
        rows.append(('OK', 'bb is running (data folder %s).' % show_home(status.get('dataDir') or '?')))
    except BbError as exc:
        return [('FAIL', str(exc))]
    try:
        version = bb.raw('--version').stdout.strip()
        rows.append(('OK', 'bb CLI %s' % version))
    except BbError:
        pass
    try:
        providers = bb.json('provider', 'list')
        names = {p.get('id'): p.get('available') for p in providers if isinstance(p, dict)}
        for pid, label in (('claude-code', 'Claude Code'), ('codex', 'Codex')):
            if names.get(pid):
                rows.append(('OK', '%s is available as a bb provider.' % label))
            else:
                rows.append(('WARN', '%s is not available in bb yet. Sign in to it, then check Settings, Providers.' % label))
    except BbError as exc:
        rows.append(('WARN', 'Could not list providers: %s' % exc))
    folder = Path(folder).expanduser()
    if not folder.is_dir():
        rows.append(('FAIL', 'The folder %s does not exist.' % show_home(str(folder))))
    elif not (folder / '.git').exists():
        rows.append(('WARN', 'The folder is not a git repository, so threads cannot have their own worktree. Run: git init && git add -A && git commit -m "Start"'))
    else:
        rows.append(('OK', 'The folder is a git repository, so each thread can get its own worktree.'))
    if folder.is_dir() and not (folder / 'AGENTS.md').exists():
        rows.append(('WARN', 'No AGENTS.md in the folder. Module 2 (or harness setup) makes one.'))
    rows.append(('OK' if bb.has_kanban() else 'WARN',
                 'A kanban plugin is installed (bb kanban).' if bb.has_kanban() else
                 'No kanban plugin: cards move between four sidebar sections instead. That works fine.'))
    return rows


def show_home(path):
    home = os.environ.get('HOME', '')
    if home and (path == home or path.startswith(home + os.sep)):
        return '~' + path[len(home):]
    return path


# ---------------------------------------------------------------- setup

def find_project(bb, folder):
    folder = str(Path(folder).expanduser().resolve())
    for project in bb.json('project', 'list') or []:
        for source in project.get('sources') or []:
            path = source.get('path')
            if path and str(Path(path).expanduser().resolve()) == folder:
                return project
    return None


def ensure_sections(bb, dry_run=False):
    existing = {s.get('name'): s.get('id') for s in (bb.json('thread', 'section', 'list') or [])}
    made = []
    for _key, name in LANES:
        if name not in existing:
            if dry_run:
                made.append(name)
                continue
            created = bb.json('thread', 'section', 'create', name)
            existing[name] = (created or {}).get('id')
            made.append(name)
    return existing, made


def setup(bb, folder, name=None, dry_run=False):
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError('The folder %s does not exist.' % folder)
    log = []
    project = find_project(bb, folder)
    if project:
        log.append('The project "%s" (%s) already points at this folder. Kept it.' % (project.get('name'), project.get('id')))
    else:
        name = name or folder.name
        if dry_run:
            log.append('Would create the bb project "%s" for %s' % (name, show_home(str(folder))))
        else:
            project = bb.json('project', 'create', '--name', name, '--root', str(folder))
            log.append('Created the bb project "%s" (%s).' % (project.get('name', name), project.get('id')))
    sections, made = ensure_sections(bb, dry_run)
    if made:
        log.append(('Would create' if dry_run else 'Created') + ' the sections: ' + ', '.join(made))
    else:
        log.append('The four sections (Backlog, In progress, Review, Done) already exist.')
    if not (folder / '.git').exists():
        log.append('Note: the folder is not a git repository yet, so "Worktree" threads will not work until you run git init.')
    return project, log


# ---------------------------------------------------------------- cards

def resolve_thread(bb, thread):
    """Accept a thread id (thr_...) or a thread's exact title, and return the id."""
    if not thread or thread.startswith('thr_'):
        return thread
    matches = [t for t in (bb.json('thread', 'list') or []) if not t.get('archivedAt') and (t.get('title') or '').strip() == thread.strip()]
    if not matches:
        raise ValueError('No open thread is called "%s". Use its id (thr_...) or its exact title.' % thread)
    if len(matches) > 1:
        raise ValueError('More than one thread is called "%s". Use the id instead: %s' % (thread, ', '.join(m['id'] for m in matches)))
    return matches[0]['id']


def move_card(bb, thread, lane, note=None):
    lane = lane_id(lane)
    thread = resolve_thread(bb, thread)
    if bb.has_kanban():
        args = ['kanban', 'move', lane]
        if thread:
            args += ['--thread', thread]
        if note:
            args += ['--note', note[:500]]
        bb.raw(*args)
        return 'Moved the card to %s on the kanban board.' % LANE_NAMES[lane]
    if not thread:
        thread = os.environ.get('BB_THREAD_ID')
    if not thread:
        raise ValueError('Give the thread id, or run this inside a bb thread.')
    sections, _ = ensure_sections(bb)
    bb.raw('thread', 'update', thread, '--section', sections[LANE_NAMES[lane]])
    return 'Moved the thread into the %s section.' % LANE_NAMES[lane]


def board(bb, project=None):
    """{lane key: [thread dicts]} for the project's open threads."""
    args = ['thread', 'list']
    if project:
        args += ['--project', project]
    threads = [t for t in (bb.json(*args) or []) if not t.get('archivedAt')]
    by_id = {t['id']: t for t in threads}
    lanes = {key: [] for key, _ in LANES}
    lanes['unsorted'] = []
    if bb.has_kanban():
        data = bb.json('kanban', 'board', '--project', project or 'all')
        placed = set()
        for card in sorted(data.get('cards') or [], key=lambda c: c.get('position') or 0):
            thread = by_id.get(card.get('threadId'))
            col = card.get('columnId')
            if thread and col in lanes:
                lanes[col].append(dict(thread, note=card.get('note')))
                placed.add(thread['id'])
        lanes['unsorted'] = [t for t in threads if t['id'] not in placed]
        return lanes
    names = {s.get('id'): s.get('name') for s in (bb.json('thread', 'section', 'list') or [])}
    reverse = {name: key for key, name in LANES}
    for thread in threads:
        key = reverse.get(names.get(thread.get('sectionId')))
        lanes[key or 'unsorted'].append(thread)
    return lanes


def title(thread):
    return (thread.get('title') or thread.get('titleFallback') or thread.get('id') or '?')[:60]


def today(bb, project=None):
    lanes = board(bb, project)
    lines = ['Start of day']
    waiting = [t for lane in lanes.values() for t in lane if t.get('hasPendingInteraction')]
    if waiting:
        lines.append('')
        lines.append('Waiting on you now (a question or an approval):')
        for t in waiting:
            lines.append('  - %s  (%s)' % (title(t), t['id']))
    for key, name in (('review', 'Review'), ('in-progress', 'In progress'), ('backlog', 'Backlog')):
        items = lanes[key]
        lines.append('')
        lines.append('%s (%d)' % (name, len(items)))
        for t in items[:12]:
            note = (' - ' + t['note']) if t.get('note') else ''
            lines.append('  - %s  [%s]%s' % (title(t), t.get('status', '?'), note))
    lines.append('')
    lines.append('Done (%d), not on the board (%d).' % (len(lanes['done']), len(lanes['unsorted'])))
    lines.append('')
    lines.append('Order of the day: answer what is waiting, review what is in Review, then hand out new work.')
    return '\n'.join(lines), lanes


def hand(bb, project, title_text, prompt_file, provider='claude', worktree=True, plan=False):
    provider_id = PROVIDERS.get(provider)
    if not provider_id:
        raise ValueError('Use --provider claude or --provider codex.')
    if not Path(prompt_file).is_file():
        raise ValueError('Write the brief into a file first, then pass it with --prompt-file.')
    args = ['thread', 'spawn', '--project', project, '--title', title_text, '--prompt-file', str(prompt_file),
            '--provider', provider_id]
    if worktree:
        args += ['--new-environment', 'worktree']
    if plan:
        args.append('--plan')
    if not bb.has_kanban():
        sections, _ = ensure_sections(bb)
        args += ['--section', sections['In progress']]
    thread = bb.json(*args)
    if bb.has_kanban():
        bb.raw('kanban', 'move', 'in-progress', '--thread', thread['id'], '--note', 'Handed out')
    return thread


def close(bb, project=None, archive_done=False):
    lanes = board(bb, project)
    lines = ['End of day']
    lines.append('')
    lines.append('Still in Review (%d): read these first thing tomorrow, or now.' % len(lanes['review']))
    for t in lanes['review']:
        lines.append('  - %s  (%s)' % (title(t), t['id']))
    running = [t for t in lanes['in-progress'] if t.get('status') in ('active', 'starting', 'pending')]
    lines.append('')
    lines.append('Still running (%d): leave them, they will be in Review when they finish.' % len(running))
    for t in running:
        lines.append('  - %s' % title(t))
    done = lanes['done']
    lines.append('')
    if archive_done and done:
        for t in done:
            bb.raw('thread', 'archive', t['id'])
        lines.append('Archived %d finished thread(s) from Done.' % len(done))
    else:
        lines.append('Done (%d). Archive them with: aios-bb close --archive-done' % len(done))
    return '\n'.join(lines)
