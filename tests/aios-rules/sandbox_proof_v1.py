#!/usr/bin/env python3
"""Install aios-rules as a new member in a throwaway HOME and record every command and its output.

Usage: python3 tests/aios-rules/sandbox_proof_v1.py [--with-claude-audit]
Writes plugins/aios-rules/proof/sandbox_v1.md. Never touches the real ~/.claude, ~/.codex or ~/.cursor.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOME = Path('/tmp/aios2-sandbox-a-foundations')
CHECKOUT = HOME / 'skool-navaigate-install'
FOLDER = HOME / 'acme-studio'
OUT = REPO / 'plugins' / 'aios-rules' / 'proof' / 'sandbox_v1.md'


def sanitise(text):
    for real, shown in (('/private' + str(CHECKOUT), '<checkout>'), (str(CHECKOUT), '<checkout>'),
                        ('/private' + str(HOME), '$HOME'), (str(HOME), '$HOME'), ('/private$HOME', '$HOME'),
                        (str(REPO), '<repo>'), (os.path.expanduser('~'), '<real-home>')):
        text = text.replace(real, shown)
    return text.replace('/private$HOME', '$HOME')


def env():
    e = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / '.claude'), CODEX_HOME=str(HOME / '.codex'))
    e['PATH'] = str(HOME / '.local/bin') + os.pathsep + e['PATH']
    return e


LOG = []


def run(cmd, cwd, note=None, shell=False, timeout=900):
    shown = cmd if shell else shlex.join(cmd)
    proc = subprocess.run(cmd, cwd=str(cwd), env=env(), capture_output=True, text=True, timeout=timeout, shell=shell)
    out = (proc.stdout + proc.stderr).rstrip()
    LOG.append((note, sanitise(shown), sanitise(out), proc.returncode, sanitise(str(cwd))))
    return proc


def prepare():
    if HOME.exists():
        shutil.rmtree(HOME)
    HOME.mkdir(parents=True)
    files = subprocess.run(['git', 'ls-files', '-z'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split('\0')
    for name in files:
        if not name or name.startswith('video/clips/'):
            continue
        source, dest = REPO / name, CHECKOUT / name
        if source.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
    # Apply the shared-file changes this stream proposes, so the sandbox models the merged branch.
    subprocess.run(['patch', '-s', '-p1', '-i', str(CHECKOUT / 'plugins/aios-rules/INTEGRATION.diff')], cwd=CHECKOUT, check=True)
    market = CHECKOUT / '.claude-plugin/marketplace.json'
    data = json.loads(market.read_text())
    entry = json.loads((CHECKOUT / 'plugins/aios-rules/MARKETPLACE_ENTRY.json').read_text())
    data['plugins'] = [p for p in data['plugins'] if p['name'] != 'aios-rules']
    data['plugins'].insert(1, entry)
    market.write_text(json.dumps(data, indent=2) + '\n')
    for name in ('bin/aios-rules', 'plugins/aios-rules/bin/aios-rules', 'plugins/aios-brain/bin/brain', 'install.sh'):
        path = CHECKOUT / name
        if path.exists():
            path.chmod(0o755)


def fill_agents():
    path = FOLDER / 'AGENTS.md'
    text = path.read_text()
    text = text.replace('{{ONE_LINE_WHAT_THE_BUSINESS_DOES}}', 'Acme Studio designs brand kits for small cafes.')
    text = text.replace('{{WHO_BUYS}}', 'cafe owners with one to three sites')
    text = text.replace('- {{ADD_YOUR_OWN_CHECK_HERE, for example: the build passes, the totals match the sheet}}',
                        '- Invoices: the total equals the sum of the lines in the source sheet.')
    text = text.replace('- {{EXAMPLE: the client list lives in 10_clients/README.md, not in a spreadsheet}}',
                        '- The client list lives in 10_clients/README.md, not in a spreadsheet.')
    path.write_text(text)


def main():
    with_claude = '--with-claude-audit' in sys.argv
    prepare()
    c = CHECKOUT
    run(['claude', '--version'], c, 'Claude Code version')
    run(['python3', '--version'], c, 'Python version')
    run(['claude', 'plugin', 'validate', 'plugins/aios-rules', '--strict'], c, 'Validate the pack')
    run(['claude', 'plugin', 'validate', '.claude-plugin/marketplace.json', '--strict'], c, 'Validate the marketplace with the aios-rules entry')
    run(['claude', 'plugin', 'marketplace', 'add', './'], c, 'Claude Code: add the review marketplace')
    run(['claude', 'plugin', 'install', 'aios@navaigate-aios'], c, 'Claude Code: install the start plugin')
    run(['claude', 'plugin', 'install', 'aios-rules@navaigate-aios'], c, 'Claude Code: install module 2')
    run('claude plugin list --json | python3 -c "import json,sys; print(json.dumps([{k:p.get(k) for k in (\'id\',\'version\',\'enabled\')} for p in json.load(sys.stdin)], indent=2))"',
        c, 'Claude Code: both plugins are installed and enabled', shell=True)
    run(['./install.sh', 'aios-rules'], c, 'Codex and Cursor: the dependency check refuses aios-rules before aios')
    run(['./install.sh', 'aios'], c, 'Codex and Cursor: install the start skill')
    run(['./install.sh', 'aios-rules'], c, 'Codex and Cursor: install module 2 (patched installer)')
    run('ls -l ~/.codex/skills ~/.cursor/skills ~/.agents/skills ~/.local/bin | sed "s/^.* \\([^ ]* -> \\)/\\1/"', c,
        'The links point into the checkout', shell=True)
    run(['mkdir', '-p', str(FOLDER)], HOME, 'A new, empty AIOS folder')
    run(['aios-rules', 'init', '--business', 'Acme Studio', '--owner', 'Sam Rivera', '--dry-run'], FOLDER, 'Dry run: nothing is written')
    run(['aios-rules', 'init', '--business', 'Acme Studio', '--owner', 'Sam Rivera'], FOLDER, 'Set up the folder and rules')
    run(['aios-rules', 'init'], FOLDER, 'A second run keeps everything')
    run(['cat', 'CLAUDE.md'], FOLDER, 'The bridge holds one line')
    run(['aios-rules', 'check'], FOLDER, 'First check: the placeholders are flagged')
    fill_agents()
    run(['grep', '-nE', 'Acme Studio|cafe|Invoices:|client list', 'AGENTS.md'], FOLDER,
        'The member fills in the four {{...}} lines (scripted here with fictional answers)')
    run(['aios-rules', 'check', '--harness', 'all'], FOLDER, 'Check all three harnesses: within budget')
    run('python3 -c "print(\'- old rule\\n\' * 240, end=\'\')" >> AGENTS.md && aios-rules check; echo "exit $?"', FOLDER,
        'Over budget on purpose: 240 extra lines make the check fail with exit 1', shell=True)
    run('python3 - <<\'EOF\'\nfrom pathlib import Path\np = Path("AGENTS.md")\np.write_text("".join(l for l in p.read_text().splitlines(True) if l != "- old rule\\n"))\nEOF\naios-rules check; echo "exit $?"', FOLDER,
        'Remove the extra lines: back within budget', shell=True)
    run(['aios-rules', 'cursor-rules'], FOLDER, 'Mirror the scoped rules for Cursor')
    run(['aios-rules', 'check', '--harness', 'cursor'], FOLDER, 'Cursor now has the same scoped rules')
    run(['aios-rules', 'audit', '--no-claude'], FOLDER, 'Audit, budget part only')
    if with_claude:
        run(['aios-rules', 'audit', '--timeout', '900'], FOLDER, 'Full audit on the member sign-in (claude -p, read-only tools)', timeout=2000)
        run('ls 80_aios/audits && tail -3 80_aios/audits/*_v2.md', FOLDER, 'The dated audit files', shell=True)
        run(['claude', '-p', 'Without reading any file, quote the line in your loaded instructions that says where invoices go. Reply with that line only.'],
            FOLDER, 'Claude Code read AGENTS.md through the bridge (answered from session context, no tools)')
        run(['claude', '-p', 'List the names of any skills you have whose names contain "rules". Names only, one per line.'],
            FOLDER, 'Claude Code sees both pack skills')
    lines = ['# aios-rules sandbox install, v1', '',
             'A new member installs module 2 in a throwaway HOME. Every command below ran for real; output is unedited',
             'apart from paths: `$HOME` is `/tmp/aios2-sandbox-a-foundations` and `<checkout>` is a copy of this branch',
             'with `INTEGRATION.diff` and `MARKETPLACE_ENTRY.json` applied (the merge this stream proposes).',
             'Environment: HOME, CLAUDE_CONFIG_DIR and CODEX_HOME all point into the sandbox. The business is fictional.', '',
             'Reproduce: `python3 tests/aios-rules/sandbox_proof_v1.py --with-claude-audit`.', '']
    for n, (note, cmd, out, code, cwd) in enumerate(LOG, 1):
        lines += ['## %d. %s' % (n, note), '', 'In `%s`:' % cwd, '', '```sh', cmd, '```', '```text', out, '[exit %d]' % code, '```', '']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines))
    print('Wrote', OUT)


if __name__ == '__main__':
    main()
