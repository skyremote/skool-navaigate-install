"""Propose removals: filler words, long pauses, stutters, dead air at each end.

A plan is a proposal. Nothing is cut until the member approves it.
"""
from .core import fps_value, snap_in

MIN_CUT = 0.08


def _cut(kind, start, end, text, reason, selected, fps, word_ids=()):
    start, end = snap_in(start, end, fps)
    if end - start < MIN_CUT:
        return None
    return {'kind': kind, 'start': start, 'end': end, 'text': text, 'reason': reason,
            'selected': selected, 'words': list(word_ids)}


def _phrase_hits(words, phrases):
    """Find multi-word soft fillers such as 'you know'. Returns (first, last) index pairs."""
    hits = []
    tokens = [w['word'] for w in words]
    for phrase in phrases:
        parts = phrase.split()
        n = len(parts)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == parts:
                hits.append((i, i + n - 1, phrase))
    return hits


def propose(words, media, settings):
    fps = fps_value(media)
    duration = media['duration']
    pad = settings['pad']
    fillers = set(settings['fillers'])
    cuts = []
    if not words:
        return []
    filler_ids = {w['id'] for w in words if w['word'] in fillers}

    def prev_end(i):
        return words[i - 1]['end'] if i > 0 else 0.0

    def next_start(i):
        return words[i + 1]['start'] if i + 1 < len(words) else duration

    # 1. Filler words, selected by default. Remove the word and the air around it, keep a little pad.
    i = 0
    while i < len(words):
        if words[i]['id'] in filler_ids:
            j = i
            while j + 1 < len(words) and words[j + 1]['id'] in filler_ids:
                j += 1
            start = max(prev_end(i) + pad, words[i]['start'] - 0.25)
            end = min(next_start(j) - pad, words[j]['end'] + 0.25)
            start = min(start, words[i]['start'])
            end = max(end, words[j]['end'])
            text = ' '.join(w['text'] for w in words[i:j + 1])
            c = _cut('filler', start, end, text, 'Filler word', True, fps, [w['id'] for w in words[i:j + 1]])
            if c:
                cuts.append(c)
            i = j + 1
        else:
            i += 1

    # 2. Stutters: the same word twice in a row ("the the"). Proposed, not selected.
    for a, b in zip(words, words[1:]):
        if a['word'] and a['word'] == b['word'] and a['id'] not in filler_ids and b['start'] - a['end'] < 0.6:
            c = _cut('stutter', a['start'] - 0.02, b['start'] - pad, a['text'], 'Repeated word', False, fps, [a['id']])
            if c:
                cuts.append(c)

    # 3. Soft fillers ("you know", "like"). Often real speech, so proposed but not selected.
    for first, last, phrase in _phrase_hits(words, settings.get('soft_fillers', [])):
        start = max(prev_end(first) + pad, words[first]['start'] - 0.1)
        end = min(next_start(last) - pad, words[last]['end'] + 0.1)
        c = _cut('soft-filler', start, end, ' '.join(w['text'] for w in words[first:last + 1]),
                 'Possible filler: "' + phrase + '". Listen before you remove it.', False, fps,
                 [w['id'] for w in words[first:last + 1]])
        if c:
            cuts.append(c)

    # 4. Long pauses between kept words, tightened to keep_pause.
    kept = [w for w in words if w['id'] not in filler_ids]
    keep = settings['keep_pause']
    for a, b in zip(kept, kept[1:]):
        gap = b['start'] - a['end']
        if gap > settings['max_pause']:
            start = a['end'] + keep / 2
            end = b['start'] - keep / 2
            c = _cut('pause', start, end, '', 'Pause of %.1f s tightened to %.1f s' % (gap, keep), True, fps)
            if c:
                cuts.append(c)

    # 5. Dead air before the first word and after the last.
    first, last = words[0], words[-1]
    if first['start'] > settings['lead_keep'] + MIN_CUT:
        c = _cut('lead', 0.0, first['start'] - settings['lead_keep'], '', 'Silence before you start', True, fps)
        if c:
            cuts.append(c)
    if duration - last['end'] > settings['tail_keep'] + MIN_CUT:
        c = _cut('tail', last['end'] + settings['tail_keep'], duration, '', 'Silence after you finish', True, fps)
        if c:
            cuts.append(c)
    return number(merge(cuts))


def merge(cuts):
    """Overlapping proposals of the same selection state are joined, so the review stays readable."""
    cuts = sorted(cuts, key=lambda c: (c['start'], c['end']))
    out = []
    for c in cuts:
        if out and c['start'] <= out[-1]['end'] and c['selected'] == out[-1]['selected']:
            last = out[-1]
            last['end'] = max(last['end'], c['end'])
            if c['kind'] != last['kind']:
                last['kind'] = last['kind'] + '+' + c['kind']
                last['reason'] = last['reason'] + '; ' + c['reason']
            last['text'] = ' '.join(t for t in (last['text'], c['text']) if t)
            last['words'] = sorted(set(last['words']) | set(c['words']))
        else:
            out.append(dict(c))
    return out


def number(cuts):
    for n, c in enumerate(cuts, 1):
        c['id'] = n
    return cuts


def selected_ranges(cuts):
    """Union of the chosen removals, as sorted non-overlapping (start, end) pairs."""
    spans = sorted((c['start'], c['end']) for c in cuts if c['selected'])
    out = []
    for s, e in spans:
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def keep_segments(removals, duration):
    segments, cursor = [], 0.0
    for s, e in removals:
        if s > cursor:
            segments.append((round(cursor, 4), round(s, 4)))
        cursor = max(cursor, e)
    if cursor < duration:
        segments.append((round(cursor, 4), round(duration, 4)))
    return [(s, e) for s, e in segments if e - s > 0.001]


def to_output(t, removals):
    """Map a source time to the edited timeline. Times inside a removal land on its join."""
    shift = 0.0
    for s, e in removals:
        if t >= e:
            shift += e - s
        elif t > s:
            return round(s - shift, 4)
        else:
            break
    return round(t - shift, 4)


def inside(t, removals):
    return any(s <= t < e for s, e in removals)


def summary(cuts, duration):
    chosen = [c for c in cuts if c['selected']]
    saved = sum(e - s for s, e in selected_ranges(cuts))
    kinds = {}
    for c in chosen:
        for k in c['kind'].split('+'):
            kinds[k] = kinds.get(k, 0) + 1
    return {'proposals': len(cuts), 'selected': len(chosen), 'by_kind': kinds,
            'seconds_removed': round(saved, 2), 'new_duration': round(duration - saved, 2)}


def markdown(cuts, media, words_file):
    s = summary(cuts, media['duration'])
    lines = ['# Edit plan', '',
             'Source length %.1f s. Selected removals take out %.1f s, leaving %.1f s.' % (
                 media['duration'], s['seconds_removed'], s['new_duration']),
             'Transcript: ' + words_file, '',
             '| # | Keep or cut | Kind | From | To | Words | Why |',
             '|---|---|---|---|---|---|---|']
    for c in cuts:
        lines.append('| %d | %s | %s | %.2f | %.2f | %s | %s |' % (
            c['id'], 'CUT' if c['selected'] else 'keep (proposed)', c['kind'], c['start'], c['end'],
            c['text'].replace('|', '/') or '(silence)', c['reason']))
    lines += ['', 'To change the plan, approve with --drop or --add. Example:',
              '`shelf-video approve --project <folder> --drop 3,7 --add 4,12`']
    return '\n'.join(lines) + '\n'
