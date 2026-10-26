"""The Stop gate: the agent cannot finish a turn while the project's checks fail.

Opt-in per project. It does nothing unless the folder (or a parent) has
.aios/verify.json. When the files have not changed since the last passing run, it
does not run the checks again, so ordinary chat replies stay fast.

After MAX_BLOCKS failed attempts on the same files it lets the turn end and tells
the person, so a check that can never pass does not trap the session.
"""
import hashlib
import json
import subprocess
from pathlib import Path

from .checks import ConfigError, find_root, run_checks

MAX_BLOCKS = 3
STATE = Path('.aios') / 'verify-state.json'


def fingerprint(root):
    """A hash of every uncommitted change, or None outside git (then the checks always run)."""
    def git(*args):
        return subprocess.run(['git'] + list(args), cwd=str(root), capture_output=True, timeout=30)
    try:
        if git('rev-parse', '--is-inside-work-tree').returncode != 0:
            return None
        digest = hashlib.sha256()
        digest.update(git('rev-parse', 'HEAD').stdout)
        digest.update(git('diff', 'HEAD', '--no-color', '--', '.', ':(exclude).aios').stdout)
        untracked = git('ls-files', '--others', '--exclude-standard', '-z', '--', '.', ':(exclude).aios').stdout
        for name in sorted(n for n in untracked.split(b'\0') if n):
            digest.update(name)
            path = Path(root) / name.decode(errors='replace')
            if path.is_file() and path.stat().st_size < 5_000_000:
                digest.update(path.read_bytes())
        return digest.hexdigest()
    except (OSError, subprocess.SubprocessError):
        return None


def read_state(root):
    try:
        return json.loads((Path(root) / STATE).read_text())
    except (OSError, ValueError):
        return {}


def write_state(root, state):
    path = Path(root) / STATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + '\n')


def evaluate(payload):
    """Return the Stop hook's JSON answer, or None to let the turn end."""
    root = find_root(payload.get('cwd') or '.')
    if root is None:
        return None
    try:
        current = fingerprint(root)
        state = read_state(root)
        if current is not None and state.get('passed') == current:
            return None
        results = run_checks(root, gate_only=True)
    except ConfigError as exc:
        return {'systemMessage': 'AIOS verify gate skipped: %s' % exc}
    failed = [item for item in results if not item['passed']]
    if not failed:
        write_state(root, {'passed': current, 'blocks': 0})
        return None
    blocks = state.get('blocks', 0) + 1 if state.get('failed') == current else 1
    write_state(root, {'passed': state.get('passed'), 'failed': current, 'blocks': blocks})
    summary = '; '.join('%s failed (exit %d): %s' % (f['name'], f['exit'], f['run']) for f in failed)
    detail = '\n\n'.join('$ %s\n%s' % (f['run'], f['tail']) for f in failed)
    if blocks > MAX_BLOCKS:
        return {'systemMessage': ('AIOS verify gate: the checks still fail after %d attempts (%s). '
                                  'The turn was allowed to end. Do not treat the work as done.' % (MAX_BLOCKS, summary))}
    reason = ('AIOS verify gate (attempt %d of %d): you cannot finish yet, because %s.\n\n%s\n\n'
              'Fix the cause, run `aios-verify run` until every check passes, then finish. '
              'If a check cannot pass, say so plainly instead of saying the work is done.'
              % (blocks, MAX_BLOCKS, summary, detail))
    return {'decision': 'block', 'reason': reason[:9000]}
