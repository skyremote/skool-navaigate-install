"""Daily brief — prompt builder.

Puts everything the model needs into one prompt:
- business context (CLAUDE.md / AGENTS.md / context/*.md)
- funnel metrics (from their database)
- meeting transcripts (if a `meetings` table exists)
- Slack messages (if a `slack_messages` table exists)

Anything they do not have is left out. No empty sections.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from _workspace import workspace_root

# ============================================================
# PRESETS
# ============================================================

PRESETS = {
    "solo": {
        "name": "Solo operator",
        "sections": ["executive_summary", "key_signals", "metrics_analysis", "action_items"],
        "word_budget": 1500,
    },
    "small_team": {
        "name": "Small team",
        "sections": [
            "executive_summary", "key_signals", "metrics_analysis",
            "meeting_highlights", "slack_digest", "strategic_recommendations", "action_items",
        ],
        "word_budget": 3000,
    },
    "agency": {
        "name": "Agency",
        "sections": [
            "executive_summary", "key_signals", "metrics_analysis", "department_analysis",
            "meeting_highlights", "slack_digest", "cross_stream_patterns",
            "strategic_recommendations", "action_items",
        ],
        "word_budget": 6000,
    },
}

# Context files, in priority order. context/*.md is added after these.
CONTEXT_FILES = ["CLAUDE.md", "AGENTS.md", "funnel.md", "context/funnel.md"]
MAX_CONTEXT_CHARS = 60_000


# ============================================================
# CONTEXT
# ============================================================

def load_business_context(root: Path | None = None) -> str:
    """Whatever context files they have, concatenated. Capped so the prompt stays sane."""
    root = root or workspace_root()
    candidates: list[Path] = [root / rel for rel in CONTEXT_FILES]
    context_dir = root / "context"
    if context_dir.is_dir():
        candidates.extend(sorted(p for p in context_dir.glob("*.md") if p.name != "funnel.md"))

    blocks = []
    seen = set()
    total = 0
    for path in candidates:
        if not path.exists() or path.resolve() in seen:
            continue
        seen.add(path.resolve())
        try:
            content = path.read_text().strip()
        except Exception:
            continue
        if not content:
            continue
        if total + len(content) > MAX_CONTEXT_CHARS:
            content = content[: max(0, MAX_CONTEXT_CHARS - total)] + "\n[truncated]"
        blocks.append(f"=== {path.relative_to(root)} ===\n{content}")
        total += len(content)
        if total >= MAX_CONTEXT_CHARS:
            break

    return "\n\n".join(blocks) if blocks else "No business context available."


def load_meeting_transcripts(conn, target_date: str) -> str:
    """Meetings for the day from a `meetings` table, if they have one."""
    if conn is None:
        return ""
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='meetings'"
        ).fetchone()
        if not row:
            return ""

        meetings = conn.execute(
            "SELECT * FROM meetings WHERE date = ? ORDER BY start_time", (target_date,)
        ).fetchall()

        if not meetings:
            yesterday = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            meetings = conn.execute(
                "SELECT * FROM meetings WHERE date BETWEEN ? AND ? ORDER BY date, start_time",
                (yesterday, target_date),
            ).fetchall()

        if not meetings:
            return ""

        blocks = []
        for i, m in enumerate(meetings, 1):
            m = dict(m)
            header = (
                f"--- CALL {i}: {m.get('title') or 'Untitled'} | {m.get('date', '')} | "
                f"{m.get('duration_minutes') or '?'} min ---\n"
                f"Department: {m.get('stream') or 'general'}\n"
                f"Participants: {m.get('participants') or 'Unknown'}"
            )
            blocks.append(f"{header}\n\n{m.get('transcript_text') or '(No transcript)'}")
        return "\n\n\n".join(blocks)
    except Exception:
        return ""


def load_slack_messages(conn, target_date: str) -> str:
    """Slack messages for the day from a `slack_messages` table, if they have one."""
    if conn is None:
        return ""
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='slack_messages'"
        ).fetchone()
        if not row:
            return ""

        messages = conn.execute(
            "SELECT * FROM slack_messages WHERE date(ts) = ? ORDER BY workspace, channel_name, ts",
            (target_date,),
        ).fetchall()
        if not messages:
            messages = conn.execute(
                "SELECT * FROM slack_messages WHERE date(collected_at) = ? "
                "ORDER BY workspace, channel_name, ts",
                (target_date,),
            ).fetchall()
        if not messages:
            return ""

        grouped: dict[str, list[str]] = {}
        for msg in messages:
            msg = dict(msg)
            key = f"{msg.get('workspace', 'main')}/{msg.get('channel_name') or msg.get('channel_id', 'unknown')}"
            grouped.setdefault(key, []).append(f"[{msg.get('user_name') or 'Unknown'}] {msg.get('text') or ''}")

        blocks = []
        for channel, msgs in grouped.items():
            blocks.append(f"--- #{channel} ({len(msgs)} messages) ---")
            blocks.append("\n".join(msgs[:50]))
        return "\n\n".join(blocks)
    except Exception:
        return ""


# ============================================================
# PROMPT
# ============================================================

def build_mega_prompt(metrics_text: str, context_text: str, meetings_text: str = "",
                      slack_text: str = "", preset: str = "small_team",
                      custom_sections: list[str] | None = None) -> str:
    """The whole prompt, ready to send."""
    config = PRESETS.get(preset, PRESETS["small_team"])
    sections = custom_sections or config["sections"]
    word_budget = config["word_budget"]

    section_instructions = _build_section_instructions(
        sections, word_budget, bool(meetings_text), bool(slack_text)
    )

    parts = [
        _build_system_instruction(word_budget),
        "\n\n=== BUSINESS CONTEXT ===\n", context_text,
        "\n\n=== FUNNEL METRICS ===\n", metrics_text,
    ]
    if meetings_text:
        parts += ["\n\n=== MEETING TRANSCRIPTS ===\n", meetings_text]
    if slack_text:
        parts += ["\n\n=== SLACK MESSAGES ===\n", slack_text]
    parts += ["\n\n=== OUTPUT INSTRUCTIONS ===\n", section_instructions]
    return "".join(parts)


def _build_system_instruction(word_budget: int) -> str:
    return f"""You are writing a daily brief for the person who runs this business. You have their business context, their funnel metrics, and (if provided) yesterday's meeting transcripts and Slack messages.

