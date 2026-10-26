# `/ai-landscape-monitor update` — the unattended doc update

Pull the live rankings, compare with what the docs say, research what
moved, rewrite only those docs. No questions, no stops. If nothing changed,
say so and exit.

Optional argument: one category (`text`, `code`, `vision`, `text-to-image`,
`image-edit`, `search`, `text-to-video`, `image-to-video`, `text-to-speech`,
`speech-to-text`). With a category given, always refresh that one.

## Categories and sources

- LMArena (`https://arena.ai/leaderboard/{category}`): text, code, vision,
  text-to-image, image-edit, search, text-to-video, image-to-video. Score is
  ELO, higher is better.
- TTS Arena V2 (`https://tts-agi-tts-arena-v2.hf.space/leaderboard`):
  text-to-speech. ELO.
- Voice Writer (`https://voicewriter.io/speech-recognition-leaderboard`):
  speech-to-text. WER %, lower is better.

## Phase 1 — pull live rankings

Fastest path: run the scanner first, it does the collection and the diff.

```bash
cd <their project>
python3 ~/.claude/skills/ai-landscape-monitor/scripts/scanner.py --force
```

Read `data/ai-scan-latest.json` (changes, categories, recommendation) and
`outputs/ai-landscape/<today>.md` (the full current rankings). If a
collector was skipped (page structure changed), fall back to `WebFetch` on
the source URL above and extract rank, model name, score, votes, provider
for the top 20.

If `OPENROUTER_API_KEY` is set, pricing for text and code models is in the
database:

```sql
SELECT model_name, price_input, price_output, context_length
FROM ai_models
WHERE source = 'openrouter'
  AND date = (SELECT MAX(date) FROM ai_models WHERE source = 'openrouter')
  AND category IN ('text-generation', 'text', 'code')
ORDER BY category, rank_in_category
LIMIT 30
```

## Phase 2 — read the current docs

For each `ai-docs/{category}/state-of-the-art.md`: if it exists, read the
`> Leader:` line. If it does not exist, mark the category `no_docs`.

## Phase 3 — diff

Per category compare live #1 with the documented #1, and live top 3 with
the documented top 3. Change types: `new_leader`, `new_top3`, `no_docs`.

No changes anywhere and no category argument: output "All docs current, no
ranking changes" and stop.

## Phase 4 — research the changes (parallel)

One subagent per changed category, run in parallel. Each researches the
top 2-3 models in its category and returns results only (writes nothing).

Agent brief:

```
Research [MODEL] for the [CATEGORY] category. It is #[RANK] on [SOURCE] with [METRIC] [SCORE] and [VOTES] votes.

Return, do not write files:
1. What it is, who makes it, what is different about it (2-3 sentences)
2. Best for (3-4 bullets) and not ideal for (1-2 bullets)
3. Pricing, exact figures per unit (tokens, images, seconds, characters, hours)
4. The exact API model ID string
5. Working Python integration code with the provider's official SDK: import, auth, one call
6. What people on Reddit and X say (2-3 sentences, what they like and what they complain about)
7. Tips and gotchas (2-3 bullets: rate limits, quirks)
8. The official API docs URL

Use WebSearch for "[model] API pricing", "[model] documentation", "[model] review", "[model] reddit";
WebFetch the official docs page for the model ID and code.
```

Document top models from two or three different providers per category
even when one provider holds every top spot.

## Phase 5 — write the docs

`ai-docs/{category}/state-of-the-art.md`, one per researched category.

LMArena categories:

```markdown
# [Category] — State of the Art

> Last updated: YYYY-MM-DD
> Source: [LMArena](https://arena.ai/leaderboard/{category}) | crowdsourced, [votes]+ votes
> Leader: [Model] ([Provider]) — ELO: [score] | [votes] votes

## Quick pick

| Use case | Model | Provider | API model ID | Cost | ELO |
|----------|-------|----------|--------------|------|-----|
| [primary use] | [model] | [provider] | `[id]` | $X/M in, $Y/M out | [score] |
| Budget option | [model] | [provider] | `[id]` | $X/M in, $Y/M out | [score] |

## Rankings (LMArena top 10)

| # | Model | Provider | ELO | Votes |
|---|-------|----------|-----|-------|

## Top models

### 1. [Model] — [Provider]
[overview, pricing, integration code, tips]

## Links
- [LMArena leaderboard](https://arena.ai/leaderboard/{category})
```

Text-to-speech: same shape, source TTS Arena V2, cost per 1K characters,
columns `ELO | Win rate | Votes`.

Speech-to-text: same shape, source Voice Writer, `> Leader: ... — WER: X% | $Y/hr`,
quick-pick columns `WER | Cost ($/hr)`, rankings columns
`System | WER | Std dev | Price/hr | Provider`.

Then update `ai-docs/README.md`: leader per category, the quick-pick
matrix, the last-scan date, one changelog row.

## Phase 6 — report

Categories checked, changes found, docs written. Or "no changes".

## Rules

- No stops, no questions. This runs unattended.
- The leaderboard numbers are the truth; opinions do not override them.
- Nothing changed: say so and stop. Do not rewrite docs for the sake of it.
- Every doc must carry working code and the exact model ID string.
- Pricing in USD.
- TTS is ELO (higher wins). STT is WER (lower wins). Do not mix them up.
