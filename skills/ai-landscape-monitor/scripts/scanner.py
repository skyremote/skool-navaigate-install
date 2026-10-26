"""
Daily AI Landscape Scanner — detects changes in AI model rankings.

Runs daily (manually or via cron). No LLM calls — pure scraping + diff logic.

Covers 10 categories:
  Tier 1 (LMArena): text, code, vision, text-to-image, image-edit, search, text-to-video, image-to-video
  Tier 2: text-to-speech (TTS Arena V2), speech-to-text (Voice Writer)

Flow:
  1. Pull latest data from ai_models table (today vs previous date)
  2. If no data for today, run all 4 collectors first
  3. Diff: detect new leaders, new models in top 10, significant ELO shifts
  4. Write summary to ai_scan_log table
  5. Output JSON to data/ai-scan-latest.json (for daily brief integration)
  6. Write markdown report to outputs/daily-intel/ai-landscape/

Usage:
    python scripts/scanner.py              # Normal scan
    python scripts/scanner.py --force      # Force re-collect even if today's data exists
    python scripts/scanner.py --dry-run    # Print results without writing
"""

import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from db import init_db, write_ai_models, write_scan_log
from config import get_scan_output_path, get_report_dir

# Change detection thresholds
ELO_SHIFT_THRESHOLD = 50  # Flag if a model's ELO changes by this much
TOP_N = 10  # Track top N models per category


def _has_todays_data(conn, today: str) -> bool:
    """Check if we have ai_models data for today."""
    row = conn.execute(
        "SELECT COUNT(*) FROM ai_models WHERE date = ?", (today,)
    ).fetchone()
    return row[0] > 0


