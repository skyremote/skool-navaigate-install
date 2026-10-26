"""Optional member-owned configuration. Never source a shell file."""
import os
import stat
from pathlib import Path

KEYS = ('AIOS_BRAIN_TURSO_URL','AIOS_BRAIN_TURSO_TOKEN','SUPADATA_API_KEY')


def load():
    values = {key:os.environ.get(key,'') for key in KEYS}
    # Hook processes can export options; MCP receives explicit mapped env values.
    # A direct shell command uses exported variables or the private env file.
    for key,option in [('AIOS_BRAIN_TURSO_URL','turso_url'),('AIOS_BRAIN_TURSO_TOKEN','turso_token')]:
        values[key] = values[key] or os.environ.get('CLAUDE_PLUGIN_OPTION_'+option.upper(),'')
    path = Path.home()/'.config/aios-brain/env'
    if path.exists():
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise ValueError('Set private permissions on the brain env file: chmod 600 ~/.config/aios-brain/env')
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            key,sep,value = line.partition('=')
            key = key.strip()
            if not sep:
                raise ValueError('Malformed private env file; use one KEY=value entry per line')
            if sep and key in KEYS and not values[key]:
                values[key] = value.strip().strip('\"\'')
    for key in ('AIOS_BRAIN_TURSO_TOKEN','SUPADATA_API_KEY'):
        if any(c.isspace() or ord(c)<32 or ord(c)==127 for c in values[key]):
            raise ValueError('Credential contains whitespace or control characters; paste it again privately')
    values['AIOS_BRAIN_TURSO_URL']=values['AIOS_BRAIN_TURSO_URL'].strip()
    if bool(values[KEYS[0]]) != bool(values[KEYS[1]]):
        raise ValueError('Set both your Turso URL and token, or leave both blank for local mode')
    return values
