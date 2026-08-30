# `/content-pipeline capture <idea>`

A raw idea goes in, a classified stub comes out. Quick. The heavy work is
`develop`.

All commands run from their project folder. `SKILLS` below means
`~/.claude/skills/content-pipeline/scripts`.

## 1. Get the core

One or two sentences from what they said. Do not pad it.

## 2. Check for duplicates

```bash
python3 - <<'EOF'
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
from db import get_connection
conn = get_connection()
rows = conn.execute("""
    SELECT id, title, production_status FROM content_ideas
    WHERE title LIKE '%KEYWORD%' ORDER BY created_at DESC LIMIT 5
""").fetchall()
for r in rows: print(f"  #{r['id']} [{r['production_status']}] {r['title']}")
if not rows: print("  No duplicates.")
conn.close()
EOF
```

`KEYWORD` is the most distinctive word in the idea. If there is a match,
say so and ask whether to carry on or develop the existing one.

## 3. Classify

Read `content/strategy.md`. Decide:

- channel (their primary platform)
- format (one of the format types in strategy.md)
- content pillar (one of theirs)
- funnel position: awareness / consideration / conversion

Show the classification. Wait for a yes.

## 4. Store the stub

```bash
python3 - <<'EOF'
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
from db import get_connection
from writer import write_content_idea
idea = {
    "title": "TITLE",
    "description": "DESCRIPTION",
    "channel": "CHANNEL",
    "format_type": "FORMAT",
    "source_type": "manual",
    "content_pillar": "PILLAR",
    "funnel_position": "POSITION",
    "notes": "NOTES",
}
conn = get_connection()
print(f"Stored as stub #{write_content_idea(conn, idea)}")
conn.close()
EOF
```

## 5. Regenerate the pipeline view

```bash
python3 ~/.claude/skills/content-pipeline/scripts/generate_pipeline.py
```

## 6. Report

Stub number, channel, format, pillar. Then: "Run `/content-pipeline
develop #N` when you want the full concept."
