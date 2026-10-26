"""Unit tests for tools-narration. No network: ElevenLabs is replaced by fakes."""
import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-narration'
sys.path.insert(0, str(PACK))

from tools_narration import cli, eleven, narration  # noqa: E402


def alignment_for(script, gap_at=(), per=0.05, gap=0.6):
    starts, ends, t = [], [], 0.0
    for i, ch in enumerate(script):
        if i in gap_at:
            t += gap
        starts.append(round(t, 3))
        ends.append(round(t + per * 0.9, 3))
        t += per
    return {'characters': list(script), 'character_start_times_seconds': starts, 'character_end_times_seconds': ends}


class Script(unittest.TestCase):
    def test_load_and_join(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 's.json'
            path.write_text(json.dumps([{'notes': ['One  two.', 'Three.']}, {'notes': 'Four.'}]))
            slides = narration.load_slides(path)
            self.assertEqual(slides, ['One two. Three.', 'Four.'])
            script, spans = narration.join(slides)
            self.assertEqual(script, 'One two. Three.\n\nFour.')
            self.assertEqual([script[a:b] for a, b in spans], slides)
            path.write_text(json.dumps([{'notes': []}]))
            with self.assertRaises(narration.NarrationError):
                narration.load_slides(path)
        with self.assertRaises(narration.NarrationError):
            narration.join(['x' * 9600])

    def test_boundaries_cut_in_the_gap(self):
        script, spans = narration.join(['Hello there.', 'Second slide.', 'Third.'])
        al = alignment_for(script, gap_at=(spans[1][0], spans[2][0]))
        cuts = narration.boundaries(al, spans, 3.0)
        self.assertEqual(len(cuts), 4)
        last = spans[0][1] - 1
        first = spans[1][0]
        self.assertGreater(cuts[1], al['character_end_times_seconds'][last])
        self.assertLess(cuts[1], al['character_start_times_seconds'][first])

    def test_bad_alignment_refused(self):
        script, spans = narration.join(['A b.', 'C d.'])
        with self.assertRaises(narration.NarrationError):
            narration.boundaries({'characters': []}, spans, 2)
        short = alignment_for(script[:3])
        with self.assertRaises(narration.NarrationError):
            narration.boundaries(short, spans, 2)
        overlap = alignment_for(script)
        overlap['character_start_times_seconds'][spans[1][0]] = 0.0
        with self.assertRaises(narration.NarrationError):
            narration.boundaries(overlap, spans, 2)


class Api(unittest.TestCase):
    def test_voice_id_required_and_key_message(self):
        with self.assertRaises(eleven.ElevenError):
            eleven.voice_id(None, env={'HOME': '/nonexistent'})
        self.assertEqual(eleven.voice_id('abc'), 'abc')
        self.assertEqual(eleven.voice_id(None, env={'ELEVENLABS_VOICE_ID': 'v1'}), 'v1')
        self.assertEqual(eleven.voice_id(None, env={'CLAUDE_PLUGIN_OPTION_VOICE_ID': 'v2'}), 'v2')

    def test_speech_request_shape(self):
        seen = {}

        def fake(method, path, key, body=None, headers=None):
            seen.update(method=method, path=path, body=body)
            return {'audio_base64': base64.b64encode(b'ID3').decode(), 'alignment': {}}
        eleven.speech_with_timings('k', 'voice 1', 'Hi', 'm', {'stability': 0.5}, send=fake)
        self.assertEqual(seen['method'], 'POST')
        self.assertIn('/text-to-speech/voice%201/with-timestamps', seen['path'])
        self.assertEqual(seen['body']['model_id'], 'm')

    def test_clone_multipart(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = Path(tmp) / 'me.mp3'
            rec.write_bytes(b'abc')
            seen = {}

            def fake(method, path, key, body=None, headers=None):
                seen.update(path=path, body=body, headers=headers)
                return {'voice_id': 'new1'}
            self.assertEqual(eleven.clone('k', 'Me', [rec], send=fake), 'new1')
            self.assertEqual(seen['path'], '/voices/add')
            self.assertIn(b'filename="me.mp3"', seen['body'])
            self.assertIn('multipart/form-data; boundary=', seen['headers']['Content-Type'])

    def test_voices_filter(self):
        fake = lambda m, p, k, body=None, headers=None: {'voices': [{'voice_id': '1', 'name': 'Sam clone'}, {'voice_id': '2', 'name': 'Other'}]}
        self.assertEqual([v['id'] for v in eleven.voices('k', 'sam', send=fake)], ['1'])


class Cli(unittest.TestCase):
    def run_bin(self, *a, home):
        env = {k: v for k, v in os.environ.items() if 'ELEVENLABS' not in k}
        env['HOME'] = home
        return subprocess.run([sys.executable, str(PACK / 'bin/tools-narration'), *map(str, a)], env=env, capture_output=True, text=True)

    def test_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_bin('clone', 'Me', 'x.mp3', home=tmp).returncode, 1)
            Path(tmp, 's.json').write_text(json.dumps(cli.SAMPLE_SLIDES))
            self.assertEqual(self.run_bin('narrate', Path(tmp, 's.json'), '--out', Path(tmp, 'n'), home=tmp).returncode, 1)
            self.assertEqual(self.run_bin('plan', Path(tmp, 's.json'), '--out', Path(tmp, 'p.txt'), home=tmp).returncode, 0)

    @unittest.skipUnless(narration.ffmpeg_ok(), 'ffmpeg not installed')
    def test_sample_and_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_bin('sample', tmp, home=tmp).returncode, 0)
            out = self.run_bin('split', '--slides', Path(tmp, 'slides.json'), '--take', Path(tmp, 'take.mp3'),
                               '--alignment', Path(tmp, 'alignment.json'), '--out', Path(tmp, 'clips_v1'), home=tmp)
            self.assertEqual(out.returncode, 0, out.stderr)
            manifest = json.loads(Path(tmp, 'clips_v1/manifest_v1.json').read_text())
            self.assertEqual(len(manifest['tracks']), 3)
            for a, b in zip(manifest['tracks'], manifest['tracks'][1:]):
                self.assertEqual(a['end'], b['start'])
            self.assertFalse(Path(tmp, 'clips_v1/master.wav').exists())
            self.assertEqual(self.run_bin('split', '--slides', Path(tmp, 'slides.json'), '--take', Path(tmp, 'take.mp3'),
                                          '--alignment', Path(tmp, 'alignment.json'), '--out', Path(tmp, 'clips_v1'), home=tmp).returncode, 1)


if __name__ == '__main__':
    unittest.main()
