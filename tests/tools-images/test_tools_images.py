"""Unit tests for tools-images. No network and no credits."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-images'
sys.path.insert(0, str(PACK))

from tools_images import cli, prompts  # noqa: E402


class Check(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(prompts.check_video(prompts.SAMPLE, 10), [])

    def test_gaps_target_hype_signature_and_sections(self):
        bad = prompts.SAMPLE.replace('SHOT 3 (0:05', 'SHOT 3 (0:06').replace('morning light', 'stunning morning light')
        text = ' '.join(prompts.check_video(bad, 15))
        self.assertIn('gap or overlap', text)
        self.assertIn('target is 15', text)
        self.assertIn('"stunning"', text)
        no_sig = prompts.SAMPLE.replace('(SIGNATURE VISUAL EFFECT)', '')
        self.assertTrue(any('SIGNATURE' in p for p in prompts.check_video(no_sig)))
        self.assertTrue(any('Missing section' in p for p in prompts.check_video(prompts.SAMPLE.replace('ENERGY ARC', 'ENDING'))))
        self.assertTrue(any('No shots' in p for p in prompts.check_video('nothing here')))

    def test_effect_line_and_shot_count(self):
        no_effect = prompts.SAMPLE.replace('• EFFECT: match cut\n', '')
        self.assertTrue(any('SHOT 3 has no' in p for p in prompts.check_video(no_effect)))
        two = 'SHOT 1 (0:00-0:05) — a\n• EFFECT: x\nSHOT 2 (0:05-0:10) — b\n• EFFECT: y SIGNATURE\n' \
              'MASTER EFFECTS INVENTORY\nEFFECTS DENSITY MAP\nENERGY ARC\nSHOT-BY-SHOT EFFECTS TIMELINE'
        self.assertTrue(any('Aim for 4 to 7' in p for p in prompts.check_video(two)))


class Log(unittest.TestCase):
    def test_manifest_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp, 'p_v1.txt')
            prompt.write_text('x')
            prompts.log(tmp, prompt, 'm1', 'j1')
            prompts.log(tmp, prompt, 'm2')
            rows = [json.loads(l) for l in Path(tmp, 'manifest_v1.jsonl').read_text().splitlines()]
            self.assertEqual([r['model'] for r in rows], ['m1', 'm2'])
            self.assertEqual(len(rows[0]['prompt_sha256']), 64)


class Cli(unittest.TestCase):
    def test_skills_detection(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertFalse(cli.skills_installed(home))
            path = Path(home, '.agents/skills/higgsfield-generate')
            path.mkdir(parents=True)
            (path / 'SKILL.md').write_text('x')
            self.assertTrue(cli.skills_installed(home))

    def test_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-images'), *a],
                                            env=dict(os.environ, HOME=tmp, PATH='/usr/bin:/bin'), capture_output=True, text=True)
            self.assertEqual(run('doctor').returncode, 2)
            self.assertEqual(run('sample', tmp).returncode, 0)
            self.assertEqual(run('check', tmp + '/northwind-cake_video-prompt_v1.txt', '--seconds', '10').returncode, 0)
            self.assertEqual(run('check', tmp + '/northwind-cake_video-prompt_v1.txt', '--seconds', '20').returncode, 1)
            self.assertEqual(run('log', tmp + '/out', '--prompt', tmp + '/northwind-cake_video-prompt_v1.txt', '--model', 'm').returncode, 0)


if __name__ == '__main__':
    unittest.main()
