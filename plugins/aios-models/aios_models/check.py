"""models-check: print the member's current models, effort, advisor and logins.

Reads settings files and asks each CLI for its login state. It never prints a token,
a key, an email address or a whole config file. Standard library only.
Exit codes: 0 report printed, 1 a warning was found and --strict was given, 2 bad input.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
SECRETISH = re.compile(r'(sk-[A-Za-z0-9_-]{8,}|eyJ[A-Za-z0-9_-]{10,}|[A-Za-z0-9_-]{32,})')
LOGINS_FILE = Path('~/.config/aios-models/logins.json')
LABEL = re.compile(r'^[a-z0-9][a-z0-9-]{0,20}$')
EFFORT_ENV = 'CLAUDE_CODE_EFFORT_LEVEL'
MODEL_ENVS = ('ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL',
              'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL')


def redact(text):
    text = EMAIL.sub('<email>', str(text))
    return SECRETISH.sub('<hidden>', text)


def home():
    return Path(os.environ.get('HOME', str(Path.home())))


def expand(path):
    text = str(path)
    if text.startswith('~/') or text == '~':
        return home() / text[2:]
    return Path(text)


def read_json(path):
    try:
        data = json.loads(Path(path).read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def run(cmd, env=None, timeout=15):
    if not shutil.which(cmd[0]):
        return None
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return {'code': -1, 'out': ''}
    return {'code': result.returncode, 'out': (result.stdout + result.stderr).strip()}


def claude_settings(config_dir, project):
    """Merge the keys we report from user, project and local settings, highest last."""
    files = [('user', config_dir / 'settings.json')]
    if (project / '.claude').resolve() != config_dir.resolve():   # in the home folder, ~/.claude is the user file, not a project
        files += [('project', project / '.claude/settings.json'), ('local', project / '.claude/settings.local.json')]
    merged, sources = {}, {}
    for scope, path in files:
        data = read_json(path)
        for key in ('model', 'effortLevel', 'advisorModel'):
            if key in data:
                merged[key], sources[key] = data[key], scope
        for name, entry in (data.get('modelSettings') or {}).items():
            if isinstance(entry, dict) and 'effortLevel' in entry:
                merged.setdefault('modelSettings', {})[name] = entry['effortLevel']
                sources['modelSettings.' + name] = scope
    return merged, sources


ENV_AUTH = ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN')


def env_auth():
    return next((name for name in ENV_AUTH if os.environ.get(name)), None)


def claude_login(config_dir):
    name = env_auth()
    if name:
        # A token in the shell wins over every folder's own login, so the folder is not tested.
        return {'state': 'through the environment (' + name + '), shared by every folder'}
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(config_dir))
    result = run(['claude', 'auth', 'status', '--json'], env=env)
    if result is None:
        return {'state': 'claude not installed'}
    try:
        data = json.loads(result['out'])
    except ValueError:
        return {'state': 'unknown (' + redact(result['out'][:80]) + ')'}
    state = 'signed in' if data.get('loggedIn') else 'signed out'
    detail = [data.get('authMethod'), data.get('subscriptionType'), data.get('apiProvider')]
    return {'state': state, 'method': ', '.join(str(d) for d in detail if d)}


def claude_report(config_dir, project, label):
    settings, sources = claude_settings(config_dir, project)
    env_model = next(((k, os.environ[k]) for k in ('ANTHROPIC_MODEL',) if os.environ.get(k)), None)
    model = env_model[1] if env_model else settings.get('model', 'default (your plan picks it)')
    model_from = 'env ' + env_model[0] if env_model else sources.get('model', 'not set')
    effort = os.environ.get(EFFORT_ENV)
    effort_from = 'env ' + EFFORT_ENV if effort else None
    if not effort:
        per_model = settings.get('modelSettings', {})
        name = str(settings.get('model', ''))
        match = [v for k, v in per_model.items() if name and (k == name or name in k)]
        if match:
            effort, effort_from = match[0], 'modelSettings'
        elif per_model:
            effort = ', '.join(f'{k}={v}' for k, v in sorted(per_model.items()))
            effort_from = 'modelSettings'
        elif settings.get('effortLevel'):
            effort, effort_from = settings['effortLevel'], sources['effortLevel'] + ' effortLevel (older key)'
        else:
            effort, effort_from = 'model default (medium on the 5.5 models)', 'not set'
    advisor = 'off (env CLAUDE_CODE_DISABLE_ADVISOR_TOOL)' if os.environ.get('CLAUDE_CODE_DISABLE_ADVISOR_TOOL') \
        else settings.get('advisorModel', 'off')
    return {'harness': 'Claude Code', 'login': label, 'config': tilde(config_dir),
            'model': str(model), 'model_from': model_from, 'effort': str(effort), 'effort_from': effort_from,
            'advisor': str(advisor), **claude_login(config_dir)}


def tilde(path):
    text = str(path)
    base = str(home())
    return '~' + text[len(base):] if text.startswith(base) else text


def toml_values(text, keys):
    """Top-level key = "value" pairs before the first [table]. Enough for model settings."""
    values, profiles = {}, []
    in_top = True
    for line in text.splitlines():
        stripped = line.strip()
        table = re.match(r'^\[([^\]]+)\]', stripped)
        if table:
            in_top = False
            name = table.group(1).strip()
            if name.startswith('profiles.'):
                profiles.append(name.split('.', 1)[1].strip('"\''))
            continue
        found = re.match(r'^([A-Za-z_][\w-]*)\s*=\s*"?([^"#\n]*)"?', stripped)
        if in_top and found and found.group(1) in keys:
            values[found.group(1)] = found.group(2).strip()
    return values, profiles


def codex_report(codex_home, label):
    text = (codex_home / 'config.toml').read_text() if (codex_home / 'config.toml').exists() else ''
    values, profiles = toml_values(text, ('model', 'model_reasoning_effort', 'profile'))
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    result = run(['codex', 'login', 'status'], env=env)
    if result is None:
        state = 'codex not installed'
    else:
        first = result['out'].splitlines()[0] if result['out'] else ''
        state = ('signed in' if result['code'] == 0 and 'not logged in' not in first.lower() else 'signed out')
        state += (' (' + redact(first) + ')') if first else ''
    return {'harness': 'Codex', 'login': label, 'config': tilde(codex_home),
            'model': values.get('model', 'default (Codex picks it)'), 'model_from': 'config.toml' if 'model' in values else 'not set',
            'effort': values.get('model_reasoning_effort', 'default (medium)'),
            'effort_from': 'config.toml' if 'model_reasoning_effort' in values else 'not set',
            'advisor': 'n/a', 'state': state, 'profiles': ', '.join(profiles) or 'none'}


def cursor_report():
    data = read_json(home() / '.cursor/cli-config.json')
    model = data.get('model') if isinstance(data.get('model'), dict) else {}
    name = model.get('displayName') or model.get('modelId') or 'default (Cursor picks it)'
    result = run(['cursor-agent', 'status'], timeout=20)
    if result is None:
        state = 'cursor-agent not installed'
    else:
        out = result['out'].lower()
        state = 'signed out' if ('not logged in' in out or 'not authenticated' in out or result['code'] != 0) else 'signed in'
    return {'harness': 'Cursor CLI', 'login': 'default', 'config': '~/.cursor',
            'model': str(name), 'model_from': 'cli-config.json' if model else 'not set',
            'effort': 'set in the model name (for example a thinking model)', 'effort_from': 'model',
            'advisor': 'n/a', 'state': state}


def bb_pool():
    result = run(['bb', 'pool', 'account', 'list', '--json'], timeout=20)
    if result is None:
        return None
    try:
        data = json.loads(result['out'])
    except ValueError:
        return {'state': 'bb found, account pool not readable'}
    accounts = data.get('accounts', data) if isinstance(data, dict) else data
    counts = {}
    for account in accounts if isinstance(accounts, list) else []:
        provider = str(account.get('provider', '?'))
        enabled = account.get('enabled', True)
        key = provider + (' enabled' if enabled else ' disabled')
        counts[key] = counts.get(key, 0) + 1
    return {'state': 'bb account pool', 'accounts': counts}


def extra_logins():
    data = read_json(expand(LOGINS_FILE))
    rows = data.get('logins', []) if isinstance(data.get('logins'), list) else []
    return [r for r in rows if isinstance(r, dict) and r.get('label')]


def routing_warnings():
    notes = []
    if os.environ.get('ANTHROPIC_API_KEY'):
        notes.append('ANTHROPIC_API_KEY is set: Claude Code bills the metered API, not your subscription.')
    if os.environ.get('ANTHROPIC_AUTH_TOKEN') or os.environ.get('CLAUDE_CODE_OAUTH_TOKEN'):
        notes.append('A Claude token is set in your shell: every Claude folder uses it, so folder logins are not checked.')
    if os.environ.get('ANTHROPIC_BASE_URL'):
        notes.append('ANTHROPIC_BASE_URL is set: requests go through a proxy (for example the bb account pool).')
    for key in MODEL_ENVS[1:]:
        if os.environ.get(key):
            notes.append(key + ' is set in your shell and changes what the model names mean.')
    return notes


def effort_warnings(rows):
    notes = []
    for row in rows:
        if row['harness'] == 'Claude Code' and re.search(r'\b(xhigh|max)\b', row['effort']):
            notes.append(f"{row['login']}: effort is {row['effort']}. Start on medium and raise it per task.")
    return notes


def collect(project):
    rows = []
    default_dir = expand(os.environ.get('CLAUDE_CONFIG_DIR') or '~/.claude')
    rows.append(claude_report(default_dir, project, 'default'))
    codex_default = expand(os.environ.get('CODEX_HOME') or '~/.codex')
    rows.append(codex_report(codex_default, 'default'))
    for login in extra_logins():
        if login.get('claude_config_dir'):
            rows.append(claude_report(expand(login['claude_config_dir']), project, login['label']))
        if login.get('codex_home'):
            rows.append(codex_report(expand(login['codex_home']), login['label']))
    rows.append(cursor_report())
    pool = bb_pool()
    return rows, pool, routing_warnings() + effort_warnings(rows)


def print_text(rows, pool, warnings):
    print('Your models, effort and logins')
    print('')
    for row in rows:
        print(f"{row['harness']} [{row['login']}] {row['config']}")
        print(f"  login    {row['state']}" + (f" ({row['method']})" if row.get('method') else ''))
        print(f"  model    {row['model']}   <- {row['model_from']}")
        print(f"  effort   {row['effort']}   <- {row['effort_from']}")
        if row['advisor'] != 'n/a':
            print(f"  advisor  {row['advisor']}")
        if row.get('profiles') and row['profiles'] != 'none':
            print(f"  profiles {row['profiles']}")
        print('')
    if pool:
        counts = ', '.join(f'{v} {k}' for k, v in sorted(pool.get('accounts', {}).items())) or 'no accounts'
        print('bb account pool: ' + counts)
        print('')
    signed_in = sum(1 for r in rows if r['harness'] == 'Claude Code' and r['state'] == 'signed in')
    pooled = sum(v for k, v in (pool or {}).get('accounts', {}).items() if k.startswith('claude') and 'enabled' in k and 'disabled' not in k)
    print(f'Claude logins ready for failover: {max(signed_in, pooled)}' + ('' if max(signed_in, pooled) > 1 else
          ' (add a second one: models-check login add <label>)'))
    for note in warnings:
        print('Warning: ' + note)
    print('In a session, /status shows the live model and account, and /usage shows your plan limits.')


def login_add(args):
    label = args.label
    if not LABEL.match(label):
        print('Stopped: use a short lower-case label, for example work.', file=sys.stderr)
        return 2
    claude_dir = args.claude_config_dir or '~/.claude-' + label
    path = expand(LOGINS_FILE)
    data = read_json(path)
    logins = [r for r in data.get('logins', []) if isinstance(r, dict) and r.get('label') != label]
    entry = {'label': label, 'claude_config_dir': claude_dir}
    if args.codex_home:
        entry['codex_home'] = args.codex_home
    logins.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'logins': logins}, indent=2) + '\n')
    expand(claude_dir).mkdir(parents=True, exist_ok=True)
    print('Saved login ' + label + ' in ' + str(LOGINS_FILE))
    print('Created ' + claude_dir + ' (empty until you sign in)')
    print('')
    print('Next, sign in to your second subscription in that folder:')
    print('  CLAUDE_CONFIG_DIR=' + claude_dir + ' claude auth login')
    print('Then add this line to your ~/.zshrc or ~/.bashrc so one word opens it:')
    print(f"  alias claude-{label}='CLAUDE_CONFIG_DIR={claude_dir} claude'")
    if args.codex_home:
        print(f"  alias codex-{label}='CODEX_HOME={args.codex_home} codex'")
    print('Settings, plugins and skills in ' + claude_dir + ' are separate: install the aios packs there too.')
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog='models-check', description='Print your models, effort, advisor and logins. Never prints secrets.')
    parser.add_argument('--json', action='store_true', help='Machine-readable output')
    parser.add_argument('--strict', action='store_true', help='Exit 1 if there is a warning')
    parser.add_argument('--project', default='.', help='Project folder whose .claude/settings*.json also apply')
    sub = parser.add_subparsers(dest='command')
    login = sub.add_parser('login', help='Record a second login').add_subparsers(dest='action', required=True)
    add = login.add_parser('add', help='Record a second Claude Code login in its own CLAUDE_CONFIG_DIR')
    add.add_argument('label')
    add.add_argument('--claude-config-dir', help='Default: ~/.claude-<label>')
    add.add_argument('--codex-home', help='Optional second Codex home, for example ~/.codex-work')
    add.set_defaults(run=login_add)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if getattr(args, 'run', None):
        return args.run(args)
    rows, pool, warnings = collect(Path(args.project).resolve())
    if args.json:
        print(json.dumps({'harnesses': rows, 'bb_pool': pool, 'warnings': warnings}, indent=2))
    else:
        print_text(rows, pool, warnings)
    return 1 if (args.strict and warnings) else 0
