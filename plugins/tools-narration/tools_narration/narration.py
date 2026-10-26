"""Continuous narration: one take for the whole script, then cut at the aligned slide boundaries.

Separate takes per slide drift in tone and level even with identical settings. One performance, cut where
the alignment says one slide's words end and the next slide's begin, sounds like one person in one room.
"""
import json
import shutil
import subprocess
from pathlib import Path

SEPARATOR = '\n\n'
MAX_CHARS = 9500  # under the per-request limit of the multilingual model; split into chapters above this
TARGET_LUFS = -16.0


class NarrationError(ValueError):
    pass


def load_slides(path):
    """slides.json: a list of {"title": ..., "notes": ["paragraph", ...]} in order. Returns the notes per slide."""
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list) or not data:
        raise NarrationError('slides.json must be a list of slides, each with "notes".')
    out = []
    for i, slide in enumerate(data, 1):
        notes = slide.get('notes') if isinstance(slide, dict) else None
        if isinstance(notes, str):
            notes = [notes]
        if not notes or not all(isinstance(n, str) and n.strip() for n in notes):
            raise NarrationError('Slide %d has no spoken notes.' % i)
        out.append(' '.join(' '.join(n.split()) for n in notes))
    return out


def join(slides):
    """The single script and each slide's (start, end) character span in it."""
    script, spans = '', []
    for i, text in enumerate(slides):
        if i:
            script += SEPARATOR
        spans.append((len(script), len(script) + len(text)))
        script += text
    if len(script) > MAX_CHARS:
        raise NarrationError('The script is %d characters; the limit for one take is %d. Split the deck into chapters '
                             'and narrate each chapter as one take.' % (len(script), MAX_CHARS))
    return script, spans


def boundaries(alignment, spans, duration):
    """Cut times: halfway between the last sound of one slide and the first sound of the next."""
    chars = alignment.get('characters') or []
    starts = alignment.get('character_start_times_seconds') or []
    ends = alignment.get('character_end_times_seconds') or []
    if not chars or len(chars) != len(starts) or len(chars) != len(ends):
        raise NarrationError('The alignment from ElevenLabs is missing or uneven; nothing was cut.')
    if spans[-1][1] > len(chars):
        raise NarrationError('The alignment is shorter than the script; the take may be cut off. Listen before using it.')
    cuts = [0.0]
    for (_, prev_end), (next_start, _) in zip(spans, spans[1:]):
        last = max(i for i in range(prev_end) if chars[i].strip())
        first = min(i for i in range(next_start, len(chars)) if chars[i].strip())
        gap = starts[first] - ends[last]
        if gap < 0:
            raise NarrationError('Slides overlap in the alignment; nothing was cut.')
        cuts.append(round((ends[last] + starts[first]) / 2, 3))
    cuts.append(round(duration, 3))
    if any(b <= a for a, b in zip(cuts, cuts[1:])):
        raise NarrationError('Cut times are not in order; nothing was cut.')
    return cuts


def ffmpeg_ok():
    return bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))


def run(args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, check=True)


def duration_of(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path]).stdout)


def loudness(path):
    err = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json',
               '-f', 'null', '-']).stderr
    return json.JSONDecoder().raw_decode(err[err.rfind('{'):])[0]


def master_and_split(take, cuts, out):
    """Level the whole take once (two-pass loudnorm to a PCM master), then cut every slide from that master."""
    m = loudness(take)
    level = ('loudnorm=I=-16:TP=-1.5:LRA=7:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true'
             % (m['input_i'], m['input_tp'], m['input_lra'], m['input_thresh'], m['target_offset']))
    master = out / 'master.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-i', take, '-af', level, '-ar', '44100', '-c:a', 'pcm_s24le', master])
    tracks = []
    for i, (start, end) in enumerate(zip(cuts, cuts[1:]), 1):
        clip = out / ('slide-%02d.mp3' % i)
        run(['ffmpeg', '-y', '-hide_banner', '-ss', start, '-i', master, '-t', round(end - start, 3),
             '-af', 'alimiter=limit=0.84:level=false', '-c:a', 'libmp3lame', '-b:a', '128k', clip])
        tracks.append({'slide': i, 'file': clip.name, 'start': start, 'end': end, 'seconds': round(duration_of(clip), 2)})
    master.unlink()
    return tracks
