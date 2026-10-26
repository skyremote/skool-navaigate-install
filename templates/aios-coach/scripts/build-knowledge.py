#!/usr/bin/env python3
"""Refresh knowledge/your-aios.json from local extras. Does not scrape Skool."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "knowledge" / "your-aios.json"
EXTRA_DIR = ROOT / "knowledge" / "extra"
URLS = ROOT / "knowledge" / "extra-urls.txt"


def main() -> None:
    if not PACK.exists():
        raise SystemExit("knowledge/your-aios.json is missing. Copy it from the plugin template.")
    data = json.loads(PACK.read_text(encoding="utf-8"))
    bits: list[str] = []
    if EXTRA_DIR.is_dir():
        for p in sorted(EXTRA_DIR.glob("*")):
            if p.suffix.lower() in {".md", ".txt", ".html"}:
                bits.append(f"# {p.name}\n{p.read_text(encoding='utf-8').strip()}")
    if URLS.exists():
        pending = [
            line.strip()
            for line in URLS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if pending:
            bits.append(
                "URLs waiting for /web-scrape (not fetched here):\n"
                + "\n".join(pending)
            )
    data["extra"] = "\n\n".join(bits)
    PACK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {PACK} extra_chars={len(data['extra'])}")


if __name__ == "__main__":
    main()
