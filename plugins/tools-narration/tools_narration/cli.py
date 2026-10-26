"""tools-narration: narrate slides and lessons in YOUR voice on YOUR ElevenLabs account, as one consistent take."""
import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

from . import __version__, config, eleven, narration

MODEL = 'eleven_multilingual_v2'
SETTINGS = {'stability': 0.5, 'similarity_boost': 0.8, 'style': 0.0, 'use_speaker_boost': True, 'speed': 1.0}
SAMPLE_SLIDES = [
    {'title': 'Welcome', 'notes': ['Welcome to Acme Studio. In the next two minutes we will look at the new booking page for Northwind Bakery.']},
    {'title': 'The problem', 'notes': ['Northwind takes about forty cake orders a week by phone, and half of them arrive while the team is baking.']},
    {'title': 'The fix', 'notes': ['So the first version takes online orders for celebration cakes only, and the prices stay the same as the shop.']},
]


def doctor(_args):
    print('tools-narration ' + __version__)
    code = 0
    print('ffmpeg and ffprobe: ' + ('found' if narration.ffmpeg_ok() else 'missing. Install with: brew install ffmpeg (Mac) or your package manager'))
    if not narration.ffmpeg_ok():
        code = 1
    for name, option, label in (('ELEVENLABS_API_KEY', 'elevenlabs_api_key', 'ElevenLabs API key'),
                                ('ELEVENLABS_VOICE_ID', 'voice_id', 'Your voice id')):
        where = config.where(name, option)
        print(label + ': ' + ('found in your ' + where + (' (not shown)' if 'KEY' in name else '') if where else 'not set'))
        if not where:
            code = code or 2
    if code == 2:
        print('You can still practise cutting a take: tools-narration sample ~/Narration-practice')
    return code


def show_account(_args):
    a = eleven.account(eleven.api_key())
    print('Plan: %s. Characters used this period: %s of %s.' % (a['tier'], a['used'], a['limit']))
    return 0


def show_voices(args):
    for v in eleven.voices(eleven.api_key(), args.search or ''):
        print('%-24s %-12s %s' % (v['name'][:24], v['category'], v['id']))
    return 0


def do_clone(args):
    if not args.consent:
        print('Clone only your OWN voice, or a voice whose owner gave you written consent. Add --consent to confirm.')
        return 1
    files = [Path(f).expanduser() for f in args.recordings]
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        print('Recording not found: ' + ', '.join(missing))
        return 1
    new_id = eleven.clone(eleven.api_key(), args.name, files)
    print('Made your voice "%s": %s' % (args.name, new_id))
    print('Save it as your voice id (plugin settings, or export ELEVENLABS_VOICE_ID=%s).' % new_id)
    return 0


def plan(args):
    slides = narration.load_slides(args.slides)
    script, spans = narration.join(slides)
    out = Path(args.out).expanduser()
    out.write_text(script + '\n')
    print('%d slides, %d characters, one take. Script saved to %s' % (len(slides), len(script), out))
    print('Read it once before you pay for it: names, numbers and anything you would say differently.')
    return 0


def save_take(result, folder):
    audio = base64.b64decode(result.get('audio_base64') or '')
    if not audio:
        raise eleven.ElevenError('ElevenLabs returned no audio.')
    take = folder / 'take_v1.mp3'
    take.write_bytes(audio)
    (folder / 'alignment_v1.json').write_text(json.dumps(result.get('alignment') or {}, indent=1))
    return take


def split(slides_path, take, alignment, folder):
    if not narration.ffmpeg_ok():
        raise narration.NarrationError('ffmpeg is missing. Install it first (brew install ffmpeg on a Mac).')
    slides = narration.load_slides(slides_path)
    _, spans = narration.join(slides)
    cuts = narration.boundaries(json.loads(Path(alignment).read_text()), spans, narration.duration_of(take))
    tracks = narration.master_and_split(take, cuts, folder)
    (folder / 'manifest_v1.json').write_text(json.dumps({'take': Path(take).name, 'requests': 1, 'tracks': tracks}, indent=2))
    for t in tracks:
        print('slide %02d  %5.1f s  %s' % (t['slide'], t['seconds'], t['file']))
    print('Listen to the first, a middle and the last clip before you use them.')
    return 0


def narrate(args):
    slides = narration.load_slides(args.slides)
    script, _ = narration.join(slides)
    folder = Path(args.out).expanduser()
    if folder.exists():
        print('Not overwriting ' + str(folder) + '. Use a new _v2 folder.')
        return 1
    if not args.yes:
        print('This is one paid request of %d characters on your ElevenLabs plan. Add --yes to go ahead.' % len(script))
        return 1
    if not narration.ffmpeg_ok():
        raise narration.NarrationError('ffmpeg is missing. Install it before you pay for a take.')
    voice = eleven.voice_id(args.voice_id)
    result = eleven.speech_with_timings(eleven.api_key(), voice, script, args.model, SETTINGS)
    folder.mkdir(parents=True)
    (folder / 'script_v1.txt').write_text(script + '\n')
    take = save_take(result, folder)
    print('One take saved: ' + str(take))
    return split(args.slides, take, folder / 'alignment_v1.json', folder)


