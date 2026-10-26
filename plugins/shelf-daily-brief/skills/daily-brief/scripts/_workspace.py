"""Where the member's project lives, and where their keys are.

The scripts in this folder are linked into ~/.claude/skills by install.sh,
so `__file__` points at the plugin, not at their project. Everything is
anchored on the folder they run from (or AIOS_WORKSPACE if they set it).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_keys() -> None:
    """Keys live in ~/.claude/.env (plugin convention). A project .env also works."""
    load_dotenv(Path.home() / ".claude" / ".env")
    load_dotenv(workspace_root() / ".env")


def workspace_root() -> Path:
    env = os.environ.get("AIOS_WORKSPACE", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return Path.cwd().resolve()


def db_path(root: Path | None = None) -> Path | None:
    """The SQLite file the brief reads numbers from, or None if there is none.

    DB_PATH in .env wins. Otherwise the first .db under data/.
    """
    root = root or workspace_root()
    env = os.environ.get("DB_PATH", "").strip()
    if env:
        p = Path(env).expanduser()
        return p if p.is_absolute() else root / p
    data_dir = root / "data"
    if data_dir.exists():
        dbs = sorted(data_dir.glob("*.db"))
        if dbs:
            return dbs[0]
    return None
