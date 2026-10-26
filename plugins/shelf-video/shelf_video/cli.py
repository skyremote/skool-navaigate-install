"""shelf-video command line. Every step writes a new versioned file and never touches the original."""
import argparse
import json
import sys
from pathlib import Path

from . import plan as planner
from . import render, review, sample, settings, transcribe
from .core import VERSION, ShelfError, init_project, latest, lock, next_version, open_project, read, write


def _ids(value):
    return [int(x) for x in value.split(',') if x.strip()] if value else []


def cmd_sample(a):
    print('Sample recording: ' + str(sample.make(a.out)))


def cmd_init(a):
    root, data = init_project(a.recording, a.project)
    m = data['media']
    print('Project: ' + str(root))
    print('Recording: %dx%d, %s fps, %.1f s, %d audio channel(s)' % (
        m['width'], m['height'], m['fps'], m['duration'], m['audio_channels']))
    print('Next: shelf-video transcribe --project "%s"' % root)


def cmd_transcribe(a):
    root, project = open_project(a.project)
    cfg = settings.load()
    with lock(root):
        file, data, reused = transcribe.transcribe(root, project, a.engine, a.model or cfg['whisper_model'],
                                                   cfg['language'], a.model_path, a.import_json, a.force)
    fillers = set(cfg['fillers'])
    found = sum(1 for w in data['words'] if w['word'] in fillers)
    print(('Reused ' if reused else 'Wrote ') + str(file))
    print('%d words, %d filler words heard (engine: %s, model: %s)' % (
        len(data['words']), found, data['engine'], data['model']))
    print('Next: shelf-video plan --project "%s"' % root)


def _words(root):
    file = latest(Path(root) / 'transcript', 'words', '.json')
    if not file:
        raise ShelfError('No transcript yet. Run: shelf-video transcribe --project <folder>')
    return file, read(file)


def cmd_plan(a):
    root, project = open_project(a.project)
    cfg = settings.load()
    if a.max_pause is not None:
        cfg['max_pause'] = a.max_pause
    words_file, words = _words(root)
    cuts = planner.propose(words['words'], project['media'], cfg)
    folder = root / 'plans'
    target = next_version(folder, 'plan', '.json')
    write(target, {'words': words_file.name, 'media': project['media'], 'settings': cfg, 'cuts': cuts})
    md = planner.markdown(cuts, project['media'], words_file.name)
    target.with_suffix('.md').write_text(md)
    s = planner.summary(cuts, project['media']['duration'])
    text = '%d proposals, %d selected: %s. Removes %.1f s, new length %.1f s.' % (
        s['proposals'], s['selected'], ', '.join('%s %d' % kv for kv in sorted(s['by_kind'].items())) or 'none',
        s['seconds_removed'], s['new_duration'])
    page = target.with_name(target.stem.replace('plan_', 'review_') + '.html')
    page.write_text(review.page(cuts, project['source'], text))
    print(md if a.show else text)
    print('Plan: ' + str(target))
    print('Review page: ' + str(page))
    print('Next: the member reads the plan, then approves it: shelf-video approve --project "%s" --yes' % root)


def cmd_approve(a):
    root, _ = open_project(a.project)
    plan_file = Path(a.plan) if a.plan else latest(root / 'plans', 'plan', '.json')
    if not plan_file:
        raise ShelfError('No plan yet. Run: shelf-video plan --project <folder>')
    if not plan_file.is_absolute():
        plan_file = root / 'plans' / plan_file
    target, record = render.approve(root, plan_file, _ids(a.drop), _ids(a.add), a.remove, a.yes, a.note)
    s = record['summary']
    print('Approved %s: %d removals, %.1f s out, new length %.1f s.' % (
        plan_file.name, s['selected'], s['seconds_removed'], s['new_duration']))
    print('Recorded: ' + str(target))
    print('Next: shelf-video render --project "%s"' % root)


def cmd_render(a):
    root, project = open_project(a.project)
    cfg = settings.load()
    _, words = _words(root)
    with lock(root):
        out, receipt = render.render(root, project, words, cfg, burn=not a.no_burn)
    print('Rendered %s in %.1f s (%d captions, burnt in: %s)' % (
        out / receipt['output'], receipt['seconds'], receipt['cue_count'], 'yes' if receipt['burnt_in'] else 'no'))
    print('Captions file: ' + str(out / 'captions.srt'))
    print('Next: shelf-video verify --project "%s"' % root)


