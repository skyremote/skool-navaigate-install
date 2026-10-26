"""Generate content/pipeline.md from the content database.

Renders all content ideas grouped by production status with key metadata.
Run after any content DB write to keep the browsable pipeline view current.

This is your "dashboard in markdown" — see your whole content pipeline
at a glance without running SQL queries.

Usage:
    python3 generate_pipeline.py
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from _workspace import workspace_root

WORKSPACE_ROOT = workspace_root()
DB_PATH = WORKSPACE_ROOT / "data" / "content.db"
OUTPUT_PATH = WORKSPACE_ROOT / "content" / "pipeline.md"

STAGE_ORDER = ["stub", "developed", "scheduled", "filmed", "editing", "published"]
STAGE_LABELS = {
    "stub": "Stubs (captured, needs development)",
    "developed": "Developed (full concept ready)",
    "scheduled": "Scheduled (has publish date)",
    "filmed": "Filmed / Created (in post-production)",
    "editing": "In Editing / Review",
    "published": "Published",
}


def generate(conn: sqlite3.Connection) -> str:
    """Generate the content pipeline markdown."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    def add(text=""):
        lines.append(text)

    add("# Content Pipeline")
    add()
    add(f"> Auto-generated from database. Last updated: {today}")
    add(
        "> Source: `data/content.db` | Regenerate: `python3 ~/.claude/skills/content-pipeline/scripts/generate_pipeline.py`"
    )
    add()

    # Summary counts
    counts = {}
    for row in conn.execute(
        "SELECT COALESCE(production_status, 'stub') as stage, COUNT(*) as cnt "
        "FROM content_ideas GROUP BY stage ORDER BY cnt DESC"
    ).fetchall():
        counts[row["stage"]] = row["cnt"]

    total = sum(counts.values())
    add(f"**Total ideas:** {total}")
    add()
    add("| Stage | Count |")
    add("|-------|-------|")
    for stage in STAGE_ORDER:
        cnt = counts.get(stage, 0)
        if cnt > 0:
            add(f"| {STAGE_LABELS.get(stage, stage)} | {cnt} |")
    # Any unknown stages
    for stage, cnt in counts.items():
        if stage not in STAGE_ORDER:
            add(f"| {stage} | {cnt} |")
    add()
    add("---")
    add()

    # Ideas by stage
    for stage in STAGE_ORDER:
        rows = conn.execute(
            """SELECT id, title, hook, channel, format_type, audience_segment,
                      content_pillar, funnel_position, priority_score, source_type,
                      production_status, created_at,
                      title_options, offer_alignment, film_by_date, publish_date
               FROM content_ideas
               WHERE COALESCE(production_status, 'stub') = ?
               ORDER BY COALESCE(priority_score, 0) DESC, created_at DESC""",
            (stage,),
        ).fetchall()

        if not rows:
            continue

        add(f"## {STAGE_LABELS.get(stage, stage)} ({len(rows)})")
        add()

        for row in rows:
            idea_id = row["id"]
            title = row["title"] or "Untitled"
            priority = row["priority_score"]
            source = row["source_type"] or "manual"
            channel = row["channel"] or "—"
            fmt = row["format_type"] or "—"
            audience = row["audience_segment"] or "—"
            pillar = row["content_pillar"] or "—"
            funnel = row["funnel_position"] or "—"
            created = (row["created_at"] or "")[:10]
            offer = row["offer_alignment"] or "—"

            priority_str = f"P{priority}" if priority else "—"
            add(f"### #{idea_id}: {title}")
            add(
                f"- **Priority:** {priority_str} | **Channel:** {channel} | "
                f"**Format:** {fmt} | **Source:** {source} | **Created:** {created}"
            )
            add(f"- **Audience:** {audience} | **Pillar:** {pillar} | **Funnel:** {funnel}")
            add(f"- **Offer:** {offer}")

            if row["hook"]:
                add(f"- **Hook:** {row['hook']}")

            if row["film_by_date"]:
                add(f"- **Film by:** {row['film_by_date']}")
            if row["publish_date"]:
                add(f"- **Publish:** {row['publish_date']}")

            if row["title_options"]:
                try:
                    titles = json.loads(row["title_options"])
                    if isinstance(titles, list) and titles:
                        add(f"- **Title options:** {len(titles)} variants")
                except (json.JSONDecodeError, TypeError):
                    pass

            add()

    return "\n".join(lines)


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'python3 ~/.claude/skills/content-pipeline/scripts/db.py' first to initialise.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    content = generate(conn)
    conn.close()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content)
    print(f"Pipeline written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
