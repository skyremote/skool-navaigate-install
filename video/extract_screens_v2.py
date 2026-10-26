#!/usr/bin/env python3
"""Save unaltered stills from real sandbox terminal recordings."""
import subprocess
from pathlib import Path

Path('video/screens').mkdir(exist_ok=True)
for clip,name in [
 ('12_verify-claude-code_v2','12_claude-code-sandbox_v2'),
 ('13_verify-codex_v2','13_codex-sandbox_v2'),
 ('14_verify-cursor-config_v2','14_cursor-sandbox-config_v2')]:
    subprocess.run(['ffmpeg','-v','error','-y','-sseof','-2','-i','video/clips/'+clip+'.mp4',
                    '-frames:v','1','video/screens/'+name+'.png'],check=True)
    print('Saved real terminal still: '+name+'.png')
