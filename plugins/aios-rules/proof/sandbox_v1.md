# aios-rules sandbox install, v1

A new member installs module 2 in a throwaway HOME. Every command below ran for real; output is unedited
apart from paths: `$HOME` is `/tmp/aios2-sandbox-a-foundations` and `<checkout>` is a copy of this branch
with `INTEGRATION.diff` and `MARKETPLACE_ENTRY.json` applied (the merge this stream proposes).
Environment: HOME, CLAUDE_CONFIG_DIR and CODEX_HOME all point into the sandbox. The business is fictional.

Reproduce: `python3 tests/aios-rules/sandbox_proof_v1.py --with-claude-audit`.

## 1. Claude Code version

In `<checkout>`:

```sh
claude --version
```
```text
2.1.310 (Claude Code)
[exit 0]
```

## 2. Python version

In `<checkout>`:

```sh
python3 --version
```
```text
Python 3.9.6
[exit 0]
```

## 3. Validate the pack

In `<checkout>`:

```sh
claude plugin validate plugins/aios-rules --strict
```
```text
Validating plugin manifest: /private<checkout>/plugins/aios-rules/.claude-plugin/plugin.json

Plugin directory checks for /private<checkout>/plugins/aios-rules. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found in the plugin. The validator looked for `icon` in plugin.json and for a file at .claude-plugin/icon.png or .svg, assets/icon.png or .svg, or a similar path.
    Fix: Add a square PNG to the plugin folder at .claude-plugin/icon.png, or set `icon` in plugin.json to the path of a square PNG or JPEG in the plugin: 512 to 2048 px on each side, under 2 MB. SVG and WebP are not accepted. That file may become the listing icon only once: the first time the plugin is saved or submitted in the developer portal. Adding or changing it later does not change the icon.

These plugin directory checks do not change the result below.

The directory also runs a safety scan and a policy review that this command does not.

✔ Validation passed
[exit 0]
```

## 4. Validate the marketplace with the aios-rules entry

In `<checkout>`:

```sh
claude plugin validate .claude-plugin/marketplace.json --strict
```
```text
Validating marketplace manifest: /private<checkout>/.claude-plugin/marketplace.json

✔ Validation passed
[exit 0]
```

## 5. Claude Code: add the review marketplace

In `<checkout>`:

```sh
claude plugin marketplace add ./
```
```text
Adding marketplace…✔ Successfully added marketplace: navaigate-aios (declared in user settings)
[exit 0]
```

## 6. Claude Code: install the start plugin

In `<checkout>`:

```sh
claude plugin install aios@navaigate-aios
```
```text
Installing plugin "aios@navaigate-aios"...✔ Successfully installed plugin: aios@navaigate-aios (scope: user)
[exit 0]
```

## 7. Claude Code: install module 2

In `<checkout>`:

```sh
claude plugin install aios-rules@navaigate-aios
```
```text
Installing plugin "aios-rules@navaigate-aios"...✔ Successfully installed plugin: aios-rules@navaigate-aios (scope: user)
[exit 0]
```

## 8. Claude Code: both plugins are installed and enabled

In `<checkout>`:

```sh
claude plugin list --json | python3 -c "import json,sys; print(json.dumps([{k:p.get(k) for k in ('id','version','enabled')} for p in json.load(sys.stdin)], indent=2))"
```
```text
[
  {
    "id": "aios-rules@navaigate-aios",
    "version": "2.0.0",
    "enabled": true
  },
  {
    "id": "aios@navaigate-aios",
    "version": "2.0.0",
    "enabled": true
  }
]
[exit 0]
```

## 9. Codex and Cursor: the dependency check refuses aios-rules before aios

In `<checkout>`:

```sh
./install.sh aios-rules
```
```text
Install stopped: aios-rules depends on aios. First run: ./install.sh aios
[exit 1]
```

## 10. Codex and Cursor: install the start skill

In `<checkout>`:

```sh
./install.sh aios
```
```text
Linked .codex/skills/aios
Linked .cursor/skills/aios
Linked .agents/skills/aios
Installed aios 2.0.0. Restart Codex and Cursor. Add ~/.local/bin to PATH for the pack commands.
[exit 0]
```

## 11. Codex and Cursor: install module 2 (patched installer)

In `<checkout>`:

```sh
./install.sh aios-rules
```
```text
Linked .codex/skills/rules
Linked .codex/skills/rules-audit
Linked .cursor/skills/rules
Linked .cursor/skills/rules-audit
Linked .agents/skills/rules
Linked .agents/skills/rules-audit
Linked .local/bin/aios-rules
Installed aios-rules 2.0.0. Restart Codex and Cursor. Add ~/.local/bin to PATH for the pack commands.
[exit 0]
```

## 12. The links point into the checkout

In `<checkout>`:

