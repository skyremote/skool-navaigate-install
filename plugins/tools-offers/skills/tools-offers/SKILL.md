---
name: tools-offers
description: Build or fix the member's offer, pricing, guarantee, offer name, bonuses, lead plan or money model with the public Hormozi Growth Engine (and say which engine skill does the job), grounded in a corpus from their own copies of the books, with book, chapter and page cited. Use for "fix my offer", "we need a guarantee", "what should we call it", "bonuses for a launch", "which tool do I use for my offer", "we need leads", "price this".
---

# Offers and growth, cited from the books you own

The "public tool" here is two things the member owns: their own copies of Alex Hormozi's three books ($100M Offers,
$100M Leads, $100M Money Models), and the public Hormozi Growth Engine (five skills and a front-door agent). This
skill is how we use them: pick the right engine skill for the job, cite every claim, and refuse to invent.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-offers"`. Codex and Cursor: `tools-offers` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `doctor [--harness claude/codex/agents]` | Engine skills installed? Corpus pointed? James Smith skill present? |
| `corpus init <folder>` | The empty corpus folders for the three books. |
| `corpus check <folder>` | Chapters distilled per book, and how many carry `[p.NNN]` page markers. |
| `corpus point <folder> [--yes]` | Points the installed engine skills at the corpus. Shows the files first; writes only with `--yes`. |

## Setup (once)

1. `doctor`. If the engine is missing:
   `git clone https://github.com/skyremote/hormozi-growth-engine ~/hormozi-growth-engine && ~/hormozi-growth-engine/install.sh claude`
   (`codex` for Codex). It copies five skills and the `hormozi` agent into their harness.
2. Their corpus: `corpus init ~/Hormozi-corpus`. They work through each book they own, one Markdown file per
   chapter, in their own words, with `[p.NNN]` page markers. Distillation, not transcription. Never copy book text
   from anywhere else, and never put the corpus in a shared or public folder.
3. `corpus check`, then `corpus point ~/Hormozi-corpus --yes`. Start a new session.
4. Optional second view: `git clone https://github.com/skyremote/james-smith ~/.claude/skills/james-smith`
   (public teaching from James Smith's business channel, cited by video).

## Which engine skill does the job

When the member asks which tool to use, name the engine skill from this table in your answer, then say how to run it.

| The member says | Use |
|---|---|
| "I need an offer", "what should I sell and for how much" | `grand-slam-offer-builder` |
| "make this offer convert", "guarantee", "bonuses", "what do I call it", a launch is coming | `offer-enhancer` |
| "we need leads", "fill the pipeline", "lead magnet" | `lead-engine-planner` |
| "how does this make money across the journey", "make acquisition pay for itself" | `money-model-architect` |
| "what do the books say about X" | `ask-hormozi` |
| small audience, coaching, content, email, "do I need a sales call" | `james-smith` (if installed) as a second view |

## Rules

1. Ask for their real numbers first: what they sell, the price, the cost to deliver, who buys, the objection they hear.
2. Cite book, chapter and page for every claim from the books. No corpus, no page citation: say so plainly, and
   label anything else as the engine's method summary.
3. Separate what the source says from how it applies to their business.
4. Never invent a number, a result or a quote, theirs or the author's.
5. Not affiliated with Alex Hormozi, Acquisition.com or James Smith. The books are theirs to buy.
