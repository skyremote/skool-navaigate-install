"""Content Pipeline writer — CRUD functions for the content_ideas table.

Provides three levels of writing:
  1. write_content_idea()  — lightweight capture (stub creation)
  2. write_developed_idea() — full concept with packaging and positioning
  3. update_status()        — status transitions with optional field updates

Plus a helper for logging published content.

Usage:
    from writer import write_content_idea, write_developed_idea, update_status
"""

import json
import sqlite3
from datetime import datetime, timezone


# How many days between filming/creating and publishing, by format type.
# Customize these for your workflow. Set to 0 for instant-publish formats.
FORMAT_TURNAROUND = {
    # YouTube formats
    "long_form": 7,
    "tutorial": 3,
    "vlog": 2,
    "short_form": 1,
    # LinkedIn formats
    "post": 0,
    "article": 1,
    "carousel": 1,
    "video_short": 1,
    # General
    "essay": 1,
    "interview": 3,
    "raw": 0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_content_idea(conn: sqlite3.Connection, idea: dict) -> int:
    """Write a content idea stub to the database. Returns the new row ID.

    This is the lightweight capture path — just enough to classify and store.
    Use write_developed_idea() for full concept development output.
    """
    fmt = idea.get("format_type")
    turnaround = idea.get("edit_turnaround_days")
    if turnaround is None and fmt:
        turnaround = FORMAT_TURNAROUND.get(fmt)

    cursor = conn.execute(
        """INSERT INTO content_ideas
            (title, hook, description, audience, topics, notes,
             channel, format_type, source_type,
             audience_segment, content_pillar, funnel_position,
             production_status, edit_turnaround_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            idea.get("title", "Untitled"),
            idea.get("hook"),
            idea.get("description"),
            idea.get("audience"),
            idea.get("topics"),
            idea.get("notes"),
            idea.get("channel"),
            fmt,
            idea.get("source_type", "manual"),
            idea.get("audience_segment"),
            idea.get("content_pillar"),
            idea.get("funnel_position"),
            idea.get("production_status", "stub"),
            turnaround,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def write_developed_idea(conn: sqlite3.Connection, idea: dict) -> int:
    """Write or update a fully-developed content idea. Returns the row ID.

    For new ideas (no 'id' key), inserts a new row.
    For existing ideas (has 'id' key), updates the existing row.
    """
    now = _now()

    def _json_field(val):
        if val is None:
            return None
        return json.dumps(val) if not isinstance(val, str) else val

    fmt = idea.get("format_type")
    turnaround = idea.get("edit_turnaround_days")
    if turnaround is None and fmt:
        turnaround = FORMAT_TURNAROUND.get(fmt)

    if idea.get("id"):
        # Update existing idea
        conn.execute(
            """UPDATE content_ideas SET
                title = COALESCE(?, title),
                hook = COALESCE(?, hook),
                description = COALESCE(?, description),
                audience = COALESCE(?, audience),
                topics = COALESCE(?, topics),
                notes = COALESCE(?, notes),
                title_options = COALESCE(?, title_options),
                thumbnail_concepts = COALESCE(?, thumbnail_concepts),
                funnel_position = COALESCE(?, funnel_position),
                content_pillar = COALESCE(?, content_pillar),
                audience_segment = COALESCE(?, audience_segment),
                offer_alignment = COALESCE(?, offer_alignment),
                cta_path = COALESCE(?, cta_path),
                proof_points = COALESCE(?, proof_points),
                authority_angle = COALESCE(?, authority_angle),
                priority_score = COALESCE(?, priority_score),
                research_json = COALESCE(?, research_json),
                channel = COALESCE(?, channel),
                format_type = COALESCE(?, format_type),
                production_status = COALESCE(?, production_status),
                film_by_date = COALESCE(?, film_by_date),
                publish_date = COALESCE(?, publish_date),
                edit_turnaround_days = COALESCE(?, edit_turnaround_days),
                developed_at = ?,
                developed_by = COALESCE(?, developed_by)
            WHERE id = ?""",
            (
                idea.get("title"),
                idea.get("hook"),
                idea.get("description"),
                idea.get("audience"),
                idea.get("topics"),
                idea.get("notes"),
                _json_field(idea.get("title_options")),
                _json_field(idea.get("thumbnail_concepts")),
                idea.get("funnel_position"),
                idea.get("content_pillar"),
                idea.get("audience_segment"),
                idea.get("offer_alignment"),
                idea.get("cta_path"),
                _json_field(idea.get("proof_points")),
                idea.get("authority_angle"),
                idea.get("priority_score"),
                _json_field(idea.get("research_json")),
                idea.get("channel"),
                idea.get("format_type"),
                idea.get("production_status", "developed"),
                idea.get("film_by_date"),
                idea.get("publish_date"),
                turnaround,
                now,
                idea.get("developed_by"),
                idea["id"],
            ),
        )
        conn.commit()
        return idea["id"]
    else:
        # Insert new idea
        cursor = conn.execute(
            """INSERT INTO content_ideas
                (title, hook, description, audience, topics, notes,
                 source_type,
                 title_options, thumbnail_concepts, funnel_position,
                 content_pillar, audience_segment, offer_alignment,
                 cta_path, proof_points, authority_angle,
                 priority_score, research_json,
                 channel, format_type, production_status,
                 film_by_date, publish_date, edit_turnaround_days,
                 developed_at, developed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                idea.get("title", "Untitled"),
                idea.get("hook"),
                idea.get("description"),
                idea.get("audience"),
                idea.get("topics"),
                idea.get("notes"),
                idea.get("source_type", "develop"),
                _json_field(idea.get("title_options")),
                _json_field(idea.get("thumbnail_concepts")),
                idea.get("funnel_position"),
                idea.get("content_pillar"),
                idea.get("audience_segment"),
                idea.get("offer_alignment"),
                idea.get("cta_path"),
                _json_field(idea.get("proof_points")),
                idea.get("authority_angle"),
                idea.get("priority_score"),
                _json_field(idea.get("research_json")),
                idea.get("channel"),
                idea.get("format_type"),
                idea.get("production_status", "developed"),
                idea.get("film_by_date"),
                idea.get("publish_date"),
                turnaround,
                now,
                idea.get("developed_by", "develop"),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def update_status(conn: sqlite3.Connection, idea_id: int, status: str, **kwargs):
    """Update production status and optional fields.

    Extra kwargs can include: film_by_date, publish_date, assigned_editor,
    assigned_thumbnail, notion_page_id, published_url.
    """
    sets = ["production_status = ?"]
    values = [status]
    allowed = (
        "film_by_date", "publish_date", "assigned_editor",
        "assigned_thumbnail", "notion_page_id", "published_url",
    )
    for key in allowed:
        if key in kwargs:
            sets.append(f"{key} = ?")
            values.append(kwargs[key])
    values.append(idea_id)
    conn.execute(f"UPDATE content_ideas SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()


def log_published_content(conn: sqlite3.Connection, entry: dict) -> int:
    """Log a published piece of content for the context aggregator.

    Use this for content published on platforms without automated collectors
    (e.g. LinkedIn posts, newsletter editions). YouTube content is usually
    logged by whatever collector they already run.
    """
    cursor = conn.execute(
        """INSERT INTO published_content
            (platform, external_id, title, published_date, url,
             description, metrics_json, content_idea_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry.get("platform"),
            entry.get("external_id"),
            entry.get("title", "Untitled"),
            entry.get("published_date"),
            entry.get("url"),
            entry.get("description"),
            json.dumps(entry.get("metrics")) if entry.get("metrics") else None,
            entry.get("content_idea_id"),
        ),
    )
    conn.commit()
    return cursor.lastrowid


if __name__ == "__main__":
    # Quick test — verify imports and functions exist
    print("Writer module loaded successfully.")
    print(f"Format turnaround mapping: {FORMAT_TURNAROUND}")
    print("Functions: write_content_idea, write_developed_idea, update_status, log_published_content")
