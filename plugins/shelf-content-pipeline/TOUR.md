# Tour: module 12, the shelf: content pipeline

`/aios learn 12 content-pipeline` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/SKILL.md"` (Codex: `ls ~/.codex/skills/content-pipeline/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-content-pipeline` (what `/aios install shelf-content-pipeline` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-content-pipeline` from the checkout and restart.

## Step 2: Make the store
- **Do:** create the local database and the empty pipeline file, in a practice folder.
- **Command:** `mkdir -p ~/content-practice && cd ~/content-practice && python3 "${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/scripts/db.py" && python3 "${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/scripts/db.py" --check`
- **They should see:** a line saying `data/content.db` exists with its two tables.
- **Check:** `ls data` shows `content.db`.

## Step 3: Make the pipeline file
- **Do:** generate the empty `content/pipeline.md`.
- **Command:** `mkdir -p content/concepts && python3 "${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/scripts/generate_pipeline.py"`
- **They should see:** a line saying the pipeline file was written.
- **Check:** `ls content` shows `pipeline.md`.

## Step 4: Capture an idea
- **Do:** ask Claude to capture one fictional idea.
- **Command:** Ask Claude: "Use the content-pipeline skill: capture the idea 'why bakeries should sell gift cards'."
- **They should see:** Claude classifies it, checks for duplicates, and stores a stub.
- **Check:** `content/pipeline.md` now lists the idea.

## Step 5: Develop it
- **Do:** develop the stub into a concept.
- **Command:** Ask Claude: "Use the content-pipeline skill: develop #1."
- **They should see:** positioning, packaging, a priority and a concept document under `content/concepts/`.
- **Check:** the concept file exists. Nothing was published.

## Recap
Store, pipeline file, capture, develop, schedule. Every step is a file you can open.
