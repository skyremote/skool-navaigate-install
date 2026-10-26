# Tour: module 12, the shelf: exec brief

`/aios learn 12 exec-brief` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/exec-brief/SKILL.md"` (Codex: `ls ~/.codex/skills/exec-brief/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-exec-brief` (what `/aios install shelf-exec-brief` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-exec-brief` from the checkout and restart.

## Step 2: See the template
- **Do:** confirm the template and design system are in the skill.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/exec-brief/assets/template.html" "${CLAUDE_PLUGIN_ROOT}/skills/exec-brief/references/design-system.md"`
- **They should see:** both paths.
- **Check:** both exist.

## Step 3: Ask for a brief
- **Do:** ask for a decision brief on a fictional company, with the figures the member really has.
- **Command:** Ask Claude: "Use the exec-brief skill: a decision brief for Acme Studio on moving hosting to a cheaper provider. I have only the current bill, GBP 480 a month."
- **They should see:** Claude names the decision in one sentence, asks who it is to, and marks what is not measured as `not yet`.
- **Check:** no invented numbers. Anything unmeasured says `not yet` or `not measured`.

## Step 4: Open it and print
- **Do:** open the file and print to PDF.
- **Command:** `open briefs/Acme_Studio_Brief_v1.html`, then print to PDF from the browser.
- **They should see:** cream paper, A4 pages, a decision block on page 1.
- **Check:** three or four pages, nothing cut off at the page edges.

## Recap
Name the decision, collect only figures you can point at, build, print, version it.
