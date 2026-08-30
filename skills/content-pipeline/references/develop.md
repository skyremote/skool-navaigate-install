# `/content-pipeline develop #N` (or a raw idea)

A stub becomes a full concept: who it is for, why they are the one to say
it, which offer it feeds, and the packaging. Two stops for confirmation.
Never blast through.

All commands run from their project folder.

## Load

1. The idea. `#N`: `SELECT * FROM content_ideas WHERE id = N`. Raw text:
   capture it first (`references/capture.md`), then develop.
2. The strategy docs, always:
   - `content/strategy.md`: platform, cadence, pillars, competitors
   - `content/brand-and-audience.md`: positioning, segments, proof
   - `content/offers-and-funnels.md`: offers, funnel, CTAs
   - `content/packaging-strategy.md` if it exists (YouTube)
3. The last seven days:
   ```bash
   python3 ~/.claude/skills/content-pipeline/scripts/context_aggregator.py --full
   ```
   That is what they published, what meetings said, what is already
   queued. Use it: "you posted about X on Tuesday, so this one should
   angle towards Y."

## Stage 1 — positioning (stop and confirm)

1. Audience: which of their segments, what problem it solves for them
2. Authority: why they are the voice on this (from brand-and-audience.md)
3. Offer: which offer it leads to and how (from offers-and-funnels.md)
4. Fit: how it connects to what they published this week
5. Funnel position: awareness / consideration / conversion
6. Pillar

Show it in a few lines. Ask: "Does this positioning feel right?" Wait.

## Stage 2 — packaging (stop and confirm)

YouTube (packaging-strategy.md exists):
1. 3-5 title options, each using two or more of the title elements, with
   the elements named in brackets
2. 2-3 thumbnail concepts: emotion, 2-4 word overlay that says something
   the title does not, one visual element, layout
3. Hook: how title, thumbnail and the first thirty seconds work together

LinkedIn:
1. 3-5 first lines (what shows before "see more")
2. The visual: image, carousel or video still
3. Format and why: post, article, carousel, video
4. 3-5 hashtags

Any platform: the text and the visual must carry different information.

Ask: "Which direction is strongest?" Wait.

## Stage 3 — store

Priority score 1-10 from: strategic value, timeliness, demand signals in
the context window, production effort, whether it is already covered.

```bash
python3 - <<'EOF'
import sys, os, json; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
from db import get_connection
from writer import write_developed_idea
idea = {
    "id": EXISTING_ID_OR_NONE,
    "title": "Chosen title",
    "hook": "Opening hook",
    "description": "Full concept",
    "audience": "Who it is for",
    "format_type": "FORMAT",
    "channel": "CHANNEL",
    "topics": "comma,separated",
    "source_type": "develop",
    "title_options": json.dumps([{"text": "Title A", "elements": ["curiosity", "authority"]}]),
    "thumbnail_concepts": json.dumps([{"emotion": "confidence", "text_overlay": "2-4 words", "visual": "..."}]),
    "funnel_position": "awareness",
    "content_pillar": "PILLAR",
    "audience_segment": "SEGMENT",
    "offer_alignment": "OFFER",
    "cta_path": "How the CTA lands",
    "proof_points": json.dumps([{"type": "result", "text": "Named number"}]),
    "authority_angle": "Why they own this",
    "production_status": "developed",
    "priority_score": 8,
    "research_json": json.dumps({"context_window": "7d"}),
    "developed_by": "develop",
}
conn = get_connection()
print(f"Saved as concept #{write_developed_idea(conn, idea)}")
conn.close()
EOF
```

Then write `content/concepts/{id}-{slug}.md` with the whole concept, and:

```bash
python3 ~/.claude/skills/content-pipeline/scripts/generate_pipeline.py
```

Report: concept number, the doc path, title or hook, channel, format,
priority. "Run `/content-pipeline schedule` when you want to put it on
the calendar." If it is a video and they want the thumbnail made, that is
`/thumbnails` with the concept.
