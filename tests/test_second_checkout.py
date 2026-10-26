"""A second copy of this repository must not block a Codex or Cursor install (found by track A, 26 Oct 2026).

The bb kit clones the repository into ~/.local/share/aios/kit. A member who also clones it by hand and runs
./install.sh there used to stop on "Existing skill preserved". Now the installer names the other copy and the
two ways forward, and --use-this-checkout moves the links here, keeping the old ones in a backup.
"""
import io
import json
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from test_brain import SandboxCase, ROOT
import install_pack as installer


class SecondCheckout(SandboxCase):
    def other_copy(self):
        other = self.home / 'elsewhere' / 'skool-navaigate-install'
        (other / '.claude-plugin').mkdir(parents=True)
        shutil.copy(ROOT / '.claude-plugin/marketplace.json', other / '.claude-plugin/marketplace.json')
        shutil.copytree(ROOT / 'plugins/aios', other / 'plugins/aios', symlinks=True)
        return other

    def link_from(self, other):
        for parent in installer.SKILL_DIRS:
            folder = self.home / parent
            folder.mkdir(parents=True, exist_ok=True)
            for skill in sorted((other / 'plugins/aios/skills').iterdir()):
                (folder / skill.name).symlink_to(skill)
        bin_dir = self.home / '.local/bin'
        bin_dir.mkdir(parents=True, exist_ok=True)
        for tool in sorted((other / 'plugins/aios/bin').iterdir()):
            (bin_dir / tool.name).symlink_to(tool)

    def test_names_the_other_copy_and_changes_nothing(self):
        other = self.other_copy()
        self.link_from(other)
        with self.assertRaisesRegex(ValueError, 'another copy of this repository') as caught:
            installer.install('aios')
        message = str(caught.exception)
        self.assertIn(str(other), message)
        self.assertIn('aios-guide install aios', message)
        self.assertIn('--use-this-checkout', message)
        for parent in installer.SKILL_DIRS:
            self.assertEqual((self.home / parent / 'aios').resolve(), (other / 'plugins/aios/skills/aios').resolve())

    def test_use_this_checkout_moves_links_and_keeps_backups(self):
        other = self.other_copy()
        self.link_from(other)
        with redirect_stdout(io.StringIO()):
            installer.install('aios', use_this_checkout=True)
        for parent in installer.SKILL_DIRS:
            self.assertEqual((self.home / parent / 'aios').resolve(), ROOT / 'plugins/aios/skills/aios')
        backups = list((self.home / '.local/share/aios/checkout-backups').glob('*/*'))
        self.assertTrue(backups)
        self.assertTrue(all(p.is_symlink() and other.resolve() in p.resolve().parents for p in backups))
        self.assertFalse(installer.check('aios', self.home, quiet=True))
        recorded = json.loads((self.home / '.local/share/aios/checkout.json').read_text())
        self.assertEqual(recorded['root'], str(ROOT))

    def test_a_foreign_link_is_still_refused(self):
        foreign = self.home / 'my-own-skill'
        foreign.mkdir()
        (foreign / 'SKILL.md').write_text('---\nname: aios\ndescription: mine\n---\n')
        folder = self.home / '.codex/skills'
        folder.mkdir(parents=True)
        (folder / 'aios').symlink_to(foreign)
        with self.assertRaisesRegex(ValueError, 'Existing skill preserved'):
            installer.install('aios', use_this_checkout=True)
        self.assertEqual((folder / 'aios').resolve(), foreign.resolve())


if __name__ == '__main__':
    unittest.main()
