"""Read whatscribe's transcript.jsonl (one message per line: at, who, type, text) and pull out what people agreed."""
import json
import re
from pathlib import Path

MONTHS = 'jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december'
DAYS = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|tonight|next week'
MONEY = re.compile(r'(?:[£$€]\s?\d[\d,]*(?:\.\d{1,2})?(?:\s?[km])?|\b\d[\d,]*(?:\.\d{1,2})?\s?(?:gbp|usd|eur|quid|pounds|euros|dollars)\b)', re.I)
DATE = re.compile(r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s(?:%s)\b|(?:%s)\s\d{1,2}(?:st|nd|rd|th)?\b|\d{1,2}/\d{1,2}(?:/\d{2,4})?|(?:%s))'
                  % (MONTHS, MONTHS, DAYS), re.I)
TIME = re.compile(r'\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\b\d{1,2}:\d{2}\b', re.I)


class ChatError(ValueError):
    pass


def load(path):
    path = Path(path).expanduser()
    if not path.is_file():
        raise ChatError('No transcript at %s. Run whatscribe sync first, or check output_dir in whatscribe config.' % path)
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            raise ChatError('Line %d of %s is not JSON.' % (number, path.name)) from None
        rows.append({'at': str(row.get('at', '')), 'who': str(row.get('who', '')), 'type': str(row.get('type', '')),
                     'text': str(row.get('text') or '')})
    return rows


def find(rows, since='', until='', contains='', kind='', who=''):
    out = []
    for row in rows:
        day = row['at'][:10]
        if since and day < since:
            continue
        if until and day > until:
            continue
        if kind and row['type'] != kind:
            continue
        if who and who.lower() not in row['who'].lower():
            continue
        if contains and contains.lower() not in row['text'].lower():
            continue
        out.append(row)
    return out


def extract(rows):
    """Every money amount, date and time mentioned, with the message it came from."""
    found = []
    for row in rows:
        for kind, pattern in (('money', MONEY), ('date', DATE), ('time', TIME)):
            for match in pattern.finditer(row['text']):
                found.append({'kind': kind, 'value': match.group(0).strip(), 'at': row['at'], 'who': row['who'],
                              'type': row['type'], 'text': row['text']})
    return found


SAMPLE = [
    {'at': '2026-10-19T08:12:00', 'id': '1', 'who': 'Me', 'type': 'text', 'text': 'Morning Dave, how is the kitchen wall looking?'},
    {'at': '2026-10-19T08:40:00', 'id': '2', 'who': 'Dave (builder)', 'type': 'voice',
     'text': 'Wall is down, we found an old pipe, so plastering moves to Thursday. The extra for the pipe is about £350.'},
    {'at': '2026-10-19T09:02:00', 'id': '3', 'who': 'Me', 'type': 'text', 'text': 'OK. Is Thursday at 8am still fine for the skip?'},
    {'at': '2026-10-19T09:15:00', 'id': '4', 'who': 'Dave (builder)', 'type': 'text', 'text': 'Skip Thursday 8am yes. Tiles arrive 24th October, total for tiles £1,240.'},
    {'at': '2026-10-21T17:30:00', 'id': '5', 'who': 'Dave (builder)', 'type': 'voice', 'text': 'Plastering done. Invoice for this week coming Friday.'},
]
