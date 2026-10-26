"""Daily brief — funnel metrics.

Reads funnel.md and queries their SQLite database to build a metrics
snapshot: each metric with yesterday's value and a 7-day average.

It adapts to their data. funnel.md says which stages and metrics matter,
and only tables that actually exist are queried.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from _workspace import workspace_root


def find_funnel_file(root: Path | None = None) -> Path | None:
    """funnel.md at the project root, or under context/."""
    root = root or workspace_root()
    for path in (root / "funnel.md", root / "context" / "funnel.md"):
        if path.exists():
            return path
    return None


def parse_funnel(funnel_path: Path | None = None) -> dict | None:
    """Parse funnel.md into stages, metrics and targets.

    Returns None when there is no funnel file.
    """
    path = funnel_path or find_funnel_file()
    if not path or not path.exists():
        return None

    text = path.read_text()
    result: dict = {"currency": "USD", "stages": [], "targets": {}}

    currency_match = re.search(r"## Currency\s*\n(\w+)", text)
    if currency_match:
        result["currency"] = currency_match.group(1).strip()

    stage_pattern = re.compile(
        r"### \d+\.\s*(.+?)\n(.*?)(?=### \d+\.|## Monthly Targets|## Targets|\Z)",
        re.DOTALL,
    )
    for match in stage_pattern.finditer(text):
        stage_name = match.group(1).strip()
        stage_body = match.group(2).strip()

        description = ""
        metrics = []
        for line in stage_body.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # "- Label -> table.column" (also accepts the arrow character)
            metric_match = re.match(r"^-\s*(.+?)\s*(?:->|→)\s*(\w+)\.(\w+)\s*$", line)
            if metric_match:
                metrics.append({
                    "label": metric_match.group(1).strip(),
                    "table": metric_match.group(2).strip(),
                    "column": metric_match.group(3).strip(),
                })
            elif not metrics and not description:
                description = line.lstrip("- ").strip()

        result["stages"].append({
            "name": stage_name,
            "description": description,
            "metrics": metrics,
        })

    targets_match = re.search(r"## (?:Monthly )?Targets\s*\n(.*?)(?=##|\Z)", text, re.DOTALL)
    if targets_match:
        for line in targets_match.group(1).strip().split("\n"):
            target_match = re.match(r"^-\s*(.+?):\s*(.+)$", line.strip())
            if target_match:
                result["targets"][target_match.group(1).strip()] = target_match.group(2).strip()

    return result


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def _get_metric_value(conn, table, column, date):
    try:
        row = conn.execute(f"SELECT {column} FROM {table} WHERE date = ?", (date,)).fetchone()
        return dict(row)[column] if row else None
    except Exception:
        return None


def _get_latest_value(conn, table, column):
    try:
        row = conn.execute(f"SELECT {column}, date FROM {table} ORDER BY date DESC LIMIT 1").fetchone()
        if row:
            r = dict(row)
            return r[column], r["date"]
        return None, None
    except Exception:
        return None, None


def _get_7day_avg(conn, table, column, end_date):
    try:
        start = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        rows = conn.execute(
            f"SELECT {column} FROM {table} WHERE date > ? AND date <= ?", (start, end_date)
        ).fetchall()
        values = [dict(r)[column] for r in rows if dict(r)[column] is not None]
        return round(sum(values) / len(values), 1) if values else None
    except Exception:
        return None


def build_funnel_metrics(conn: sqlite3.Connection | None, target_date: str | None = None) -> dict:
    """Full metrics snapshot. Works with no database (empty stages)."""
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    funnel = parse_funnel()
    if not funnel or conn is None:
        return {"date": target_date, "currency": "USD", "stages": [], "targets": (funnel or {}).get("targets", {})}

    result = {
        "date": target_date,
        "currency": funnel["currency"],
        "stages": [],
        "targets": funnel.get("targets", {}),
    }

    for stage in funnel["stages"]:
        stage_data = {"name": stage["name"], "description": stage["description"], "metrics": []}

        for metric in stage["metrics"]:
            if not _table_exists(conn, metric["table"]):
                continue

            value = _get_metric_value(conn, metric["table"], metric["column"], target_date)
            date_used = target_date
            if value is None:
                value, date_used = _get_latest_value(conn, metric["table"], metric["column"])

            avg_7d = _get_7day_avg(conn, metric["table"], metric["column"], date_used or target_date)

            direction = "on_par"
            if value is not None and avg_7d is not None and avg_7d > 0:
                ratio = value / avg_7d
                if ratio > 1.05:
                    direction = "above"
                elif ratio < 0.95:
                    direction = "below"

            stage_data["metrics"].append({
                "label": metric["label"],
                "value": value,
                "avg_7d": avg_7d,
                "direction": direction,
                "date": date_used,
            })

        if any(m["value"] is not None for m in stage_data["metrics"]):
            result["stages"].append(stage_data)

    return result


def format_metrics_text(metrics: dict) -> str:
    """Plain-text metrics for the model prompt."""
    if not metrics or not metrics.get("stages"):
        return "No funnel metrics available."

    lines = [f"Date: {metrics['date']}", f"Currency: {metrics['currency']}", ""]

    for stage in metrics["stages"]:
        lines.append(f"{stage['name'].upper()}:")
        if stage["description"]:
            lines.append(f"  ({stage['description']})")

        for m in stage["metrics"]:
            val = m["value"]
            avg = m["avg_7d"]
            if val is None:
                lines.append(f"  {m['label']}: No data")
                continue

            if isinstance(val, float) and val > 1000:
                val_str = f"{val:,.0f}"
            elif isinstance(val, float):
                val_str = f"{val:.1f}"
            else:
                val_str = f"{val:,}" if isinstance(val, int) else str(val)

            avg_str = ""
            if avg is not None:
                if isinstance(avg, float) and avg > 1000:
                    avg_str = f" (7d avg: {avg:,.0f})"
                elif isinstance(avg, float):
                    avg_str = f" (7d avg: {avg:.1f})"
                else:
                    avg_str = f" (7d avg: {avg})"

            arrow = ""
            if m["direction"] == "above":
                arrow = " (up)"
            elif m["direction"] == "below":
                arrow = " (down)"

            lines.append(f"  {m['label']}: {val_str}{arrow}{avg_str}")

        lines.append("")

    if metrics.get("targets"):
        lines.append("MONTHLY TARGETS:")
        for name, target in metrics["targets"].items():
            lines.append(f"  {name}: {target}")

    return "\n".join(lines)


if __name__ == "__main__":
    funnel = parse_funnel()
    if funnel:
        print(f"Currency: {funnel['currency']}")
        print(f"Stages: {len(funnel['stages'])}")
        for s in funnel["stages"]:
            print(f"  {s['name']}: {len(s['metrics'])} metrics")
            for m in s["metrics"]:
                print(f"    - {m['label']} -> {m['table']}.{m['column']}")
    else:
        print("No funnel.md found in this folder (or context/).")
        print("Copy templates/funnel.md from the daily-brief skill and fill it in.")
