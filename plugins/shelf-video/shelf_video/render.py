"""Approve a plan, then render the cut, the captions and the export in one FFmpeg pass."""
import json
import time
from pathlib import Path

from . import captions, plan
from .core import ShelfError, digest, latest, need, next_version, read, run, signature, write

FADE = 0.012


def approve(root, plan_file, drop=(), add=(), remove=(), confirmed=False, note=''):
    """Record the member's decision. Only run this after the member has said yes in their own words."""
    if not confirmed:
        raise ShelfError('Approval needs --yes, typed by the member after they have read the plan. '
                         'An agent must not approve on their behalf.')
    plan_file = Path(plan_file)
    data = read(plan_file)
    cuts = [dict(c) for c in data['cuts']]
    ids = {c['id'] for c in cuts}
    for n in list(drop) + list(add):
        if n not in ids:
            raise ShelfError('No proposal number %d in %s' % (n, plan_file.name))
    for c in cuts:
        if c['id'] in drop:
            c['selected'] = False
        if c['id'] in add:
            c['selected'] = True
    media = data['media']
    next_id = max(ids or {0}) + 1
    for span in remove:
        try:
            a, b = (float(x) for x in span.split(':'))
        except ValueError:
            raise ShelfError('Use --remove START:END in seconds, such as 12.4:13.1')
        if not 0 <= a < b <= media['duration']:
            raise ShelfError('Range %s is outside the recording.' % span)
        cuts.append({'id': next_id, 'kind': 'manual', 'start': a, 'end': b, 'text': '', 'words': [],
                     'reason': 'Removed by the member', 'selected': True})
        next_id += 1
    folder = Path(root) / 'approvals'
    target = next_version(folder, 'approval', '.json')
    record = {'plan': plan_file.name, 'plan_sha256': digest(plan_file), 'approved_by': 'member',
              'approved_at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'note': note, 'cuts': cuts,
              'summary': plan.summary(cuts, media['duration'])}
    record['signature'] = signature({'plan_sha256': record['plan_sha256'], 'cuts': cuts})
    write(target, record)
    return target, record


def current_approval(root):
    file = latest(Path(root) / 'approvals', 'approval', '.json')
    if not file:
        raise ShelfError('No approval yet. Show the member the plan, then they run: shelf-video approve --yes')
    record = read(file)
    plan_file = Path(root) / 'plans' / record['plan']
    if not plan_file.exists() or digest(plan_file) != record['plan_sha256']:
        raise ShelfError('The approved plan has changed since approval. Make a new plan and approve it again.')
    if signature({'plan_sha256': record['plan_sha256'], 'cuts': record['cuts']}) != record['signature']:
        raise ShelfError(file.name + ' was edited by hand. Approve again with shelf-video approve.')
    return file, record


def filtergraph(segments, fps, burn, loudnorm):
    parts, labels = [], []
    for i, (s, e) in enumerate(segments):
        length = e - s
        fade = min(FADE, length / 4)
        parts.append('[0:v]trim=start=%.4f:end=%.4f,setpts=PTS-STARTPTS[v%d]' % (s, e, i))
        parts.append('[0:a]atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=%.4f,'
                     'afade=t=out:st=%.4f:d=%.4f[a%d]' % (s, e, fade, max(0, length - fade), fade, i))
        labels.append('[v%d][a%d]' % (i, i))
    parts.append('%sconcat=n=%d:v=1:a=1[vc][ac]' % (''.join(labels), len(segments)))
    video = '[vc]'
    if burn:
        parts.append('[1:v]fps=%s,format=rgba[cap]' % fps)
        parts.append('[vc][cap]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[vo]')
        video = '[vo]'
    else:
        parts.append('[vc]format=yuv420p[vo]')
        video = '[vo]'
    audio = '[ac]'
    if loudnorm:
        parts.append('[ac]loudnorm=I=-16:TP=-1.5:LRA=11[an]')
        audio = '[an]'
    return ';'.join(parts), video, audio