def say(args):
    out = Path(args.out).expanduser()
    if out.exists():
        print('Not overwriting ' + str(out) + '.')
        return 1
    result = eleven.speech_with_timings(eleven.api_key(), eleven.voice_id(args.voice_id), args.text, args.model, SETTINGS)
    out.write_bytes(base64.b64decode(result.get('audio_base64') or ''))
    print('Saved ' + str(out))
    return 0


def do_split(args):
    folder = Path(args.out).expanduser()
    if folder.exists():
        print('Not overwriting ' + str(folder) + '. Use a new _v2 folder.')
        return 1
    folder.mkdir(parents=True)
    return split(args.slides, args.take, args.alignment, folder)


def sample(args):
    """Practice files: three fictional slides, a tone 'take' and a matching alignment. No account needed."""
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'slides.json').write_text(json.dumps(SAMPLE_SLIDES, indent=2))
    script, spans = narration.join([s['notes'][0] for s in SAMPLE_SLIDES])
    per_char = 0.06
    starts = [round(i * per_char, 3) for i in range(len(script))]
    ends = [round(s + per_char * 0.9, 3) for s in starts]
    for (_, end), (start, _) in zip(spans, spans[1:]):
        shift = 0.8  # a real pause between slides
        starts[start:] = [s + shift for s in starts[start:]]
        ends[start:] = [e + shift for e in ends[start:]]
    (folder / 'alignment.json').write_text(json.dumps({'characters': list(script), 'character_start_times_seconds': starts,
                                                       'character_end_times_seconds': ends}))
    total = ends[-1] + 0.5
    if narration.ffmpeg_ok():
        narration.run(['ffmpeg', '-y', '-hide_banner', '-f', 'lavfi', '-i', 'sine=frequency=220:duration=%.2f' % total,
                       '-c:a', 'libmp3lame', '-b:a', '128k', folder / 'take.mp3'])
    print('Practice files in %s: slides.json, alignment.json%s.' % (folder, ', take.mp3 (a tone, not a voice)' if narration.ffmpeg_ok() else ''))
    print('Next: tools-narration split --slides %s --take %s --alignment %s --out %s' % (
        folder / 'slides.json', folder / 'take.mp3', folder / 'alignment.json', folder / 'clips_v1'))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-narration', description=__doc__)
    p.add_argument('--version', action='version', version='tools-narration ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='ffmpeg, your key and your voice id').set_defaults(run=doctor)
    sub.add_parser('account', help='your plan and characters used').set_defaults(run=show_account)
    s = sub.add_parser('voices', help='the voices on your account')
    s.add_argument('--search')
    s.set_defaults(run=show_voices)
    s = sub.add_parser('clone', help='an instant clone of YOUR voice from your own recordings')
    s.add_argument('name')
    s.add_argument('recordings', nargs='+')
    s.add_argument('--consent', action='store_true', help='confirms it is your own voice, or you have written consent')
    s.set_defaults(run=do_clone)
    s = sub.add_parser('plan', help='join slide notes into one script (free, local)')
    s.add_argument('slides')
    s.add_argument('--out', required=True)
    s.set_defaults(run=plan)
    s = sub.add_parser('narrate', help='one paid take for all slides, then cut per slide')
    s.add_argument('slides')
    s.add_argument('--out', required=True)
    s.add_argument('--voice-id')
    s.add_argument('--model', default=MODEL)
    s.add_argument('--yes', action='store_true')
    s.set_defaults(run=narrate)
    s = sub.add_parser('say', help='one short line to an MP3')
    s.add_argument('text')
    s.add_argument('-o', '--out', required=True)
    s.add_argument('--voice-id')
    s.add_argument('--model', default=MODEL)
    s.set_defaults(run=say)
    s = sub.add_parser('split', help='cut an existing take at its aligned slide boundaries (free, local)')
    s.add_argument('--slides', required=True)
    s.add_argument('--take', required=True)
    s.add_argument('--alignment', required=True)
    s.add_argument('--out', required=True)
    s.set_defaults(run=do_split)
    s = sub.add_parser('sample', help='practice files, no account needed')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except (eleven.ElevenError, config.KeyError_) as error:
        print(str(error), file=sys.stderr)
        return 2
    except narration.NarrationError as error:
        print(str(error), file=sys.stderr)
        return 1
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
