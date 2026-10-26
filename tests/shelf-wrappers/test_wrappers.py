"""Tests for the eleven shelf wrapper packs (shelf-hormozi was dropped: tools-offers ships the Hormozi engine).

Run: python3 -m unittest discover -s tests/shelf-wrappers

The drift guard is the important one: each pack ships a byte-for-byte copy of a first-generation skill, so a change
to skills/<name>/ must be followed by `python3 tests/shelf-wrappers/sync_copies.py`.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import sync_copies  # noqa: E402

PACKS = sync_copies.PACKS
REQUIRED_STEP_LINES = ('- **Do:**', '- **Command:**', '- **They should see:**', '- **Check:**')
# The two privacy scans from the shared brief. One character of each plain word sits in a [bracket] so that this file
# does not match its own scan.
PRIVACY = [
    r'/Users/(sky|daniel|wrightd)', r'dw@navaigat[e]', r'daniel\.wright198[8]', r'libsql:/[/]',
    r'eyJ[A-Za-z0-9_-]{20,}', r'sk-[A-Za-z0-9]{20,}', r'xdIcOt8Sxf0Mov8aWkZ[b]',
    r'124/17[0]', r'DE46431214[5]', r'HRA 453[0]', r'HRB 1300[7]',
    r'DE[0-9]{2} ?[0-9]{4} ?[0-9]{4} ?[0-9]{4} ?[0-9]{4} ?[0-9]{2}',
    r'000026844[1]', r'000026769[8]', r'450018771[3]', r'450017462[3]', r'Amit Pur[i]', r'REQ318008[5]',
    r'Gerhart-Hauptman[n]', r'8505[5]', r'1585670[8]', r'Qont[o]', r'QNTODEB[2]', r'Ingolstad[t]',
    r'Daniel Stephen Anthon[y]', r'Karin Dietric[h]', r'Morell[o]', r'NAVAI[-]', r'Autodes[k]', r'ComX[o]',
    r'Katan[a]', r'Rich Fone[s]', r'Martin Boyl[e]',
]
PRIVACY_RE = [re.compile(p) for p in PRIVACY]


def pack_dir(pack):
    return ROOT / 'plugins' / pack


def text_files(base):
    for path in sorted(base.rglob('*')):
        if path.is_file() and '.git' not in path.parts and '__pycache__' not in path.parts:
            yield path


def read_text_or_none(path):
    data = path.read_bytes()
    if b'\0' in data:
        return None  # binary: grep -I skips it too, and archives are checked by hand
    return data.decode('utf-8', errors='replace')


def frontmatter(text):
    match = re.match(r'---\n(.*?)\n---\n', text, re.S)
    return match.group(1) if match else ''


class CopyTests(unittest.TestCase):
    def test_every_pack_exists(self):
        self.assertEqual(len(PACKS), 11)
        for pack in PACKS:
            self.assertTrue(pack_dir(pack).is_dir(), pack)

    def test_no_separate_hormozi_pack(self):
        """The Hormozi engine ships in tools-offers; a second pack would compete with it."""
        self.assertNotIn('shelf-hormozi', PACKS)
        self.assertFalse(pack_dir('shelf-hormozi').exists())

    def test_skill_copy_matches_source_byte_for_byte(self):
        """The drift guard."""
        for pack, skills in PACKS.items():
            for skill in skills:
                source = ROOT / 'skills' / skill
                copy = pack_dir(pack) / 'skills' / skill
                self.assertTrue((source / 'SKILL.md').is_file(), 'missing 1.x source ' + skill)
                diff = sync_copies.differences(source, copy)
                self.assertEqual(diff, [], '%s/%s has drifted from skills/%s. Run: python3 tests/shelf-wrappers/sync_copies.py'
                                 % (pack, skill, skill))

    def test_pack_carries_exactly_the_listed_skills(self):
        for pack, skills in PACKS.items():
            found = sorted(p.name for p in (pack_dir(pack) / 'skills').iterdir())
            self.assertEqual(found, sorted(skills), pack)

    def test_no_symlinks_anywhere_in_a_pack(self):
        for pack in PACKS:
            for path in pack_dir(pack).rglob('*'):
                self.assertFalse(path.is_symlink(), 'symlink breaks plugin caching: ' + str(path))

    def test_deep_research_carries_the_web_scrape_helper(self):
        helper = pack_dir('shelf-deep-research') / 'skills/web-scrape/scripts/webscrape.py'
        self.assertTrue(helper.is_file())
        self.assertIn('skills/web-scrape/', (pack_dir('shelf-deep-research') / 'skills/deep-research/SKILL.md').read_text())

    def test_skill_files_are_well_formed(self):
        for pack, skills in PACKS.items():
            for skill in skills:
                text = (pack_dir(pack) / 'skills' / skill / 'SKILL.md').read_text()
                self.assertLess(len(text.splitlines()), 500, pack)
                self.assertIn('name: ' + skill, frontmatter(text), pack)
                self.assertIn('description:', frontmatter(text), pack)

    def test_sync_script_check_mode_passes(self):
        result = subprocess.run([sys.executable, str(HERE / 'sync_copies.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_sync_script_repairs_drift_in_a_scratch_copy(self):
        """Run the real script against a scratch tree: break a copy, sync, and it matches again."""
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            (scratch / 'tests/shelf-wrappers').mkdir(parents=True)
            shutil.copy(HERE / 'sync_copies.py', scratch / 'tests/shelf-wrappers/sync_copies.py')
            shutil.copytree(ROOT / 'skills/writing-style', scratch / 'skills/writing-style')
            shutil.copytree(ROOT / 'skills/writing-style', scratch / 'plugins/shelf-writing-style/skills/writing-style')
            script = scratch / 'tests/shelf-wrappers/sync_copies.py'
            target = scratch / 'plugins/shelf-writing-style/skills/writing-style/SKILL.md'
            target.write_text(target.read_text() + '\nlocal edit that must not survive\n')
            (target.parent / 'stray.txt').write_text('stray')
            drifted = subprocess.run([sys.executable, str(script), '--check', 'shelf-writing-style'], capture_output=True, text=True)
            self.assertEqual(drifted.returncode, 1)
            self.assertIn('DRIFT', drifted.stdout)
            fixed = subprocess.run([sys.executable, str(script), 'shelf-writing-style'], capture_output=True, text=True)
            self.assertEqual(fixed.returncode, 0, fixed.stderr)
            self.assertEqual(sync_copies.differences(scratch / 'skills/writing-style', target.parent), [])
            self.assertFalse((target.parent / 'stray.txt').exists())


class ManifestTests(unittest.TestCase):
    def manifest(self, pack):
        return json.loads((pack_dir(pack) / '.claude-plugin/plugin.json').read_text())

    def test_plugin_json_required_fields(self):
        for pack in PACKS:
            data = self.manifest(pack)
            self.assertEqual(data['name'], pack)
            self.assertEqual(data['version'], '2.0.0')
            self.assertTrue(data['description'].strip().endswith('.'), pack)
            self.assertEqual(data['description'].count('. '), 0, pack + ': one sentence')
            self.assertEqual(data['author'], {'name': 'skyremote'})
            self.assertEqual(data['license'], 'MIT')
            self.assertTrue(data['keywords'] and all(isinstance(k, str) for k in data['keywords']), pack)
            self.assertEqual(data['dependencies'], ['aios'])
            self.assertEqual(data['metadata'], {'module': 12})

    def test_user_config_keys_are_sensitive_and_optional(self):
        for pack in PACKS:
            for key, spec in (self.manifest(pack).get('userConfig') or {}).items():
                self.assertIs(spec.get('sensitive'), True, pack + ' ' + key)
                self.assertIs(spec.get('required'), False, pack + ' ' + key)
                self.assertEqual(spec.get('type'), 'string')
                self.assertNotRegex(json.dumps(spec), r'sk-|eyJ')

    def test_packs_that_call_paid_apis_declare_their_keys(self):
        expect = {'shelf-deep-research': {'exa_api_key', 'firecrawl_api_key'},
                  'shelf-web-scrape': {'exa_api_key', 'firecrawl_api_key'},
                  'shelf-transcripts': {'supadata_api_key'},
                  'shelf-podcasts': {'exa_api_key', 'firecrawl_api_key', 'supadata_api_key'},
                  'shelf-thumbnails': {'gemini_api_key'}}
        for pack, keys in expect.items():
            self.assertEqual(set(self.manifest(pack)['userConfig']), keys, pack)
        for pack in set(PACKS) - set(expect) - {'shelf-daily-brief'}:
            self.assertNotIn('userConfig', self.manifest(pack), pack)

    def test_marketplace_entry_matches_manifest(self):
        for pack in PACKS:
            data = self.manifest(pack)
            entry = json.loads((pack_dir(pack) / 'MARKETPLACE_ENTRY.json').read_text())
            self.assertEqual(entry['name'], data['name'])
            self.assertEqual(entry['version'], data['version'])
            self.assertEqual(entry['source'], './plugins/' + pack)
            self.assertTrue(entry['description'])
            self.assertEqual(set(entry), {'name', 'source', 'version', 'description'}, pack)

    def test_entries_are_not_yet_in_the_shared_marketplace_or_are_identical(self):
        shared = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        by_name = {p['name']: p for p in shared['plugins']}
        for pack in PACKS:
            if pack in by_name:
                entry = json.loads((pack_dir(pack) / 'MARKETPLACE_ENTRY.json').read_text())
                self.assertEqual(by_name[pack]['version'], entry['version'], pack)
                self.assertEqual(by_name[pack]['source'], entry['source'], pack)


class DocumentTests(unittest.TestCase):
    def test_prompts_have_two_or_three_prompts(self):
        for pack in PACKS:
            text = (pack_dir(pack) / 'prompts.md').read_text()
            headings = re.findall(r'^## Prompt \d+', text, re.M)
            self.assertIn(len(headings), (2, 3), pack)
            blocks = re.findall(r'^```text\n(.+?)\n```', text, re.M | re.S)
            self.assertEqual(len(blocks), len(headings), pack + ': one fenced text block per prompt')
            for block in blocks:
                self.assertGreater(len(block.split()), 12, pack + ': a prompt is a real request, not a stub')

    def test_prompts_use_fictional_data(self):
        for pack in PACKS:
            text = (pack_dir(pack) / 'prompts.md').read_text()
            self.assertRegex(text, r'Acme Studio|Northwind Bakery', pack)

    def test_readme_has_both_install_routes_and_keys(self):
        for pack in PACKS:
            text = (pack_dir(pack) / 'README.md').read_text()
            self.assertIn('/aios install ' + pack, text)
            self.assertIn('/plugin install %s@navaigate-aios' % pack, text)
            self.assertIn('./install.sh ' + pack, text)
            self.assertIn('## Keys', text)

    def test_tour_steps_follow_the_house_format(self):
        for pack in PACKS:
            text = (pack_dir(pack) / 'TOUR.md').read_text()
            steps = re.split(r'^## Step \d+: ', text, flags=re.M)[1:]
            self.assertGreaterEqual(len(steps), 2, pack)
            last = steps[-1].split('## Recap')[0]
            for step in steps[:-1] + [last]:
                for line in REQUIRED_STEP_LINES:
                    self.assertIn(line, step, pack)
            self.assertIn('## Recap', text)

    def test_integration_notes_name_source_copy_sync_and_marketplace_line(self):
        for pack, skills in PACKS.items():
            text = (pack_dir(pack) / 'INTEGRATION.md').read_text()
            for skill in skills:
                self.assertIn('skills/%s/' % skill, text)
            self.assertIn('byte-for-byte copy', text)
            self.assertIn('sync_copies.py', text)
            self.assertIn('"name": "%s"' % pack, text)
            self.assertIn('Marketplace line to add', text)

    def test_evals_are_three_cases_with_a_skill_fired_indicator(self):
        for pack, skills in PACKS.items():
            cases = sorted(p for p in (pack_dir(pack) / 'evals').iterdir() if p.is_dir() and p.name != 'results')
            self.assertEqual(len(cases), 3, pack)
            for case in cases:
                prompt = (case / 'prompt.md').read_text()
                self.assertIn('plugins: ["../..", "../../../aios"]', prompt)
                graders = sorted((case / 'graders').glob('*.md'))
                self.assertGreaterEqual(len(graders), 2, case)
                fired = (case / 'graders/skill-fired.md').read_text()
                self.assertIn('type: tool_used', fired)
                self.assertIn(skills[0], fired)


class PrivacyTests(unittest.TestCase):
    def scan(self, bases):
        hits = []
        for base in bases:
            for path in text_files(base):
                text = read_text_or_none(path)
                if text is None:
                    continue
                for number, line in enumerate(text.splitlines(), 1):
                    for pattern in PRIVACY_RE:
                        if pattern.search(line):
                            hits.append('%s:%d: %s' % (os.path.relpath(path, ROOT), number, pattern.pattern))
        return hits

    def test_no_private_data_in_packs_or_tests(self):
        bases = [pack_dir(p) for p in PACKS] + [HERE]
        self.assertEqual(self.scan(bases), [])

    def test_the_scan_can_actually_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / 'note.md'
            sample.write_text('see /Users/' + 'sky/Documents and Auto' + 'desk\n')
            self.assertEqual(len(self.scan([Path(tmp)])), 2)

    def test_no_archives_or_images_that_could_hide_data(self):
        for pack in PACKS:
            icon = pack_dir(pack) / '.claude-plugin/icon.png'
            for path in pack_dir(pack).rglob('*'):
                if path == icon:
                    continue
                self.assertNotIn(path.suffix.lower(), ('.zip', '.docx', '.pptx', '.xlsx', '.jpeg', '.jpg', '.png'), str(path))

    def test_icon_is_a_plain_512_square_png_with_no_metadata(self):
        for pack in PACKS:
            data = (pack_dir(pack) / '.claude-plugin/icon.png').read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n', pack)
            self.assertEqual(int.from_bytes(data[16:20], 'big'), 512, pack)
            self.assertEqual(int.from_bytes(data[20:24], 'big'), 512, pack)
            self.assertLess(len(data), 20000, pack)
            for chunk in (b'tEXt', b'iTXt', b'zTXt', b'eXIf'):
                self.assertNotIn(chunk, data, pack + ' carries metadata')


class InstallerTests(unittest.TestCase):
    """Several packs carry web-scrape. Codex and Cursor link skills by name, so the installer accepts a byte-identical
    copy that another pack already linked (merged into scripts/install_pack.py on aios2/shelf-v2)."""

    PACKS_USED = ('aios', 'shelf-web-scrape', 'shelf-deep-research', 'shelf-transcripts')

    def make_checkout(self, tmp, patched):
        checkout = Path(tmp) / 'checkout'
        (checkout / 'scripts').mkdir(parents=True)
        (checkout / 'skills').mkdir()
        shutil.copy(ROOT / 'scripts/install_pack.py', checkout / 'scripts/install_pack.py')
        for pack in self.PACKS_USED:
            shutil.copytree(ROOT / 'plugins' / pack, checkout / 'plugins' / pack, ignore=shutil.ignore_patterns('evals', '__pycache__'))
        return checkout

    def run_installer(self, checkout, home, *args):
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / '.codex'))
        return subprocess.run([sys.executable, str(checkout / 'scripts/install_pack.py'), *args], env=env, capture_output=True, text=True)

    def test_the_installer_has_the_shared_copy_change(self):
        self.assertIn('def shared_copy', (ROOT / 'scripts/install_pack.py').read_text())

    def test_patched_installer_installs_all_packs_that_share_web_scrape(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout, home = self.make_checkout(tmp, patched=True), Path(tmp) / 'home'
            for pack in ('shelf-web-scrape', 'shelf-deep-research', 'shelf-transcripts'):
                result = self.run_installer(checkout, home, pack)
                self.assertEqual(result.returncode, 0, pack + ': ' + result.stderr)
                self.assertEqual(self.run_installer(checkout, home, pack, '--check').returncode, 0, pack)
            for harness in ('.codex', '.cursor', '.agents'):
                link = home / harness / 'skills/web-scrape'
                self.assertTrue(link.is_symlink())
                self.assertTrue((link / 'scripts/webscrape.py').is_file())
                self.assertTrue((home / harness / 'skills/deep-research/SKILL.md').is_file())
                self.assertTrue((home / harness / 'skills/transcripts/SKILL.md').is_file())

    def test_patched_installer_still_refuses_a_different_skill_with_the_same_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout, home = self.make_checkout(tmp, patched=True), Path(tmp) / 'home'
            elsewhere = Path(tmp) / 'elsewhere/web-scrape'
            elsewhere.mkdir(parents=True)
            (elsewhere / 'SKILL.md').write_text('---\nname: web-scrape\ndescription: someone else\n---\n')
            (home / '.codex/skills').mkdir(parents=True)
            (home / '.codex/skills/web-scrape').symlink_to(elsewhere)
            result = self.run_installer(checkout, home, 'shelf-web-scrape')
            self.assertEqual(result.returncode, 1)
            self.assertIn('Existing skill preserved', result.stderr)


if __name__ == '__main__':
    unittest.main()
