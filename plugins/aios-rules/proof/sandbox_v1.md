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
Validating plugin manifest: <checkout>/plugins/aios-rules/.claude-plugin/plugin.json

Plugin directory checks for <checkout>/plugins/aios-rules. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

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
Validating marketplace manifest: <checkout>/.claude-plugin/marketplace.json

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
aios -> <checkout>/plugins/aios/skills/aios
rules -> <checkout>/plugins/aios-rules/skills/rules
rules-audit -> <checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.codex/skills:
total 0
aios -> <checkout>/plugins/aios/skills/aios
rules -> <checkout>/plugins/aios-rules/skills/rules
rules-audit -> <checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.cursor/skills:
total 0
aios -> <checkout>/plugins/aios/skills/aios
rules -> <checkout>/plugins/aios-rules/skills/rules
rules-audit -> <checkout>/plugins/aios-rules/skills/rules-audit

$HOME/.local/bin:
total 0
aios-rules -> <checkout>/plugins/aios-rules/bin/aios-rules
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
grep -nE 'Acme Studio|cafe|Invoices:|client list' AGENTS.md
```
```text
1:# Acme Studio: rules for every agent
7:- Sam Rivera runs Acme Studio. Acme Studio designs brand kits for small cafes.
8:- Customers: cafe owners with one to three sites.
43:- Invoices: the total equals the sum of the lines in the source sheet.
47:- The client list lives in 10_clients/README.md, not in a spreadsheet.
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
python3 - <<'EOF'
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

## 26. Full audit on the member sign-in (claude -p, read-only tools)

In `$HOME/acme-studio`:

```sh
aios-rules audit --timeout 900
```
```text
Wrote ./80_aios/audits/2026-10-26_rules-audit_v2.md
Budget ok; prompt audit ok; skill doctor unavailable.
[exit 0]
```

## 27. The dated audit files

In `$HOME/acme-studio`:

```sh
ls 80_aios/audits && tail -3 80_aios/audits/*_v2.md
```
```text
2026-10-26_rules-audit_v1.md
2026-10-26_rules-audit_v2.md
- [ ] Next audit date:

Status: budget ok; prompt audit ok; skill doctor unavailable.
[exit 0]
```

## 28. Claude Code read AGENTS.md through the bridge (answered from session context, no tools)

In `$HOME/acme-studio`:

```sh
claude -p 'Without reading any file, quote the line in your loaded instructions that says where invoices go. Reply with that line only.'
```
```text
| `30_finance/` | Invoices, receipts and contracts. Never bank logins or card numbers. |
[exit 0]
```

## 29. Claude Code sees both pack skills

In `$HOME/acme-studio`:

```sh
claude -p 'List the names of any skills you have whose names contain "rules". Names only, one per line.'
```
```text
aios-rules:rules
aios-rules:rules-audit
[exit 0]
```

## Appendix: the full audit file the member gets (2026-10-26_rules-audit_v2.md)

````markdown
# Rules audit, 2026-10-26

Folder: `acme-studio`. Nothing in your rules was changed by this audit.

