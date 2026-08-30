"""Daily brief — Telegram delivery (optional).

Sends the brief to a topic in their Telegram group:
1. dashboard PNG
2. the day in brief + key signals
3. recommendations + action items

Pairs with /telegram-command-bot, which is where the bot token and group
come from. Without a token the brief is still saved to disk.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re

from _workspace import workspace_root

logger = logging.getLogger(__name__)

TELEGRAM_MESSAGE_LIMIT = 4096
TOPIC_NAME = "Daily Brief"


def _topic_cache_path():
    return workspace_root() / "data" / "daily-brief-topic.json"


def _md_to_telegram_html(text: str) -> str:
    if not text:
        return ""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"^#{2,3} (.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _truncate_at_sentence(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    for end in [". ", ".\n", "! ", "!\n", "? ", "?\n"]:
        idx = truncated.rfind(end)
        if idx > max_chars * 0.5:
            return truncated[: idx + 1].rstrip()
    last_nl = truncated.rfind("\n")
    if last_nl > max_chars * 0.5:
        return truncated[:last_nl].rstrip()
    return truncated.rstrip() + "..."


def extract_sections(brief_text: str) -> dict[str, str]:
    """{section name: body} from the ## headers."""
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in brief_text.split("\n"):
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(lines).strip()
            current = line.lstrip("# ").strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        sections[current] = "\n".join(lines).strip()
    return sections


def build_telegram_messages(brief_text: str, date: str) -> list[tuple[str, str]]:
    """[(text, parse_mode)] for Telegram."""
    sections = extract_sections(brief_text)
    messages = []

    parts = []
    summary = sections.get("The Day in Brief", "")
    if summary:
        parts.append(f"<b>THE DAY IN BRIEF  {date}</b>\n")
        parts.append(_truncate_at_sentence(_md_to_telegram_html(summary), 1800))
    signals = sections.get("Key Signals", "")
    if signals:
        parts.append("\n\n<b>KEY SIGNALS</b>\n")
        parts.append(_truncate_at_sentence(_md_to_telegram_html(signals), 1200))
    if parts:
        messages.append((_truncate_at_sentence("\n".join(parts), TELEGRAM_MESSAGE_LIMIT - 10), "HTML"))

    strat = []
    recs = sections.get("Strategic Recommendations", "")
    if recs:
        strat.append("<b>STRATEGIC RECOMMENDATIONS</b>\n")
        strat.append(_truncate_at_sentence(_md_to_telegram_html(recs), 2000))
    actions = sections.get("Action Items", "")
    if actions:
        strat.append("\n\n<b>ACTION ITEMS</b>\n")
        strat.append(_truncate_at_sentence(_md_to_telegram_html(actions), 1500))
    if strat:
        messages.append((_truncate_at_sentence("\n".join(strat), TELEGRAM_MESSAGE_LIMIT - 10), "HTML"))

    return messages


async def _get_or_create_topic(bot, group_id: int):
    cache = _topic_cache_path()
    if cache.exists():
        try:
            cached_id = json.loads(cache.read_text()).get("topic_id")
            if cached_id:
                return cached_id
        except (json.JSONDecodeError, KeyError):
            pass
    try:
        result = await bot.create_forum_topic(chat_id=group_id, name=TOPIC_NAME)
        topic_id = result.message_thread_id
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"topic_id": topic_id}))
        logger.info("Created forum topic '%s' (id: %s)", TOPIC_NAME, topic_id)
        return topic_id
    except Exception as e:
        if any(k in str(e).upper() for k in ["FORUM", "TOPIC", "400"]):
            logger.info("Forum topics not enabled on this group. Sending to the main chat.")
            return None
        logger.warning("Could not create forum topic: %s", e)
        return None


async def _send_to_telegram(image_bytes, messages, date):
    from aiogram import Bot
    from aiogram.types import BufferedInputFile

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    group_id_str = os.environ.get("TELEGRAM_GROUP_ID", "").strip()
    if not bot_token or not group_id_str:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_GROUP_ID must be set")

    group_id = int(group_id_str)
    bot = Bot(token=bot_token)
    try:
        env_topic = os.environ.get("TELEGRAM_DAILY_BRIEF_TOPIC_ID", "").strip()
        topic_id = int(env_topic) if env_topic else await _get_or_create_topic(bot, group_id)

        if image_bytes:
            await bot.send_photo(
                chat_id=group_id,
                photo=BufferedInputFile(image_bytes, filename=f"brief-{date}.png"),
                caption=f"Daily Brief  {date}",
                message_thread_id=topic_id,
            )
        for text, parse_mode in messages:
            await bot.send_message(chat_id=group_id, text=text, parse_mode=parse_mode,
                                   message_thread_id=topic_id)
        return True
    finally:
        await bot.session.close()


def telegram_configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
                and os.environ.get("TELEGRAM_GROUP_ID", "").strip())


def deliver_brief(image_bytes, brief_text: str, date: str) -> bool:
    """Send to Telegram. False on any failure (the brief is already on disk)."""
    messages = build_telegram_messages(brief_text, date)
    try:
        return asyncio.run(_send_to_telegram(image_bytes, messages, date))
    except Exception as e:
        logger.error("Telegram delivery failed: %s", e)
        return False


if __name__ == "__main__":
    sample = """## The Day in Brief
Yesterday was a strong day. Revenue hit 12,400 from 2 new deals, above the 7-day average of 8,200.

## Key Signals
[win] **Two new deals closed**: 12,400 total, both from webinar attendees
[risk] **Churn up**: 3 cancellations yesterday vs a 1.5 daily average

## Strategic Recommendations
### Concerns
1. **Churn acceleration**: check whether the three cancellations share a billing date.

## Action Items
- [ ] Review the 3 churn cases
"""
    for i, (text, mode) in enumerate(build_telegram_messages(sample, "2026-08-29"), 1):
        print(f"--- Message {i} ({mode}, {len(text)} chars) ---")
        print(text[:300])
        print()
