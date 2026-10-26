#!/usr/bin/env python3
"""Recopy each shelf wrapper's skill folders from the first-generation skills/ at the repo root.

The wrapper packs ship byte-for-byte copies (never symlinks: they break when Claude Code caches a plugin).
When a 1.x skill changes, run this, then the tests:

    python3 tests/shelf-wrappers/sync_copies.py            # recopy every pack
    python3 tests/shelf-wrappers/sync_copies.py --check    # report drift, change nothing (exit 1 on drift)
    python3 tests/shelf-wrappers/sync_copies.py shelf-hormozi shelf-diagrams   # only these packs

It only ever writes inside plugins/shelf-<name>/skills/. It never touches the root skills/ folders.
"""
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# pack -> the 1.x skills it carries. deep-research, transcripts and podcasts carry web-scrape because their
# SKILL.md files call its helper "in this plugin".
PACKS = {
    'shelf-design-brain': ['design-brain'],
    'shelf-deep-research': ['deep-research', 'web-scrape'],
    'shelf-web-scrape': ['web-scrape'],
    'shelf-transcripts': ['transcripts', 'web-scrape'],
    'shelf-podcasts': ['podcasts', 'web-scrape'],
    'shelf-thumbnails': ['thumbnails'],
    'shelf-diagrams': ['diagrams'],
    'shelf-daily-brief': ['daily-brief'],
    'shelf-content-pipeline': ['content-pipeline'],
    'shelf-exec-brief': ['exec-brief'],
    'shelf-hormozi': ['hormozi'],
    'shelf-writing-style': ['writing-style'],
}
IGNORE = ('__pycache__', '*.pyc', '.DS_Store')


def differences(source, copy):
    """Return a list of paths that differ between the two trees. Empty means identical."""
    if not copy.is_dir():
        return ['(missing copy) ' + copy.name]
    found = []
    cmp = filecmp.dircmp(source, copy, ignore=['__pycache__', '.DS_Store'])
    found += [str(Path(source.name) / n) + ' (only in source)' for n in cmp.left_only]
    found += [str(Path(copy.name) / n) + ' (only in copy)' for n in cmp.right_only]
    for name in cmp.common_files:
        if (source / name).read_bytes() != (copy / name).read_bytes():
            found.append(str(Path(source.name) / name) + ' (bytes differ)')
    for name in cmp.common_dirs:
        found += differences(source / name, copy / name)
    return found


def main(argv):
    check = '--check' in argv
    wanted = [a for a in argv if not a.startswith('--')] or list(PACKS)
    unknown = [w for w in wanted if w not in PACKS]
    if unknown:
        print('Unknown pack: ' + ', '.join(unknown) + '. Known: ' + ', '.join(PACKS), file=sys.stderr)
        return 2
    drift = 0
    for pack in wanted:
        for skill in PACKS[pack]:
            source = ROOT / 'skills' / skill
            copy = ROOT / 'plugins' / pack / 'skills' / skill
            if not (source / 'SKILL.md').is_file():
                print('FAIL %s: skills/%s/SKILL.md not found' % (pack, skill), file=sys.stderr)
                return 2
            diff = differences(source, copy)
            if check:
                if diff:
                    drift += 1
                    print('DRIFT %s/%s: %s' % (pack, skill, '; '.join(diff)))
                else:
                    print('ok    %s/%s' % (pack, skill))
                continue
            if copy.is_symlink():
                copy.unlink()
            elif copy.exists():
                shutil.rmtree(copy)
            shutil.copytree(source, copy, ignore=shutil.ignore_patterns(*IGNORE), symlinks=False)
            print('copied %s/%s%s' % (pack, skill, ' (already identical)' if not diff else ''))
    return 1 if drift else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
