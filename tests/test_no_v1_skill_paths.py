"""No shipped plugin file points at the first-generation install folder for its own scripts.

A 2.0 install puts a skill in the Claude Code plugin cache, or in ~/.codex/skills, ~/.cursor/skills or ~/.agents/skills.
A path such as `~/.claude/skills/<skill>/scripts/...` exists only after a 1.x `install.sh`, so a skill must name its
scripts as "the scripts/ folder next to this SKILL.md" (and Python must use Path(__file__).resolve().parent).

Rule 1 (no exceptions): no shipped file names a script, reference, template or asset under `.claude/skills/<skill>/`.
Rule 2: no shipped file names the personal skills folder itself (`~/.claude/skills`), except the files listed in
ALLOWED, which name it on purpose as a destination the member chooses, never as the place this pack's code lives.
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
RULE_2 = re.compile(HOME_FORMS + SKILLS_DIR + r'\b')

ALLOWED = {
    # Core packs that teach and manage the member's personal skills folder (Claude Code's documented location).
    'plugins/aios-harnesses/README.md': 'harness setup links shared skills into the personal skills folder',
    'plugins/aios-harnesses/skills/harness-check/SKILL.md': 'checks the personal skills folder',
    'plugins/aios-harnesses/skills/harness-setup/SKILL.md': 'creates links in the personal skills folder',
    'plugins/aios-harnesses/skills/harness-setup/reference.md': 'table of each harness\'s skills folders',
    'plugins/aios-skills/README.md': '`aios-skill new` writes a new skill there by default',
    'plugins/aios-skills/TOUR.md': 'the tour checks the skill the member just created there',
    'plugins/aios-skills/aios_skills/audit.py': 'the audit reads personal skills',
    'plugins/aios-skills/aios_skills/cli.py': 'help text for the default destination',
    'plugins/aios-skills/evals/hide-long-tail/prompt.md': 'an eval prompt in the member\'s words',
    'plugins/aios-skills/skills/new-skill/SKILL.md': 'personal versus project destination',
    'plugins/aios-skills/skills/skill-craft/SKILL.md': 'skillOverrides for personal skills',
    # Design Brain's corpus is a separate zip the member unzips into their own skills folder.
    'plugins/shelf-design-brain/README.md': 'where the member unzips the corpus',
    'plugins/shelf-design-brain/TOUR.md': 'checks the unzipped corpus',
    'plugins/shelf-design-brain/INTEGRATION.md': 'explains where the corpus goes',
    'plugins/shelf-design-brain/skills/design-brain/SKILL.md': 'where the member unzips the corpus (1.x copy)',
}


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

    def test_personal_skills_folder_only_where_allowed(self):
        hits = [f'{rel}:{n}' for rel, text in shipped_files() if rel not in ALLOWED
                for n, line in enumerate(text.splitlines(), 1) if RULE_2.search(line)]
        self.assertEqual(hits, [], 'a 2.0 install does not put this pack there')

    def test_every_allowed_file_still_exists_and_still_needs_it(self):
        texts = dict(shipped_files())
        for rel in ALLOWED:
            self.assertIn(rel, texts, rel + ' is gone: drop it from ALLOWED')
            self.assertRegex(texts[rel], RULE_2, rel + ' no longer names the folder: drop it from ALLOWED')

    def test_the_scan_catches_the_old_forms(self):
        old = '~' + SKILLS_DIR.replace('\\', '') + '/web-scrape/scripts/webscrape.py'
        self.assertTrue(RULE_1.search(old))
        self.assertTrue(RULE_2.search(old))
        self.assertTrue(RULE_2.search('__HOME__' + SKILLS_DIR.replace('\\', '') + '/daily-brief'))


if __name__ == '__main__':
    unittest.main()
