#!/usr/bin/env python3
"""Save unaltered stills from real sandbox terminal recordings."""
import subprocess
from pathlib import Path

Path('video/screens').mkdir(exist_ok=True)
for clip,name in [
 ('12_verify-claude-code','12_claude-code-sandbox_v1'),
 ('13_verify-codex','13_codex-sandbox_v1'),
 ('14_verify-cursor-config','14_cursor-sandbox-config_v1')]:
    subprocess.run(['ffmpeg','-v','error','-y','-sseof','-2','-i','video/clips/'+clip+'.mp4',
                    '-frames:v','1','video/screens/'+name+'.png'],check=True)
    print('Saved real terminal still: '+name+'.png')