```sh
ls -l ~/.codex/skills ~/.cursor/skills ~/.agents/skills ~/.local/bin | sed "s/^.* \([^ ]* -> \)/\1/"
```
```text
$HOME/.agents/skills:
total 0
aios -> /private<checkout>/plugins/aios/skills/aios
rules -> /private<checkout>/plugins/aios-rules/skills/rules
rules-audit -> /private<checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.codex/skills:
total 0
aios -> /private<checkout>/plugins/aios/skills/aios
rules -> /private<checkout>/plugins/aios-rules/skills/rules
rules-audit -> /private<checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.cursor/skills:
total 0
aios -> /private<checkout>/plugins/aios/skills/aios
rules -> /private<checkout>/plugins/aios-rules/skills/rules
rules-audit -> /private<checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.local/bin:
total 0
aios-rules -> /private<checkout>/plugins/aios-rules/bin/aios-rules
[exit 0]
```

## 13. A new, empty AIOS folder

In `$HOME`:

```sh
mkdir -p $HOME/acme-studio
```
```text

[exit 0]
```

## 14. Dry run: nothing is written

In `$HOME/acme-studio`:

```sh
aios-rules init --business 'Acme Studio' --owner 'Sam Rivera' --dry-run
```
```text
CREATED  ./00_inbox  (folder)
CREATED  ./10_clients  (folder)
CREATED  ./20_offers  (folder)
CREATED  ./30_finance  (folder)
CREATED  ./40_content  (folder)
CREATED  ./50_projects  (folder)
CREATED  ./80_aios  (folder)
CREATED  ./90_archive  (folder)
CREATED  ./AGENTS.md  (starter rules file: fill in the {{...}} lines)
CREATED  ./CLAUDE.md  (one-line bridge so Claude Code reads AGENTS.md)
CREATED  ./.claude/rules/clients.md  (path-scoped rule)
CREATED  ./.claude/rules/finance.md  (path-scoped rule)
CREATED  ./.claude/rules/content.md  (path-scoped rule)
Next: fill in the {{...}} lines in AGENTS.md, then run: aios-rules check
[exit 0]
```

## 15. Set up the folder and rules

In `$HOME/acme-studio`:

```sh
aios-rules init --business 'Acme Studio' --owner 'Sam Rivera'
```
```text
CREATED  ./00_inbox  (folder)
CREATED  ./10_clients  (folder)
CREATED  ./20_offers  (folder)
CREATED  ./30_finance  (folder)
CREATED  ./40_content  (folder)
CREATED  ./50_projects  (folder)
CREATED  ./80_aios  (folder)
CREATED  ./90_archive  (folder)
CREATED  ./AGENTS.md  (starter rules file: fill in the {{...}} lines)
CREATED  ./CLAUDE.md  (one-line bridge so Claude Code reads AGENTS.md)
CREATED  ./.claude/rules/clients.md  (path-scoped rule)
CREATED  ./.claude/rules/finance.md  (path-scoped rule)
CREATED  ./.claude/rules/content.md  (path-scoped rule)
Next: fill in the {{...}} lines in AGENTS.md, then run: aios-rules check
[exit 0]
```

## 16. A second run keeps everything

In `$HOME/acme-studio`:

```sh
aios-rules init
```
```text
KEPT     ./00_inbox  (folder already there)
KEPT     ./10_clients  (folder already there)
KEPT     ./20_offers  (folder already there)
KEPT     ./30_finance  (folder already there)
KEPT     ./40_content  (folder already there)
KEPT     ./50_projects  (folder already there)
KEPT     ./80_aios  (folder already there)
KEPT     ./90_archive  (folder already there)
KEPT     ./AGENTS.md  (your rules file is unchanged; compare it with the starter in the pack)
KEPT     ./CLAUDE.md  (already imports AGENTS.md)
KEPT     ./.claude/rules/clients.md  (rule already there)
KEPT     ./.claude/rules/finance.md  (rule already there)
KEPT     ./.claude/rules/content.md  (rule already there)
Next: fill in the {{...}} lines in AGENTS.md, then run: aios-rules check
[exit 0]
```

## 17. The bridge holds one line

In `$HOME/acme-studio`:

```sh
cat CLAUDE.md
```
```text
@AGENTS.md
[exit 0]
```

## 18. First check: the placeholders are flagged

In `$HOME/acme-studio`:

```sh
aios-rules check
```
```text
CLAUDE CODE: WARN
  Always loaded: 2 files, 48 lines, about 619 tokens (budget 300 lines, 4000 tokens).
        1 lines       3 tokens  project       ./CLAUDE.md
       47 lines     616 tokens  import        ./AGENTS.md  (via ./CLAUDE.md)
  On demand (loads only for matching files):
        6 lines      79 tokens  ./.claude/rules/clients.md  paths: 10_clients/**
        6 lines      62 tokens  ./.claude/rules/content.md  paths: 40_content/**
        6 lines      78 tokens  ./.claude/rules/finance.md  paths: 30_finance/**
  WARN ./AGENTS.md: This file still has {{...}} placeholders. Fill them in or delete those lines.
  Note: Plugin skills, MCP tool names and the system prompt are not counted. Run /context in a session for the full picture.
[exit 0]
```

## 19. The member fills in the four {{...}} lines (scripted here with fictional answers)

In `$HOME/acme-studio`:

```sh
edit AGENTS.md
```
```text

[exit 0]
```

## 20. Check all three harnesses: within budget

