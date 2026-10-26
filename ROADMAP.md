# YOUR AIOS 2.0 roadmap v1

Phase 1 ships the start plugin and brain pack only. Every other row below is
planned. Each future pack declares `aios` as a dependency; it can add another
pack dependency only when its job requires it. Installing a pack does not prove
a member has finished a lesson. The start skill follows the member's progress.

## Twelve modules

| Module | Lesson | Pack | Phase 1 |
|---|---|---|---|
| 1 | Start here: one loop, small context, checks it can run | aios | Shipped for local review |
| 2 | Your folders and your rules | aios-rules | Planned: AGENTS.md, short rules, CLAUDE.md bridge |
| 3 | The harnesses | aios-harnesses | Planned: Claude Code, Codex, Cursor, Grok Bot |
| 4 | bb as the cockpit | aios-bb | Planned: threads, sections, kanban, inline output |
| 5 | Memory you own | aios-brain | Shipped for local review |
| 6 | Skills that earn their place | aios-skills-kit | Planned: small skills, descriptions, evals |
| 7 | Agents without sprawl | aios-agents | Planned: one loop first, delegation when justified |
| 8 | Make it verifiable | aios-verify | Planned: tests, reviews, REVIEW.md, hooks |
| 9 | Working methods | aios-methods | Planned: interview, loops, worktrees, GSD, compound engineering |
| 10 | Models, effort and cost | aios-models | Planned: model choice, effort, subscription costs |
| 11 | Ship it to others | aios-ship-it | Planned: member-owned plugins and cross-harness installs |
| 12 | The shelf | Optional packs below | Planned; one tool at a time |

## Module 12 shelf

| Pack | First useful job | Boundary |
|---|---|---|
| aios-video | Cut a recording and prepare a film | Generic cutroom/NavMotion process; member media |
| aios-decks | Build and verify a presentation | Member brand and figures |
| aios-invoices | Build an invoice from member details | No shared tax, register or bank details |
| aios-voice | Write in the member's voice and add narration | Member samples and authorised voice account |
| aios-design | Thumbnails, diagrams, frontend design, design rules, charts | Check corpus count/licence before shipping |
| aios-research | Search, extract, podcasts, transcripts, ask your numbers | Member sources and optional paid keys |
| aios-content | Content coach, pipeline, daily brief and executive briefs | Member brand, numbers and accounts |

The audit keeps "Ask your numbers" on the shelf. It belongs to aios-research as
an optional data lesson rather than disappearing because there is no core data
module. The old Social Content Psychology and Chart gallery lessons stay under
content/design; neither is a separate 1.x skill directory.

## Every old skill

The source is the 25 October classroom audit: 11 lessons kept, 13 updated and
four retired. Lessons and skills are different inventories: all **28** skill
directories from the old repository are mapped here. "Keep" retains the method,
with install instructions and private-data checks updated when its pack ships.
No planned skill is exposed by the phase 1 marketplace.

| Old skill | Decision | 2.0 home and audit reason |
|---|---|---|
| aios | Keep, rewrite | aios, M1: keep empty/halfway/already running; replace five layers with twelve modules |
| aios-coach | Retire standalone install | aios, M1 guidance and M11 packaging example; audit identifies its repeated old closing link, not a requirement for another hosted app |
| install-crew | Retire standalone install | M7 aios-agents: fold in when delegation earns its place, following retired lesson 6 |
| layer-1 | Merge | M2 aios-rules: folders, short AGENTS.md and CLAUDE.md bridge |
| layer-2 | Merge | M12 aios-research, Ask your numbers: keep the data lesson |
| layer-3 | Split and merge | M5 aios-brain capture; M3 aios-harnesses Grok Bot; M12 aios-research tools |
| layer-4 | Merge | M9 aios-methods: task audit, schedules and a check after each run |
| layer-5 | Retire duplicate index | M12 shelf in aios; retired lesson 11 repeats the shelf |
| your-brain | Merge, rebuild | M5 aios-brain: generic local memory, optional own-account sync |
| your-voice | Keep | M12 aios-voice: member samples and calibration |
| your-ops | Keep process | M12 aios-invoices: member-owned invoice builder |
| thumbnails | Keep | M12 aios-design: image first, real headline layer after |
| diagrams | Keep | M12 aios-design: render, inspect, fix |
| web-scrape | Keep | M12 aios-research: web search/extraction; honest costs |
| podcasts | Keep | M12 aios-research: find, rank, then retrieve words |
| transcripts | Keep | M12 aios-research: general media transcript workflow; M5 brain keeps saved YouTube captions |
| deep-research | Keep, update title | M12 aios-research: remove emoji from the old lesson title |
| daily-brief | Keep, move | M12 aios-content; capture integration can depend on aios-brain when needed |
| ai-landscape-monitor | Merge | M10 aios-models: verify current model information, avoid stale counts |
| content-pipeline | Keep | M12 aios-content: capture, develop, schedule |
| writing-style | Keep | M12 aios-content: editing pass; personal voice remains aios-voice |
| new-app | Merge | M9 aios-methods: interview, plan, phases and a check per phase |
| new-capability | Merge | M6 aios-skills-kit: short skill, three evals and no-skill baseline |
| frontend-design | Keep | M12 aios-design: make choices, build and review |
| exec-brief | Keep | M12 aios-content: member figures and decision papers |
| design-brain | Keep, verify | M12 aios-design: check corpus/licence and count before release |
| content-coach | Keep | M12 aios-content: retain the method as a skill |
| hormozi | Merge | Optional M9 aios-methods business workbench; member's own books, no automatic agent |

The aios-coach retirement is a phase 1 packaging interpretation, recorded here
for review: the audit flags its stale repeated footer but does not explicitly
retire that skill. No live lesson or member installation has been changed.

## Version and migration boundary

The new manifests are 2.0.0 under plugins/aios and plugins/aios-brain. The archived
first-generation files remain in legacy/v1. Their original manifest actually
says **0.1.0** in this checkout; "1.x" in the brief names the old generation,
not an invented historical release. Original source commit: f305917.

2.0 uses new plugin IDs. It never runs an automatic old-to-new installer, removes
old user skills or edits an existing member's data. Old cached installations
remain as installed. A future public release must decide how long to retain the
old marketplace entry or point legacy members to a pinned ref; changing the
marketplace on the default branch is deliberately outside phase 1.

## Three decisions before phase 2

1. Confirm the next build order: rules, harnesses and bb before the remaining core
   modules, or bring skills/verify forward. Only start and brain are built now.
2. Confirm the old-generation support and release policy: keep a separate legacy
   catalogue/ref, set its support period, and decide how members opt into 2.0.
   Also approve folding the standalone hosted coach into the path.
3. Choose the first shelf releases and their order: video, decks and invoices
   as proposed, or a different priority. Scheduled capture and managed two-machine
   onboarding remain separate future proposals to scope; local memory stays the default.
