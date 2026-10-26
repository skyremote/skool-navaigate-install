"""The release-clock gate. Approving a post is not a time. A post goes out only on an explicit
"publish now", or on a date, time and timezone the member gave, and the hook checks Blotato's call against it.
"""
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

QUESTION = 'When should this go live? Please give me the date, time and timezone, or say "publish now".'
LIVE = re.compile(r'\b(publish|post|send it live|go live|put it live|send it)\s+(it\s+)?(right\s+)?now\b|\bimmediately\b|\blive now\b', re.I)
TIME_WORD = re.compile(r'\b\d{1,2}(:\d{2})?\s*(am|pm)\b|\b\d{1,2}:\d{2}\b|\bnoon\b|\bmidday\b', re.I)
TTL = 30 * 60
WRITE_TOOLS = re.compile(r'blotato_(create_post|update_schedule)$', re.I)


class ReleaseError(ValueError):
    pass


def receipt_path():
    base = os.environ.get('XDG_DATA_HOME') or str(Path.home() / '.local/share')
    return Path(base) / 'tools-social/release.json'


def live(words):
    if not LIVE.search(words or ''):
        raise ReleaseError('Those words do not ask for an immediate post. ' + QUESTION)
    return {'level': 'live', 'words': words, 'utc': None, 'created': time.time()}


def scheduled(words, at, zone):
    if not TIME_WORD.search(words or ''):
        raise ReleaseError("The member's words give no time of day. " + QUESTION)
    try:
        tz = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise ReleaseError('Unknown timezone "%s". Use a name like Europe/London or America/New_York.' % zone) from None
    try:
        local = datetime.fromisoformat(at)
    except ValueError:
        raise ReleaseError('Give the time as YYYY-MM-DDTHH:MM, for example 2026-10-28T09:00.') from None
    if local.tzinfo is None:
        local = local.replace(tzinfo=tz)
    utc = local.astimezone(timezone.utc)
    if utc.timestamp() < time.time():
        raise ReleaseError('That time has already passed: %s.' % local.isoformat())
    return {'level': 'scheduled', 'words': words, 'utc': utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'local': local.strftime('%A %d %B %Y, %H:%M ') + zone, 'created': time.time()}


def save(receipt, path=None):
    path = path or receipt_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2))
    return path


def load(path=None, now=None):
    path = path or receipt_path()
    if not path.exists():
        return None
    receipt = json.loads(path.read_text())
    if (now or time.time()) - receipt.get('created', 0) > TTL:
        return None
    return receipt


def parse_utc(value):
    value = value.replace('Z', '+00:00')
    stamp = datetime.fromisoformat(value)
    if stamp.tzinfo is None:
        return None
    return stamp.astimezone(timezone.utc)


def decide(tool_name, tool_input, receipt):
    """Return a deny reason, or None to allow."""
    if not tool_name.startswith('mcp__') or not WRITE_TOOLS.search(tool_name):
        return None
    if not receipt:
        return 'No release time on record. Ask the member: ' + QUESTION + ' Then run tools-social release.'
    when = (tool_input or {}).get('scheduledTime')
    if (tool_input or {}).get('useNextFreeSlot'):
        return 'The next free slot is not a time the member gave. ' + QUESTION
    if receipt['level'] == 'live':
        if when:
            return 'The member asked to publish now, but this call schedules for %s. Ask again.' % when
        return None
    if not when:
        return 'The member gave a time (%s), but this call would publish now. Pass scheduledTime=%s.' % (receipt['local'], receipt['utc'])
    stamp = parse_utc(when)
    if stamp is None:
        return 'scheduledTime has no timezone. Pass %s.' % receipt['utc']
    if abs((stamp - parse_utc(receipt['utc'])).total_seconds()) > 60:
        return 'scheduledTime %s is not the time the member gave (%s, which is %s).' % (when, receipt['local'], receipt['utc'])
    return None