In `$HOME/acme-studio`:

```sh
aios-rules check --harness all
```
```text
CLAUDE CODE: OK
  Always loaded: 2 files, 48 lines, about 620 tokens (budget 300 lines, 4000 tokens).
        1 lines       3 tokens  project       ./CLAUDE.md
       47 lines     617 tokens  import        ./AGENTS.md  (via ./CLAUDE.md)
  On demand (loads only for matching files):
        6 lines      79 tokens  ./.claude/rules/clients.md  paths: 10_clients/**
        6 lines      62 tokens  ./.claude/rules/content.md  paths: 40_content/**
        6 lines      78 tokens  ./.claude/rules/finance.md  paths: 30_finance/**
  Note: Plugin skills, MCP tool names and the system prompt are not counted. Run /context in a session for the full picture.

CODEX: OK
  Always loaded: 1 files, 47 lines, about 617 tokens (budget 300 lines, 4000 tokens).
       47 lines     617 tokens  agents        ./AGENTS.md
  Note: Codex does not expand @imports and does not read CLAUDE.md or .claude/rules/.

CURSOR: OK
  Always loaded: 1 files, 47 lines, about 617 tokens (budget 300 lines, 4000 tokens).
       47 lines     617 tokens  agents        ./AGENTS.md
  Note: Cursor user rules live in its settings, not in files, so they are not counted.
[exit 0]
```

## 21. Over budget on purpose: 240 extra lines make the check fail with exit 1

In `$HOME/acme-studio`:

```sh
python3 -c "print('- old rule\n' * 240, end='')" >> AGENTS.md && aios-rules check; echo "exit $?"
```
```text
CLAUDE CODE: OVER
  Always loaded: 2 files, 288 lines, about 1280 tokens (budget 300 lines, 4000 tokens).
        1 lines       3 tokens  project       ./CLAUDE.md
      287 lines    1277 tokens  import        ./AGENTS.md  (via ./CLAUDE.md)
  On demand (loads only for matching files):
        6 lines      79 tokens  ./.claude/rules/clients.md  paths: 10_clients/**
        6 lines      62 tokens  ./.claude/rules/content.md  paths: 40_content/**
        6 lines      78 tokens  ./.claude/rules/finance.md  paths: 30_finance/**
  OVER ./AGENTS.md: This file is 287 lines, over the 200-line limit. Move detail into skills or path-scoped rules.
  Note: Plugin skills, MCP tool names and the system prompt are not counted. Run /context in a session for the full picture.
exit 1
[exit 0]
```

## 22. Remove the extra lines: back within budget

In `$HOME/acme-studio`:

```sh
git init -q . 2>/dev/null; python3 - <<'EOF'
from pathlib import Path
p = Path("AGENTS.md")
p.write_text("".join(l for l in p.read_text().splitlines(True) if l != "- old rule\n"))
EOF
aios-rules check; echo "exit $?"
```
```text
CLAUDE CODE: OK
  Always loaded: 2 files, 48 lines, about 620 tokens (budget 300 lines, 4000 tokens).
        1 lines       3 tokens  project       ./CLAUDE.md
       47 lines     617 tokens  import        ./AGENTS.md  (via ./CLAUDE.md)
  On demand (loads only for matching files):
        6 lines      79 tokens  ./.claude/rules/clients.md  paths: 10_clients/**
        6 lines      62 tokens  ./.claude/rules/content.md  paths: 40_content/**
        6 lines      78 tokens  ./.claude/rules/finance.md  paths: 30_finance/**
  Note: Plugin skills, MCP tool names and the system prompt are not counted. Run /context in a session for the full picture.
exit 0
[exit 0]
```

## 23. Mirror the scoped rules for Cursor

In `$HOME/acme-studio`:

```sh
aios-rules cursor-rules
```
```text
WRITTEN  ./.cursor/rules/clients.mdc  (from .claude/rules/clients.md)
WRITTEN  ./.cursor/rules/content.mdc  (from .claude/rules/content.md)
WRITTEN  ./.cursor/rules/finance.mdc  (from .claude/rules/finance.md)
[exit 0]
```

## 24. Cursor now has the same scoped rules

In `$HOME/acme-studio`:

```sh
aios-rules check --harness cursor
```
```text
CURSOR: OK
  Always loaded: 1 files, 47 lines, about 617 tokens (budget 300 lines, 4000 tokens).
       47 lines     617 tokens  agents        ./AGENTS.md
  On demand (loads only for matching files):
        6 lines     107 tokens  ./.cursor/rules/clients.mdc  paths: 10_clients/**
        6 lines      90 tokens  ./.cursor/rules/content.mdc  paths: 40_content/**
        6 lines     106 tokens  ./.cursor/rules/finance.mdc  paths: 30_finance/**
  Note: Cursor user rules live in its settings, not in files, so they are not counted.
[exit 0]
```

## 25. Audit, budget part only

In `$HOME/acme-studio`:

```sh
aios-rules audit --no-claude
```
```text
Wrote ./80_aios/audits/2026-10-26_rules-audit_v1.md
Budget ok; prompt audit skipped; skill doctor skipped.
[exit 0]
```
