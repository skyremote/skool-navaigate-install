# `/content-pipeline schedule` (or `schedule review`)

Pick developed ideas, give them dates, work out when each has to be made.
Optional push to Notion. They pick; nothing is scheduled on their behalf.

All commands run from their project folder.

## Load

1. `content/strategy.md` for cadence and how they like to plan.
2. The pipeline:
   ```bash
   python3 - <<'EOF'
   import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
   from db import get_connection
   conn = get_connection()
   developed = conn.execute("""
       SELECT id, title, channel, format_type, priority_score, edit_turnaround_days,
              audience_segment, offer_alignment, created_at
       FROM content_ideas WHERE production_status = 'developed'
       ORDER BY COALESCE(priority_score, 0) DESC, created_at DESC""").fetchall()
   scheduled = conn.execute("""
       SELECT id, title, channel, format_type, film_by_date, publish_date, production_status
       FROM content_ideas WHERE production_status IN ('scheduled', 'filmed', 'editing')
       ORDER BY publish_date ASC""").fetchall()
   print("=== DEVELOPED (ready to schedule) ===")
   for r in developed:
       p = f"P{r['priority_score']}" if r["priority_score"] else "-"
       print(f"  #{r['id']} [{r['channel'] or '?'}] {r['title']} ({p}, {r['edit_turnaround_days'] or 0} days to make)")
   print("\n=== SCHEDULED ===")
   for r in scheduled:
       print(f"  #{r['id']} [{r['channel'] or '?'}] {r['title']} publish {r['publish_date'] or 'TBD'} ({r['production_status']})")
   conn.close()
   EOF
   ```
3. `content/offers-and-funnels.md` for campaigns with dates.

## Stage 1 — where they are

Scheduled and in-progress items with dates. Gaps against their cadence.
Channel mix against what they said they wanted. One compact table.

## Stage 2 — what is ready

Developed ideas ranked by priority: id, title, channel, format, priority,
days to make. Point at the gaps they would fill and any campaign they
line up with.

Ask: "Which ones, and what publish dates?" Wait.

## Stage 3 — dates

For each pick: `film_by_date = publish_date - edit_turnaround_days`. Flag
two things due to be made on the same day. Show the table: make-by,
publish, title, channel, format. Ask: "Does this work?" Wait.

## Stage 4 — write it

```bash
python3 - <<'EOF'
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
from db import get_connection
from writer import update_status
conn = get_connection()
update_status(conn, IDEA_ID, "scheduled", film_by_date="YYYY-MM-DD", publish_date="YYYY-MM-DD")
conn.close()
print("Scheduled.")
EOF
```

Notion, only if `NOTION_API_TOKEN` is set and they say yes:

```bash
python3 - <<'EOF'
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/skills/content-pipeline/scripts"))
from db import get_connection
from notion_sync import push_idea_to_notion
conn = get_connection()
for idea_id in [LIST_OF_IDS]:
    idea = dict(conn.execute("SELECT * FROM content_ideas WHERE id = ?", (idea_id,)).fetchone())
    page_id = push_idea_to_notion(idea)
    if page_id:
        conn.execute("UPDATE content_ideas SET notion_page_id = ? WHERE id = ?", (page_id, idea_id))
        conn.commit()
        print(f"  #{idea_id} -> Notion {page_id}")
conn.close()
EOF
```

Then `python3 ~/.claude/skills/content-pipeline/scripts/generate_pipeline.py`
and report: how many scheduled, the next make-by date and what it is.

## `schedule review`

Show everything scheduled or in progress. Flag overdue (make-by date
passed, still "scheduled"). Let them move items to filmed, editing,
published (`update_status` with the new status, `published_url` when
there is one). Mirror status changes to Notion with
`update_notion_status(page_id, status)` if configured.

## Rules

- Confirm before every write.
- Two things to make on one day: say so.
- A long video needs more lead time than a post. The turnaround table in
  `writer.py` (`FORMAT_TURNAROUND`) is theirs to edit.
