"""Before a notebook is made: which of your files can go in, which cannot, and how to split if there are too many."""
import re
from pathlib import Path

# NotebookLM's published limits change; these are the free-plan figures we plan against. Check notebooklm.google.com.
MAX_SOURCES = 50
MAX_WORDS = 500_000
MAX_BYTES = 200 * 1024 * 1024
ACCEPTED = {'.pdf', '.txt', '.md', '.docx', '.pptx', '.csv', '.mp3', '.wav', '.m4a', '.png', '.jpg', '.jpeg'}
TEXT = {'.txt', '.md', '.csv'}
URL = re.compile(r'^https?://\S+$')


def inventory(folder):
    """Every file in the folder (not hidden), and any links listed one per line in links.txt."""
    folder = Path(folder).expanduser()
    if not folder.is_dir():
        raise ValueError('No folder at %s' % folder)
    rows = []
    for path in sorted(p for p in folder.rglob('*') if p.is_file() and not any(part.startswith('.') for part in p.relative_to(folder).parts)):
        if path.name == 'links.txt':
            for line in path.read_text(errors='ignore').splitlines():
                line = line.strip()
                if URL.match(line):
                    rows.append({'source': line, 'kind': 'link', 'ok': True, 'why': ''})
            continue
        suffix = path.suffix.lower()
        size = path.stat().st_size
        row = {'source': str(path.relative_to(folder)), 'kind': suffix.lstrip('.') or 'file', 'ok': True, 'why': ''}
        if suffix not in ACCEPTED:
            row.update(ok=False, why='NotebookLM does not take %s files; export it as PDF or text' % (suffix or 'this'))
        elif size > MAX_BYTES:
            row.update(ok=False, why='over 200 MB; split it')
        elif suffix in TEXT and len(path.read_text(errors='ignore').split()) > MAX_WORDS:
            row.update(ok=False, why='over 500,000 words; split it')
        elif size == 0:
            row.update(ok=False, why='empty file')
        rows.append(row)
    return rows


def batches(rows, size=MAX_SOURCES):
    ok = [r for r in rows if r['ok']]
    return [ok[i:i + size] for i in range(0, len(ok), size)]
