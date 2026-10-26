"""Unit tests for tools-boards: the scene validator (from our skill) and the practice scenes."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[2] / 'plugins/tools-boards'
sys.path.insert(0, str(PACK))

from tools_boards import cli, validate_scene  # noqa: E402

EXAMPLE = PACK / 'skills/tools-boards/assets/release-workflow.example.json'


class Validator(unittest.TestCase):
    def test_examples_are_clean(self):
        for scene in (json.loads(EXAMPLE.read_text()), cli.SAMPLE):
            report = validate_scene.validate(scene)
            self.assertTrue(report['ready'], report)
            self.assertEqual(report['warnings'], [], report)

    def test_rejects_small_node_and_bad_edge(self):
        report = validate_scene.validate({'nodes': [{'id': 'a', 'label': 'A', 'x': 0, 'y': 0, 'width': 200, 'height': 55}],
                                          'edges': [{'from_id': 'a', 'to_id': 'missing'}]})
        self.assertFalse(report['ready'])
        text = ' '.join(report['errors'])
        self.assertIn('height must be between 60 and 2000', text)
        self.assertIn('missing', text)

    def test_overlap_warning_and_payload_strips_extra_keys(self):
        scene = {'nodes': [{'id': 'one', 'label': 'One', 'x': 0, 'y': 0, 'width': 200, 'height': 80, 'role': 'card'},
                           {'id': 'two', 'label': 'Two', 'x': 40, 'y': 20, 'width': 200, 'height': 80}]}
        self.assertTrue(any('one overlaps two' in w for w in validate_scene.validate(scene)['warnings']))
        payload = validate_scene.mcp_payload(scene)
        self.assertNotIn('role', payload['nodes'][0])


class Runway(unittest.TestCase):
    def test_runway_shape(self):
        scene = cli.runway('T', 'S', [('A', ['x']), ('B', ['y', 'z'])], 'END')
        self.assertEqual(len(scene['edges']), 1)
        self.assertEqual(scene['nodes'][-1]['id'], 'takeaway')
        self.assertEqual(len(cli.SAMPLE['nodes']), 17)
        self.assertEqual(len(cli.SAMPLE['edges']), 4)


class Cli(unittest.TestCase):
    def test_sample_validate_strict_and_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run([sys.executable, str(PACK / 'bin/tools-boards'), *a], env=dict(os.environ, HOME=tmp), capture_output=True, text=True)
            self.assertEqual(run('sample', tmp).returncode, 0)
            out = run('validate', tmp + '/northwind-workshop_scene_v1.json', '--payload', tmp + '/p.json', '--strict')
            self.assertEqual(out.returncode, 0, out.stdout)
            self.assertEqual(set(json.loads(Path(tmp, 'p.json').read_text())), {'nodes', 'edges'})
            bad = Path(tmp, 'bad.json')
            bad.write_text('[]')
            self.assertEqual(run('validate', str(bad)).returncode, 1)

    def test_manifest_has_no_token(self):
        mcp = json.loads((PACK / '.mcp.json').read_text())['mcpServers']['bluplai']
        self.assertEqual(mcp, {'type': 'http', 'url': 'https://mcp.bluplai.com/mcp'})


if __name__ == '__main__':
    unittest.main()
