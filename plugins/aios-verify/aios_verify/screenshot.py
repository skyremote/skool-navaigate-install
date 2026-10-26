"""Take a screenshot of a page or local HTML file with a headless Chrome, Chromium or Edge."""
import os
import shutil
import subprocess
from pathlib import Path

CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge', 'chrome',
]


def find_browser():
    override = os.environ.get('AIOS_VERIFY_BROWSER')
    for candidate in ([override] if override else []) + CANDIDATES:
        path = candidate if os.path.isabs(candidate) else shutil.which(candidate)
        if path and os.path.exists(path):
            return path
    return None


def target_url(target, cwd='.'):
    if '://' in target:
        return target
    path = (Path(cwd) / target).resolve()
    if not path.exists():
        raise FileNotFoundError('%s does not exist. Run the build first.' % target)
    return path.as_uri()


def take(target, out='.aios/screenshot.png', size='1280,800', cwd='.'):
    browser = find_browser()
    if not browser:
        raise RuntimeError('No Chrome, Chromium or Edge found. Install one, or set AIOS_VERIFY_BROWSER to its path.')
    url = target_url(target, cwd)
    out_path = (Path(cwd) / out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                    '--window-size=%s' % size, '--screenshot=%s' % out_path, url],
                   capture_output=True, timeout=90, stdin=subprocess.DEVNULL)
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError('The browser ran but wrote no screenshot for %s' % url)
    return out_path
