"""Shared helpers: commands, hashes, media probe and the project folder.

The digest, lock and frame-snapping ideas come from cutroom-starter
(MIT, Copyright (c) 2026 NavAIgate), rewritten for this pack.
"""
import contextlib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

VERSION = '2.0.0'


class ShelfError(ValueError):
    """A problem the member can fix. The CLI prints it without a traceback."""


def need(tool, hint):
    if not shutil.which(tool):
        raise ShelfError(tool + ' is not on PATH. ' + hint)


def run(args, capture=True):
    result = subprocess.run([str(x) for x in args], capture_output=capture, text=True)
    if result.returncode:
        tail = (result.stderr or result.stdout or '')[-2500:]
        raise ShelfError('Command failed: ' + Path(str(args[0])).name + '\n' + tail)
    return result.stdout if capture else ''


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def signature(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n')


def next_version(folder, stem, suffix):
    """Return folder/stem_vN.suffix for the first unused N."""
    folder = Path(folder)
    n = 1
    while (folder / (stem + '_v' + str(n) + suffix)).exists():
        n += 1
    return folder / (stem + '_v' + str(n) + suffix)


def latest(folder, stem, suffix):
    folder = Path(folder)
    found = []
    for item in folder.glob(stem + '_v*' + suffix):
        match = re.fullmatch(re.escape(stem) + r'_v(\d+)' + re.escape(suffix), item.name)
        if match:
            found.append((int(match.group(1)), item))
    return max(found)[1] if found else None


@contextlib.contextmanager
def lock(root):
    flag = Path(root) / '.busy'
    try:
        fd = os.open(str(flag), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ShelfError('Another shelf-video step is running in this project. If it crashed, delete '
                         + str(flag) + ' after checking no ffmpeg or whisper process is still running.')
    os.close(fd)
    try:
        yield
    finally:
        flag.unlink()


def probe(source):
    need('ffprobe', 'Install FFmpeg: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux).')
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', source]))
    videos = [s for s in info.get('streams', []) if s.get('codec_type') == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    audios = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
    if len(videos) != 1:
        raise ShelfError('Use a recording with exactly one video stream.')
    if not audios:
        raise ShelfError('This recording has no audio, so there is nothing to transcribe.')
    video = videos[0]
    fps = Fraction(video.get('avg_frame_rate') or '0/1')
    if not 1 <= fps <= 120:
        raise ShelfError('Unsupported frame rate. Export a constant-frame-rate copy first.')
    width, height = int(video['width']), int(video['height'])
    if width % 2 or height % 2:
        raise ShelfError('Width and height must be even numbers. Export a resized copy first.')
    rotation = 0
    for side in video.get('side_data_list', []) or []:
        if 'rotation' in side:
            rotation = int(side['rotation'])
    if rotation or video.get('tags', {}).get('rotate'):
        raise ShelfError('This file carries rotation metadata (common on phones). Export an upright copy first.')
    duration = float(info.get('format', {}).get('duration') or video.get('duration') or 0)
    if duration <= 0:
        raise ShelfError('Could not read the duration.')
    return {
        'width': width,
        'height': height,
        'fps': str(fps.numerator) + '/' + str(fps.denominator),
        'duration': round(duration, 3),
        'audio_channels': int(audios[0].get('channels') or 2),
        'audio_rate': int(audios[0].get('sample_rate') or 48000),
        'video_codec': video.get('codec_name'),
        'audio_codec': audios[0].get('codec_name'),
    }


def fps_value(meta):
    return float(Fraction(meta['fps']))


def snap_in(start, end, fps):
    """Snap a removal inwards to whole frames, so no kept frame is lost."""
    first = math.ceil(round(start * fps, 6)) / fps
    last = math.floor(round(end * fps, 6)) / fps
    return round(first, 4), round(last, 4)


def init_project(source, project=None):
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ShelfError('Recording not found: ' + str(source))
    meta = probe(source)
    if project:
        root = Path(project).expanduser().resolve()
    else:
        n = 1
        while (source.parent / (source.stem + '_EDIT_v' + str(n))).exists():
            n += 1
        root = source.parent / (source.stem + '_EDIT_v' + str(n))
    if (root / 'project.json').exists():
        old = read(root / 'project.json')
        if old.get('source_sha256') != digest(source):
            raise ShelfError('This project belongs to a different recording. Choose a new project folder.')
        return root, old
    root.mkdir(parents=True, exist_ok=True)
    data = {'tool': 'shelf-video', 'version': VERSION, 'source': str(source),
            'source_sha256': digest(source), 'media': meta}
    write(root / 'project.json', data)
    return root, data


def open_project(project):
    root = Path(project).expanduser().resolve()
    file = root / 'project.json'
    if not file.exists():
        raise ShelfError('No project.json in ' + str(root) + '. Run: shelf-video init <recording>')
    data = read(file)
    source = Path(data['source'])
    if not source.exists():
        raise ShelfError('The original recording has moved: ' + str(source) + '. Put it back or start a new project.')
    return root, data
