"""The member's brand: colours, fonts, logo and footer. One JSON file for every harness.

Default file: ~/.config/aios/shelf-decks.json (AIOS_CONFIG_DIR moves it). A deck can also
name its own brand file with --brand, which is how the sample deck stays separate.
"""
import copy
import json
import os
import re
from pathlib import Path

DEFAULTS = {
    'name': 'Your Company',
    'footer': '',
    'colours': {
        'background': '#FFFFFF',
        'text': '#1E1E1E',
        'muted': '#5C5C5C',
        'accent': '#2B5D8A',
        'accent_text': '#FFFFFF',
        'surface': '#F2F2EF',
    },
    'fonts': {
        'heading': 'Arial',
        'body': 'Arial',
        'heading_file': '',
        'body_file': '',
    },
    'logo': '',
}

HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')


class BrandError(ValueError):
    pass


def config_dir():
    override = os.environ.get('AIOS_CONFIG_DIR', '').strip()
    return Path(override) if override else Path.home() / '.config' / 'aios'


def default_path():
    return config_dir() / 'shelf-decks.json'


def _merge(base, extra):
    out = copy.deepcopy(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(path=None):
    file = Path(path).expanduser() if path else default_path()
    if path and not file.exists():
        raise BrandError('Brand file not found: ' + str(file))
    data = json.loads(file.read_text()) if file.exists() else {}
    brand = _merge(DEFAULTS, data)
    brand['_file'] = str(file) if file.exists() else ''
    brand['_dir'] = str(file.parent)
    validate(brand)
    return brand


def resolve(brand, value):
    """Paths in a brand file are relative to that file, so a brand folder can move as one."""
    if not value:
        return ''
    p = Path(os.path.expanduser(value))
    if not p.is_absolute():
        p = Path(brand['_dir']) / p
    return str(p)


def validate(brand):
    for key, value in brand['colours'].items():
        if not HEX.match(str(value)):
            raise BrandError('Colour %s must be a hex value such as #2B5D8A, not %r' % (key, value))
    for key in ('heading_file', 'body_file'):
        value = brand['fonts'].get(key)
        if value and not Path(resolve(brand, value)).exists():
            raise BrandError('Font file not found for %s: %s' % (key, value))
    if brand['logo']:
        logo = Path(resolve(brand, brand['logo']))
        if not logo.exists():
            raise BrandError('Logo not found: ' + brand['logo'])
        if logo.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            raise BrandError('Use a PNG or JPG logo. PowerPoint cannot place an SVG from this tool; export a PNG first.')


def set_value(dotted, value, path=None):
    file = Path(path).expanduser() if path else default_path()
    data = json.loads(file.read_text()) if file.exists() else {}
    parts = dotted.split('.')
    node, defaults = data, DEFAULTS
    for part in parts[:-1]:
        if part not in defaults or not isinstance(defaults[part], dict):
            raise BrandError('Unknown brand setting: ' + dotted)
        node = node.setdefault(part, {})
        defaults = defaults[part]
    if parts[-1] not in defaults or isinstance(defaults[parts[-1]], dict):
        raise BrandError('Unknown brand setting: ' + dotted)
    if dotted.endswith(('_file',)) or dotted == 'logo':
        value = str(Path(os.path.expanduser(value)).resolve()) if value else ''
    node[parts[-1]] = value
    merged = _merge(DEFAULTS, data)
    merged['_dir'] = str(file.parent)
    validate(merged)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(data, indent=2) + '\n')
    return file


def rgb(hex_value):
    h = hex_value.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(hex_value):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb(hex_value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def contrast_report(brand):
    """WCAG 2.2 ratios for the pairs the layouts actually use."""
    c = brand['colours']
    pairs = [('text on background', c['text'], c['background'], 4.5),
             ('muted on background', c['muted'], c['background'], 4.5),
             ('accent on background (large text)', c['accent'], c['background'], 3.0),
             ('accent_text on accent', c['accent_text'], c['accent'], 4.5),
             ('text on surface', c['text'], c['surface'], 4.5)]
    return [{'pair': name, 'ratio': contrast(fg, bg), 'needs': need, 'ok': contrast(fg, bg) >= need}
            for name, fg, bg, need in pairs]