def cmd_verify(a):
    root, _ = open_project(a.project)
    export = Path(a.export) if a.export else latest(root / 'exports', 'edit', '')
    if not export or not (export / 'receipt.json').exists():
        raise ShelfError('No finished export to check. Run: shelf-video render --project <folder>')
    result = render.verify(export, settings.load())
    print('PASS' if result['ok'] else 'FAIL')
    print('Duration %.2f s (expected %.2f s), %d joins, %d captions' % (
        result['duration'], result['expected'], result['joins'], result['captions']))
    for p in result['problems']:
        print('Problem: ' + p)
    for n in result['notes']:
        print('Note: ' + n)
    print('Look at these stills before you publish: ' + str(export / 'checks'))
    return 0 if result['ok'] else 1


def cmd_settings(a):
    if a.action == 'set':
        if not a.pair or '=' not in a.pair:
            raise ShelfError('Use: shelf-video settings set caption.colour=#FFD400')
        key, value = a.pair.split('=', 1)
        settings.set_value(key.strip(), value.strip())
    elif a.action == 'init' and not settings.path().exists():
        settings.save(settings.load())
    print(json.dumps(settings.load(), indent=2))
    print('Settings file: ' + str(settings.path()) + ('' if settings.path().exists() else ' (not created; defaults shown)'))


def parser():
    p = argparse.ArgumentParser(prog='shelf-video', description='Edit a talking-head recording on your own machine.')
    p.add_argument('--version', action='version', version='shelf-video ' + VERSION)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('sample', help='Make a practice recording with a fictional presenter')
    s.add_argument('--out', default='shelf-video-sample/sam_acme_v1.mp4')
    s.set_defaults(func=cmd_sample)
    s = sub.add_parser('init', help='Start a project for one recording')
    s.add_argument('recording')
    s.add_argument('--project', help='Folder for the edit (default: beside the recording)')
    s.set_defaults(func=cmd_init)
    s = sub.add_parser('transcribe', help='Word-timed transcript with Whisper, on this machine')
    s.add_argument('--project', required=True)
    s.add_argument('--engine', choices=['whisper', 'whisper-cpp'], default='whisper')
    s.add_argument('--model', help='Whisper model name, such as small.en or medium')
    s.add_argument('--model-path', help='whisper.cpp ggml model file')
    s.add_argument('--import-json', help='Use a Whisper JSON you already have')
    s.add_argument('--force', action='store_true', help='Transcribe again even if a transcript exists')
    s.set_defaults(func=cmd_transcribe)
    s = sub.add_parser('plan', help='Propose removals: fillers, long pauses, stutters')
    s.add_argument('--project', required=True)
    s.add_argument('--max-pause', type=float, help='Tighten pauses longer than this many seconds')
    s.add_argument('--show', action='store_true', help='Print the full plan table')
    s.set_defaults(func=cmd_plan)
    s = sub.add_parser('approve', help="Record the member's approval of a plan")
    s.add_argument('--project', required=True)
    s.add_argument('--plan', help='Plan file (default: newest)')
    s.add_argument('--drop', help='Proposal numbers to keep in the film, such as 3,7')
    s.add_argument('--add', help='Proposed-but-unselected numbers to cut as well')
    s.add_argument('--remove', action='append', default=[], help='Extra range to cut, START:END in seconds')
    s.add_argument('--note', default='')
    s.add_argument('--yes', action='store_true', help='The member has read the plan and approves it')
    s.set_defaults(func=cmd_approve)
    s = sub.add_parser('render', help='Cut, caption and export the approved edit')
    s.add_argument('--project', required=True)
    s.add_argument('--no-burn', action='store_true', help='Captions as a separate SRT only')
    s.set_defaults(func=cmd_render)
    s = sub.add_parser('verify', help='Check the finished file')
    s.add_argument('--project', required=True)
    s.add_argument('--export', help='Export folder (default: newest)')
    s.set_defaults(func=cmd_verify)
    s = sub.add_parser('settings', help='Show or change your settings')
    s.add_argument('action', nargs='?', choices=['show', 'init', 'set'], default='show')
    s.add_argument('pair', nargs='?')
    s.set_defaults(func=cmd_settings)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        code = args.func(args)
    except ShelfError as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 1
    return code or 0
