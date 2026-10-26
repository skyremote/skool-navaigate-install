#!/usr/bin/env python3
"""A stand-in for the bb CLI with the same JSON shapes, keeping state in $FAKE_BB_STATE.

Set FAKE_BB_KANBAN=1 to behave as if a kanban plugin is installed.
"""
import json
import os
import sys

STATE = os.environ['FAKE_BB_STATE']
KANBAN = os.environ.get('FAKE_BB_KANBAN') == '1'


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'projects': [], 'sections': [], 'threads': [], 'cards': [], 'calls': [], 'n': 0}


def save(s):
    json.dump(s, open(STATE, 'w'), indent=1)


def new_id(s, prefix):
    s['n'] += 1
    return '%s_%04d' % (prefix, s['n'])


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def out(obj):
    print(json.dumps(obj))


def main(argv):
    s = load()
    s['calls'].append(argv)
    a = [x for x in argv if x != '--json']
    if a[:1] == ['--version']:
        print('0.47.0')
    elif a[:1] == ['status']:
        out({'project': None, 'thread': None, 'dataDir': os.environ.get('HOME', '') + '/.bb'})
    elif a[:2] == ['provider', 'list']:
        out([{'id': 'claude-code', 'available': True}, {'id': 'codex', 'available': True}])
    elif a[:2] == ['project', 'list']:
        out(s['projects'])
    elif a[:2] == ['project', 'create']:
        p = {'id': new_id(s, 'proj'), 'kind': 'project', 'name': opt(a, '--name'),
             'sources': [{'id': new_id(s, 'src'), 'path': opt(a, '--root'), 'isDefault': True}]}
        s['projects'].append(p)
        out(p)
    elif a[:3] == ['thread', 'section', 'list']:
        out(s['sections'])
    elif a[:3] == ['thread', 'section', 'create']:
        sec = {'id': new_id(s, 'sec'), 'name': a[3]}
        s['sections'].append(sec)
        out(sec)
    elif a[:2] == ['thread', 'list']:
        proj = opt(a, '--project')
        out([t for t in s['threads'] if not proj or t['projectId'] == proj])
    elif a[:2] == ['thread', 'spawn']:
        t = {'id': new_id(s, 'thr'), 'projectId': opt(a, '--project'), 'title': opt(a, '--title'),
             'providerId': opt(a, '--provider', 'codex'), 'status': 'active', 'sectionId': opt(a, '--section'),
             'archivedAt': None, 'hasPendingInteraction': False,
             'worktree': opt(a, '--new-environment') == 'worktree', 'plan': '--plan' in a}
        s['threads'].append(t)
        out(t)
    elif a[:2] == ['thread', 'update']:
        for t in s['threads']:
            if t['id'] == a[2]:
                t['sectionId'] = opt(a, '--section')
        out({'ok': True})
    elif a[:2] == ['thread', 'archive']:
        for t in s['threads']:
            if t['id'] == a[2]:
                t['archivedAt'] = 1
        out({'ok': True})
    elif a[:1] == ['kanban'] and not KANBAN:
        print('Error: Unknown command group \'kanban\'.')
        save(s)
        return 1
    elif a[:2] == ['kanban', '--help']:
        print('bb kanban - Move thread cards on the Kanban board')
    elif a[:2] == ['kanban', 'board']:
        out({'columns': [{'id': k, 'name': k} for k in ('backlog', 'in-progress', 'review', 'done')], 'cards': s['cards']})
    elif a[:2] == ['kanban', 'move']:
        tid = opt(a, '--thread')
        s['cards'] = [c for c in s['cards'] if c['threadId'] != tid]
        s['cards'].append({'threadId': tid, 'columnId': a[2], 'note': opt(a, '--note'), 'position': len(s['cards'])})
        out({'ok': True})
    else:
        print(json.dumps({'ok': False, 'error': {'message': 'unknown command ' + ' '.join(a)}}))
        save(s)
        return 1
    save(s)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