def render(root, project, words_data, settings, burn=True):
    need('ffmpeg', 'Install FFmpeg: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux).')
    approval_file, record = current_approval(root)
    media = project['media']
    removals = plan.selected_ranges(record['cuts'])
    segments = plan.keep_segments(removals, media['duration'])
    if not segments:
        raise ShelfError('The approved plan removes everything. Approve a plan that keeps some speech.')
    out = next_version(Path(root) / 'exports', 'edit', '')
    out.mkdir(parents=True)
    kept = captions.kept_words(words_data['words'], removals)
    style = settings['caption']
    cues = captions.build_cues(kept, style['max_chars'], style['max_seconds'], uppercase=style['uppercase'])
    (out / 'captions.srt').write_text(captions.srt(cues))
    expected = round(sum(e - s for s, e in segments), 3)
    graph, video, audio = filtergraph(segments, media['fps'], burn and bool(cues), settings['export']['loudnorm'])
    args = ['ffmpeg', '-v', 'error', '-y', '-i', project['source']]
    if burn and cues:
        listing, boxes = captions.overlay_images(cues, media['width'], media['height'], style, out / 'caption_frames')
        args += ['-f', 'concat', '-safe', '0', '-i', listing]
    else:
        boxes = []
    final = out / 'edited.mp4'
    args += ['-filter_complex', graph, '-map', video, '-map', audio, '-r', media['fps'],
             '-c:v', 'libx264', '-preset', 'medium', '-crf', str(settings['export']['crf']),
             '-c:a', 'aac', '-b:a', settings['export']['audio_bitrate'], '-ar', '48000',
             '-movflags', '+faststart', '-t', '%.3f' % expected, final]
    started = time.time()
    run(args)
    edit_map = {'source': project['source'], 'segments': segments, 'removals': removals,
                'expected_duration': expected, 'joins': _joins(segments)}
    write(out / 'edit_map.json', edit_map)
    receipt = {'tool': 'shelf-video', 'approval': approval_file.name, 'approval_signature': record['signature'],
               'output': final.name, 'output_sha256': digest(final), 'captions': 'captions.srt',
               'burnt_in': bool(burn and cues), 'cue_count': len(cues), 'caption_boxes': boxes[:3],
               'seconds': round(time.time() - started, 1), 'expected_duration': expected,
               'settings': {'caption': style, 'export': settings['export']}}
    write(out / 'receipt.json', receipt)
    return out, receipt


def _joins(segments):
    joins, t = [], 0.0
    for s, e in segments[:-1]:
        t += e - s
        joins.append(round(t, 3))
    return joins


def verify(export_dir, settings):
    """Check the real file: duration, a full decode, captions inside the film, frames at the joins."""
    export_dir = Path(export_dir)
    receipt = read(export_dir / 'receipt.json')
    edit_map = read(export_dir / 'edit_map.json')
    final = export_dir / receipt['output']
    problems, notes = [], []
    if digest(final) != receipt['output_sha256']:
        problems.append('The MP4 changed after rendering.')
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', final]))
    duration = float(info['format']['duration'])
    kinds = sorted(s['codec_type'] for s in info['streams'])
    if kinds != ['audio', 'video']:
        problems.append('Expected one video and one audio stream, found: ' + ', '.join(kinds))
    if abs(duration - edit_map['expected_duration']) > 0.15:
        problems.append('Duration %.2f s, expected %.2f s.' % (duration, edit_map['expected_duration']))
    decode = run(['ffmpeg', '-v', 'error', '-i', final, '-f', 'null', '-'])
    if decode.strip():
        problems.append('Decode warnings: ' + decode.strip()[:300])
    cues = captions.parse_srt((export_dir / 'captions.srt').read_text())
    last = 0.0
    for c in cues:
        if c['start'] < last - 0.001 or c['end'] <= c['start'] or c['end'] > duration + 0.05:
            problems.append('Caption out of order or outside the film: %s' % c['text'][:40])
            break
        last = c['end']
    fillers = set(settings['fillers'])
    left = [c['text'] for c in cues if any(captions_word(t) in fillers for t in c['text'].split())]
    if left:
        notes.append('%d caption(s) still contain a filler word you chose to keep.' % len(left))
    checks = export_dir / 'checks'
    checks.mkdir(exist_ok=True)
    stills = []
    points = [0.5] + [j + 0.15 for j in edit_map['joins'][:3]]
    if cues:
        points.append((cues[len(cues) // 2]['start'] + cues[len(cues) // 2]['end']) / 2)
    for n, t in enumerate(points, 1):
        if t < duration:
            still = checks / ('check_%02d_%06.2fs.png' % (n, t))
            run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % t, '-i', final, '-frames:v', '1', still])
            stills.append(still.name)
    result = {'ok': not problems, 'duration': round(duration, 3), 'expected': edit_map['expected_duration'],
              'joins': len(edit_map['joins']), 'captions': len(cues), 'problems': problems, 'notes': notes,
              'stills': stills}
    write(export_dir / 'verify.json', result)
    return result


def captions_word(token):
    return ''.join(ch for ch in token.lower() if ch.isalnum() or ch == "'")
