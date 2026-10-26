"""Hide the long tail: set a skill's visibility with skillOverrides.

Writes one key in a settings file and keeps every other byte of meaning.
A backup is written first. Plugin skills are not affected by skillOverrides,
so a namespaced name (plugin:skill) is refused with the right advice.
"""
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

STATES = ('on', 'name-only', 'user-invocable-only', 'off')
SCOPES = {
    'local': lambda home, cwd: cwd / '.claude' / 'settings.local.json',
    'project': lambda home, cwd: cwd / '.claude' / 'settings.json',
    'user': lambda home, cwd: home / '.claude' / 'settings.json',
}


class HideError(ValueError):
    pass


def settings_path(scope, home=None, cwd=None):
    if scope not in SCOPES:
        raise HideError('Scope must be one of: ' + ', '.join(SCOPES))
    return SCOPES[scope](Path(home or Path.home()), Path(cwd or Path.cwd()))


def plan(skill, state, scope='local', home=None, cwd=None):
    """Return (path, old settings, new settings) without writing anything."""
    if ':' in skill:
        raise HideError('%s is a plugin skill. skillOverrides does not apply to plugin skills: '
                        'disable the plugin with /plugin, or test it with claude plugin eval.' % skill)
    if state not in STATES:
        raise HideError('State must be one of: ' + ', '.join(STATES))
    path = settings_path(scope, home, cwd)
    old = {}
    if path.exists():
        try:
            old = json.loads(path.read_text() or '{}')
        except ValueError as exc:
            raise HideError('%s is not valid JSON (%s); fix it before changing it' % (path, exc))
        if not isinstance(old, dict):
            raise HideError('%s must hold a JSON object' % path)
    overrides = old.get('skillOverrides', {})
    if not isinstance(overrides, dict):
        raise HideError('skillOverrides in %s must be an object' % path)
    new = dict(old)
    new_overrides = dict(overrides)
    if state == 'on':
        new_overrides.pop(skill, None)   # absent means on
    else:
        new_overrides[skill] = state
    if new_overrides:
        new['skillOverrides'] = new_overrides
    else:
        new.pop('skillOverrides', None)
    return path, old, new


def apply(skill, state, scope='local', home=None, cwd=None):
    path, old, new = plan(skill, state, scope, home, cwd)
    if old == new and path.exists():
        return path, None, False
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if path.exists():
        backup = path.with_name(path.name + '.backup-%d' % time.time_ns())
        shutil.copy2(path, backup)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(json.dumps(new, indent=2) + '\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return path, backup, True
