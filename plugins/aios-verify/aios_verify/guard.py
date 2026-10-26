"""Three hard rules as a PreToolUse hook on Bash:

1. No secrets in commits: `git commit` is denied when the staged change adds a key, token or private key.
2. No destructive git: force push, hard reset, clean -f, branch -D and the like are denied.
3. Confirm before live production: deploy and publish commands ask the person first.

Rules 1 and 2 deny; the agent sees the reason and must find a safe way. Rule 3 asks, so a
person decides. Nothing here stops a person typing the command in their own terminal.
"""
import json
import re
import shlex
import subprocess
from pathlib import Path

SECRET_PATTERNS = [
    ('private key', re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY')),
    ('AWS access key', re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b')),
    ('Anthropic or OpenAI key', re.compile(r'\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}')),
    ('GitHub token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})')),
    ('Slack token', re.compile(r'\bxox[abposr]-[A-Za-z0-9-]{10,}')),
    ('Google API key', re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b')),
    ('Stripe live key', re.compile(r'\b[rs]k_live_[0-9A-Za-z]{16,}')),
    ('JSON web token', re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')),
    ('password or key in a setting', re.compile(
        r'(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|password|passwd)\b["\']?\s*[:=]\s*["\'][^"\'\s]{12,}["\']')),
]
SECRET_FILES = re.compile(r'(?:^|/)(?:\.env(?:\.[\w.-]+)?|id_rsa|id_ed25519|id_ecdsa|[\w.-]+\.pem|[\w.-]+\.p12|[\w.-]+\.key|credentials\.json)$')
SAFE_ENV_FILES = re.compile(r'\.env\.(?:example|sample|template)$')

PRODUCTION = [
    ('Vercel production deploy', re.compile(r'\bvercel\b.*(?:--prod\b|--production\b)|\bvercel\s+promote\b')),
    ('Netlify production deploy', re.compile(r'\bnetlify\s+deploy\b.*--prod\b')),
    ('package publish', re.compile(r'\b(?:npm|pnpm|yarn)\s+publish\b|\btwine\s+upload\b|\bcargo\s+publish\b|\bgem\s+push\b')),
    ('Fly deploy', re.compile(r'\b(?:fly|flyctl)\s+deploy\b')),
    ('Railway deploy', re.compile(r'\brailway\s+(?:up|deploy|redeploy)\b')),
    ('Firebase deploy', re.compile(r'\bfirebase\s+deploy\b')),
    ('Cloudflare deploy', re.compile(r'\bwrangler\s+(?:deploy|publish)\b')),
    ('Heroku deploy', re.compile(r'\bgit\s+push\s+heroku\b|\bheroku\s+releases:rollback\b')),
    ('Terraform apply', re.compile(r'\bterraform\s+(?:apply|destroy)\b')),
    ('Kubernetes change', re.compile(r'\bkubectl\s+(?:apply|delete|rollout|scale|set)\b')),
    ('database migration on a remote database', re.compile(r'\bsupabase\s+db\s+push\b|\bprisma\s+migrate\s+deploy\b')),
    ('GitHub release', re.compile(r'\bgh\s+release\s+create\b')),
    ('image push', re.compile(r'\bdocker\s+push\b')),
]
PROTECTED_BRANCHES = ('main', 'master', 'production', 'prod', 'release')
SPLIT = re.compile(r'\s*(?:&&|\|\||;|\||\n)\s*')


def segments(command):
    """Split a shell line into simple commands, each a list of words."""
    out = []
    for part in SPLIT.split(command or ''):
        part = part.strip()
        if not part:
            continue
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and (re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', words[0]) or words[0] in ('sudo', 'command', 'env', 'nohup', 'time')):
            words = words[1:]
        if words:
            out.append(words)
    return out


def git_args(words):
    """Return (repo_dir, subcommand words) for a git command, else (None, None)."""
    if not words or Path(words[0]).name != 'git':
        return None, None
    repo, i = None, 1
    while i < len(words) and words[i].startswith('-'):
        if words[i] == '-C' and i + 1 < len(words):
            repo = words[i + 1]
            i += 2
        elif words[i] in ('-c', '--git-dir', '--work-tree') and i + 1 < len(words):
            i += 2
        else:
            i += 1
    return repo, words[i:]


def short_flags(args):
    flags = set()
    for arg in args:
        if re.match(r'^-[A-Za-z]+$', arg):
            flags.update(arg[1:])
    return flags


def destructive_git(sub):
    """Return a reason if a git subcommand can destroy work, else None."""
    if not sub:
        return None
    name, args = sub[0], sub[1:]
    flags = short_flags(args)
    if name == 'push':
        if any(a == '--force' or a.startswith('--force=') or a == '--mirror' for a in args) or 'f' in flags:
            return 'force push rewrites the remote and can delete other people\'s work. Pull, merge, then push normally.'
        if '--delete' in args or 'd' in flags or any(re.match(r'^:[^/]', a) for a in args[1:]):
            return 'deleting a remote branch. Ask the person to do it themselves if they really want it gone.'
        if any(a.startswith('+') for a in args[1:]):
            return 'a +refspec forces the push. Push normally instead.'
    if name == 'reset' and '--hard' in args:
        return 'reset --hard throws away uncommitted work. Commit or use a new branch instead.'
    if name == 'clean' and ('f' in flags or '--force' in args):
        return 'clean -f deletes untracked files for good. Leave them, or list them with git clean -n.'
    if name == 'checkout' and ('.' in args or ('--' in args and args[args.index('--') + 1:] in (['.'], ['*']))):
        return 'checkout of the whole tree discards uncommitted changes. Commit first, or name one file.'
    if name == 'restore' and '.' in args and '--staged' not in args:
        return 'restore . discards uncommitted changes in every file. Name the one file to restore.'
    if name == 'branch' and ('D' in flags or ('--delete' in args and '--force' in args)):
        return 'branch -D deletes a branch even if it is not merged. Use branch -d, which refuses unmerged work.'
    if name == 'stash' and args[:1] in (['drop'], ['clear']):
        return 'stash drop/clear deletes saved work for good.'
    if name in ('filter-branch', 'filter-repo'):
        return 'history rewriting changes every commit after it.'
    if name == 'reflog' and args[:1] == ['expire']:
        return 'reflog expire removes the safety net for lost commits.'
    if name == 'update-ref' and '-d' in args:
        return 'update-ref -d deletes a reference directly.'
    if name == 'gc' and any(a.startswith('--prune') for a in args):
        return 'gc --prune removes unreachable commits you might still need.'
    return None


def current_branch(cwd):
    try:
        out = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd, capture_output=True,
                             text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def production(words, cwd, extra):
    line = ' '.join(words)
    for name, pattern in PRODUCTION:
        if pattern.search(line):
            return name
    for pattern in extra:
        try:
            if re.search(pattern, line):
                return 'a production command listed in .aios/verify.json'
        except re.error:
            continue
    repo, sub = git_args(words)
    if sub and sub[0] == 'push':
        targets = [a for a in sub[1:] if not a.startswith('-')]
        refs = targets[1:] if len(targets) > 1 else []
        branches = [r.split(':')[-1].replace('refs/heads/', '') for r in refs]
        if not refs:
            branch = current_branch(repo or cwd)
            branches = [branch] if branch else []
        hit = [b for b in branches if b in PROTECTED_BRANCHES]
        if hit:
            return 'push to %s, which usually deploys or is shared' % hit[0]
    return None


def staged_secrets(cwd, all_tracked=False):
    """Scan what a commit would add. Returns findings without the secret values."""
    findings = []
    diff_cmd = ['git', 'diff', '--cached', '--no-color', '-U0']
    names_cmd = ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM']
    if all_tracked:
        diff_cmd = ['git', 'diff', 'HEAD', '--no-color', '-U0']
        names_cmd = ['git', 'diff', 'HEAD', '--name-only', '--diff-filter=AM']
    try:
        names = subprocess.run(names_cmd, cwd=cwd, capture_output=True, text=True, timeout=20).stdout.split()
        diff = subprocess.run(diff_cmd, cwd=cwd, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return findings
    for name in names:
        if SECRET_FILES.search(name) and not SAFE_ENV_FILES.search(name):
            findings.append((name, 'a secrets file'))
    current = None
    for line in diff.splitlines():
        if line.startswith('+++ '):
            current = line[6:] if line.startswith('+++ b/') else line[4:]
            continue
        if not line.startswith('+') or line.startswith('+++'):
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append((current, label))
                break
    return sorted(set(findings))


def decide(command, cwd='.', extra_production=()):
    """Return (decision, reason). decision is 'deny', 'ask' or None (no opinion)."""
    for words in segments(command):
        repo, sub = git_args(words)
        reason = destructive_git(sub)
        if reason:
            return 'deny', 'AIOS hard rule, no destructive git: ' + reason
        if sub and sub[0] == 'commit':
            all_tracked = 'a' in short_flags(sub[1:]) or '--all' in sub
            found = staged_secrets(repo or cwd, all_tracked)
            if found:
                where = ', '.join('%s (%s)' % (f or '?', label) for f, label in found[:5])
                return 'deny', ('AIOS hard rule, no secrets in commits: the commit would add %s. Remove the '
                                'value, load it from an environment variable or a file listed in .gitignore, '
                                'unstage it with git restore --staged <file>, then commit again.' % where)
    for words in segments(command):
        name = production(words, cwd, extra_production)
        if name:
            return 'ask', 'AIOS hard rule, confirm before live production: this is a %s. Check it is meant to go live now.' % name
    return None, None


def load_extra(cwd):
    for folder in [Path(cwd)] + list(Path(cwd).resolve().parents):
        config = folder / '.aios' / 'verify.json'
        if config.is_file():
            try:
                data = json.loads(config.read_text())
            except ValueError:
                return []
            values = data.get('production_commands', []) if isinstance(data, dict) else []
            return [v for v in values if isinstance(v, str)]
    return []


def hook(payload):
    """Turn a PreToolUse payload into the hook's JSON answer, or None for no opinion."""
    if payload.get('tool_name') != 'Bash':
        return None
    command = (payload.get('tool_input') or {}).get('command', '')
    cwd = payload.get('cwd') or '.'
    decision, reason = decide(command, cwd, load_extra(cwd))
    if not decision:
        return None
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': decision,
                                   'permissionDecisionReason': reason}}
