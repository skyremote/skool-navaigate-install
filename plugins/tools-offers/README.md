# tools-offers (AIOS 2.0, module 12: the shelf, tools)

Build and fix your offer with the books you own. You bring your own copies of Alex Hormozi's three books and install
the public **Hormozi Growth Engine** (five skills and a front-door agent). This pack gives your agent our way of using
it: the right engine skill for the job, a corpus you build from your books so answers cite book, chapter and page,
and James Smith's public teaching as a second view.

- **Your books, your corpus.** No book content ships with anything. You distil your own copies.
- **Cited or labelled.** Without a corpus the engine runs on its method summaries and says it cannot cite pages.
- **Local.** No account, no API key.

## Install

1. Install the start plugin `aios` first (module 1).
2. The engine, once: `git clone https://github.com/skyremote/hormozi-growth-engine ~/hormozi-growth-engine && ~/hormozi-growth-engine/install.sh claude`
   (use `codex` for Codex, `all` for both).
3. Optional: `git clone https://github.com/skyremote/james-smith ~/.claude/skills/james-smith`.

**Claude Code:** `/aios install tools-offers` (or `/plugin install tools-offers@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-offers
./install.sh tools-offers --check
```

## Use

```
tools-offers doctor
tools-offers corpus init ~/Hormozi-corpus
tools-offers corpus check ~/Hormozi-corpus
tools-offers corpus point ~/Hormozi-corpus --yes
```

Three starter prompts: [prompts.md](prompts.md). Which engine skill does which job: [skills/tools-offers/SKILL.md](skills/tools-offers/SKILL.md).

## Licence

MIT for this pack. The Hormozi Growth Engine and the James Smith skill are separate public repositories with their
own terms; this pack links to them and does not copy them. Not affiliated with Alex Hormozi, Acquisition.com or
James Smith. Buy the books at acquisition.com/books.
