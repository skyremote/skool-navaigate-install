# Research method — running a rigorous multi-source pass

How to run a deep, multi-source research pass with **our** existing agents and the
free sources in this skill. This is **method, not machinery** — it does not install
or replace an orchestrator. Drive it with:

- the **`deep-research` harness** (the built-in slash command) for a single-session
  fan-out and synthesis, or
- **`chief-of-staff`** when the question spans ventures and you want it to spawn
  parallel topic agents itself (only the main session can spawn subagents).

The sources it pulls from (free/keyless, or using keys we already have — except
Supadata, which is paid):

| Source | Script | Best for |
|--------|--------|----------|
| Reddit | `scripts/sources/reddit.py` | practitioner sentiment, lived failure modes |
| Academic | `scripts/sources/academic.py` | primary research, citation-weighted credibility |
| Substack | `scripts/sources/substack.py` | named-author long-form analysis |
| Supadata *(paid, metered)* | `scripts/sources/supadata.py` | video/transcript evidence (YouTube search + multi-platform transcripts) — use only when video evidence is wanted |
| X-Search *(paid; dormant until xAI funded)* | `scripts/sources/xsearch.py` | real-time X/Twitter sentiment + recent posts (xAI Grok X Search tool) — wired but **dormant** until the xAI account has billing/credit (console.x.ai) |
| Exa | `scripts/webscrape.py search` | semantic discovery across the open web |
| Firecrawl | `scripts/webscrape.py scrape` | reading JS-heavy / dynamic pages |

> **Supadata is credit-metered (paid).** Its `research` returns the same bundle
> shape as the others (`{topic, search_results_count, search_results,
> extracted_count, extracted_transcripts}`), so topic agents consume it unchanged —
> but only reach for it when video/transcript evidence is specifically wanted, not
> on every pass. Keep `--videos` small.
>
> **X-Search** (`scripts/sources/xsearch.py`, paid) is **wired but dormant** —
> its `research` returns the same bundle shape, but every call is rejected at xAI's
> billing gate until the account has credit (console.x.ai). It activates with no code
> change once funded; treat it as available-but-paused for now. **Podcast** has no
> dedicated endpoint — covered by Supadata YouTube search + transcript (or a direct
> media-file URL).

---

## The flow

```
Scope interview          (3-4 questions — never skip)
      │
Recon pass               (one shallow sweep per source; rate each HOT / WARM / COLD)
      │
HUMAN CHECKPOINT         (review the signal map; confirm the topic-agent roster)
      │
Parallel topic agents    (one per angle; breadth-first then depth-first; score every source)
      │
Critic pass              (review-only; no new searching; flag the 10 failure modes)
      │
Synthesis                (confidence-labelled master report; do NOT flatten confidence)
```

For a first or quick run, collapse it: skip recon and critic, run 2-3 topic agents
straight from the scope answers, then synthesise. Add recon + critic once the core
loop is trusted or when the stakes justify it.

### Scope interview (ask every time)
1. **Core question** — what are you actually trying to find out?
2. **Time period** — how recent must it be? (30d / 90d / 1yr / any)
3. **Starting points** — known people, publications, repos, subreddits to prioritise?
4. **Depth vs breadth** — one sharp angle, or a broad survey?

### Recon → HOT / WARM / COLD
Run **one or two** shallow searches per source on the topic, then rate each source:

- **HOT** — meaningful signal, active discussion, multiple credible sources → send a
  topic agent here.
- **WARM** — some signal, worth a deeper look.
- **COLD** — little or nothing relevant → don't waste an agent on it.

Output a **signal map** (source → HOT/WARM/COLD + one-line reason), 3-8 **key people**
surfacing, the most promising **threads/URLs**, 4-8 candidate **angles**, and the
**queries** that worked. This is what the human approves at the checkpoint.

### Parallel topic agents
One agent per approved angle. To get true parallelism, **launch them in a single
message** (multiple agent calls at once) — sequential launches serialise. Typical
rosters:

- *Tooling/tech trends:* (1) what practitioners ship & what breaks, (2) thought
  leaders & their frameworks, (3) research frontier vs production reality, (4)
  ecosystem — emerging / consolidating / dying.
- *A person's work & influence:* (1) their primary work, (2) reception & criticism,
  (3) intellectual lineage.
- *Market landscape:* (1) incumbents, (2) challengers, (3) practitioner sentiment,
  (4) research direction, (5) business-model & pricing.

---

