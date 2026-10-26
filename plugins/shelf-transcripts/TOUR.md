# Tour: module 12, the shelf: transcripts

`/aios learn 12 transcripts` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/transcripts/SKILL.md"` (Codex: `ls ~/.codex/skills/transcripts/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-transcripts` (what `/aios install shelf-transcripts` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-transcripts` from the checkout and restart.

## Step 2: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(SUPADATA_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `SUPADATA_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there.

## Step 3: Find the client
- **Do:** check that the transcript client starts.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/sources/supadata.py" --help` (Codex: `~/.codex/skills/web-scrape/...`).
- **They should see:** the commands: search, transcript, research.
- **Check:** if `requests` is missing, run `python3 -m pip install --user requests`.

## Step 4: Pull one transcript
- **Do:** pull one short public video the member picks. This uses credits, so one is enough.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/sources/supadata.py" transcript "<video url>" --lang en`
- **They should see:** the words of the video, with timestamps if the video has them.
- **Check:** `401` means the key is wrong. `404` means the video has no captions.

## Step 5: Ask Claude for the job
- **Do:** have Claude use the full transcript for a task.
- **Command:** Ask Claude: "Use the transcripts skill on <video url> and list every objection the speaker raises, with the quote."
- **They should see:** a list of objections, each with an exact quote from the transcript.
- **Check:** quotes match the transcript word for word. A paraphrase with no quote is a fail.

## Recap
Key once, one URL, the full words, then the job. Do not bulk-pull: it is metered.
