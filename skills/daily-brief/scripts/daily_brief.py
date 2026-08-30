#!/usr/bin/env python3
"""Daily brief — the run.

Pulls their numbers, context, meetings and Slack together, sends one
Gemini call, saves the brief to outputs/daily-brief/, and (if they have
the Telegram bot) sends it to their phone.

Run it from the project folder (or set AIOS_WORKSPACE):

    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --test        # print, save nothing
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py               # yesterday, save, deliver if Telegram is set
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --date 2026-08-28
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --no-deliver  # save only
    python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --preset solo
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


def _call_gemini(prompt: str, model: str | None = None) -> dict:
    """One Gemini call. Returns text, tokens and an estimated cost."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.error("GEMINI_API_KEY is missing. Put it in ~/.claude/.env.")
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.error("google-genai is not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    model = model or os.environ.get("BRIEF_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    # USD per 1M tokens. Update if Google changes the list.
    pricing = {
        "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
        "gemini-3-pro-preview": {"input": 2.00, "output": 12.00},
        "gemini-3.1-pro-preview": {"input": 2.00, "output": 12.00},
    }
    model_pricing = pricing.get(model, pricing["gemini-2.5-flash"])

    config = types.GenerateContentConfig(
        max_output_tokens=16384,
        temperature=0.3,
        http_options=types.HttpOptions(timeout=300_000),
    )
    try:
        response = client.models.generate_content(model=model, contents=prompt, config=config)
        input_tokens = response.usage_metadata.prompt_token_count or 0
        output_tokens = response.usage_metadata.candidates_token_count or 0
        cost = (input_tokens * model_pricing["input"] + output_tokens * model_pricing["output"]) / 1_000_000
        logger.info("Gemini: %s in, %s out, $%.4f", f"{input_tokens:,}", f"{output_tokens:,}", cost)
        return {
            "text": response.text or "",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "model": model,
        }
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return {"text": "", "error": str(e), "cost_usd": 0.0}


def run_daily_brief(target_date: str | None = None, preset: str = "small_team",
                    dry_run: bool = False, deliver: bool = True, model: str | None = None):
    """The full run. Returns the saved path, or the brief text on a dry run."""
    from dashboard import generate_dashboard_image
    from deliver import deliver_brief, telegram_configured
    from metrics import build_funnel_metrics, format_metrics_text
    from prompt import build_mega_prompt, load_business_context, load_meeting_transcripts, load_slack_messages

    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    root = workspace_root()
    output_dir = root / "outputs" / "daily-brief"
    logger.info("Daily brief for %s (preset: %s) in %s", target_date, preset, root)

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

    result = _call_gemini(mega_prompt, model=model)
    if result.get("error"):
        logger.error("Brief generation failed: %s", result["error"])
        if conn:
            conn.close()
        return None

    header = (
        f"# Daily Brief  {target_date}\n\n"
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"> Model: {result.get('model', 'unknown')}\n"
        f"> Tokens: {result.get('input_tokens', 0):,} in / {result.get('output_tokens', 0):,} out\n"
        f"> Cost: ${result.get('cost_usd', 0):.4f}\n"
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

    image_bytes = None
    try:
        image_bytes = generate_dashboard_image(funnel_metrics, save_path=str(output_dir / f"{target_date}.png"))
    except Exception:
        logger.exception("Dashboard image failed (continuing without it)")

    if deliver:
        if not telegram_configured():
            logger.info("No TELEGRAM_BOT_TOKEN / TELEGRAM_GROUP_ID. Brief saved to disk only.")
        else:
            try:
                if deliver_brief(image_bytes, result["text"], target_date):
                    logger.info("Delivered to Telegram")
                else:
                    logger.warning("Telegram delivery failed (brief is still saved)")
            except Exception:
                logger.exception("Telegram delivery error (brief is still saved)")

    if conn:
        conn.close()
    logger.info("Done. Cost $%.4f. Saved to %s", result.get("cost_usd", 0), output_path)
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Daily brief")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (default: yesterday)")
    parser.add_argument("--preset", choices=["solo", "small_team", "agency"], default=None,
                        help="Report preset (default: BRIEF_PRESET in .env, else small_team)")
    parser.add_argument("--model", help="Override the Gemini model")
    parser.add_argument("--dry-run", action="store_true", help="Print the brief, save nothing")
    parser.add_argument("--no-deliver", dest="deliver", action="store_false", help="Skip Telegram")
    parser.add_argument("--test", action="store_true", help="Same as --dry-run")
    args = parser.parse_args()

    preset = args.preset or os.environ.get("BRIEF_PRESET", "small_team")
    dry_run = args.dry_run or args.test

    result = run_daily_brief(target_date=args.date, preset=preset, dry_run=dry_run,
                             deliver=args.deliver and not dry_run, model=args.model)
    if dry_run and result:
        print(result)
    elif result:
        print(f"Brief saved to: {result}")
    else:
        print("Brief generation failed. See the log lines above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
