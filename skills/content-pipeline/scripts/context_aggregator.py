"""7-day context aggregator for content development.

Assembles the recent context window that develop uses to make
informed content decisions. Pulls from:
  - Recent published content (published_content table, plus a youtube_videos table if they have one)
  - Recent meetings (a meetings table, if they have one)
  - Content pipeline state (stubs, developed, scheduled ideas)

Returns structured dict that can be formatted into a prompt context block.

Usage:
    python3 context_aggregator.py              # Print context summary
    python3 context_aggregator.py --full       # Print full formatted context

    # In code:
    from scripts.context_aggregator import build_context_window, format_context_for_prompt
    context = build_context_window(days=7)
    prompt_block = format_context_for_prompt(context)
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

from _workspace import workspace_root

WORKSPACE_ROOT = workspace_root()
DB_PATH = WORKSPACE_ROOT / "data" / "content.db"

def _get_extra_connection() -> sqlite3.Connection | None:
    """Look for another SQLite file in data/ that holds published videos or meetings.
    Returns None if there is none."""
    # Any other .db under data/ with youtube_videos or meetings tables
    data_dir = WORKSPACE_ROOT / "data"
    if not data_dir.exists():
        return None
    for db_file in sorted(data_dir.glob("*.db")):
        if db_file == DB_PATH:
            continue
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        # Check if it has tables we need
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        if "youtube_videos" in tables or "meetings" in tables:
            return conn
        conn.close()
    return None


def build_context_window(days: int = 7) -> dict:
    """Build the context window from the database(s).

    Returns:
        {
            "recent_content": [{"title", "platform", "published_date", "url", "description"}],
            "recent_meetings": [{"title", "date", "summary", "duration_minutes"}],
            "pipeline_state": {
                "stubs": [{"id", "title", "channel", "format_type", "created_at"}],
                "developed": [{"id", "title", "channel", "format_type"}],
                "scheduled": [{"id", "title", "channel", "film_by_date", "publish_date"}],
            },
            "window_start": "YYYY-MM-DD",
            "window_end": "YYYY-MM-DD",
        }
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    window_end = datetime.now().strftime("%Y-%m-%d")
    window_start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # --- Recent published content (from our table) ---
    recent_content = []
    try:
        rows = conn.execute(
            """SELECT platform, title, published_date, url, description
            FROM published_content
            WHERE published_date >= ?
            ORDER BY published_date DESC""",
            (window_start,),
        ).fetchall()
        for r in rows:
            recent_content.append(
                {
                    "title": r["title"],
                    "platform": r["platform"],
                    "published_date": r["published_date"],
                    "url": r["url"],
                    "description": r["description"],
                }
            )
    except sqlite3.OperationalError:
        pass  # Table doesn't exist yet

    # --- Another database with published videos (and transcripts), if they have one ---
    extra_db = _get_extra_connection()
    if extra_db:
        try:
            tables = [
                r[0]
                for r in extra_db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ]

            # YouTube videos with transcripts
            if "youtube_videos" in tables:
                # Check if transcript_text column exists
                cols = [
                    r[1]
                    for r in extra_db.execute(
                        "PRAGMA table_info(youtube_videos)"
                    ).fetchall()
                ]
                has_transcripts = "transcript_text" in cols

                if has_transcripts:
                    videos = extra_db.execute(
                        """SELECT title, published_date, views,
                                  SUBSTR(transcript_text, 1, 3000) as transcript_excerpt
                        FROM youtube_videos
                        WHERE published_date >= ?
                          AND transcript_text IS NOT NULL AND transcript_text != ''
                        ORDER BY published_date DESC""",
                        (window_start,),
                    ).fetchall()
                else:
                    videos = extra_db.execute(
                        """SELECT title, published_date, views
                        FROM youtube_videos
                        WHERE published_date >= ?
                        ORDER BY published_date DESC""",
                        (window_start,),
                    ).fetchall()

                for v in videos:
                    entry = {
                        "title": v["title"],
                        "platform": "youtube",
                        "published_date": v["published_date"],
                        "url": None,
                        "description": None,
                        "views": v["views"],
                    }
                    if has_transcripts and v["transcript_excerpt"]:
                        entry["transcript_excerpt"] = v["transcript_excerpt"]
                    recent_content.append(entry)
        except sqlite3.OperationalError:
            pass

    # Sort all content by date
    recent_content.sort(key=lambda x: x.get("published_date", ""), reverse=True)

    # --- Recent meetings, if a meetings table exists ---
    recent_meetings = []
    if extra_db:
        try:
            tables = [
                r[0]
                for r in extra_db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ]
            if "meetings" in tables:
                meetings = extra_db.execute(
                    """SELECT title, date, summary, duration_minutes
                    FROM meetings
                    WHERE date >= ?
                      AND summary IS NOT NULL AND summary != ''
                    ORDER BY date DESC
                    LIMIT 15""",
                    (window_start,),
                ).fetchall()
                for m in meetings:
                    recent_meetings.append(
                        {
                            "title": m["title"],
                            "date": m["date"],
                            "summary": m["summary"],
                            "duration_minutes": m["duration_minutes"],
                        }
                    )
        except sqlite3.OperationalError:
            pass

    if extra_db:
        extra_db.close()

    # --- Pipeline state (always from content DB) ---
    pipeline_rows = conn.execute(
        """SELECT id, title, channel, format_type, production_status,
                  created_at, film_by_date, publish_date
        FROM content_ideas
        WHERE production_status IN ('stub', 'developed', 'scheduled')
        ORDER BY CASE production_status
            WHEN 'scheduled' THEN 1
            WHEN 'developed' THEN 2
            WHEN 'stub' THEN 3
        END, created_at DESC"""
    ).fetchall()

    pipeline_state = {"stubs": [], "developed": [], "scheduled": []}
    for r in pipeline_rows:
        entry = {
            "id": r["id"],
            "title": r["title"],
            "channel": r["channel"],
            "format_type": r["format_type"],
        }
        status = r["production_status"]
        if status == "stub":
            entry["created_at"] = r["created_at"]
            pipeline_state["stubs"].append(entry)
        elif status == "developed":
            pipeline_state["developed"].append(entry)
        elif status == "scheduled":
            entry["film_by_date"] = r["film_by_date"]
            entry["publish_date"] = r["publish_date"]
            pipeline_state["scheduled"].append(entry)

    conn.close()

    return {
        "recent_content": recent_content,
        "recent_meetings": recent_meetings,
        "pipeline_state": pipeline_state,
        "window_start": window_start,
        "window_end": window_end,
    }


