"""Unit and end-to-end tests for the shelf-video pack. Run: python3 -m unittest discover -s tests/shelf-video"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plugins/shelf-video'))
from shelf_video import captions, core, plan, render, settings, transcribe  # noqa: E402
from shelf_video.cli import main  # noqa: E402

MEDIA = {'width': 640, 'height': 360, 'fps': '25/1', 'duration': 10.0, 'audio_channels': 1, 'audio_rate': 48000}


def w(i, text, start, end):
    return {'id': i, 'text': text, 'word': transcribe.norm(text), 'start': start, 'end': end, 'p': 1.0}


WORDS = [w(0, 'Hello,', 1.0, 1.4), w(1, 'um,', 1.6, 1.9), w(2, 'this', 2.1, 2.3), w(3, 'is', 2.35, 2.5),
         w(4, 'the', 2.55, 2.7), w(5, 'the', 2.8, 2.95), w(6, 'plan.', 3.0, 3.4), w(7, 'You', 5.0, 5.2),
         w(8, 'know', 5.25, 5.5), w(9, 'it', 5.6, 5.7), w(10, 'works.', 5.75, 6.2)]


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='shelf-video-test-')
        self.dir = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {'AIOS_CONFIG_DIR': str(self.dir / 'config'), 'HOME': str(self.dir)})
        self.env.start()
        self.cfg = settings.load()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()


class TranscriptTests(unittest.TestCase):
    def test_openai_whisper_json(self):
        data = {'segments': [{'words': [{'word': ' Um,', 'start': 0.0, 'end': 0.3, 'probability': 0.8},
                                        {'word': ' hello', 'start': 0.4, 'end': 0.8, 'probability': 0.9}]}]}
        words = transcribe.normalise(data)
        self.assertEqual([x['word'] for x in words], ['um', 'hello'])
        self.assertEqual(words[1]['id'], 1)

    def test_whisper_cpp_tokens_join_into_words(self):
        data = {'transcription': [{'tokens': [
            {'text': '[_BEG_]', 'offsets': {'from': 0, 'to': 0}},
            {'text': ' Hel', 'offsets': {'from': 0, 'to': 200}, 'p': 0.9},
            {'text': 'lo', 'offsets': {'from': 200, 'to': 400}, 'p': 0.9},
            {'text': ',', 'offsets': {'from': 400, 'to': 410}, 'p': 0.9},
            {'text': ' uh', 'offsets': {'from': 600, 'to': 800}, 'p': 0.7}]}]}
        words = transcribe.normalise(data)
        self.assertEqual([x['text'] for x in words], ['Hello,', 'uh'])
        self.assertAlmostEqual(words[1]['start'], 0.6)

    def test_unknown_json_is_refused(self):
        with self.assertRaises(core.ShelfError):
            transcribe.normalise({'text': 'no timings'})

    def test_empty_words_refused(self):
        with self.assertRaises(core.ShelfError):
            transcribe.normalise({'segments': [{'words': []}]})


class PlanTests(Sandbox):
    def cuts(self):
        return plan.propose(WORDS, MEDIA, self.cfg)

    def test_filler_selected_and_soft_filler_not(self):
        cuts = self.cuts()
        filler = [c for c in cuts if 'filler' in c['kind'].split('+')]
        soft = [c for c in cuts if 'soft-filler' in c['kind']]
        self.assertTrue(filler and all(c['selected'] for c in filler))
        self.assertTrue(filler[0]['start'] <= 1.6 and filler[0]['end'] >= 1.9)
        self.assertTrue(soft and not any(c['selected'] for c in soft))

    def test_stutter_proposed_not_selected(self):
        stutter = [c for c in self.cuts() if 'stutter' in c['kind']]
        self.assertEqual(len(stutter), 1)
        self.assertFalse(stutter[0]['selected'])

    def test_long_pause_tightened_to_keep_pause(self):
        pause = [c for c in self.cuts() if c['kind'] == 'pause']
        self.assertEqual(len(pause), 1)
        remaining = (5.0 - 3.4) - (pause[0]['end'] - pause[0]['start'])
        self.assertAlmostEqual(remaining, self.cfg['keep_pause'], delta=0.05)

    def test_lead_and_tail_trimmed(self):
        kinds = [c['kind'] for c in self.cuts()]
        self.assertIn('lead', kinds)
        self.assertIn('tail', kinds)

    def test_cuts_snap_to_frames_and_are_numbered(self):
        cuts = self.cuts()
        for n, c in enumerate(cuts, 1):
            self.assertEqual(c['id'], n)
            self.assertAlmostEqual(c['start'] * 25, round(c['start'] * 25), places=3)
            self.assertAlmostEqual(c['end'] * 25, round(c['end'] * 25), places=3)

    def test_ranges_segments_and_timeline_map(self):
        removals = plan.selected_ranges([{'start': 1, 'end': 2, 'selected': True},
                                         {'start': 1.5, 'end': 3, 'selected': True},
                                         {'start': 5, 'end': 6, 'selected': False}])
        self.assertEqual(removals, [(1, 3)])
        self.assertEqual(plan.keep_segments(removals, 10.0), [(0.0, 1), (3, 10.0)])
        self.assertEqual(plan.to_output(4.0, removals), 2.0)
        self.assertEqual(plan.to_output(2.0, removals), 1.0)
        self.assertEqual(plan.to_output(0.5, removals), 0.5)

    def test_summary_counts(self):
        s = plan.summary(self.cuts(), 10.0)
        self.assertGreater(s['seconds_removed'], 0)
        self.assertAlmostEqual(s['new_duration'], 10.0 - s['seconds_removed'], places=2)


class CaptionTests(Sandbox):
    def test_kept_words_tidy_punctuation_and_capitals(self):
        words = [w(0, 'show', 0, 0.3), w(1, 'you,', 0.35, 0.6), w(2, 'uh,', 0.8, 1.0), w(3, 'how', 1.2, 1.4),
                 w(4, 'Erm,', 2.0, 2.3), w(5, 'the', 2.5, 2.7)]
        kept = captions.kept_words(words, [(0.7, 1.1), (1.9, 2.4)])
        self.assertEqual([x['text'] for x in kept], ['show', 'you', 'how', 'The'])
        self.assertAlmostEqual(kept[2]['start'], 0.8, places=3)

    def test_cues_respect_limits_and_sentences(self):
        words = [w(i, t, i * 0.4, i * 0.4 + 0.3) for i, t in enumerate(
            'One two three. Four five six seven eight nine ten eleven twelve thirteen.'.split())]
        cues = captions.build_cues(words, max_chars=20, max_seconds=3.0)
        self.assertEqual(cues[0]['text'], 'One two three.')
        self.assertTrue(all(len(c['text']) <= 20 for c in cues))
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a['end'], b['start'])

    def test_srt_round_trip(self):
        cues = [{'start': 0.0, 'end': 1.25, 'text': 'Hello there.'}, {'start': 3661.5, 'end': 3662.0, 'text': 'Late'}]
        text = captions.srt(cues)
        self.assertIn('01:01:01,500 --> 01:01:02,000', text)
        self.assertEqual(captions.parse_srt(text), cues)

    def test_colour_parsing(self):
        self.assertEqual(captions.colour('#FFFFFF'), (255, 255, 255, 255))
        self.assertEqual(captions.colour('000000B8'), (0, 0, 0, 184))
        with self.assertRaises(core.ShelfError):
            captions.colour('#FFF')

    def test_caption_sits_at_least_90px_above_bottom(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest('Pillow not installed')
        image, box = captions.draw_cue('Hello from Acme Studio', 1920, 1080, self.cfg['caption'])
        self.assertLessEqual(box['bottom'], 1080 - 90)
        self.assertEqual(image.size, (1920, 1080))


class SettingsTests(Sandbox):
    def test_defaults_without_file(self):
        self.assertEqual(settings.load()['keep_pause'], 0.3)
        self.assertFalse(settings.path().exists())

    def test_set_values_with_types(self):
        settings.set_value('caption.colour', '#FFD400')
        settings.set_value('max_pause', '0.8')
        settings.set_value('export.loudnorm', 'true')
        settings.set_value('fillers', 'um, uh')
        data = settings.load()
        self.assertEqual(data['caption']['colour'], '#FFD400')
        self.assertEqual(data['max_pause'], 0.8)
        self.assertIs(data['export']['loudnorm'], True)
        self.assertEqual(data['fillers'], ['um', 'uh'])
        self.assertTrue(str(settings.path()).startswith(str(self.dir)))

    def test_unknown_key_refused(self):
        with self.assertRaises(ValueError):
            settings.set_value('caption.sparkle', '1')


class ApprovalTests(Sandbox):
    def make_plan(self):
        root = self.dir / 'proj'
        (root / 'plans').mkdir(parents=True)
        cuts = plan.propose(WORDS, MEDIA, self.cfg)
        file = root / 'plans' / 'plan_v1.json'
        core.write(file, {'media': MEDIA, 'cuts': cuts})
        return root, file, cuts

    def test_approval_needs_member_yes(self):
        root, file, _ = self.make_plan()
        with self.assertRaises(core.ShelfError):
            render.approve(root, file)

    def test_drop_add_and_manual_ranges(self):
        root, file, cuts = self.make_plan()
        soft = [c['id'] for c in cuts if not c['selected']][0]
        target, record = render.approve(root, file, drop=[1], add=[soft], remove=['8.0:8.5'], confirmed=True)
        by_id = {c['id']: c for c in record['cuts']}
        self.assertFalse(by_id[1]['selected'])
        self.assertTrue(by_id[soft]['selected'])
        self.assertEqual(record['cuts'][-1]['kind'], 'manual')
        self.assertEqual(target.name, 'approval_v1.json')

    def test_bad_ids_and_ranges_refused(self):
        root, file, _ = self.make_plan()
        with self.assertRaises(core.ShelfError):
            render.approve(root, file, drop=[999], confirmed=True)
        with self.assertRaises(core.ShelfError):
            render.approve(root, file, remove=['9:30'], confirmed=True)

    def test_hand_edited_approval_refused(self):
        root, file, _ = self.make_plan()
        target, record = render.approve(root, file, confirmed=True)
        record['cuts'][0]['selected'] = not record['cuts'][0]['selected']
        core.write(target, record)
        with self.assertRaises(core.ShelfError):
            render.current_approval(root)

    def test_changed_plan_refused(self):
        root, file, _ = self.make_plan()
        render.approve(root, file, confirmed=True)
        file.write_text(file.read_text().replace('Filler word', 'Edited'))
        with self.assertRaises(core.ShelfError):
            render.current_approval(root)

    def test_versions_increment(self):
        root, file, _ = self.make_plan()
        a, _ = render.approve(root, file, confirmed=True)
        b, _ = render.approve(root, file, confirmed=True)
        self.assertEqual((a.name, b.name), ('approval_v1.json', 'approval_v2.json'))
        self.assertEqual(core.latest(root / 'approvals', 'approval', '.json'), b)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg not installed')
class EndToEndTests(Sandbox):
    def make_clip(self):
        clip = self.dir / 'clip.mp4'
        tone = "aevalsrc='if(between(t,1,3.4)+between(t,5,6.2),0.3*sin(2*PI*440*t),0)':s=48000:d=10"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=10',
                        '-f', 'lavfi', '-i', tone, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                        '-shortest', str(clip)], check=True)
        words = self.dir / 'words.json'
        words.write_text(json.dumps({'segments': [{'words': [
            {'word': ' ' + x['text'], 'start': x['start'], 'end': x['end']} for x in WORDS]}]}))
        return clip, words

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main([str(a) for a in args])
        return code, out.getvalue(), err.getvalue()

    def test_full_run_on_a_generated_clip(self):
        clip, words = self.make_clip()
        project = self.dir / 'clip_EDIT_v1'
        self.assertEqual(self.cli('init', clip, '--project', project)[0], 0)
        self.assertEqual(self.cli('transcribe', '--project', project, '--import-json', words)[0], 0)
        self.assertEqual(self.cli('plan', '--project', project)[0], 0)
        code, _, err = self.cli('render', '--project', project)
        self.assertEqual(code, 1)
        self.assertIn('No approval yet', err)
        self.assertEqual(self.cli('approve', '--project', project)[0], 1)
        self.assertEqual(self.cli('approve', '--project', project, '--yes')[0], 0)
        try:
            import PIL  # noqa: F401
            burn = []
        except ImportError:
            burn = ['--no-burn']
        code, out, err = self.cli('render', '--project', project, *burn)
        self.assertEqual(code, 0, err)
        code, out, err = self.cli('verify', '--project', project)
        self.assertEqual(code, 0, out + err)
        result = core.read(project / 'exports/edit_v1/verify.json')
        self.assertTrue(result['ok'])
        self.assertLess(result['duration'], 10.0)
        srt = (project / 'exports/edit_v1/captions.srt').read_text()
        self.assertIn('Hello', srt)
        self.assertNotIn('um', srt.lower().split())
        self.assertTrue(result['stills'])
        self.assertTrue((Path(clip)).exists(), 'the original must stay in place')

    def test_init_refuses_a_different_recording(self):
        clip, _ = self.make_clip()
        project = self.dir / 'p'
        core.init_project(clip, project)
        other = self.dir / 'other.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=2',
                        '-f', 'lavfi', '-i', 'sine=d=2', '-shortest', str(other)], check=True)
        with self.assertRaises(core.ShelfError):
            core.init_project(other, project)

    def test_silent_video_refused(self):
        silent = self.dir / 'silent.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=1',
                        str(silent)], check=True)
        with self.assertRaises(core.ShelfError):
            core.probe(silent)


class CliTests(Sandbox):
    def test_missing_project_is_a_clean_error(self):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = main(['plan', '--project', str(self.dir / 'nowhere')])
        self.assertEqual(code, 1)
        self.assertIn('No project.json', err.getvalue())

    def test_settings_set_via_cli(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(['settings', 'set', 'caption.max_chars=30']), 0)
        self.assertEqual(settings.load()['caption']['max_chars'], 30)


if __name__ == '__main__':
    unittest.main()
