"""Content Pipeline database — schema, connection, and initialization.

Creates a SQLite database with the content_ideas table for tracking
your full content lifecycle from raw idea capture through to publishing.

Usage:
    python3 db.py              # Initialize or verify database
    python3 db.py --check      # Show table info and row counts
"""

import sqlite3
import sys
from pathlib import Path

from _workspace import workspace_root

WORKSPACE_ROOT = workspace_root()
DB_PATH = WORKSPACE_ROOT / "data" / "content.db"

SCHEMA_SQL = """
-- Content ideas — full lifecycle from capture to publish
-- Each row is one content idea that moves through: stub → developed → scheduled → filmed → editing → published
CREATE TABLE IF NOT EXISTS content_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core idea
    title TEXT NOT NULL,
    hook TEXT,
    description TEXT,
    audience TEXT,
    topics TEXT,
    notes TEXT,

    -- Classification (set during capture)
    channel TEXT,                          -- e.g. youtube, linkedin, podcast, newsletter
    format_type TEXT,                      -- e.g. long_form, short_form, tutorial, post, article, carousel
    source_type TEXT DEFAULT 'manual',     -- how it was captured: manual, voice, meeting

    -- Strategic positioning (set by develop)
    audience_segment TEXT,                 -- which of your defined audience segments
    content_pillar TEXT,                   -- which of your defined content pillars
    funnel_position TEXT,                  -- awareness / consideration / conversion
    offer_alignment TEXT,                  -- which offer this drives toward
    cta_path TEXT,                         -- the call-to-action strategy
    authority_angle TEXT,                  -- why YOU own this topic

    -- Packaging (set by develop, mainly for YouTube)
    title_options TEXT,                    -- JSON: array of title variants with viral elements
    thumbnail_concepts TEXT,              -- JSON: array of thumbnail concepts
    proof_points TEXT,                    -- JSON: array of proof points by type

    -- Production tracking
    production_status TEXT DEFAULT 'stub', -- stub / developed / scheduled / filmed / editing / published
    priority_score INTEGER,               -- 1-10 composite score
    film_by_date TEXT,                    -- YYYY-MM-DD (calculated from publish_date - turnaround)
    publish_date TEXT,                    -- YYYY-MM-DD
    edit_turnaround_days INTEGER,         -- days between filming and publish
    assigned_editor TEXT,
    assigned_thumbnail TEXT,

    -- Research & context
    research_json TEXT,                   -- JSON: research notes from develop

    -- External links
    published_url TEXT,                   -- URL of the published content
    notion_page_id TEXT,                  -- Notion page ID (if using Notion sync)

    -- Metadata
    developed_at TEXT,
    developed_by TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Published content log — lightweight record of what you've published
-- Used by the context aggregator to build the "recent content" window
-- If a collector already logs YouTube videos, this table supplements it
-- with non-YouTube content (LinkedIn posts, newsletters, etc.)
CREATE TABLE IF NOT EXISTS published_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,               -- youtube, linkedin, tiktok, newsletter, etc.
    external_id TEXT,                     -- platform-specific ID (video_id, post URL, etc.)
    title TEXT NOT NULL,
    published_date TEXT NOT NULL,
    url TEXT,
    description TEXT,
    metrics_json TEXT,                    -- JSON: platform-specific metrics (views, likes, etc.)
    content_idea_id INTEGER,              -- links back to content_ideas if it started there
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (content_idea_id) REFERENCES content_ideas(id)
);
""";


def get_connection() -> sqlite3.Connection:
    """Get a connection to the content database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> sqlite3.Connection:
    """Initialize the database, creating all tables if they don't exist."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


if __name__ == "__main__":
    if "--check" in sys.argv:
        if not DB_PATH.exists():
            print(f"Database not found at {DB_PATH}")
            print("Run without --check to initialize it.")
            sys.exit(1)
        conn = get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row["name"] for row in cursor.fetchall()]
        print(f"Database: {DB_PATH}")
        print(f"Tables ({len(tables)}):")
        for t in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
            print(f"  {t}: {count} rows")
        conn.close()
    else:
        conn = init_db()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row["name"] for row in cursor.fetchall()]
        print(f"Database initialized at: {DB_PATH}")
        print(f"Tables ({len(tables)}): {', '.join(tables)}")
        conn.close()