def _collect_fresh_data(conn, today: str):
    """Run all 4 collectors to get fresh data for today."""
    scripts_dir = Path(__file__).resolve().parent
    collectors = {
        "lmarena": "lmarena.py",
        "openrouter": "openrouter.py",
        "tts_arena": "tts_arena.py",
        "stt_leaderboard": "stt_leaderboard.py",
    }

    for name, filename in collectors.items():
        try:
            path = scripts_dir / filename
            spec = importlib.util.spec_from_file_location(name, str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            result = mod.collect()
            if result.get("status") == "success":
                records = write_ai_models(conn, result, today)
                print(f"  {name}: {records} records", file=sys.stderr)
            elif result.get("status") == "skipped":
                print(f"  {name}: skipped ({result.get('reason', '')})", file=sys.stderr)
            else:
                print(f"  {name}: error ({result.get('reason', '')})", file=sys.stderr)
        except Exception as e:
            print(f"  {name}: exception ({e})", file=sys.stderr)


def _get_category_rankings(conn, date: str) -> dict:
    """Get top models per category for a given date."""
    rows = conn.execute(
        """SELECT category, model_name, elo_score, provider, source, rank_in_category
           FROM ai_models
           WHERE date = ? AND elo_score IS NOT NULL
           ORDER BY category, rank_in_category""",
        (date,)
    ).fetchall()

    rankings = defaultdict(list)
    for r in rows:
        cat = r[0]
        if len(rankings[cat]) < TOP_N:
            rankings[cat].append({
                "model_name": r[1], "elo_score": r[2],
                "provider": r[3], "source": r[4], "rank": r[5],
            })
    return dict(rankings)


def _detect_changes(current: dict, previous: dict) -> list[dict]:
    """Compare current and previous rankings, return list of changes."""
    changes = []
    all_categories = set(list(current.keys()) + list(previous.keys()))

    for cat in sorted(all_categories):
        curr_models = current.get(cat, [])
        prev_models = previous.get(cat, [])

        if not prev_models and curr_models:
            changes.append({
                "category": cat, "type": "new_category",
                "detail": f"New category with {len(curr_models)} models",
                "model": curr_models[0]["model_name"] if curr_models else None,
                "elo": curr_models[0]["elo_score"] if curr_models else None,
            })
            continue

        if not curr_models:
            continue

        # Leader change
        curr_leader = curr_models[0] if curr_models else None
        prev_leader = prev_models[0] if prev_models else None
        if curr_leader and prev_leader and curr_leader["model_name"] != prev_leader["model_name"]:
            changes.append({
                "category": cat, "type": "new_leader",
                "detail": f"{curr_leader['model_name']} overtook {prev_leader['model_name']}",
                "model": curr_leader["model_name"], "elo": curr_leader["elo_score"],
            })

        # New models in top N
        prev_names = {m["model_name"] for m in prev_models}
        for m in curr_models:
            if m["model_name"] not in prev_names:
                score_str = f"ELO: {m['elo_score']:.0f}" if m["elo_score"] else ""
                changes.append({
                    "category": cat, "type": "new_model",
                    "detail": f"New in top {TOP_N}: {m['model_name']} ({score_str})",
                    "model": m["model_name"], "elo": m["elo_score"],
                })

        # Significant ELO shifts
        prev_by_name = {m["model_name"]: m for m in prev_models}
        for m in curr_models:
            prev_m = prev_by_name.get(m["model_name"])
            if prev_m and m["elo_score"] and prev_m["elo_score"]:
                shift = m["elo_score"] - prev_m["elo_score"]
                if abs(shift) >= ELO_SHIFT_THRESHOLD:
                    direction = "up" if shift > 0 else "down"
                    changes.append({
                        "category": cat, "type": "elo_shift",
                        "detail": f"{m['model_name']} ELO {direction} by {abs(shift):.0f} "
                                  f"({prev_m['elo_score']:.0f} -> {m['elo_score']:.0f})",
                        "model": m["model_name"], "elo": m["elo_score"],
                    })

    return changes


def _metric_label(category: str) -> str:
    return "WER" if category == "speech-to-text" else "ELO"


def _format_score(category: str, score: float | None) -> str:
    if score is None:
        return "—"
    if category == "speech-to-text":
        return f"{abs(score):.1f}% WER"
    return f"{score:.0f}"


def _format_summary(changes: list[dict]) -> str:
    if not changes:
        return "No significant AI landscape changes detected."
    new_categories = [c for c in changes if c["type"] == "new_category"]
    if new_categories and len(new_categories) == len(changes):
        return f"First scan: {len(new_categories)} categories recorded, nothing to compare yet."
    leader_changes = [c for c in changes if c["type"] == "new_leader"]
    new_models = [c for c in changes if c["type"] == "new_model"]
    elo_shifts = [c for c in changes if c["type"] == "elo_shift"]
    parts = []
    if leader_changes:
        for c in leader_changes:
            parts.append(f"New #1 in {c['category']}: {c['detail']}")
    if new_models:
        parts.append(f"{len(new_models)} new model(s) entered top rankings")
    if elo_shifts:
        parts.append(f"{len(elo_shifts)} significant ELO shift(s)")
    return "; ".join(parts)


def _write_daily_report(scan_date: str, current: dict, previous: dict,
                        changes: list[dict], compared_to: str | None) -> str:
    """Write a markdown report to outputs/daily-intel/ai-landscape/."""
    report_dir = get_report_dir()
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{scan_date}.md"

    lines = [
        f"# AI Landscape Report — {scan_date}", "",
        f"> Automated scan | Compared against: {compared_to or 'N/A (first scan)'}",
        f"> Categories: {len(current)} | Models tracked: {sum(len(v) for v in current.values())}", "",
    ]

    if changes:
        lines.append("## Changes Detected")
        lines.append("")
        for change_type, label in [("new_leader", "New Category Leaders"),
                                    ("new_model", "New Models in Top Rankings"),
                                    ("elo_shift", "Significant ELO Shifts"),
                                    ("new_category", "New Categories")]:
            typed = [c for c in changes if c["type"] == change_type]
            if typed:
                lines.append(f"### {label}")
                lines.append("")
                for c in typed:
                    lines.append(f"- **{c['category']}:** {c['detail']}")
                lines.append("")
    else:
        lines.extend(["## No Changes Detected", "",
                       "All category leaders and rankings remain stable.", ""])

    lines.append("## Current Rankings by Category")
    lines.append("")
    for cat in sorted(current.keys()):
        models = current[cat]
        metric = _metric_label(cat)
        lines.append(f"### {cat.replace('-', ' ').title()}")
        lines.append("")
        lines.append(f"| Rank | Model | {metric} | Provider | Source |")
        lines.append("|------|-------|-----|----------|--------|")
        for m in models:
            score_str = _format_score(cat, m.get("elo_score"))
            lines.append(f"| {m.get('rank', '—')} | {m['model_name']} | {score_str} "
                         f"| {m.get('provider', '—')} | {m.get('source', '—')} |")
        lines.append("")

    lines.extend(["---", "", "*Generated by AI Landscape Monitor*"])
    report_path.write_text("\n".join(lines))
    print(f"  Report: {report_path}", file=sys.stderr)
    return str(report_path)


def scan(conn=None, force: bool = False, dry_run: bool = False) -> dict:
    """Run the full scan pipeline. Returns the scan result dict."""
    if conn is None:
        conn = init_db()

    start_time = time.time()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"[{today}] AI Landscape scan starting...", file=sys.stderr)

    # Step 1: Ensure we have today's data
    if force or not _has_todays_data(conn, today):
        print("  Collecting fresh data...", file=sys.stderr)
        _collect_fresh_data(conn, today)

    if not _has_todays_data(conn, today):
        return {
            "scan_date": today, "has_changes": False,
            "summary": "No data available — check your internet connection",
            "changes": [], "recommendation": None,
        }

    # Step 2: Get current and previous rankings
    current = _get_category_rankings(conn, today)
    row = conn.execute(
        "SELECT DISTINCT date FROM ai_models WHERE date < ? ORDER BY date DESC LIMIT 1",
        (today,)
    ).fetchone()
    prev_date = row[0] if row else None
    previous = _get_category_rankings(conn, prev_date) if prev_date else {}

    # Step 3: Detect changes
    changes = _detect_changes(current, previous)
    summary = _format_summary(changes)
    duration = time.time() - start_time

    result = {
        "scan_date": today, "compared_to": prev_date,
        "has_changes": len(changes) > 0, "summary": summary,
        "changes": changes, "categories_scanned": list(current.keys()),
        "total_models": sum(len(v) for v in current.values()),
        "duration_seconds": round(duration, 1),
    }

    if changes:
        changed_cats = sorted(set(c["category"] for c in changes))
        result["recommendation"] = f"Run /ai-landscape-monitor update for: {', '.join(changed_cats)}"
    else:
        result["recommendation"] = None

    # Step 4: Write results
    if not dry_run:
        write_scan_log(
            conn, today, "daily_scan",
            categories=",".join(current.keys()),
            new_models=sum(1 for c in changes if c["type"] == "new_model"),
            ranking_changes=sum(1 for c in changes if c["type"] in ("new_leader", "elo_shift")),
            summary=summary, duration=duration,
        )

        output_path = get_scan_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, default=str))
        print(f"  Results: {output_path}", file=sys.stderr)

        report_path = _write_daily_report(today, current, previous, changes, prev_date)
        result["report_path"] = report_path

    print(f"[{today}] Scan complete: {summary} ({duration:.1f}s)", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Daily AI Landscape Scanner")
    parser.add_argument("--force", action="store_true",
                        help="Force re-collect even if today's data exists")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing to DB")
    args = parser.parse_args()

    conn = init_db()
    result = scan(conn, force=args.force, dry_run=args.dry_run)
    conn.close()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
