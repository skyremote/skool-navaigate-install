"""Shot-by-shot video prompts: the four sections we write for every AI video, and a check before credits are spent."""
import hashlib
import json
import re
import time
from pathlib import Path

SECTIONS = ('SHOT-BY-SHOT EFFECTS TIMELINE', 'MASTER EFFECTS INVENTORY', 'EFFECTS DENSITY MAP', 'ENERGY ARC')
SHOT = re.compile(r'^SHOT\s+(\d+)\s*\((\d+):(\d{2})\s*[-–]\s*(\d+):(\d{2})\)', re.M)
HYPE = ('stunning', 'breathtaking', 'epic', 'mind-blowing', 'jaw-dropping', 'incredible')
CALIBRATION = [(10, 4, 7), (20, 8, 14), (30, 12, 20)]  # up to N seconds: min and max shots

SAMPLE = """SHOT-BY-SHOT EFFECTS TIMELINE

SHOT 1 (0:00-0:02) — Flour in the light
• EFFECT: slow motion (approximately 25% speed)
• Flour drifts through a beam of morning light above a wooden bench in a small bakery (fictional Northwind Bakery)
• Static camera, close, shallow depth of field
• Exits on a soft focus pull to the next shot

SHOT 2 (0:02-0:05) — The cake
• EFFECT: slow push-in + rack focus
• A lemon sponge on a stand, the baker's hands placing the last berry
• Camera pushes in slowly at eye level
• Cut on the hands lifting away

SHOT 3 (0:05-0:08) — The phone (SIGNATURE VISUAL EFFECT)
• EFFECT: match cut
• The same cake appears on a phone screen in a customer's hand, the order button pressed
• Over-the-shoulder, handheld, gentle sway
• Hard cut on the press

SHOT 4 (0:08-0:10) — Collected
• EFFECT: speed ramp (deceleration)
• The customer collects the boxed cake at the counter and smiles
• Wide, static
• Fades to warm white

MASTER EFFECTS INVENTORY
1. Slow motion, used 1x (shot 1): sets a calm opening.
2. Push-in and rack focus, used 1x (shot 2): draws the eye to the product.
3. Match cut, used 1x (shot 3): links the cake to ordering online.
4. Speed ramp, used 1x (shot 4): lands the ending.

EFFECTS DENSITY MAP
0:00-0:05 = LOW DENSITY (slow motion, push-in: 2 effects in 5 s)
0:05-0:10 = MEDIUM DENSITY (match cut, speed ramp: 2 effects in 5 s)

ENERGY ARC
Act 1: quiet craft in the bakery. Act 2: the match cut to the phone is the hook. Act 3: the cake in the customer's hands resolves it.
"""


def seconds(m, s):
    return int(m) * 60 + int(s)


def check_video(text, target=None):
    problems = []
    for name in SECTIONS:
        if name not in text.upper():
            problems.append('Missing section: ' + name)
    shots = [(int(n), seconds(a, b), seconds(c, d)) for n, a, b, c, d in SHOT.findall(text)]
    if not shots:
        return problems + ['No shots found. Each shot starts "SHOT 1 (0:00-0:02) — name".']
    expected = 0
    for i, (number, start, end) in enumerate(shots):
        if number != i + 1:
            problems.append('Shots are not numbered in order at SHOT %d.' % number)
        if start != expected:
            problems.append('SHOT %d starts at %d s, but the previous shot ended at %d s (gap or overlap).' % (number, start, expected))
        if end <= start:
            problems.append('SHOT %d ends before it starts.' % number)
        expected = end
    blocks = re.split(r'^SHOT\s+\d+', text, flags=re.M)[1:]
    for i, block in enumerate(blocks, 1):
        body = block.split('MASTER EFFECTS INVENTORY')[0]
        if 'EFFECT:' not in body.upper():
            problems.append('SHOT %d has no "EFFECT:" line.' % i)
    total = shots[-1][2]
    if target and abs(total - target) > 1:
        problems.append('The shots add up to %d s, but the target is %d s.' % (total, target))
    for limit, low, high in CALIBRATION:
        if total <= limit:
            if not low <= len(shots) <= high:
                problems.append('%d shots for %d s. Aim for %d to %d shots at this length.' % (len(shots), total, low, high))
            break
    if 'SIGNATURE' not in text.upper():
        problems.append('Name one SIGNATURE VISUAL EFFECT, the shot people remember.')
    for word in HYPE:
        if re.search(r'\b' + word + r'\b', text, re.I):
            problems.append('Remove "%s". Describe what happens on screen instead.' % word)
    return problems


def log(folder, prompt_file, model, job='', result='', note=''):
    """Append one generation to the folder's manifest, so every output keeps its prompt, model and job."""
    folder = Path(folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    prompt = Path(prompt_file).expanduser()
    text = prompt.read_text()
    entry = {'when': time.strftime('%Y-%m-%dT%H:%M:%S'), 'prompt_file': prompt.name,
             'prompt_sha256': hashlib.sha256(text.encode()).hexdigest(), 'model': model, 'job': job,
             'result': result, 'note': note}
    with open(folder / 'manifest_v1.jsonl', 'a') as handle:
        handle.write(json.dumps(entry) + '\n')
    return entry
