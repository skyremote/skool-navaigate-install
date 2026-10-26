# Tour: module 12, the shelf: design brain

`/aios learn 12 design-brain` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/design-brain/SKILL.md"` (Codex: `ls ~/.codex/skills/design-brain/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-design-brain` (what `/aios install shelf-design-brain` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-design-brain` from the checkout and restart.

## Step 2: Is the corpus on this machine?
- **Do:** look for the data file.
- **Command:** `ls ~/.claude/skills/design-brain/data/design-brain.json` (Codex and Cursor: `~/design-brain/data/design-brain.json`).
- **They should see:** the path, or `No such file or directory`.
- **Check:** if missing, go to step 3. If present, skip to step 4.

## Step 3: Download and unzip the corpus
- **Do:** fetch the zip the lesson links and unzip it.
- **Command:** `curl -L -o ~/Downloads/design-brain_v1.zip "https://f003.backblazeb2.com/file/NavAIgate-Website/navbot-community/downloads/your-aios/design-brain_v1.zip"` then `unzip -o ~/Downloads/design-brain_v1.zip -d ~/.claude/skills` (Codex and Cursor: `-d ~`).
- **They should see:** `inflating: ... design-brain/data/design-brain.json`.
- **Check:** `ls` on the data file now shows it. Restart the harness so it loads the skill folder.

## Step 4: Ask it a question
- **Do:** ask one design question and look for a citation.
- **Command:** Ask Claude: "Use the design-brain skill: what contrast ratio does body text need?"
- **They should see:** an answer with a figure (4.5:1 for body text) and an entry number with a named source (WCAG).
- **Check:** every claim carries `#number` and a source. If it cites nothing, the corpus was not found: redo step 3.

## Step 5: Critique something of yours
- **Do:** paste or point at a page, deck or chart of the member's own.
- **Command:** Ask Claude: "Use the design-brain skill to critique this page" and point at the file.
- **They should see:** findings in severity order: violation, entry number and title, the rule, the source, the fix.
- **Check:** it also names one or two things done well. A critique with no entry numbers is not a Design Brain critique.

## Recap
Install the pack, download the corpus once, ask a question, critique your own work. Every answer cites an entry and a source.
