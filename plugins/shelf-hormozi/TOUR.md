# Tour: module 12, the shelf: hormozi

`/aios learn 12 hormozi` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/hormozi/SKILL.md"` (Codex: `ls ~/.codex/skills/hormozi/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-hormozi` (what `/aios install shelf-hormozi` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-hormozi` from the checkout and restart.

## Step 2: Are the book-grounded skills here?
- **Do:** look for the Hormozi skills in the member's skills folder.
- **Command:** `ls ~/.claude/skills | grep -i -E "hormozi|grand-slam|offer-enhancer|lead-engine|money-model"` (Codex: `~/.codex/skills`).
- **They should see:** skill names, or nothing.
- **Check:** nothing means: go to the Inner Circle gold lesson and build them from the member's own book files (step 3).

## Step 3: Install from your own books
- **Do:** follow the gold lesson.
- **Command:** Open the lesson linked in the skill and follow it with the member's own book files.
- **They should see:** the five skills appear in the skills folder.
- **Check:** step 2 now lists them. Never copy anyone else's book corpus.

## Step 4: Ask a cited question
- **Do:** ask one question about the member's offer.
- **Command:** Ask Claude: "Use the hormozi skill: what would Hormozi say about the guarantee on my Northwind Bakery subscription box?"
- **They should see:** an answer with book, chapter and page.
- **Check:** no citation, no claim. If the corpus is not installed, it says so plainly.

## Recap
Front door, your own books, then cited answers on your offer.
