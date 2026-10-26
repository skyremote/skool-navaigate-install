"""tools-voice: build YOUR writing voice from your own words, check drafts against it, and record your corrections."""
import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__, voice

CLONE = 'git clone https://github.com/skyremote/voice-skill-builder ~/.claude/skills/voice-skill-builder'

SAMPLE_TRANSCRIPT = """Sam: So the way I'd do it is we pick one client and we fix the booking page first, and then we see what happens to the calls.
Sam: Right, and honestly it's a one-afternoon job, and there's nothing clever in it, we just move the form above the photos.
Client: What about the price list?
Sam: Look, we leave the prices alone for now, because Northwind sold 40 cakes last week without changing a thing.
Sam: Okay, so next step, I'll send you the layout on Friday and you tell me what's wrong with it.
"""
SAMPLE_GOOD = ("So the way we'd do it is we fix the booking page first, and it's a one-afternoon job, "
               "and there's nothing clever in it, because Northwind sold 40 cakes last week without a new price list.\n")
SAMPLE_BAD = ("Unlock your bakery's potential. Seamless booking. Zero friction. Real growth. "
              "We leverage a robust, powerful and practical process to elevate your brand.\n")


def doctor(_args):
    print('tools-voice ' + __version__)
    builder = voice.find_builder()
    if builder:
        print('voice-skill-builder: found at ' + str(builder))
        return 0
    print('voice-skill-builder: not installed. It is the public tool that pulls evidence from your own transcripts.')
    print('Install it once: ' + CLONE)
    print('Codex or Cursor: clone it into ~/.agents/skills/voice-skill-builder instead.')
    return 2


def new(args):
    target = voice.scaffold(args.name, args.folder)
    print('Made your voice skill: ' + str(target))
    print('Next: tools-voice evidence <your transcripts folder> --speaker "%s" --out <private folder>/VOICE_EVIDENCE.md' % args.name)
    return 0


def evidence(args):
    builder = voice.find_builder()
    if not builder:
        print('voice-skill-builder is not installed. Install it once: ' + CLONE)
        return 2
    command = [sys.executable, str(builder / 'scripts/extract_voice_evidence.py'), *args.inputs, '--out', args.out]
    if args.speaker:
        command += ['--speaker', args.speaker]
    return subprocess.run(command).returncode


def check(args):
    profile = Path(args.profile).expanduser().read_text() if args.profile else ''
    problems = voice.check(Path(args.draft).expanduser().read_text(), profile)
    if problems:
        print('FAIL: %d line(s) to fix' % len(problems))
        for p in problems:
            print('- ' + p)
        return 1
    print('PASS: no banned words, no fragment chains, no dash or adjective stacks. Now read it aloud.')
    return 0


def calibrate(args):
    voice.calibrate(args.profile, args.before, args.after, args.lesson)
    print('Added to the calibration log in ' + args.profile + '. It now overrules older rules where they disagree.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'sam-call_transcript_v1.txt').write_text(SAMPLE_TRANSCRIPT)
    (folder / 'draft-good_v1.md').write_text(SAMPLE_GOOD)
    (folder / 'draft-bad_v1.md').write_text(SAMPLE_BAD)
    print('Practice files for Sam, a fictional designer at Acme Studio, in ' + str(folder) + ':')
    print('  sam-call_transcript_v1.txt, draft-good_v1.md, draft-bad_v1.md')
    print('Next: tools-voice check ' + str(folder / 'draft-bad_v1.md'))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-voice', description=__doc__)
    p.add_argument('--version', action='version', version='tools-voice ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='is voice-skill-builder installed?').set_defaults(run=doctor)
    s = sub.add_parser('new', help='make <name>-voice/ with SKILL.md, PROFILE.md and EXAMPLES.md')
    s.add_argument('name', help='your first name')
    s.add_argument('--folder', default='~/.claude/skills', help='your skills folder (Codex/Cursor: ~/.agents/skills)')
    s.set_defaults(run=new)
    s = sub.add_parser('evidence', help='run voice-skill-builder on your own transcripts')
    s.add_argument('inputs', nargs='+')
    s.add_argument('--speaker')
    s.add_argument('--out', required=True, help='a PRIVATE file, outside any shared or public folder')
    s.set_defaults(run=evidence)
    s = sub.add_parser('check', help='check a draft against the house rules and your profile')
    s.add_argument('draft')
    s.add_argument('--profile')
    s.set_defaults(run=check)
    s = sub.add_parser('calibrate', help='record one of your own corrections')
    s.add_argument('--profile', required=True)
    s.add_argument('--before', required=True)
    s.add_argument('--after', required=True)
    s.add_argument('--lesson', required=True)
    s.set_defaults(run=calibrate)
    s = sub.add_parser('sample', help='fictional practice files (Sam at Acme Studio)')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except voice.VoiceError as error:
        print(str(error), file=sys.stderr)
        return 1
    except FileNotFoundError as error:
        print('File not found: ' + str(error.filename), file=sys.stderr)
        return 1
