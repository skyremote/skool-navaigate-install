# tools-research (AIOS 2.0, module 12: the shelf, tools)

Research beyond a normal web search. Research papers from **OpenAlex** (free), posts from **Substack** (free), threads
from **Reddit** through your own free Reddit app, and optionally **YouTube consensus** with the public `consensus`
skill. Every finding goes into a ledger with a link and an honest confidence label, and `tools-research check` fails
a ledger that is unsourced or overconfident.

## Install

1. Install the start plugin `aios` first (module 1).
2. For Reddit: make your own free app at reddit.com/prefs/apps ("create another app", type "script"). Copy the id
   under the name and the secret.
3. Optional, YouTube consensus: `git clone https://github.com/GoodLadTom/consensus ~/.claude/skills/consensus` and
   follow its README (it uses your own Supadata key).

**Claude Code:** `/aios install tools-research` (or `/plugin install tools-research@navaigate-aios`), `/reload-plugins`,
then `/plugin`, tools-research, Configure: the Reddit app id and secret.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-research
./install.sh tools-research --check
```
Then `export REDDIT_CLIENT_ID=...` and `export REDDIT_CLIENT_SECRET=...` in your shell profile.

Needs Python 3.9 or later. For general web search and JavaScript-heavy pages, pair it with `shelf-web-scrape`.

## Use

```
tools-research doctor
tools-research papers "online ordering small restaurants"
tools-research substack archive www.lennysnewsletter.com
tools-research reddit search "ai receptionist" --subreddit smallbusiness
tools-research new ~/Research/receptionists_v1.md --question "Do AI receptionists work for small clinics?"
tools-research check ~/Research/receptionists_v1.md
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-research/SKILL.md](skills/tools-research/SKILL.md).

## Licence

MIT. OpenAlex data is CC0. Reddit and Substack content belongs to its authors; use it under those sites' terms.
The `consensus` skill is MIT and installed by you from its own repository.
