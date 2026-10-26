"""Run a project's checks from .aios/verify.json and report each one honestly.

{
  "checks": [
    {"name": "tests", "run": "python3 -m unittest"},
    {"name": "build", "run": "python3 build.py"},
    {"name": "screenshot", "run": "aios-verify screenshot dist/index.html --out .aios/screenshot.png", "gate": false}
  ],
  "timeout_seconds": 300,
  "production_commands": ["./deploy.sh"]
}

A check with "gate": false runs in `aios-verify run` but not in the Stop gate.
"""
import json
import os
import subprocess
import time
from pathlib import Path

CONFIG = Path('.aios') / 'verify.json'
BIN = Path(__file__).resolve().parents[1] / 'bin'


def check_env():
    """The checks may call aios-verify itself (the screenshot), even from a hook with a short PATH."""
    env = dict(os.environ)
    env['PATH'] = str(BIN) + os.pathsep + env.get('PATH', '')
    return env


class ConfigError(ValueError):
    pass


def find_root(start='.'):
    """The nearest folder at or above start that has .aios/verify.json."""
    start = Path(start).resolve()
    for folder in [start] + list(start.parents):
        if (folder / CONFIG).is_file():
            return folder
    return None


def load(root):
    path = Path(root) / CONFIG
    try:
        data = json.loads(path.read_text())
    except ValueError as exc:
        raise ConfigError('%s is not valid JSON: %s' % (path, exc))
    checks = data.get('checks') if isinstance(data, dict) else None
    if not isinstance(checks, list) or not checks:
        raise ConfigError('%s needs a "checks" list with at least one {"name", "run"}' % path)
    for check in checks:
        if not isinstance(check, dict) or not check.get('name') or not check.get('run'):
            raise ConfigError('Every check needs a "name" and a "run" command')
    return data


def run_checks(root, gate_only=False, timeout=None):
    """Run every check in order. Returns a list of result dicts; never raises on a failing check."""
    data = load(root)
    limit = timeout or int(data.get('timeout_seconds', 300))
    results = []
    for check in data['checks']:
        if gate_only and check.get('gate') is False:
            continue
        started = time.time()
        try:
            proc = subprocess.run(check['run'], shell=True, cwd=str(root), capture_output=True, text=True,
                                  timeout=limit, stdin=subprocess.DEVNULL, env=check_env())
            code, output = proc.returncode, (proc.stdout + proc.stderr)
        except subprocess.TimeoutExpired as exc:
            code = 124
            output = ((exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or ''))
            output += '\nTimed out after %d seconds' % limit
        results.append({'name': check['name'], 'run': check['run'], 'exit': code, 'passed': code == 0,
                        'seconds': round(time.time() - started, 1), 'tail': '\n'.join(output.strip().splitlines()[-15:])})
    return results


def format_results(results):
    lines = []
    for item in results:
        lines.append('%s  %-12s %5.1fs  %s' % ('PASS' if item['passed'] else 'FAIL', item['name'], item['seconds'], item['run']))
        if not item['passed'] and item['tail']:
            lines += ['        ' + line for line in item['tail'].splitlines()]
    passed = sum(1 for item in results if item['passed'])
    lines.append('%d of %d checks passed.' % (passed, len(results)))
    return '\n'.join(lines)
