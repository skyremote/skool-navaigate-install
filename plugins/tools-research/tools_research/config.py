"""The member's own keys. Never printed, never written by this pack.

Order: the shell variable, then the Claude Code plugin option, then the private
file ~/.config/aios-tools/env (one KEY=value per line, chmod 600).
"""
import os
import stat
from pathlib import Path

ENV_FILE = Path.home() / '.config/aios-tools/env'


class KeyError_(ValueError):
    pass


def env_file_values(path=None):
    path = Path(path or Path.home() / '.config/aios-tools/env')
    if not path.exists():
        return {}
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise KeyError_('Make the key file private first: chmod 600 ' + str(path))
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, sep, value = line.partition('=')
        if not sep:
            raise KeyError_('Each line in ' + str(path) + ' must be KEY=value')
        values[key.strip().removeprefix('export ').strip()] = value.strip().strip('"\'')
    return values


def get(name, option=None, env=None, path=None):
    """Return the member's value for NAME, or '' when it is not set anywhere."""
    env = os.environ if env is None else env
    value = env.get(name, '').strip()
    if not value and option:
        value = env.get('CLAUDE_PLUGIN_OPTION_' + option.upper(), '').strip()
    if not value:
        value = env_file_values(path).get(name, '').strip()
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise KeyError_(name + ' contains spaces or control characters; paste it again')
    return value


def where(name, option=None, env=None, path=None):
    """Say where a key was found, without showing it."""
    env = os.environ if env is None else env
    if env.get(name, '').strip():
        return 'shell variable ' + name
    if option and env.get('CLAUDE_PLUGIN_OPTION_' + option.upper(), '').strip():
        return 'Claude Code plugin setting ' + option
    if env_file_values(path).get(name, '').strip():
        return 'private file ~/.config/aios-tools/env'
    return ''
