"""Member settings for shelf-video. One JSON file, the same for every harness.

The file lives at ~/.config/aios/shelf-video.json. Set AIOS_CONFIG_DIR to use another
folder (tests and sandboxes do this). Nothing in it is secret: this pack needs no keys.
"""
import copy
import json
import os
from pathlib import Path

DEFAULTS = {
    'whisper_model': 'small.en',
    'language': 'en',
    'fillers': ['um', 'umm', 'uh', 'uhh', 'uhm', 'er', 'erm', 'ah', 'ahh', 'hmm', 'mm', 'mhm'],
    'soft_fillers': ['you know', 'i mean', 'sort of', 'kind of', 'like', 'basically', 'actually', 'so yeah'],
    'max_pause': 0.6,
    'keep_pause': 0.3,
    'pad': 0.06,
    'lead_keep': 0.2,
    'tail_keep': 0.4,
    'caption': {
        'font': '',
        'size_ratio': 0.055,
        'colour': '#FFFFFF',
        'box': '#000000B8',
        'margin_ratio': 0.11,
        'max_chars': 36,
        'max_seconds': 3.0,
        'uppercase': False,
    },
    'export': {
        'crf': 18,
        'audio_bitrate': '192k',
        'loudnorm': False,
    },
}


def config_dir():
    override = os.environ.get('AIOS_CONFIG_DIR', '').strip()
    return Path(override) if override else Path.home() / '.config' / 'aios'


def path():
    return config_dir() / 'shelf-video.json'


def _merge(base, extra):
    out = copy.deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load():
    file = path()
    if not file.exists():
        return copy.deepcopy(DEFAULTS)
    data = json.loads(file.read_text())
    if not isinstance(data, dict):
        raise ValueError('Settings file must hold a JSON object: ' + str(file))
    return _merge(DEFAULTS, data)


def _coerce(old, raw):
    if isinstance(old, bool):
        if raw.lower() in ('true', 'yes', '1', 'on'):
            return True
        if raw.lower() in ('false', 'no', '0', 'off'):
            return False
        raise ValueError('Use true or false')
    if isinstance(old, int) and not isinstance(old, bool):
        return int(raw)
    if isinstance(old, float):
        return float(raw)
    if isinstance(old, list):
        return [x.strip() for x in raw.split(',') if x.strip()]
    return raw


def set_value(dotted, raw):
    """Set one value, such as caption.colour=#FFD400. Unknown keys are refused."""
    current = load()
    parts = dotted.split('.')
    node, defaults = current, DEFAULTS
    for part in parts[:-1]:
        if part not in defaults or not isinstance(defaults[part], dict):
            raise ValueError('Unknown setting: ' + dotted)
        node, defaults = node[part], defaults[part]
    leaf = parts[-1]
    if leaf not in defaults or isinstance(defaults[leaf], dict):
        raise ValueError('Unknown setting: ' + dotted)
    node[leaf] = _coerce(defaults[leaf], raw)
    save(current)
    return current


def save(data):
    file = path()
    file.parent.mkdir(parents=True, exist_ok=True)
    tmp = file.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(tmp, file)