def format_context_for_prompt(context: dict) -> str:
    """Format context dict into a prompt-ready markdown block."""
    sections = []
    sections.append(
        f"## 7-Day Context Window ({context['window_start']} to {context['window_end']})"
    )

    # Recent content
    content = context["recent_content"]
    sections.append(f"\n### Recent Published Content ({len(content)})")
    if content:
        for c in content:
            platform = c.get("platform", "?")
            views = f" — {c['views']:,} views" if c.get("views") else ""
            sections.append(
                f"\n**{c['title']}** [{platform}] ({c.get('published_date', '?')}){views}"
            )
            excerpt = c.get("transcript_excerpt", "")
            if excerpt:
                if len(excerpt) > 2000:
                    excerpt = excerpt[:2000] + "..."
                sections.append(f"<transcript>\n{excerpt}\n</transcript>")
    else:
        sections.append("No content published in this window.")

    # Recent meetings
    meetings = context["recent_meetings"]
    sections.append(f"\n### Recent Meetings ({len(meetings)})")
    if meetings:
        for m in meetings:
            duration = (
                f" ({m['duration_minutes']}min)" if m.get("duration_minutes") else ""
            )
            sections.append(f"\n**{m['title']}** ({m['date']}){duration}")
            summary = m.get("summary", "")
            if summary:
                if len(summary) > 1000:
                    summary = summary[:1000] + "..."
                sections.append(summary)
    else:
        sections.append(
            "No meetings in this window."
        )

    # Pipeline state
    ps = context["pipeline_state"]
    sections.append("\n### Content Pipeline State")

    scheduled = ps["scheduled"]
    sections.append(f"**Scheduled ({len(scheduled)}):**")
    if scheduled:
        for s in scheduled:
            dates = ""
            if s.get("film_by_date"):
                dates += f" | Film by: {s['film_by_date']}"
            if s.get("publish_date"):
                dates += f" | Publish: {s['publish_date']}"
            channel = f" [{s.get('channel', '?')}]" if s.get("channel") else ""
            sections.append(f"- #{s['id']} {s['title']}{channel}{dates}")
    else:
        sections.append("- (none)")

    developed = ps["developed"]
    sections.append(f"**Developed ({len(developed)}):**")
    if developed:
        for d in developed:
            channel = f" [{d.get('channel', '?')}]" if d.get("channel") else ""
            fmt = f" ({d.get('format_type', '')})" if d.get("format_type") else ""
            sections.append(f"- #{d['id']} {d['title']}{channel}{fmt}")
    else:
        sections.append("- (none)")

    stubs = ps["stubs"]
    sections.append(f"**Stubs ({len(stubs)}):**")
    if stubs:
        for s in stubs:
            channel = f" [{s.get('channel', '?')}]" if s.get("channel") else ""
            fmt = f" ({s.get('format_type', '')})" if s.get("format_type") else ""
            sections.append(f"- #{s['id']} {s['title']}{channel}{fmt}")
    else:
        sections.append("- (none)")

    return "\n".join(sections)


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'python3 ~/.claude/skills/content-pipeline/scripts/db.py' first to initialise.")
        sys.exit(1)

    ctx = build_context_window(days=7)
    print(f"Recent content: {len(ctx['recent_content'])}")
    print(f"Recent meetings: {len(ctx['recent_meetings'])}")
    print(
        f"Pipeline — Stubs: {len(ctx['pipeline_state']['stubs'])}, "
        f"Developed: {len(ctx['pipeline_state']['developed'])}, "
        f"Scheduled: {len(ctx['pipeline_state']['scheduled'])}"
    )

    if "--full" in sys.argv:
        prompt = format_context_for_prompt(ctx)
        print(f"\nPrompt length: {len(prompt)} chars (~{len(prompt) // 4} tokens)")
        print("\n" + prompt)
    else:
        print("\nRun with --full to see the formatted context block.")
