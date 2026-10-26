"""Set up verification in a project: the checks file, the verify skill, REVIEW.md and the PR template.

Never overwrites: an existing file is kept and reported as skipped.
"""
import json
import os
import shutil
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / 'templates'


def detect_checks(root):
    """Guess the test and build commands from the files in the project."""
    root = Path(root)
    checks = []
    package = root / 'package.json'
    if package.is_file():
        try:
            scripts = json.loads(package.read_text()).get('scripts', {})
        except ValueError:
            scripts = {}
        runner = 'pnpm' if (root / 'pnpm-lock.yaml').exists() else 'yarn' if (root / 'yarn.lock').exists() else 'npm'
        if 'test' in scripts:
            checks.append({'name': 'tests', 'run': '%s test' % runner if runner != 'npm' else 'npm test'})
        if 'build' in scripts:
            checks.append({'name': 'build', 'run': '%s run build' % runner})
    elif (root / 'pyproject.toml').exists() or list(root.glob('test_*.py')) or (root / 'tests').is_dir():
        if (root / 'pytest.ini').exists() or 'pytest' in _read(root / 'pyproject.toml'):
            checks.append({'name': 'tests', 'run': 'python3 -m pytest -q'})
        else:
            checks.append({'name': 'tests', 'run': 'python3 -m unittest'})
        if (root / 'build.py').exists():
            checks.append({'name': 'build', 'run': 'python3 build.py'})
    elif (root / 'Makefile').is_file():
        text = _read(root / 'Makefile')
        if '\ntest:' in '\n' + text:
            checks.append({'name': 'tests', 'run': 'make test'})
        if '\nbuild:' in '\n' + text:
            checks.append({'name': 'build', 'run': 'make build'})
    return checks


def _read(path):
    try:
        return path.read_text()
    except OSError:
        return ''


def plan(root, git_hook=False):
    """Return a list of (relative path, content or source path, mode)."""
    root = Path(root)
    checks = detect_checks(root)
    if not checks:
        checks = [{'name': 'tests', 'run': 'echo "Replace this with your test command" && exit 1'}]
    index = next((p for p in ('dist/index.html', 'build/index.html', 'public/index.html', 'index.html')
                  if (root / p).exists()), 'dist/index.html')
    if (root / 'package.json').exists() or (root / 'build.py').exists():
        checks.append({'name': 'screenshot', 'run': 'aios-verify screenshot %s --out .aios/screenshot.png' % index,
                       'gate': False})
    config = {'checks': checks, 'timeout_seconds': 300, 'production_commands': []}
    files = [
        ('.aios/verify.json', json.dumps(config, indent=2) + '\n', 0o644),
        ('.claude/skills/verify/SKILL.md', TEMPLATES / 'verify-SKILL.md', 0o644),
        ('REVIEW.md', TEMPLATES / 'REVIEW.md', 0o644),
        ('.github/pull_request_template.md', TEMPLATES / 'github' / 'pull_request_template.md', 0o644),
    ]
    if git_hook:
        files.append(('.git/hooks/pre-commit', TEMPLATES / 'pre-commit', 0o755))
    return files


def apply(root, git_hook=False, dry_run=False):
    """Write the files that do not exist yet. Returns (written, skipped)."""
    root = Path(root)
    if git_hook and not (root / '.git').is_dir():
        raise ValueError('--git-hook needs a git repository at %s (run git init first)' % root)
    written, skipped = [], []
    for relative, content, mode in plan(root, git_hook):
        target = root / relative
        if target.exists():
            skipped.append(relative)
            continue
        written.append(relative)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, Path):
            shutil.copyfile(content, target)
        else:
            target.write_text(content)
        os.chmod(target, mode)
    ignore = root / '.gitignore'
    line = '.aios/verify-state.json'
    if not dry_run and (root / '.git').exists() and line not in _read(ignore).splitlines():
        with open(ignore, 'a') as stream:
            stream.write(('\n' if _read(ignore) and not _read(ignore).endswith('\n') else '') + line + '\n.aios/screenshot.png\n')
        written.append('.gitignore (added .aios/verify-state.json)')
    return written, skipped
