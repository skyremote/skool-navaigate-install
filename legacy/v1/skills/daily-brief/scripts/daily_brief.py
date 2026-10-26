#!/usr/bin/env python3
"""Daily brief — the run.

Pulls their numbers, context, meetings and Slack together, sends one
model call, and saves the brief plus a dashboard PNG to
outputs/daily-brief/ in their project.

Run it from the project folder (or set AIOS_WORKSPACE):

    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --test        # print, save nothing
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py               # yesterday, saved
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --date 2026-08-28
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --preset solo
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --model gpt-5.4-mini
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _workspace import db_path, load_keys, workspace_root  # noqa: E402

load_keys()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("daily_brief")


def _get_db_connection() -> sqlite3.Connection | None:
    path = db_path()
    if not path or not path.exists():
        logger.info("No SQLite database found (DB_PATH or data/*.db). Running without metrics.")
        return None
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def run_daily_brief(target_date: str | None = None, preset: str = "small_team",
                    dry_run: bool = False, model: str | None = None):
    """The full run. Returns the saved path, or the brief text on a dry run."""
    from dashboard import generate_dashboard_image
    from metrics import build_funnel_metrics, format_metrics_text
    from model import call_model, pick_provider
    from prompt import build_mega_prompt, load_business_context, load_meeting_transcripts, load_slack_messages

    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    root = workspace_root()
    output_dir = root / "outputs" / "daily-brief"
    logger.info("Daily brief for %s (preset: %s) in %s", target_date, preset, root)

    picked = pick_provider()
    if not picked:
        logger.error("No model key found. Put OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY "
                     "or GEMINI_API_KEY in ~/.claude/.env.")
        return None
    logger.info("Model: %s / %s", picked[0], model or picked[2])

    conn = _get_db_connection()

    funnel_metrics = build_funnel_metrics(conn, target_date)
    metrics_text = format_metrics_text(funnel_metrics)
    logger.info("Funnel metrics: %d stages", len(funnel_metrics.get("stages", [])))

    context_text = load_business_context(root)
    logger.info("Business context: ~%s tokens", f"{len(context_text) // 4:,}")

    meetings_text = load_meeting_transcripts(conn, target_date)
    logger.info("Meetings: %s", f"~{len(meetings_text) // 4:,} tokens" if meetings_text else "none")

    slack_text = load_slack_messages(conn, target_date)
    logger.info("Slack: %s", f"~{len(slack_text) // 4:,} tokens" if slack_text else "none")

    mega_prompt = build_mega_prompt(metrics_text, context_text, meetings_text, slack_text, preset)
    logger.info("Prompt: ~%s tokens", f"{len(mega_prompt) // 4:,}")

    result = call_model(mega_prompt, model=model)
    if result.get("error") or not result.get("text"):
        logger.error("Brief generation failed: %s", result.get("error") or "empty response")
        if conn:
            conn.close()
        return None
    logger.info("%s: %s in, %s out", result["provider"], f"{result['input_tokens']:,}", f"{result['output_tokens']:,}")

    header = (
        f"# Daily Brief  {target_date}\n\n"
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"> Model: {result['provider']} / {result['model']}\n"
        f"> Tokens: {result['input_tokens']:,} in / {result['output_tokens']:,} out\n"
        f"> Preset: {preset}\n\n---\n\n"
    )
    full_brief = header + result["text"]

    if dry_run:
        if conn:
            conn.close()
        return full_brief

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{target_date}.md"
    output_path.write_text(full_brief)
    logger.info("Saved: %s", output_path)

    try:
        generate_dashboard_image(funnel_metrics, save_path=str(output_dir / f"{target_date}.png"))
        logger.info("Dashboard: %s", output_dir / f"{target_date}.png")
    except Exception:
        logger.exception("Dashboard image failed (the brief is still saved)")

    if conn:
        conn.close()
    logger.info("Done. Saved to %s", output_path)
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Daily brief")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (default: yesterday)")
    parser.add_argument("--preset", choices=["solo", "small_team", "agency"], default=None,
                        help="Report preset (default: BRIEF_PRESET in .env, else small_team)")
    parser.add_argument("--model", help="Override the model name for whichever provider is picked")
    parser.add_argument("--dry-run", action="store_true", help="Print the brief, save nothing")
    parser.add_argument("--test", action="store_true", help="Same as --dry-run")
    args = parser.parse_args()

    preset = args.preset or os.environ.get("BRIEF_PRESET", "small_team")
    dry_run = args.dry_run or args.test

    result = run_daily_brief(target_date=args.date, preset=preset, dry_run=dry_run, model=args.model)
    if dry_run and result:
        print(result)
    elif result:
        print(f"Brief saved to: {result}")
    else:
        print("Brief generation failed. See the log lines above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
