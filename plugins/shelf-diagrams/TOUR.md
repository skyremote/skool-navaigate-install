# Tour: module 12, the shelf: diagrams

`/aios learn 12 diagrams` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/diagrams/SKILL.md"` (Codex: `ls ~/.codex/skills/diagrams/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-diagrams` (what `/aios install shelf-diagrams` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-diagrams` from the checkout and restart.

## Step 2: Is D2 installed?
- **Do:** check for the d2 command.
- **Command:** `d2 --version`
- **They should see:** a version number.
- **Check:** if not found, install it from https://d2lang.com (`curl -fsSL https://d2lang.com/install.sh | sh -s --`) and run it again.

## Step 3: Prove it with one box
- **Do:** render the smallest diagram.
- **Command:** `mkdir -p diagrams && printf 'hello: Acme Studio\n' > diagrams/test.d2 && d2 diagrams/test.d2 diagrams/test.png`
- **They should see:** `success: successfully compiled diagrams/test.d2 to diagrams/test.png`.
- **Check:** `diagrams/test.png` exists and opens.

## Step 4: Draw a real one
- **Do:** describe a flow in plain English.
- **Command:** Ask Claude: "Use the diagrams skill: draw how an order moves from the Northwind Bakery website to the oven. One version for a client, one expanded for me."
- **They should see:** `diagrams/<slug>.d2`, a rendered PNG, and Claude saying what it fixed after looking.
- **Check:** open the PNG. Labels do not overlap and the flow reads left to right or top to bottom.

## Recap
Install D2, prove it with one box, describe the flow, look at the picture, fix, hand over two versions.
