#!/usr/bin/env python3
"""A disposable physical checkout for path-neutral real-software recordings."""
from pathlib import Path
import shutil
import time

root=Path(__file__).resolve().parents[1]
target=Path('/tmp/aios-video-checkout-v2')
if target.exists():
    target.rename('/tmp/aios-video-checkout-old-'+str(time.time_ns()))
target.mkdir()
for name in ['.claude-plugin','plugins','skills','lessons','references','templates','scripts','install.sh','README.md','ROADMAP.md','LICENSE']:
    source=root/name
    if source.is_dir():
        shutil.copytree(source,target/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    else:
        shutil.copy2(source,target/name)
print('Prepared a disposable source copy at /tmp/aios-video-checkout-v2')