## Source-scoring rubric (score every source before going deep)

```
RECENCY:      Primary work (any date): 2 | <30d: 3 | <90d: 2 | <1yr: 1 | older current-tech: 0
SOURCE TYPE:  Primary/academic: 3 | Named practitioner: 2 | Tech journalism: 1 | Aggregator: 0
SPECIFICITY:  Numbers / code / failure modes: 2 | Some specifics: 1 | Generic: 0
INDEPENDENCE: Not citing existing sources: 1 | Cites existing: 0.5 | Same org: 0

TOTAL ≥ 5: pursue | 3-4: include with a caveat | < 3: drop
```

**Domain pre-filter before fetching.** High-value: `arxiv.org`, `github.com/issues`,
`github.com/discussions`, official docs, known practitioners. Low-value: SEO farms,
`/blog/ai-guide-YYYY` URL patterns, AI-content-pivot domains, Medium (unless a known
author).

**Low engagement ≠ low quality.** A practitioner post with zero likes but specific
version numbers and failure modes may be the highest-signal find. Score specificity,
not popularity.

**Triangulation rule.** No factual claim enters a report on **one** source unless
labelled. Independent = not same org, not one citing the other, not published within
7 days of each other. Labels: `[SINGLE SOURCE — NEEDS VERIFICATION]`, `[UNVERIFIED]`,
`[CONFLICTING SOURCES EXIST]`.

**Negative rejection.** If no reliable source supports a claim, say so. Do not
synthesise from poor sources to fill a gap. "We found no reliable primary source for
X" is a valid, valuable finding.

---

## Prompt templates

Populate the `{VARS}` from the scope interview and recon, then hand each block to a
subagent. `{SESSION_SLUG}` = `{YYYY-MM-DD}-{kebab-topic}`. These mirror the rubric
above; tune freely per run.

### Recon prompt

```
You are a research recon agent doing a fast, SHALLOW sweep to find where the signal
lives. You are NOT researching deeply.

TOPIC: {TOPIC_BRAIN_DUMP}
TIME PERIOD: {TIME_PERIOD}    STARTING POINTS: {STARTING_POINTS}

Tools (all free; run 1-2 searches each):
  Reddit:    python3 scripts/sources/reddit.py search "{q}" --time month --limit 10
             python3 scripts/sources/reddit.py subreddits "{topic}" --limit 5
  Academic:  python3 scripts/sources/academic.py search "{q}" --limit 5 --from-year 2024
  Substack:  python3 scripts/sources/substack.py search "{q}" --limit 5
  Web (Exa): python3 scripts/webscrape.py search "{q}" --num 8

Method: 1-2 searches per source. Rate each source HOT / WARM / COLD for THIS topic.

Return a signal map:
1. Source Signal Map — HOT/WARM/COLD per source + one-line reason
2. Key People — 3-8 practitioners, with source and why they look credible
3. Key Threads/Sources — most promising URLs, one line each
4. Emerging Angles — 4-8 distinct angles worth a dedicated agent
5. Query Intelligence — search terms that worked
6. Time-Period Assessment — hot or cold topic now? where is the freshest primary work?
```

### Topic-agent prompt

