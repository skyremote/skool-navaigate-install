"""
Database layer for AI Landscape Monitor.

Creates and manages the ai_models and ai_scan_log tables in a SQLite database.
Self-contained — no external imports from other workspace modules.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import get_db_path

SCHEMA_SQL = """
-- AI model rankings from benchmark sources (LMArena, TTS Arena, Voice Writer, OpenRouter)
CREATE TABLE IF NOT EXISTS ai_models (
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    provider TEXT,
    elo_score REAL,
    quality_index REAL,
    speed_score REAL,
    price_input REAL,
    price_output REAL,
    context_length INTEGER,
    rank_in_category INTEGER,
    metadata TEXT,
    PRIMARY KEY (date, category, source, model_id)
);

-- Scan run audit trail
CREATE TABLE IF NOT EXISTS ai_scan_log (
    scan_date TEXT NOT NULL,
    scan_type TEXT NOT NULL,
    categories_scanned TEXT,
    new_models_found INTEGER DEFAULT 0,
    ranking_changes INTEGER DEFAULT 0,
    docs_updated TEXT,
    cost_usd REAL DEFAULT 0,
    duration_seconds REAL,
    summary TEXT,
    PRIMARY KEY (scan_date, scan_type)
);
"""


def init_db() -> sqlite3.Connection:
    """Initialize the database and create tables if they don't exist."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def write_ai_models(conn: sqlite3.Connection, result: dict, date: str) -> int:
    """Write AI model ranking data to the database. Returns number of records written."""
    if result.get("status") != "success":
        return 0

    data = result["data"]
    source_name = result.get("source", "unknown")
    models = data.get("models", [])
    records = 0

    for model in models:
        meta = model.get("metadata")
        meta_str = json.dumps(meta) if meta else None

        conn.execute(
            "INSERT OR REPLACE INTO ai_models "
            "(date, category, source, model_id, model_name, provider, "
            "elo_score, quality_index, speed_score, price_input, price_output, "
            "context_length, rank_in_category, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (date, model.get("category", "unknown"), source_name,
             model.get("model_id", ""), model.get("model_name", ""),
             model.get("provider"), model.get("elo_score"),
             model.get("quality_index"), model.get("speed_score"),
             model.get("price_input"), model.get("price_output"),
             model.get("context_length"), model.get("rank_in_category"),
             meta_str)
        )
        records += 1

    conn.commit()
    return records


def write_scan_log(conn: sqlite3.Connection, scan_date: str, scan_type: str,
                   categories: str, new_models: int, ranking_changes: int,
                   summary: str, duration: float = 0, cost: float = 0,
                   docs_updated: str | None = None):
    """Log a scan run to the ai_scan_log table."""
    conn.execute(
        "INSERT OR REPLACE INTO ai_scan_log "
        "(scan_date, scan_type, categories_scanned, new_models_found, "
        "ranking_changes, docs_updated, cost_usd, duration_seconds, summary) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scan_date, scan_type, categories, new_models, ranking_changes,
         docs_updated, cost, duration, summary)
    )
    conn.commit()


if __name__ == "__main__":
    conn = init_db()
    # Verify tables exist
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ai_models', 'ai_scan_log')"
    ).fetchall()]
    print(f"Database initialized at: {get_db_path()}")
    print(f"Tables: {', '.join(tables)}")

    # Show row counts
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
    conn.close()
