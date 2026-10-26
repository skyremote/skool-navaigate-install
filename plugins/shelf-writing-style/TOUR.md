# Tour: module 12, the shelf: writing style

`/aios learn 12 writing-style` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/writing-style/SKILL.md"` (Codex: `ls ~/.codex/skills/writing-style/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-writing-style` (what `/aios install shelf-writing-style` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-writing-style` from the checkout and restart.

## Step 2: Make a practice draft
- **Do:** save a short sloppy draft to edit.
- **Command:** `printf "At Northwind Bakery, we leverage a robust, seamless loyalty platform — it's not just a card, it's a game-changer. Moreover, sales rose 38%% to £4,200.\n" > draft.txt`
- **They should see:** no output.
- **Check:** `cat draft.txt` shows the draft.

## Step 3: Run the editor
- **Do:** ask for the scrub.
- **Command:** Ask Claude: "Use the writing-style skill on draft.txt."
- **They should see:** a list of hits (em dash, banned words, binary contrast, a "Moreover") and a rewrite.
- **Check:** the rewrite keeps `Northwind Bakery`, `38%` and `£4,200`, and has no em dash.

## Recap
Grade it, list the hits, rewrite the failures, keep the facts.
