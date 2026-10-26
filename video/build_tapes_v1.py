#!/usr/bin/env python3
"""Author ordered tutorial steps, with full commands and reading pauses."""
from pathlib import Path
import json

STEPS = [
 ('01_install-aios',[('claude plugin marketplace add ./',8),('claude plugin install aios@navaigate-aios',14)]),
 ('02_install-brain',[('claude plugin install aios-brain@navaigate-aios',20)]),
 ('03_install-aios-codex-cursor',[('./install.sh aios',14)]),
 ('04_install-brain-codex-cursor',[('./install.sh aios-brain',18),('export PATH="$HOME/.local/bin:$PATH"',6)]),
 ('05_init-brain',[('brain init',16)]),
 ('06_prepare-demo-sessions',[('python3 scripts/sandbox_fixtures_v1.py --home /tmp/aios-member-sandbox',12)]),
 ('07_capture-sessions',[('brain capture',20)]),
 ('08_repeat-capture',[('brain capture',16)]),
 ('09_search-memory',[("brain search 'Lighthouse budget'",20)]),
 ('10_read-memory',[('brain read @SEARCH_REF@',22)]),
 ('11_check-health',[('brain status',26)]),
 ('12_verify-claude-code',[('claude plugin list',22)]),
 ('13_verify-codex',[('codex mcp list',22)]),
 ('14_verify-cursor-config',[('cat "$HOME/.cursor/mcp.json"',20)]),
 ('15_check-all-harnesses',[('python3 plugins/aios/scripts/status.py | more',18)])
]
COMMON = '''Require python3
Set Shell "bash"
Set Width 1920
Set Height 1080
Set FontFamily "Menlo"
Set FontSize 28
Set LineHeight 1.2
Set Padding 40
Set Theme "Catppuccin Mocha"
Set TypingSpeed 85ms
Set Framerate 30
Hide
Type@0ms `export HOME=/tmp/aios-member-sandbox CLAUDE_CONFIG_DIR=/tmp/aios-member-sandbox/.claude CODEX_HOME=/tmp/aios-member-sandbox/.codex; export PATH="$HOME/.local/bin:$PATH"; export PS1='$ '; unset PROMPT_COMMAND; set +m; clear`
Enter
Sleep 500ms
Show
'''


def build(ref=None):
    for name,commands in STEPS:
        tape='Output video/clips/'+name+'.mp4\n'+COMMON
        for command,seconds in commands:
            tape+='Type `'+command.replace('@SEARCH_REF@',ref or '@SEARCH_REF@')+'`\n'
            if name=='15_check-all-harnesses':
                tape+='Sleep 3s\n'
            tape+='Enter\nSleep '+str(seconds)+'s\n'
        if name=='15_check-all-harnesses':
            tape+='Space\nSleep 18s\nSpace\nSleep 18s\nSpace\nSleep 12s\n'
        (Path('video/tapes')/(name+'_v1.tape')).write_text(tape)
    Path('video/steps_v1.json').write_text(json.dumps([{'name':n,'commands':[c.replace('@SEARCH_REF@',ref or '@SEARCH_REF@') for c,_ in commands]} for n,commands in STEPS],indent=2)+'\n')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--ref')
    build(parser.parse_args().ref)
