"""Read the small part of TOML that Codex MCP tables use, on Python 3.9+.

Python 3.11+ uses the standard tomllib. On older Pythons this reader handles
tables, dotted and quoted keys, strings, numbers, booleans, arrays and inline
tables. Arrays of tables ([[...]]) are skipped, because MCP tables never use them.
"""
import json
import re

try:  # pragma: no cover - depends on the Python version
    import tomllib as _tomllib
except ImportError:  # pragma: no cover
    _tomllib = None


class TomlError(ValueError):
    pass


def loads(text, force_fallback=False):
    if _tomllib is not None and not force_fallback:
        try:
            return _tomllib.loads(text)
        except Exception as exc:  # tomllib.TOMLDecodeError
            raise TomlError(str(exc))
    return _Parser(text).parse()


def split_key(raw):
    """Split a dotted TOML key, keeping quoted parts whole."""
    parts, buf, quote = [], '', None
    for ch in raw.strip():
        if quote:
            if ch == quote:
                quote = None
            else:
                buf += ch
        elif ch in '"\'':
            quote = ch
        elif ch == '.':
            parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
    if quote:
        raise TomlError('Unclosed quote in key: ' + raw)
    parts.append(buf.strip())
    if any(p == '' for p in parts):
        raise TomlError('Empty key part: ' + raw)
    return parts


class _Parser:
    def __init__(self, text):
        self.s = text
        self.i = 0

    def parse(self):
        root = {}
        table = root
        skipping = False
        while self.i < len(self.s):
            self._skip_ws_comments()
            if self.i >= len(self.s):
                break
            if self.s.startswith('[[', self.i):
                end = self.s.index(']]', self.i)
                self.i = end + 2
                skipping = True
                continue
            if self.s[self.i] == '[':
                end = self.s.index(']', self.i)
                table = root
                for part in split_key(self.s[self.i + 1:end]):
                    table = table.setdefault(part, {})
                    if not isinstance(table, dict):
                        raise TomlError('Key is both a value and a table')
                self.i = end + 1
                skipping = False
                continue
            key_end = self.s.index('=', self.i)
            keys = split_key(self.s[self.i:key_end])
            self.i = key_end + 1
            value = self._value()
            if not skipping:
                target = table
                for part in keys[:-1]:
                    target = target.setdefault(part, {})
                target[keys[-1]] = value
            self._skip_line_rest()
        return root

    def _skip_ws_comments(self):
        while self.i < len(self.s):
            ch = self.s[self.i]
            if ch in ' \t\r\n':
                self.i += 1
            elif ch == '#':
                nl = self.s.find('\n', self.i)
                self.i = len(self.s) if nl < 0 else nl + 1
            else:
                break

    def _skip_inline_ws(self):
        while self.i < len(self.s) and self.s[self.i] in ' \t':
            self.i += 1

    def _skip_line_rest(self):
        self._skip_inline_ws()
        if self.i < len(self.s) and self.s[self.i] == '#':
            nl = self.s.find('\n', self.i)
            self.i = len(self.s) if nl < 0 else nl + 1

    def _value(self):
        self._skip_inline_ws()
        s, i = self.s, self.i
        if s.startswith('"""', i) or s.startswith("'''", i):
            q = s[i:i + 3]
            end = s.index(q, i + 3)
            self.i = end + 3
            body = s[i + 3:end]
            if body.startswith('\n'):
                body = body[1:]
            return body
        if s[i] == '"':
            m = re.compile(r'"((?:[^"\\\n]|\\.)*)"').match(s, i)
            if not m:
                raise TomlError('Bad string at %d' % i)
            self.i = m.end()
            return json.loads('"' + m.group(1) + '"')
        if s[i] == "'":
            end = s.index("'", i + 1)
            self.i = end + 1
            return s[i + 1:end]
        if s[i] == '[':
            self.i += 1
            items = []
            while True:
                self._skip_ws_comments()
                if s[self.i] == ']':
                    self.i += 1
                    return items
                items.append(self._value())
                self._skip_ws_comments()
                if s[self.i] == ',':
                    self.i += 1
        if s[i] == '{':
            self.i += 1
            out = {}
            while True:
                self._skip_inline_ws()
                if s[self.i] == '}':
                    self.i += 1
                    return out
                eq = s.index('=', self.i)
                keys = split_key(s[self.i:eq])
                self.i = eq + 1
                val = self._value()
                target = out
                for part in keys[:-1]:
                    target = target.setdefault(part, {})
                target[keys[-1]] = val
                self._skip_inline_ws()
                if s[self.i] == ',':
                    self.i += 1
        m = re.compile(r'[^\s,\]}#]+').match(s, i)
        if not m:
            raise TomlError('Bad value at %d' % i)
        self.i = m.end()
        word = m.group(0)
        if word == 'true':
            return True
        if word == 'false':
            return False
        try:
            return int(word.replace('_', ''))
        except ValueError:
            try:
                return float(word.replace('_', ''))
            except ValueError:
                return word


def dumps_string(value):
    return json.dumps(str(value))


def dumps_array(values):
    return '[' + ', '.join(dumps_string(v) for v in values) + ']'
