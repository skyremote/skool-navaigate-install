#!/usr/bin/env python3
"""Check the complete ordered tutorial material. No artificial duration cap."""
import json
import subprocess
from pathlib import Path

expected={step['name']+'.mp4' for step in json.loads(Path('video/steps_v2.json').read_text())}
paths=sorted(Path('video/clips').glob('*.mp4'))
assert {p.name for p in paths}==expected,'Clip inventory must match the shot list'
rows=[]
for path in paths:
    probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,codec_type','-of','json',str(path)],capture_output=True,text=True,check=True)
    info=json.loads(probe.stdout)
    video=next(s for s in info['streams'] if s['codec_type']=='video')
    seconds=float(info['format']['duration'])
    assert (video['width'],video['height'])==(1920,1080),str(path)
    assert seconds>0,str(path)
    rows.append({'file':str(path),'seconds':round(seconds,2),'width':1920,'height':1080})
Path('video/clips/manifest_v2.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