```
You are a deep recursive research agent investigating {TOPIC_ANGLE} within the goal
below. Follow signal wherever it leads.

BIG PICTURE: {TOPIC_BRAIN_DUMP}
YOUR ANGLE: {TOPIC_ANGLE}
TIME PERIOD: {TIME_PERIOD}  (recent ≠ better; a primary source from 2022 beats last
week's AI commentary on it — optimise for PRIMARY sources)
RECON: hot sources = {RECON_HOT}; key people = {RECON_PEOPLE}; queries = {RECON_QUERIES}

Tools (add --json when you need to parse fields):
  Reddit    scripts/sources/reddit.py {search|thread|research} ...
  Academic  scripts/sources/academic.py {search|paper|citations|pdf|research} ...
  Substack  scripts/sources/substack.py {search|archive|post|research} ...
  Supadata  scripts/sources/supadata.py {search|transcript|metadata|research} ...  (PAID/metered — only when video evidence is wanted; keep --videos small)
  Exa       scripts/webscrape.py search "{q}" [--text --max-chars N --include-domains ...]
  Firecrawl scripts/webscrape.py scrape "{url}" [--wait 3000]

Method:
  R1 Platform dip — 3-5 query variants (technical / failure modes / practitioner /
     academic / recent); 1-2 searches per source; note which sources have signal.
  R2 Signal chase — for top hits: pull a person's full output; extract full threads
     and follow cited sources; get a paper's full text + its forward citations; read
     a repo's issues/discussions. Cross-reference a find from one source on the others.
  R3 Contradiction search — actively search AGAINST your strongest findings:
     "{finding} is wrong", "problems with {tool}", "{person} criticism".
  Repeat to 3+ levels or clear diminishing returns.

SCORE EVERY SOURCE before going deep (RECENCY/SOURCE/SPECIFICITY/INDEPENDENCE; ≥5
pursue, 3-4 caveat, <3 drop). Triangulate: no claim on one source without a label.
Negative rejection: if no reliable source, say so — never paper over a gap.

For anyone cited 3+ times, add a source profile: who they are / what they've shipped,
platform & audience, biases / commercial interest, why credible on THIS topic.

Output a report:
  # {TOPIC_ANGLE}
  ## Executive Summary (3-5 sentences: top finding, biggest unknown)
  ## Key Findings (each: claim + evidence + Confidence High/Med/Low + Based on: src1+src2)
  ## Source Profiles (for 3+ citation people)
  ## Cross-Source Validation (findings confirmed by 2+ independent sources)
  ## Tensions & Contradictions (where sources disagree — analyse WHY)
  ## Primary Sources vs Commentary
  ## Gaps & Negative Rejections
  ## All Citations (table: Source | Type | Signal Score | URL)
Include ALL source URLs. Never summarise a source you didn't actually read.
```

### Critic prompt (review-only — no searching, no fetching)

```
You are a research critic. Read all topic-agent reports and flag quality problems
before synthesis. You do NOT search, fetch, or produce new research.

TOPIC: {TOPIC_BRAIN_DUMP}   REPORTS: {LIST_OF_AGENT_REPORTS}

Flag each, citing the exact report + claim:
  1. Missing source profile (person cited 3+ times, no profile)
  2. Echo chamber ("independent" sources tracing to the same 2-3 people / one org → ONE data point)
  3. Claim-weight mismatch (big claim, low-credibility sources only)
  4. Unlabeled single-source claim
  5. Recency bias (recent AI summary used where older primary work exists)
  6. Negative-rejection failure (gap synthesised over instead of flagged [UNVERIFIED])
  7. Unsupported generalisation (broad claim, no specific evidence)
  8. AI-content signals (5-7 parallel bullets, "What is X?/Why does X matter?" headers,
     no byline, tools described with no failure modes, "comprehensive solution")
  9. Cross-report contradiction (two agents, opposing conclusions on the same fact)
 10. Verification need (does it need a follow-up search, or just a label change?)

Output: Summary · Critical Flags (fix before synthesis) · Minor Flags · Cross-Report
Contradictions · Verification Queue.
```

### Synthesis prompt

```
You are the synthesis agent. Produce ONE authoritative master report from the topic
reports and the critic notes.

TOPIC: {TOPIC_BRAIN_DUMP}   TIME PERIOD: {TIME_PERIOD}
INPUTS: {LIST_OF_AGENT_REPORTS} + critic notes

Method: read everything first. Map themes across reports (high-confidence signal),
contradictions, critic-flagged gaps, single-source claims needing labels. Weight
confidence by: how many independent sources confirm it, source tier (primary/
practitioner > aggregator), critic flags, and cross-source confirmation (Reddit +
academic + Substack > any one). DO NOT flatten everything to one confidence level —
a synthesis that treats everything as equal is worse than none.

Output:
  ## The Short Version (5-10 bullets, each labelled [HIGH] / [MEDIUM] / [LOW/SINGLE SOURCE])
  ## High-Confidence Findings (2+ independent sources; what, why confident, which sources)
  ## Medium-Confidence Findings (what + the caveat)
  ## Tensions & Contradictions (the tension, why it exists, what would resolve it)
  ## Key People & Sources (consolidated profiles, ranked citations × credibility × independence)
  ## Source Signal Map (table: Source | Signal Level | Best use for this topic)
  ## What We Don't Know (gaps, [UNVERIFIED], critic verification queue)
  ## Recommended Next Steps
  ## Source Registry (master table: Source | Type | Signal Score | Report(s) | URL)
```

---

## Persistence

Sources return to **stdout / files** only. Whether to persist runs to a database is a
separate, deliberate decision — not wired here. For now, write topic reports and the
synthesis to a session folder and link to them; do not add a DB dependency.
