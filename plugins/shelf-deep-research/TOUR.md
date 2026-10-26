# Tour: module 12, the shelf: deep research

`/aios learn 12 deep-research` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/deep-research/SKILL.md"` (Codex: `ls ~/.codex/skills/deep-research/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-deep-research` (what `/aios install shelf-deep-research` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-deep-research` from the checkout and restart.

## Step 2: Find the helper
- **Do:** check that the helper in the bundled web-scrape skill runs.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/webscrape.py" --help` (Codex: `~/.codex/skills/web-scrape/scripts/webscrape.py`).
- **They should see:** the list of commands: search, contents, answer, scrape, crawl-search.
- **Check:** if `requests` is missing, run `python3 -m pip install --user requests`, then again.

## Step 3: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(EXA_API_KEY|FIRECRAWL_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `EXA_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there. SUPADATA_API_KEY are optional.

## Step 4: Try one keyless source
- **Do:** search academic papers, which needs no key.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/web-scrape/scripts/sources/academic.py" search "customer loyalty programmes small business" --from-year 2020 --limit 3`
- **They should see:** three papers with year, citations and a link.
- **Check:** an error here is the network, not a key. Fix that first.

## Step 5: Run a small research pass
- **Do:** ask for research on a fictional question, so the member sees every stage.
- **Command:** Ask Claude: "Use the deep-research skill: should Northwind Bakery switch from punch cards to a loyalty app? Scope it first and wait for my yes."
- **They should see:** a one-sentence scope for the member to agree, then a hot/warm/cold recon of each source.
- **Check:** nothing is researched before the member says yes to the scope.

## Step 6: Read the write-up
- **Do:** let it finish, then check the write-up.
- **Command:** Say yes to the scope and wait.
- **They should see:** findings with a confidence label each, quotes from sources, and the critic pass noted.
- **Check:** each claim has a source link and a label. A claim with no source is a fail.

## Recap
Keys once, scope with a yes, recon, live sources, critic pass, labelled write-up.
