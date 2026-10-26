"""Read-only client for Granola's official public API (https://public-api.granola.ai/v1).

Notes: GET /notes?limit=10[&cursor=...] -> {notes, hasMore, cursor}
One:   GET /notes/{id}?include=transcript -> note, transcript and summary
Transcript segments carry speaker.source: "microphone" (the account owner) or
"speaker" (everyone else; Granola does not name other people here).
"""
import json
import urllib.error
import urllib.parse
import urllib.request

from . import config

BASE = 'https://public-api.granola.ai/v1'
NO_KEY = ('No Granola API key found.\n'
          'Granola needs a Business or Enterprise plan for the API. In the Granola app open\n'
          'Settings, Connectors, API keys, and create a key (it starts grn_). Then either:\n'
          '  Claude Code: /plugin, tools-meetings, Configure, paste it as "Granola API key"\n'
          '  Codex or Cursor: export GRANOLA_API_KEY=grn_... in your shell profile\n'
          'Never paste the key into a chat.')


class GranolaError(RuntimeError):
    pass


def api_key(env=None):
    key = config.get('GRANOLA_API_KEY', 'granola_api_key', env=env)
    if not key:
        raise GranolaError(NO_KEY)
    if not key.startswith('grn_'):
        raise GranolaError('That Granola key does not start with grn_. Create a new one in Settings, Connectors, API keys.')
    return key


def fetch(path, key, opener=urllib.request.urlopen):
    request = urllib.request.Request(BASE + path, headers={
        'Authorization': 'Bearer ' + key, 'Accept': 'application/json', 'User-Agent': 'aios-tools-meetings/2.0'})
    try:
        with opener(request, timeout=90) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        hint = {401: 'the key was refused; create a new one', 403: 'your plan or this note does not allow API access',
                404: 'no note with that id, or it is not yours'}.get(error.code, 'see the message above')
        raise GranolaError('Granola said HTTP %d: %s' % (error.code, hint)) from None
    except urllib.error.URLError as error:
        raise GranolaError('Could not reach Granola: %s' % error.reason) from None


def list_notes(limit, key, get=fetch):
    out, cursor = [], None
    while len(out) < limit:
        path = '/notes?limit=10' + ('&cursor=' + urllib.parse.quote(cursor) if cursor else '')
        page = get(path, key)
        out += page.get('notes', [])
        cursor = page.get('cursor')
        if not page.get('hasMore') or not cursor:
            break
    return out[:limit]


def note(note_id, key, transcript=False, get=fetch):
    data = get('/notes/' + urllib.parse.quote(note_id) + ('?include=transcript' if transcript else ''), key)
    return data.get('note', data) if isinstance(data, dict) else data


def title_of(n):
    return n.get('title') or '(untitled)'


def date_of(n):
    return str(n.get('created_at') or n.get('updated_at') or '')[:16].replace('T', ' ')


def attendees_of(n):
    names = []
    for person in n.get('attendees') or []:
        names.append(person.get('name') or person.get('email') or '' if isinstance(person, dict) else str(person))
    return [x for x in names if x]


def transcript_text(n, me='Me', raw=False):
    """Merge consecutive segments from the same side into labelled turns."""
    def label(source):
        return me if source == 'microphone' else 'Others'
    segments = n.get('transcript') or []
    if raw:
        return '\n'.join('[%s] %s: %s' % ((s.get('start_time') or '')[11:19], label((s.get('speaker') or {}).get('source')),
                                          (s.get('text') or '').strip()) for s in segments)
    turns, current, words = [], None, []
    for s in segments:
        source = (s.get('speaker') or {}).get('source', 'speaker')
        text = (s.get('text') or '').strip()
        if not text:
            continue
        if source == current:
            words.append(text)
            continue
        if words:
            turns.append(label(current) + ': ' + ' '.join(words))
        current, words = source, [text]
    if words:
        turns.append(label(current) + ': ' + ' '.join(words))
    return '\n'.join(turns)