Your job is to connect things, not to summarise. Spot patterns across the sources. Flag what needs attention. Be specific: names, numbers, percentages, direct quotes.

RULES:
- Total output: approximately {word_budget} words
- Use the currency given in the funnel metrics section
- Lead with the single most important signal
- Compare metrics to the 7-day averages with the actual numbers
- If meeting transcripts are provided, pull out decisions, action items and notable signals
- If Slack messages are provided, pull out the threads that matter and the decisions made
- Plain English. No hype, no filler, no emojis
- Use markdown headers (## for sections)
- Be specific: "$53K from 3 deals" not "a good revenue day"
- If there is no data for a section, leave the section out entirely. Never write "No data available"
"""


def _build_section_instructions(sections, word_budget, has_meetings, has_slack) -> str:
    budget_map = {
        "executive_summary": 300, "key_signals": 200, "metrics_analysis": 400,
        "meeting_highlights": 500, "department_analysis": 800, "slack_digest": 400,
        "cross_stream_patterns": 400, "strategic_recommendations": 500, "action_items": 200,
    }

    section_defs = {
        "executive_summary": (
            "## The Day in Brief\n"
            "200-300 words of flowing prose, no bullet points, that tells what happened. "
            "Lead with the single most important signal. Connect metrics to causes "
            "(new content, weekend, campaign). End with one sentence on what to watch today."
        ),
        "key_signals": (
            "## Key Signals\n"
            "8-12 one-line signals. Start each line with one tag in square brackets:\n"
            "[win] wins, momentum, deals closed\n"
            "[risk] risks, drops, blockers\n"
            "[pattern] recurring patterns, strategic themes\n"
            "[idea] opportunities\n"
            "[metric] notable metric movements\n"
            "Every signal must be specific: names, numbers, quotes. No generic observations."
        ),
        "metrics_analysis": (
            "## Metrics Analysis\n"
            "Go through the funnel by stage. For each stage with data:\n"
            "- What happened (specific numbers vs averages)\n"
            "- Why it might have happened (events, content, campaigns)\n"
            "- What it means for the business\n"
            "Focus on movements and anomalies, not flat numbers."
        ),
        "meeting_highlights": (
            "## Meeting Highlights\n"
            "For each meeting or call:\n"
            "- Decisions made\n"
            "- Action items (who committed to what)\n"
            "- Notable signals (prospects, risks, opportunities)\n"
            "- Direct quotes where they carry weight\n"
            "Group by department if the meetings span teams."
            if has_meetings else None
        ),
        "department_analysis": (
            "## Department Analysis\n"
            "Break the meetings down by department or stream. For each:\n"
            "- Team patterns (what is working, what is struggling)\n"
            "- Individual performance signals\n"
            "- Process gaps (coaching calls)\n"
            "- Retention signals (success calls)\n"
            "- Pipeline health (sales calls)\n"
            "Name people, quote them, cite patterns."
            if has_meetings else None
        ),
        "slack_digest": (
            "## Slack Digest\n"
            "The Slack threads that matter:\n"
            "- Decisions made\n"
            "- Requests waiting on a reply\n"
            "- Team dynamics signals\n"
            "- Anything the owner should know about or respond to\n"
            "Skip channels with nothing notable."
            if has_slack else None
        ),
        "cross_stream_patterns": (
            "## Cross-Stream Patterns\n"
            "2-4 patterns that only show up when you put the sources together "
            "(metrics + meetings + Slack). For each:\n"
            "- Name the pattern in a bold heading\n"
            "- Explain the connection with specific evidence from two or more sources\n"
            "- Say why it matters right now\n"
            "Skip the obvious. Only connections that are genuinely new."
            if (has_meetings or has_slack) else None
        ),
        "strategic_recommendations": (
            "## Strategic Recommendations\n"
            "From everything above:\n"
            "1. **Concerns** (1-3) that should worry the owner. Be specific.\n"
            "2. **Opportunities** (1-3) to act on right now.\n"
            "3. **Quick SWOT**, one sentence each, from today's data only.\n"
            "Every recommendation should be something a named person or team can do."
        ),
        "action_items": (
            "## Action Items\n"
            "One list of everything that needs doing:\n"
            "- Tasks from meetings (who, what, deadline)\n"
            "- Replies owed on Slack\n"
            "- Metric-driven actions (for example: investigate the churn spike)\n"
            "Most urgent first. Maximum 10 items."
        ),
    }

    instructions = ["Produce the following sections in this exact order. Use ## markdown headers exactly as shown.\n"]
    for section in sections:
        definition = section_defs.get(section)
        if definition is None:
            continue
        instructions.append(f"\n{definition}\n(~{budget_map.get(section, 300)} words)")
    return "\n".join(instructions)


if __name__ == "__main__":
    ctx = load_business_context()
    print(f"Business context loaded: ~{len(ctx) // 4:,} tokens")
    print(f"Files found: {ctx.count('===') // 2}")
    print()
    for key, val in PRESETS.items():
        print(f"Preset '{key}' ({val['name']}): {', '.join(val['sections'])} (~{val['word_budget']} words)")
