"""Configuration for the AI landscape monitor.

Where the member's project is, where their keys are, where the scan writes.

The scripts are linked into ~/.claude/skills by install.sh, so `__file__`
points at the plugin, not at their project. Everything is anchored on the
folder they run from (or AIOS_WORKSPACE if they set it).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _workspace_root() -> Path:
    env = os.environ.get("AIOS_WORKSPACE", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd().resolve()


WORKSPACE_ROOT = _workspace_root()

# Keys live in ~/.claude/.env (plugin convention). A project .env also works.
load_dotenv(Path.home() / ".claude" / ".env")
load_dotenv(WORKSPACE_ROOT / ".env")


def get_env(key: str) -> str | None:
    """An environment variable, or None if unset or blank."""
    value = os.getenv(key, "").strip()
    return value if value else None


def get_db_path() -> Path:
    """The SQLite file the scan writes to.

    DB_PATH in .env wins. Otherwise the first .db under data/, else data/workspace.db.
    """
    env_path = get_env("DB_PATH")
    if env_path:
        p = Path(env_path).expanduser()
        return p if p.is_absolute() else WORKSPACE_ROOT / p

    data_dir = WORKSPACE_ROOT / "data"
    if data_dir.exists():
        db_files = sorted(data_dir.glob("*.db"))
        if db_files:
            return db_files[0]
    return data_dir / "workspace.db"


def get_ai_docs_dir() -> Path:
    return WORKSPACE_ROOT / "ai-docs"


def get_scan_output_path() -> Path:
    return WORKSPACE_ROOT / "data" / "ai-scan-latest.json"


def get_report_dir() -> Path:
    return WORKSPACE_ROOT / "outputs" / "ai-landscape"


if __name__ == "__main__":
    print(f"Workspace root: {WORKSPACE_ROOT}")
    print(f"DB path: {get_db_path()}")
    print(f"AI docs dir: {get_ai_docs_dir()}")
    print(f"OpenRouter key: {'set' if get_env('OPENROUTER_API_KEY') else 'not set'}")
