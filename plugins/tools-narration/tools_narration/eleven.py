"""The member's own ElevenLabs account: voices, quota, speech with timings, and an instant clone of their own voice."""
import json
import mimetypes
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from . import config

BASE = 'https://api.elevenlabs.io/v1'
NO_KEY = ('No ElevenLabs API key found.\n'
          'Create one at elevenlabs.io: your profile menu, API Keys. Then either:\n'
          '  Claude Code: /plugin, tools-narration, Configure, paste it as "ElevenLabs API key"\n'
          '  Codex or Cursor: export ELEVENLABS_API_KEY=... in your shell profile\n'
          'Never paste the key into a chat.')
NO_VOICE = ('No voice chosen. Pick one of YOUR voices: tools-narration voices, then set its id:\n'
            '  Claude Code: /plugin, tools-narration, Configure, "Your ElevenLabs voice id"\n'
            '  Codex or Cursor: export ELEVENLABS_VOICE_ID=... in your shell profile\n'
            'or pass --voice-id for one run.')


class ElevenError(RuntimeError):
    pass


def api_key(env=None):
    key = config.get('ELEVENLABS_API_KEY', 'elevenlabs_api_key', env=env)
    if not key:
        raise ElevenError(NO_KEY)
    return key


def voice_id(explicit=None, env=None):
    value = explicit or config.get('ELEVENLABS_VOICE_ID', 'voice_id', env=env)
    if not value:
        raise ElevenError(NO_VOICE)
    return value


def call(method, path, key, body=None, headers=None, raw=False, opener=urllib.request.urlopen):
    head = {'xi-api-key': key, 'User-Agent': 'aios-tools-narration/2.0'}
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode()
        head['Content-Type'] = 'application/json'
    head.update(headers or {})
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=head)
    try:
        with opener(req, timeout=300) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:300].decode(errors='ignore')
        hint = {401: 'the key was refused', 402: 'your plan has run out of characters',
                422: 'a setting was not accepted'}.get(error.code, 'see the message')
        raise ElevenError('ElevenLabs said HTTP %d (%s): %s' % (error.code, hint, detail)) from None
    except urllib.error.URLError as error:
        raise ElevenError('Could not reach ElevenLabs: %s' % error.reason) from None
    return data if raw else json.loads(data.decode() or '{}')


def account(key, send=call):
    data = send('GET', '/user/subscription', key)
    return {'tier': data.get('tier', '?'), 'used': data.get('character_count', 0), 'limit': data.get('character_limit', 0)}


def voices(key, search='', send=call):
    data = send('GET', '/voices', key)
    rows = [{'id': v.get('voice_id', ''), 'name': v.get('name', ''), 'category': v.get('category', '')}
            for v in data.get('voices', [])]
    return [r for r in rows if search.lower() in r['name'].lower()]


def speech_with_timings(key, voice, text, model, settings, send=call):
    path = '/text-to-speech/%s/with-timestamps?output_format=mp3_44100_128' % urllib.parse.quote(voice)
    return send('POST', path, key, {'text': text, 'model_id': model, 'voice_settings': settings})


def multipart(fields, files):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields:
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, name, value)).encode())
    for name, path in files:
        path = Path(path)
        kind = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                      % (boundary, name, path.name, kind)).encode() + path.read_bytes() + b'\r\n')
    parts.append(('--%s--\r\n' % boundary).encode())
    return b''.join(parts), 'multipart/form-data; boundary=' + boundary


def clone(key, name, recordings, send=call):
    """Instant voice clone from the member's OWN recordings. Returns the new voice id."""
    body, kind = multipart([('name', name), ('description', 'My own voice, cloned with my consent')],
                           [('files', r) for r in recordings])
    return send('POST', '/voices/add', key, body, headers={'Content-Type': kind}).get('voice_id', '')
