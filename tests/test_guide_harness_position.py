"""--harness works before or after the aios-guide command (agents put it after)."""
import subprocess
import sys
import unittest
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "plugins" / "aios" / "scripts" / "guide.py"


class HarnessPositionTest(unittest.TestCase):
    def run_guide(self, *args):
        return subprocess.run([sys.executable, str(GUIDE), *args], capture_output=True, text=True)

    def test_harness_after_the_command(self):
        result = self.run_guide("where", "--harness", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_harness_before_the_command(self):
        result = self.run_guide("--harness", "claude", "where")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_value_before_is_kept_when_after_is_absent(self):
        result = self.run_guide("--harness", "codex", "where")
        self.assertIn("Checkout", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
