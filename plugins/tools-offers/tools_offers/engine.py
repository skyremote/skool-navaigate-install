"""The public Hormozi Growth Engine plus a corpus the member builds from the books they own.

The engine's skills read <CORPUS_ROOT>. This module checks the install, makes the empty corpus folders, measures
how much of each book the member has distilled, and points the installed skills at their corpus.
"""
import re
from pathlib import Path

SKILLS = ('ask-hormozi', 'grand-slam-offer-builder', 'lead-engine-planner', 'money-model-architect', 'offer-enhancer')
BOOKS = {'offers': '$100M Offers', 'leads': '$100M Leads', 'money-models': '$100M Money Models'}
PLACEHOLDER = '<CORPUS_ROOT>'
PAGE = re.compile(r'\[p\.\s?\d{1,3}\]')
HARNESS_DIRS = {'claude': ('.claude/skills', '.claude/agents/hormozi.md'),
                'codex': ('.codex/skills', '.codex/agents/hormozi.toml'),
                'agents': ('.agents/skills', None)}


class EngineError(ValueError):
    pass


def installed(home, harness='claude'):
    skills_dir, agent = HARNESS_DIRS[harness]
    found = {s: (Path(home) / skills_dir / s / 'SKILL.md').is_file() for s in SKILLS}
    agent_ok = bool(agent and (Path(home) / agent).is_file())
    return found, agent_ok


def pointed(home, harness='claude'):
    """'placeholder' if any installed skill still reads <CORPUS_ROOT>, 'set' if none do, 'missing' if none installed."""
    skills_dir, _ = HARNESS_DIRS[harness]
    files = [p for s in SKILLS for p in (Path(home) / skills_dir / s).rglob('*.md')]
    if not files:
        return 'missing'
    return 'placeholder' if any(PLACEHOLDER in f.read_text(errors='ignore') for f in files) else 'set'


def init(root):
    root = Path(root).expanduser()
    made = []
    for book in BOOKS:
        for sub in ('corpus', 'figures'):
            folder = root / book / sub
            if not folder.exists():
                folder.mkdir(parents=True)
                made.append(folder)
    summary = root / 'EXTRACTION-SUMMARY.md'
    if not summary.exists():
        summary.write_text('# Extraction summary\n\nYour own distillation of the books you own. Never share these files.\n\n'
                           '| Book | Chapters done | Notes |\n|---|---|---|\n' +
                           ''.join('| %s | 0 | |\n' % title for title in BOOKS.values()))
        made.append(summary)
    return made


def coverage(root):
    """Per book: chapter files, files with page markers, and total page markers."""
    root = Path(root).expanduser()
    if not root.is_dir():
        raise EngineError('No corpus folder at %s. Make it with: tools-offers corpus init %s' % (root, root))
    report = {}
    for book in BOOKS:
        files = sorted((root / book / 'corpus').glob('*.md')) if (root / book / 'corpus').is_dir() else []
        marked = [f for f in files if PAGE.search(f.read_text(errors='ignore'))]
        report[book] = {'chapters': len(files), 'with_pages': len(marked),
                        'page_markers': sum(len(PAGE.findall(f.read_text(errors='ignore'))) for f in files)}
    return report


def point(home, root, harness='claude', write=False):
    """Replace <CORPUS_ROOT> in the member's installed engine files. Returns the files that change."""
    root = str(Path(root).expanduser().resolve()).rstrip('/')
    if PLACEHOLDER in root or '|' in root:
        raise EngineError('That corpus path cannot be used.')
    skills_dir, agent = HARNESS_DIRS[harness]
    candidates = [p for s in SKILLS for p in (Path(home) / skills_dir / s).rglob('*') if p.is_file()]
    if agent and (Path(home) / agent).is_file():
        candidates.append(Path(home) / agent)
    changed = [p for p in candidates if PLACEHOLDER in p.read_text(errors='ignore')]
    if write:
        for path in changed:
            path.write_text(path.read_text().replace(PLACEHOLDER, root))
    return changed
