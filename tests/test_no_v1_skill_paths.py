"""No shipped plugin file points at the first-generation install folder for its own scripts.

A 2.0 install puts a skill in the Claude Code plugin cache, or in ~/.codex/skills, ~/.cursor/skills or ~/.agents/skills.
A path such as `~/.claude/skills/<skill>/scripts/...` exists only after a 1.x `install.sh`, so a skill must name its
scripts as "the scripts/ folder next to this SKILL.md" (and Python must use Path(__file__).resolve().parent).

Rule 1 (no exceptions): no shipped file names a script, reference, template or asset under `.claude/skills/<skill>/`.
Rule 2: no shipped file names `~/.claude/skills/<name>` where <name> is a skill this repo ships under `plugins/`,
because that is where a 1.x install put it, not a 2.0 install. Naming the personal skills folder as a destination the
member chooses (for example `git clone <public skill> ~/.claude/skills/<their name>`) is fine. ALLOWED lists the only
exceptions, each with its reason.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / 'plugins'
SKIP_DIRS = {'node_modules', '__pycache__', '.git', 'results'}

# Built from pieces so this test file does not match its own scan.
HOME_FORMS = r'(~|\$HOME|\$\{HOME\}|__HOME__)'
SKILLS_DIR = r'/\.claude/skill' + 's'
RULE_1 = re.compile(r'\.claude/skill' + r's/[\w.-]+/(scripts|references|templates|assets)/')
RULE_2 = re.compile(HOME_FORMS + SKILLS_DIR + r'/([\w.-]+)')

ALLOWED = {
    # Design Brain's corpus is a separate zip the member downloads and unzips into their own skills folder, where it
    # makes its own design-brain folder. The pack's skill points the member there on purpose.
    'plugins/shelf-design-brain/TOUR.md': 'checks the unzipped corpus',
    'plugins/shelf-design-brain/skills/design-brain/SKILL.md': 'where the member unzips the corpus (1.x copy)',
}


def shipped_skill_names():
    return {d.name for d in PLUGINS.glob('*/skills/*') if d.is_dir()}


def shipped_files():
    for path in sorted(PLUGINS.rglob('*')):
        if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(PLUGINS).parts):
            data = path.read_bytes()
            if b'\0' not in data:
                yield path.relative_to(ROOT).as_posix(), data.decode('utf-8', errors='replace')


class NoFirstGenerationSkillPaths(unittest.TestCase):
    def test_no_script_paths_under_the_v1_install_folder(self):
        hits = [f'{rel}:{n}' for rel, text in shipped_files()
                for n, line in enumerate(text.splitlines(), 1) if RULE_1.search(line)]
        self.assertEqual(hits, [], 'name "the scripts/ folder next to this SKILL.md" instead')

    def test_no_shipped_skill_named_in_the_personal_skills_folder(self):
        names = shipped_skill_names()
        hits = [f'{rel}:{n}' for rel, text in shipped_files() if rel not in ALLOWED
                for n, line in enumerate(text.splitlines(), 1)
                for m in RULE_2.finditer(line) if m.group(2) in names]
        self.assertEqual(hits, [], 'a 2.0 install does not put this skill there')

    def test_every_allowed_file_still_exists_and_still_needs_it(self):
        texts, names = dict(shipped_files()), shipped_skill_names()
        for rel in ALLOWED:
            self.assertIn(rel, texts, rel + ' is gone: drop it from ALLOWED')
            self.assertTrue(any(m.group(2) in names for m in RULE_2.finditer(texts[rel])),
                            rel + ' no longer names a shipped skill there: drop it from ALLOWED')

    def test_the_scan_catches_the_old_forms(self):
        folder = SKILLS_DIR.replace('\\', '')
        old = '~' + folder + '/web-scrape/scripts/webscrape.py'
        self.assertTrue(RULE_1.search(old))
        self.assertEqual(RULE_2.search(old).group(2), 'web-scrape')
        self.assertEqual(RULE_2.search('__HOME__' + folder + '/daily-brief/x').group(2), 'daily-brief')
        self.assertIn('web-scrape', shipped_skill_names())

if __name__ == '__main__':
    unittest.main()
