"""`harness`: set up and check Claude Code, Codex, Cursor and Grok Bot for one AIOS folder."""
import argparse
import json
import sys

from . import __version__
from . import harness as h


def _paths(args):
    return h.Paths(args.folder)


def _print_log(log, notes):
    for line in log:
        print(line)
    for note in notes:
        print('Note: ' + note)


def cmd_check(args):
    report = h.check(_paths(args), live=args.live)
    if args.json:
        print(json.dumps(h.report_json(report), indent=2))
    else:
        print(h.render(report))
    return 1 if report['differs'] else 0


def cmd_setup(args):
    log, notes = h.setup(_paths(args), dry_run=args.dry_run)
    _print_log(log or ['Nothing to change.'], notes)
    if not args.dry_run:
        print('Next: run `harness check`, then restart each harness so it reloads.')
    return 1 if notes and any('Left alone' in n or 'already defines' in n for n in notes) else 0


def cmd_sync(args):
    log, conflicts = h.sync(_paths(args), dry_run=args.dry_run)
    _print_log(log or ['Everything already matches.'], conflicts)
    return 1 if conflicts else 0


def _env_pairs(pairs):
    env = {}
    for pair in pairs or []:
        if '=' not in pair:
            raise ValueError("Use --env NAME=value or --env 'NAME=${NAME}' (in single quotes, so the shell does not fill in the value).")
        key, value = pair.split('=', 1)
        env[key] = value
    return env


def cmd_mcp(args):
    p = _paths(args)
    if args.mcp_cmd == 'list':
        servers = h.canonical_servers(p)
        if not servers:
            print('No MCP servers in .aios/mcp.json yet.')
        for name, server in sorted(servers.items()):
            env = sorted((server.get('env') or {}).keys())
            print('%s: %s%s' % (name, h.describe(server), ('  env: ' + ', '.join(env)) if env else ''))
        return 0
    if args.mcp_cmd == 'add':
        command = list(args.command or [])
        if bool(args.url) == bool(command):
            raise ValueError('Give either --url URL or -- COMMAND [ARGS].')
        log, conflicts = h.mcp_add(p, args.name, command=command[0] if command else None,
                                   args=command[1:], url=args.url, env=_env_pairs(args.env))
        print('Added "%s" to .aios/mcp.json.' % args.name)
        _print_log(log, conflicts)
        print('Then add it in Grok Bot by hand: harness grok')
        return 1 if conflicts else 0
    log, conflicts = h.mcp_remove(p, args.name)
    print('Removed "%s" from .aios/mcp.json.' % args.name)
    _print_log(log, conflicts)
    return 1 if conflicts else 0


def cmd_grok(args):
    print(h.grok_instructions(_paths(args)))
    return 0


def cmd_defaults(args):
    p = _paths(args)
    if args.apply:
        for line in h.apply_defaults(p, args.effort) or ['Defaults already set.']:
            print(line)
    print('%-12s %-26s %-22s %s' % ('Harness', 'Model', 'Effort', 'Where it is set'))
    for key, model, effort, where in h.defaults(p):
        print('%-12s %-26s %-22s %s' % (h.LABEL[key], str(model)[:25], str(effort)[:21], where))
    print('\nKeys: model and effortLevel (Claude Code), model and model_reasoning_effort (Codex).')
    print('Start at medium effort. Raise it for one hard job, not for the whole day.')
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog='harness', description=__doc__)
    parser.add_argument('--version', action='version', version='harness ' + __version__)
    parser.add_argument('--folder', default='.', help='Your AIOS folder (default: this folder)')
    sub = parser.add_subparsers(dest='cmd')
    c = sub.add_parser('check', help='Show what each harness sees and what differs (exit 1 if anything differs)')
    c.add_argument('--json', action='store_true')
    c.add_argument('--live', action='store_true', help='Also ask each installed CLI for the rules phrase (one short prompt each)')
    s = sub.add_parser('setup', help='Create AGENTS.md, the CLAUDE.md bridge and .aios/mcp.json, then sync')
    s.add_argument('--dry-run', action='store_true')
    y = sub.add_parser('sync', help='Link shared skills and write .aios/mcp.json into every harness')
    y.add_argument('--dry-run', action='store_true')
    m = sub.add_parser('mcp', help='Add, remove or list MCP servers for every harness at once')
    msub = m.add_subparsers(dest='mcp_cmd')
    msub.add_parser('list')
    a = msub.add_parser('add')
    a.add_argument('name')
    a.add_argument('--url')
    a.add_argument('--env', action='append', help='NAME=value or NAME=${NAME} (secrets as references only)')
    a.set_defaults(command=[])
    r = msub.add_parser('remove')
    r.add_argument('name')
    sub.add_parser('grok', help='Print the Grok Bot steps and the probe prompt')
    d = sub.add_parser('defaults', help='Show model and effort per harness')
    d.add_argument('--apply', action='store_true', help='Write the effort default into this folder')
    d.add_argument('--effort', default='medium', choices=['low', 'medium', 'high', 'xhigh'])
    return parser


def main(argv=None):
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    command = []
    if '--' in argv:  # everything after -- is the MCP server's own command line
        cut = argv.index('--')
        argv, command = argv[:cut], argv[cut + 1:]
    args = parser.parse_args(argv)
    if command:
        if getattr(args, 'mcp_cmd', None) != 'add':
            parser.error('-- COMMAND is only used with: harness mcp add NAME -- COMMAND [ARGS]')
        args.command = command
    handlers = {'check': cmd_check, 'setup': cmd_setup, 'sync': cmd_sync, 'mcp': cmd_mcp,
                'grok': cmd_grok, 'defaults': cmd_defaults}
    if args.cmd not in handlers or (args.cmd == 'mcp' and not args.mcp_cmd):
        parser.print_help()
        return 2
    try:
        return handlers[args.cmd](args)
    except ValueError as exc:
        print('Stopped: %s' % exc, file=sys.stderr)
        return 2
