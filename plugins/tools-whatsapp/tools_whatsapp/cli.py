"""tools-whatsapp: your WhatsApp chats archived on your own Mac with the public whatscribe, then searched and summarised."""
import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

from . import __version__, chat

INSTALL = 'git clone https://github.com/GoodLadTom/whatscribe ~/whatscribe && cd ~/whatscribe && ./install.sh && whatscribe setup'


def doctor(_args):
    print('tools-whatsapp ' + __version__)
    code = 0
    mac = platform.system() == 'Darwin'
    print('macOS: ' + ('yes' if mac else 'no. whatscribe reads the Mac WhatsApp app; on Windows see GoodLadTom/whatscribe-windows'))
    app = any(Path(p).exists() for p in ('/Applications/WhatsApp.app', str(Path.home() / 'Applications/WhatsApp.app')))
    print('WhatsApp desktop app: ' + ('found' if app else 'not found. Install it from whatsapp.com/download and sign in'))
    cli = shutil.which('whatscribe')
    print('whatscribe: ' + ('installed' if cli else 'not installed. ' + INSTALL))
    if not (mac and app and cli):
        code = 2
    if cli:
        print('Next: whatscribe doctor (it checks Full Disk Access and the chat it syncs)')
    return code


def show(rows, as_json):
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    for row in rows:
        print('%s  %-18s %-5s %s' % (row['at'][:16].replace('T', ' '), row['who'][:18], row['type'][:5], row['text']))
    if not rows:
        print('No messages matched.')
    return 0 if rows else 1


def do_find(args):
    rows = chat.find(chat.load(args.transcript), args.since or '', args.until or '', args.contains or '', args.type or '', args.who or '')
    return show(rows, args.json)


def do_extract(args):
    rows = chat.find(chat.load(args.transcript), args.since or '', args.until or '')
    found = chat.extract(rows)
    if args.json:
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return 0
    if not found:
        print('No dates, times or amounts found in that range.')
        return 1
    for item in found:
        print('%-5s %-14s %s  %s%s' % (item['kind'], item['value'], item['at'][:10], item['who'],
                                       ' (voice note)' if item['type'] == 'voice' else ''))
    print('Each line comes from one message. Check the message before you rely on a figure.')
    return 0


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'transcript.jsonl'
    path.write_text(''.join(json.dumps(r) + '\n' for r in chat.SAMPLE))
    print('A practice chat with a fictional builder, in whatscribe\'s format: %s' % path)
    print('Next: tools-whatsapp extract %s' % path)
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-whatsapp', description=__doc__)
    p.add_argument('--version', action='version', version='tools-whatsapp ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='macOS, the WhatsApp app and whatscribe').set_defaults(run=doctor)
    s = sub.add_parser('find', help="search whatscribe's transcript.jsonl")
    s.add_argument('transcript')
    s.add_argument('--since', help='YYYY-MM-DD')
    s.add_argument('--until', help='YYYY-MM-DD')
    s.add_argument('--contains')
    s.add_argument('--type', choices=['text', 'voice', 'image', 'video', 'document'])
    s.add_argument('--who')
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=do_find)
    s = sub.add_parser('extract', help='every date, time and amount mentioned, with its message')
    s.add_argument('transcript')
    s.add_argument('--since')
    s.add_argument('--until')
    s.add_argument('--json', action='store_true')
    s.set_defaults(run=do_extract)
    s = sub.add_parser('sample', help='a practice chat in whatscribe\'s format')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except chat.ChatError as error:
        print(str(error), file=sys.stderr)
        return 1
