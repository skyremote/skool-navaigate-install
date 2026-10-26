# Tour: module 12, the shelf: web scrape

`/aios learn 12 web-scrape` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/SKILL.md"` (Codex: `ls ~/.codex/skills/web-scrape/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-web-scrape` (what `/aios install shelf-web-scrape` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-web-scrape` from the checkout and restart.

## Step 2: Run the helper
- **Do:** check that the helper starts.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/webscrape.py" --help` (Codex: `~/.codex/skills/web-scrape/scripts/webscrape.py`).
- **They should see:** the commands: search, contents, answer, scrape, crawl-search.
- **Check:** if `requests` is missing, run `python3 -m pip install --user requests`.

## Step 3: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(EXA_API_KEY|FIRECRAWL_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `EXA_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there. SUPADATA_API_KEY are optional.

## Step 4: Find by meaning
- **Do:** run one Exa search with highlights.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/webscrape.py" search "how bakeries run loyalty schemes" --highlights`
- **They should see:** a few results, each with a title, a link and an excerpt.
- **Check:** `401` means the Exa key is wrong. Fix `~/.claude/.env`.

## Step 5: Read one page
- **Do:** render one page to markdown with Firecrawl.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/webscrape.py" scrape "https://example.com"`
- **They should see:** the page as clean markdown.
- **Check:** on a dynamic page that comes back empty, add `--wait 3000`.

## Step 6: Ask Claude to do it
- **Do:** let Claude choose the tool.
- **Command:** Ask Claude: "Use the web-scrape skill: find three sources on bakery loyalty apps and give me the key point of each with its link."
- **They should see:** Exa to find, Firecrawl only if a page needs reading, links on every point.
- **Check:** the answer carries the links it read. No links, no proof.

## Recap
Keys once, search to find, scrape to read, links on everything.
