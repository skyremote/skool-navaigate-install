# Tour: module 12, the shelf: thumbnails

`/aios learn 12 thumbnails` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/thumbnails/SKILL.md"` (Codex: `ls ~/.codex/skills/thumbnails/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-thumbnails` (what `/aios install shelf-thumbnails` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-thumbnails` from the checkout and restart.

## Step 2: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(GEMINI_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `GEMINI_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there.

## Step 3: Photos first
- **Do:** check the member has their own photo catalogue. If not, stop and build it.
- **Command:** Ask Claude: "Use the thumbnails skill. I have not catalogued my photos yet. Help me set that up."
- **They should see:** a request for a small set of the member's own photos, tagged by expression, pose and setting.
- **Check:** no thumbnail is made until at least a few of the member's own photos are tagged.

## Step 4: Four concepts
- **Do:** ask for a thumbnail for a topic.
- **Command:** Ask Claude: "Use the thumbnails skill: a 16:9 thumbnail for my video 'How Northwind Bakery doubled Saturday sales'."
- **They should see:** a 2x2 sheet of four scene concepts with no words on them.
- **Check:** there is no text in the images. The model must not render words.

## Step 5: Pick and add the headline
- **Do:** choose one in plain English.
- **Command:** Say "the second one, warmer, face left".
- **They should see:** a final PNG with the headline in heavy condensed type, white fill and dark stroke.
- **Check:** the headline is spelled exactly as asked. The file is saved as `<topic>_thumbnail.png`.

## Recap
Photos first, four concepts with no text, you pick, the headline goes on as a layer.
