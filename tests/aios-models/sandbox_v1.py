#!/usr/bin/env python3
"""Sandbox proof for aios-models: install, check models and logins, add a second login, run one headless session."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'aios-methods'))
from sandbox_lib_v1 import main  # noqa: E402


def use(box):
    # A new member has no bb: drop the host's bb from PATH so its account pool is not read.
    box.env['PATH'] = os.pathsep.join(p for p in box.env['PATH'].split(os.pathsep) if 'bb.app' not in p)
    # A new member has no proxy token either. Keep it aside for the one headless session in step 6.
    proxy = {k: box.env.pop(k) for k in list(box.env) if k.startswith('ANTHROPIC_')}
    box.note('## 4. First use: what am I on?')
    box.run('models-check')
    box.note('## 5. Record a second login for failover')
    box.run('models-check login add work')
    box.run('cat ~/.config/aios-models/logins.json')
    box.run('CLAUDE_CONFIG_DIR=~/.claude-work claude auth status --text',
            show='CLAUDE_CONFIG_DIR=~/.claude-work claude auth status --text   # before signing in', expect=1)
    box.run('models-check')
    box.note('## 6. One real session on Sonnet at medium effort with an Opus advisor')
    box.note('This sandbox signs in through a local account-pool token for this one step only, because a new member '
             'would sign in with `claude auth login` in the browser, which a script cannot do.')
    box.env.update(proxy)
    box.run('claude -p --model sonnet --effort medium --advisor opus --output-format json '
            '"Reply with the single word ready." < /dev/null | python3 -c \'import json,sys; d=json.load(sys.stdin); '
            'print("result:", d.get("result")); print("models used:", sorted(d.get("modelUsage", {})))\'',
            show='claude -p --model sonnet --effort medium --advisor opus --output-format json "Reply with the single word ready."',
            timeout=240)
    for key in proxy:
        box.env.pop(key)
    box.note('## 7. Strict mode for scripts: exit 1 when a warning is found')
    (box.home / '.claude/settings.json').write_text('{"effortLevel": "xhigh"}\n')
    box.run('cat ~/.claude/settings.json', show='cat ~/.claude/settings.json   # an old setting from months ago')
    box.run('models-check --strict', expect=1)


if __name__ == '__main__':
    sys.exit(main('aios-models', use))