## 1. Always-loaded budget (aios-rules check)

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
  On demand (loads only for matching files):
        6 lines     107 tokens  ./.cursor/rules/clients.mdc  paths: 10_clients/**
        6 lines      90 tokens  ./.cursor/rules/content.mdc  paths: 40_content/**
        6 lines     106 tokens  ./.cursor/rules/finance.mdc  paths: 30_finance/**
  Note: Cursor user rules live in its settings, not in files, so they are not counted.
```

## 2. Prompt audit (/doctor prompt-audit)

## Prompt audit: Acme Studio Claude Code configuration

The project's configuration has nothing to fix, so the proposed diff is empty. Nothing was edited. The only real findings are two in one plugin skill, and those are reported only, as you asked.

To check the work, I read every file in scope and tied each finding to a `file:line`, a named pattern, and something in the repository or the model's documented behaviour.

### Assumptions
- **Target model:** Claude Opus 5.5 (`claude-opus-5-5`), the model running this session. None of the files pins a model.
- **Scope:** only Claude Code configuration that loads into sessions here. Settings files, `.mcp.json` and `~/.claude.json` were not read.
- **User-level configuration:** I took `~/.claude` to be `$HOME/.claude`, because the plugin cache and auto-memory live there. It has no `CLAUDE.md`, rules, skills, commands, agents or output styles. I couldn't confirm any other home directory, so that part is unverified.
- **No git repository,** so I couldn't trace where any line came from.
- **No non-Anthropic provider markers** were found.

### What I read
| File | Loads |
|---|---|
| `CLAUDE.md` | every session (contains only `@AGENTS.md`) |
| `AGENTS.md` | every session, through the import |
| `.claude/rules/clients.md`, `finance.md`, `content.md` | only for `10_clients/**`, `30_finance/**` and `40_content/**` |
| Plugin skills `aios`, `aios-rules:rules`, `aios-rules:rules-audit` | when triggered; report only |

- There are no `CLAUDE.md`, `AGENTS.md` or `CLAUDE.local.md` files in the folders above the project or nested inside it.
- There is no `.claude/CLAUDE.md`, no `.claude/AGENTS.md`, and no managed-policy `CLAUDE.md`.
- `AGENTS.md` imports nothing.
- I didn't audit `.cursor/rules/*.mdc` or `80_aios/audits/2026-10-26_rules-audit_v1.md`, because Claude Code doesn't load them.

### Summary
- **Project files:** clean. There is no emphatic or pressure language, no step-by-step scripts for judgement tasks, no leftovers written for older models, and no contradictions.
- **Rules that overlap:** where the rule files repeat `AGENTS.md`, they agree with it. `finance.md` adds tax IDs to the "never write bank logins" rule, and `content.md` says nothing is published without your yes. Both just narrow `AGENTS.md`, so I left them alone.
- **Findings by group:**
  - Group 1 (dated prompt text): 0
  - Group 2 (brittle configuration files): 1 low-confidence flag in the project, plus 2 plugin findings reported only
  - Group 3 (tool descriptions): not applicable
  - Group 4 (request code): not applicable

### Findings

| Location | Evidence | Pattern | Why | Confidence | Action |
|---|---|---|---|---|---|
| plugin `aios/2.0.0/skills/aios/SKILL.md:32` | "Only `aios` and `aios-brain` ship in phase 1. Say when a pack is planned; do not try to install it." | Group 2, out-of-date facts | `aios-rules` 2.0.0 comes from the same marketplace, is installed here, and its skills load in this session. The skill would wrongly call it "planned". | High | Report only (plugin file) |
| plugin `aios/2.0.0/skills/aios/SKILL.md:46` | "For this unpublished review, add the local checkout path instead of GitHub." | Group 2, time-sensitive content | It describes one stage of a release and will go stale once the pack is published. | Medium | Report only (plugin file) |
| `AGENTS.md:51` | "The client list lives in 10_clients/README.md, not in a spreadsheet." | Group 2, out-of-date facts / a rule written for one incident | Neither `10_clients/` nor that README exists yet. The folder map looks like a plan, so a missing file doesn't prove the line wrong. But the section's own rule says a gotcha needs two mistakes behind it, and this project has no history to show any. | Low | Flag |

### Proposed diff
None. No project finding reaches medium confidence, and the plugin findings are report-only.

### Your decision
- **The client-list gotcha (`AGENTS.md:51`):** keep it if an agent really did look for a spreadsheet twice. If not, delete it, or keep it once you've created `10_clients/README.md`.
- **The `aios` plugin skill:** to fix it, tell the plugin's maintainer, not this project.

## 3. Skill usage (/skill-doctor)

**Not available in this session.** Open Claude Code in a terminal on this machine, run `/skill-doctor`, and paste its report under this heading.

> `/skill-doctor` isn't installed in this session, so it did not run.
> 
> I looked for skills it could check by hand. This folder has none: there are no `SKILL.md` files. `.claude/` holds only three path-scoped rules (`clients.md`, `finance.md`, `content.md`). The skills you can use here all come from plugins (`aios`, `aios-rules`) or are built in.
> 
> Your options:
> - **Run `/aios-rules:rules-audit`.** It's your monthly audit. It runs the rules budget check and lists `/skill-doctor` as one of its steps, so it may say how to get that command.
> - **Add `/skill-doctor`** as an organisation plugin or a project skill, if you need that exact command. I'm not sure of the install steps, so I won't guess them.
> 
> Do you want me to run `/aios-rules:rules-audit` now?

## 4. Decisions

- [ ] Lines to cut from AGENTS.md (move detail to a skill or a path-scoped rule):
- [ ] Skills to hide or turn off (from section 3):
- [ ] Findings from section 2 to apply (ask Claude to apply only the ones you tick):
- [ ] Next audit date:

Status: budget ok; prompt audit ok; skill doctor unavailable.
````

