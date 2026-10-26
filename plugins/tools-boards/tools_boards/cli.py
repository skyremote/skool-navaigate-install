"""tools-boards: plan an editable BluPlai board as native shapes, validate it, then build it through BluPlai's MCP."""
import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__, validate_scene

ASSETS = Path(__file__).resolve().parents[1] / 'skills/tools-boards/assets'


def runway(title, subtitle, columns, takeaway):
    """A left-to-right workshop runway: one header per column, its cards under it, one arrow between headers."""
    nodes = [{'id': 'title', 'label': title, 'x': 0, 'y': 0, 'width': 1520, 'height': 80, 'size': 'xl', 'color': 'black', 'fill': 'none'},
             {'id': 'subtitle', 'label': subtitle, 'x': 0, 'y': 100, 'width': 1520, 'height': 60, 'size': 'm', 'color': 'grey', 'fill': 'none'}]
    edges = []
    colours = ['blue', 'light-blue', 'violet', 'green', 'orange']
    for i, (head, cards) in enumerate(columns):
        x = i * 320
        hid = 'col%d' % i
        nodes.append({'id': hid, 'label': head.upper(), 'x': x, 'y': 200, 'width': 280, 'height': 80, 'size': 'l',
                      'color': colours[i % len(colours)], 'fill': 'semi'})
        for j, card in enumerate(cards):
            nodes.append({'id': '%s-%d' % (hid, j), 'label': card, 'x': x, 'y': 320 + j * 120, 'width': 280, 'height': 96,
                          'size': 's', 'color': 'grey', 'fill': 'none'})
        if i:
            edges.append({'from_id': 'col%d' % (i - 1), 'to_id': hid, 'label': '', 'bend': 0})
    bottom = 320 + max(len(c) for _, c in columns) * 120 + 40
    nodes.append({'id': 'takeaway', 'label': takeaway, 'x': 0, 'y': max(bottom, 720), 'width': 1520, 'height': 80,
                  'size': 'l', 'color': 'green', 'fill': 'none'})
    return {'nodes': nodes, 'edges': edges}


SAMPLE = runway('NORTHWIND BAKERY: BOOKING PAGE KICK-OFF', 'Acme Studio workshop (fictional). Read left to right, then write on the board.', [
    ('Question', ['What should version one\nof the booking page do?']),
    ('Evidence', ['40 cake orders a week by phone', 'Half arrive while baking']),
    ('Synthesis', ['The phone is where\norders get lost']),
    ('Decision', ['Celebration cakes only, online', 'Prices stay as the shop']),
    ('Owner', ['Layout: Acme Studio, Friday', 'Photos: Northwind', 'Deposit: open question']),
], 'WRITE YOUR QUESTIONS ON THE BOARD BEFORE FRIDAY')


def validate(args):
    argv = [args.scene] + (['--emit-mcp-payload', args.payload] if args.payload else []) + (['--strict'] if args.strict else [])
    return validate_scene.main(argv)


def sample(args):
    folder = Path(args.folder).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'northwind-workshop_scene_v1.json').write_text(json.dumps(SAMPLE, indent=2))
    shutil.copy(ASSETS / 'release-workflow.example.json', folder / 'release-workflow_scene_example.json')
    print('Two practice scenes in %s:' % folder)
    print('  northwind-workshop_scene_v1.json  (a workshop runway, fictional)')
    print('  release-workflow_scene_example.json  (a teaching workflow with zones)')
    print('Next: tools-boards validate %s --payload %s' % (folder / 'northwind-workshop_scene_v1.json', folder / 'northwind-workshop.mcp.json'))
    return 0


def parser():
    p = argparse.ArgumentParser(prog='tools-boards', description=__doc__)
    p.add_argument('--version', action='version', version='tools-boards ' + __version__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('validate', help='check a scene and write the MCP payload')
    s.add_argument('scene')
    s.add_argument('--payload', help='where to write the nodes and edges to send to BluPlai')
    s.add_argument('--strict', action='store_true', help='fail on warnings too')
    s.set_defaults(run=validate)
    s = sub.add_parser('sample', help='two practice scenes')
    s.add_argument('folder')
    s.set_defaults(run=sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    return args.run(args)
