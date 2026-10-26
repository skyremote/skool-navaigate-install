# Tour: module 12, the shelf: podcasts

`/aios learn 12 podcasts` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/podcasts/SKILL.md"` (Codex: `ls ~/.codex/skills/podcasts/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-podcasts` (what `/aios install shelf-podcasts` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-podcasts` from the checkout and restart.

## Step 2: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(EXA_API_KEY|FIRECRAWL_API_KEY|SUPADATA_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `EXA_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there.

## Step 3: The wide net
- **Do:** search the open web for the topic.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/webscrape.py" search "podcast interview bakery owner loyalty scheme" --text --max-chars 800`
- **They should see:** show-site and listing pages with excerpts.
- **Check:** results come back with links. `401` means a wrong Exa key.

## Step 4: The deep net
- **Do:** search YouTube through Supadata (metered, keep it small).
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/sources/supadata.py" search "bakery owner interview loyalty" --limit 5`
- **They should see:** five videos with title, channel, views and length.
- **Check:** a missing key stops with the key name.

## Step 5: Ask Claude for a shortlist
- **Do:** have Claude rank, not dump.
- **Command:** Ask Claude: "Use the podcasts skill: find the best three episodes where bakery operators talk about loyalty schemes. Rank them and say why."
- **They should see:** three episodes, best first, each with views, length and why it made the cut.
- **Check:** it asks which to pull before spending credits on transcripts.

## Step 6: Pull one transcript
- **Do:** the member picks one; Claude pulls its full transcript.
- **Command:** Say "pull the second one".
- **They should see:** the full transcript, then quotes from the guest on the theme you asked for.
- **Check:** quotes are word for word.

## Recap
Wide net, deep net, a shortlist of three, then one full transcript.
