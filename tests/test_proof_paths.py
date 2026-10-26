import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from proof_paths import portable


class PortableProofTests(unittest.TestCase):
    def test_proof_output_uses_placeholders_for_checkout_and_member_home(self):
        self.assertEqual(portable(str(ROOT)+'/plugins/aios'),'<worktree>/plugins/aios')
        self.assertEqual(portable('/Users/'+'recording-member/private.txt'),'$HOME/private.txt')
