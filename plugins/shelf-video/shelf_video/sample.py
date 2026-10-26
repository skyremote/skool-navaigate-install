"""Make a practice recording: a drawn, fictional presenter ("Sam from Acme Studio") who says
um and uh and pauses too long. Speech comes from the computer's own voice (macOS say,
or espeak-ng on Linux), so there is no licence question and no real person on screen.
"""
import math
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

from .captions import find_font
from .core import ShelfError, need, run

SCRIPT = ("Hi, I'm Sam from Acme Studio. Um, today I want to show you, uh, how we plan a week of client work. "
          "[[slnc 1600]] So, the first thing is, um, we write every job on one list. "
          "Uh, then we pick the three jobs that matter most. [[slnc 1300]] "
          "Erm, the rest can wait. And, uh, at the end of each day we tick off what is done, "
          "and we move the rest to tomorrow. [[slnc 1500]] That's the whole system. Um, thanks for watching.")

W, H, FPS = 1280, 720, 25


def speak(text, wav):
    if shutil.which('say'):
        aiff = Path(str(wav) + '.aiff')
        voice = []
        listing = subprocess.run(['say', '-v', '?'], capture_output=True, text=True).stdout
        for name in ('Samantha', 'Karen', 'Moira', 'Alex'):
            if listing.startswith(name + ' ') or ('\n' + name + ' ') in listing:
                voice = ['-v', name]
                break
        run(['say'] + voice + ['-r', '165', '-o', aiff, text])
        run(['ffmpeg', '-v', 'error', '-y', '-i', aiff, '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', wav])
        aiff.unlink()
    elif shutil.which('espeak-ng'):
        plain = text.replace('[[slnc 1600]]', '...... ').replace('[[slnc 1300]]', '..... ').replace('[[slnc 1500]]', '..... ')
        run(['espeak-ng', '-v', 'en-gb', '-s', '150', '-w', wav, plain])
    else:
        raise ShelfError('No speech engine found. On macOS the say command is built in; on Linux run: '
                         'sudo apt install espeak-ng')


def envelope(wav):
    with wave.open(str(wav)) as w:
        rate, n, width = w.getframerate(), w.getnframes(), w.getsampwidth()
        raw = w.readframes(n)
    if width != 2:
        raise ShelfError('Unexpected sample width in the generated speech.')
    samples = struct.unpack('<%dh' % (len(raw) // 2), raw)
    step = rate // FPS
    levels = []
    for i in range(0, len(samples), step):
        chunk = samples[i:i + step]
        levels.append(math.sqrt(sum(x * x for x in chunk) / max(1, len(chunk))) / 32768.0)
    peak = max(levels) or 1.0
    return [min(1.0, v / peak * 1.6) for v in levels]


def frame(draw, t, level, font=None):
    draw.rectangle([0, 0, W, H], fill=(236, 232, 222))
    draw.rectangle([0, H - 180, W, H], fill=(214, 207, 192))
    draw.rounded_rectangle([60, 50, 470, 110], radius=12, fill=(255, 255, 255))
    draw.text((80, 64), 'SAMPLE: fictional presenter, Acme Studio', fill=(90, 70, 40), font=font)
    cx, cy = W // 2, 330
    draw.ellipse([cx - 230, cy + 150, cx + 230, cy + 520], fill=(63, 101, 96))
    draw.ellipse([cx - 120, cy - 150, cx + 120, cy + 120], fill=(232, 190, 160))
    draw.pieslice([cx - 128, cy - 165, cx + 128, cy + 40], 180, 360, fill=(70, 52, 40))
    blink = (t % 4.0) < 0.12
    for ex in (cx - 48, cx + 48):
        if blink:
            draw.line([ex - 14, cy - 10, ex + 14, cy - 10], fill=(40, 30, 25), width=4)
        else:
            draw.ellipse([ex - 12, cy - 22, ex + 12, cy + 2], fill=(40, 30, 25))
    open_h = int(6 + 34 * level)
    draw.rounded_rectangle([cx - 36, cy + 50, cx + 36, cy + 50 + open_h], radius=10, fill=(120, 40, 45))


def make(out_path):
    need('ffmpeg', 'Install FFmpeg: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux).')
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ShelfError('The sample needs Pillow. Run: python3 -m pip install --user Pillow')
    out_path = Path(out_path).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='shelf-video-sample-') as tmp:
        wav = Path(tmp) / 'speech.wav'
        speak(SCRIPT, wav)
        levels = envelope(wav)
        frames = len(levels) + FPS
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                 '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-', '-i', str(wav),
                                 '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac',
                                 '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(out_path)],
                                stdin=subprocess.PIPE)
        path = find_font('')
        font = ImageFont.truetype(path, 22) if path else None
        image = Image.new('RGB', (W, H))
        draw = ImageDraw.Draw(image)
        for i in range(frames):
            level = levels[i] if i < len(levels) else 0.0
            frame(draw, i / FPS, level, font)
            proc.stdin.write(image.tobytes())
        proc.stdin.close()
        if proc.wait():
            raise ShelfError('FFmpeg could not encode the sample.')
    return out_path
