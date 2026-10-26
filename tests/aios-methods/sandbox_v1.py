#!/usr/bin/env python3
"""Sandbox proof for aios-methods: install, then run one feature through interview files, a worktree and a loop file."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sandbox_lib_v1 import main  # noqa: E402


def use(box):
    site = box.home / 'acme-site'
    site.mkdir()
    box.note('## 4. First use: one feature, start to finish (Codex/Cursor path, ~/.local/bin/aios-methods)')
    box.run('git init -q && echo "# Acme Studio site" > README.md && git add . && git commit -qm start && git log --oneline', cwd=site)
    box.run('aios-methods glossary init', cwd=site)
    box.run('aios-methods glossary add "Client" "a business that pays Acme Studio" --avoid "customer, account"', cwd=site)
    box.run('aios-methods glossary add "Invoice" "one bill to one client for one month" --avoid "bill, statement"', cwd=site)
    box.run('aios-methods glossary check', cwd=site)
    box.run('aios-methods spec new invoice-export', cwd=site)
    box.run('aios-methods spec check docs/specs/invoice-export.md', cwd=site, expect=1,
            show='aios-methods spec check docs/specs/invoice-export.md   # the empty template fails')
    spec = site / 'docs/specs/invoice-export.md'
    spec.write_text('# Invoice export\n\n## Goal\nExport one month of invoices as a CSV file.\n\n## Who it is for\nThe studio owner, on a laptop.\n\n'
                    '## Done when\n- [ ] `python3 -m unittest test_export.py`\n\n## Out of scope\nEmailing the file.\n\n'
                    '## Decisions\n- CSV, one row per invoice.\n\n## Open questions\n- None\n')
    box.run('cat docs/specs/invoice-export.md', cwd=site, show='cat docs/specs/invoice-export.md   # filled in from the interview answers')
    box.run('aios-methods spec check docs/specs/invoice-export.md', cwd=site)
    box.run('git add . && git commit -qm "Spec and glossary for invoice export" && git log --oneline', cwd=site)
    box.run('aios-methods worktree new invoice-export', cwd=site)
    box.run('aios-methods worktree list', cwd=site)
    tree = box.home / 'acme-site-invoice-export'
    box.run('aios-methods loop init', cwd=tree)
    box.run('cat .claude/loop.md', cwd=tree)
    (tree / 'export.py').write_text('def rows(invoices):\n    return [[i["client"], i["total"]] for i in invoices]\n')
    (tree / 'test_export.py').write_text('import unittest\nfrom export import rows\n\n\nclass T(unittest.TestCase):\n'
                                         '    def test_rows(self):\n        self.assertEqual(rows([{"client": "Acme", "total": 120}]), [["Acme", 120]])\n')
    box.run('python3 -m unittest test_export.py', cwd=tree, show='python3 -m unittest test_export.py   # the spec\'s check, as one loop run would do')
    box.run('git add . && git commit -qm "Invoice export" && git log --oneline', cwd=tree)
    box.run('aios-methods worktree done invoice-export', cwd=site, expect=2,
            show='aios-methods worktree done invoice-export   # refused: not merged yet')
    box.run('git merge -q work/invoice-export && git log --oneline', cwd=site)
    box.run('aios-methods worktree done invoice-export', cwd=site)
    box.run('aios-methods worktree list', cwd=site)


if __name__ == '__main__':
    sys.exit(main('aios-methods', use))
