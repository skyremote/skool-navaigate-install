"""Build and keep the member's OWN writing voice: scaffold, check drafts, record corrections."""
import os
import re
from datetime import date
from pathlib import Path

# Words and shapes that make text read as generated. The member's profile adds their own.
SLOP = ['delve', 'unlock', 'unleash', 'elevate', 'game-changer', 'game changer', 'revolutionise', 'revolutionize',
        'seamless', 'seamlessly', 'leverage', 'empower', 'robust', 'cutting-edge', 'in today\'s fast-paced world',
        'take it to the next level', 'whether you\'re a beginner or an expert', 'ever wondered', 'tapestry',
        'testament to', 'navigate the complexities', 'it\'s important to note', 'in conclusion', 'synergy']
JARGON = ['wedge', 'moat', 'flywheel', 'north star', 'land and expand']

PROFILE = """# {title}: writing voice profile

Built from {owner}'s own words. Every strong rule has a quote or a correction behind it.

## What the voice is doing
- <who you write to, and how: one person or a room; blunt or gentle>

## Rhythm and sentence shape
- <a rule, with a quote from your own transcript>

## Openers, pivots and closers
- Openers: <your real openers, e.g. "So", "Right">
- Closers: <how you end>

## Pronouns and reader relationship
- <when you say I, we and you>

## Signature vocabulary
- <phrases you really repeat, with the context>

## Proof habits
- <how you prove things: names, numbers, a story from this week>

## Language to remove
- <words you would never say, one per line>

## Draft checks
1. Read it aloud. Could you hear yourself say it?
2. Run: tools-voice check <draft> --profile PROFILE.md
3. Every strong claim has a real name or number behind it.
4. Apply the calibration log below.

## Calibration log
"""

SKILL = """---
name: {name}
description: Write anything in {owner}'s own voice (emails, posts, pages, messages) and check drafts against it. Use whenever text will carry {owner}'s name.
---

# {owner}'s voice

1. Read PROFILE.md and EXAMPLES.md in this folder before drafting.
2. Draft, then run `tools-voice check <draft> --profile PROFILE.md` and fix every line it flags.
3. Read it aloud. If {owner} could not say it on a call, rewrite it as one spoken sentence.
4. When {owner} corrects a line, record it: `tools-voice calibrate --profile PROFILE.md --before "..." --after "..." --lesson "..."`.
   The calibration log is the authority when it disagrees with anything else.
"""

EXAMPLES = """# {owner}: approved examples

Only pieces {owner} has read and approved go here. One per situation: an email, a public post, a teaching piece.
"""


class VoiceError(ValueError):
    pass


def slug(name):
    value = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not value:
        raise VoiceError('Give your voice a name, for example your first name.')
    return value


def scaffold(owner, folder):
    """Make <folder>/<slug>-voice with SKILL.md, PROFILE.md and EXAMPLES.md. Never overwrites."""
    name = slug(owner) + '-voice'
    target = Path(folder).expanduser() / name
    if target.exists():
        raise VoiceError(str(target) + ' already exists. Edit it, or pick a new folder.')
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text(SKILL.format(name=name, owner=owner))
    (target / 'PROFILE.md').write_text(PROFILE.format(title=owner, owner=owner))
    (target / 'EXAMPLES.md').write_text(EXAMPLES.format(owner=owner))
    return target


def profile_bans(text):
    """Bullet lines under '## Language to remove' (placeholders ignored)."""
    bans, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip().lower() == '## language to remove'
            continue
        if inside and line.strip().startswith(('-', '*')):
            word = line.strip().lstrip('-* ').strip().strip('"').strip()
            if word and not word.startswith('<'):
                bans.append(word.lower())
    return bans


def sentences(text):
    body = re.sub(r'```.*?```', ' ', text, flags=re.S)
    body = re.sub(r'^#.*$', ' ', body, flags=re.M)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', ' '.join(body.split())) if s.strip()]


def check(draft, profile_text=''):
    """Return a list of problems with the draft. Empty means it passes."""
    problems = []
    lower = ' ' + ' '.join(draft.lower().split()) + ' '
    for word in SLOP + JARGON + profile_bans(profile_text):
        if re.search(r'(?<![a-z])' + re.escape(word) + r'(?![a-z])', lower):
            problems.append('Remove "%s": it is on the %s list.' % (word, 'jargon' if word in JARGON else
                                                                     'generated-text' if word in SLOP else 'your own'))
    run = []
    for s in sentences(draft) + ['']:
        if s and len(s.split()) <= 4:
            run.append(s)
            continue
        if len(run) >= 3:
            problems.append('Three or more fragments in a row: "%s". Join them into one spoken sentence.' % ' '.join(run)[:80])
        run = []
    dashes = draft.count('—')
    if dashes > 1:
        problems.append('%d long dashes. Use commas, or split the sentence.' % dashes)
    triads = re.findall(r'\b(\w+), (\w+),? and (\w+)\b', draft)
    adjective_ends = ('ful', 'ive', 'al', 'ic', 'ous', 'ble')
    for triad in triads:
        if all(w.lower().endswith(adjective_ends) for w in triad):
            problems.append('An adjective stack: "%s, %s and %s". Keep the one you can prove.' % triad)
    return problems


def calibrate(profile_path, before, after, lesson, when=None):
    path = Path(profile_path).expanduser()
    text = path.read_text()
    if '## Calibration log' not in text:
        text = text.rstrip() + '\n\n## Calibration log\n'
    entry = '\n**%s**\n- Draft: "%s"\n- Rewrite: "%s"\n- Lesson: %s\n' % (when or date.today().isoformat(), before, after, lesson)
    path.write_text(text.rstrip() + '\n' + entry)
    return entry


def find_builder(env=None):
    """Where the public voice-skill-builder is installed, or None."""
    env = os.environ if env is None else env
    home = Path(env.get('HOME') or Path.home())
    candidates = [env.get('VOICE_SKILL_BUILDER', '')] + [str(home / d / 'voice-skill-builder') for d in
                                                          ('.claude/skills', '.agents/skills', '.codex/skills', '.cursor/skills')]
    for c in candidates:
        if c and (Path(c) / 'scripts/extract_voice_evidence.py').is_file():
            return Path(c)
    return None
