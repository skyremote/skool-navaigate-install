"""Unit tests for tools-voice. Local only."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-voice'
sys.path.insert(0, str(PACK))

from tools_voice import cli, voice  # noqa: E402


class Check(unittest.TestCase):
    def test_good_passes_bad_fails(self):
        self.assertEqual(voice.check(cli.SAMPLE_GOOD), [])
        problems = voice.check(cli.SAMPLE_BAD)
        self.assertTrue(any('"seamless"' in p for p in problems))
        self.assertTrue(any('fragments' in p for p in problems))

    def test_profile_bans_jargon_dashes_and_stacks(self):
        profile = '## Language to remove\n- synergise\n- <placeholder>\n## Calibration log\n- not a ban\n'
        self.assertEqual(voice.profile_bans(profile), ['synergise'])
        problems = voice.check('We will synergise the moat — fast — now, with a powerful, practical and magical plan.', profile)
        text = ' '.join(problems)
        self.assertIn('your own list', text)
        self.assertIn('jargon', text)
        self.assertIn('long dashes', text)
        self.assertIn('adjective stack', text)

    def test_word_boundaries(self):
        self.assertEqual(voice.check('We spoke about the elevator and the leverage-free plan for robustness checks in our long meeting.'),
                         ['Remove "leverage": it is on the generated-text list.'])

    def test_code_blocks_and_headings_ignored_for_fragments(self):
        self.assertEqual(voice.check('# Title\n```\na. b. c. d.\n```\nSo we ran it on the real data, and it worked first time.'), [])


class Scaffold(unittest.TestCase):
    def test_scaffold_calibrate_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = voice.scaffold('Sam Lee', tmp)
            self.assertEqual(target.name, 'sam-lee-voice')
            self.assertIn('name: sam-lee-voice', (target / 'SKILL.md').read_text())
            with self.assertRaises(voice.VoiceError):
                voice.scaffold('Sam Lee', tmp)
            with self.assertRaises(voice.VoiceError):
                voice.slug('!!!')
            voice.calibrate(target / 'PROFILE.md', 'Not big.', 'nothing like big', 'soften', when='2026-10-26')
            text = (target / 'PROFILE.md').read_text()
            self.assertIn('**2026-10-26**', text)
            self.assertEqual(text.count('## Calibration log'), 1)


class Builder(unittest.TestCase):
    def test_find_builder(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(voice.find_builder({'HOME': tmp}))
            script = Path(tmp) / '.agents/skills/voice-skill-builder/scripts/extract_voice_evidence.py'
            script.parent.mkdir(parents=True)
            script.write_text('')
            self.assertEqual(voice.find_builder({'HOME': tmp}), script.parents[1])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp)
            env.pop('VOICE_SKILL_BUILDER', None)
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-voice'), *a], env=env, capture_output=True, text=True)
            self.assertEqual(run('doctor').returncode, 2)
            self.assertEqual(run('evidence', tmp, '--out', tmp + '/e.md').returncode, 2)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/draft-bad_v1.md').returncode, 1)
            self.assertEqual(run('check', tmp + '/draft-good_v1.md').returncode, 0)
            self.assertEqual(run('new', 'Sam', '--folder', tmp + '/skills').returncode, 0)
            self.assertEqual(run('new', 'Sam', '--folder', tmp + '/skills').returncode, 1)


if __name__ == '__main__':
    unittest.main()
