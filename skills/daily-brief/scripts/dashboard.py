"""Daily brief — dashboard image.

A dark funnel dashboard PNG from the metrics snapshot. Stages and metrics
come from funnel.md, so it fits whatever business they run.

matplotlib with the Agg backend, so it runs from cron with no display.
"""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BG_COLOR = "#1a1a2e"
TEXT_COLOR = "#e8e8e8"
MUTED_COLOR = "#8b8b9e"
GREEN = "#4ade80"
RED = "#f87171"
ACCENT = "#818cf8"
HEADER_COLOR = "#c084fc"
RULE_COLOR = "#2a2a4e"

# Layout in "pixels" (1 unit = 1/100 inch at figure scale).
WIDTH = 600
PAD = 24
ROW_TITLE = 34
ROW_STAGE = 24
ROW_DESC = 16
ROW_METRIC = 20
ROW_GAP = 14
ROW_TARGET = 16


def _fmt(val) -> str:
    if isinstance(val, bool):
        return str(val)
    if isinstance(val, (int, float)) and val >= 1000:
        return f"{val:,.0f}"
    if isinstance(val, float):
        return f"{val:,.1f}"
    return str(val)


def _height_for(stages: list[dict], targets: dict) -> int:
    h = PAD + ROW_TITLE
    for s in stages:
        h += ROW_STAGE + (ROW_DESC if s.get("description") else 0)
        h += ROW_METRIC * sum(1 for m in s["metrics"] if m["value"] is not None)
        h += ROW_GAP
    if targets:
        h += ROW_STAGE + ROW_TARGET * len(targets)
    return h + PAD


def generate_dashboard_image(metrics: dict, width: int = WIDTH, save_path: str | None = None) -> bytes:
    """PNG bytes for the metrics snapshot. Optionally saved to save_path too."""
    stages = metrics.get("stages", [])
    targets = metrics.get("targets", {}) or {}
    date = metrics.get("date", "")
    if not stages:
        return _generate_empty_dashboard(date, save_path)

    height = _height_for(stages, targets)
    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)  # y grows downwards, like a page
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    y = PAD
    ax.text(width / 2, y + ROW_TITLE / 2, f"DAILY BRIEF  {date}", ha="center", va="center",
            fontsize=11, fontweight="bold", color=HEADER_COLOR)
    y += ROW_TITLE

    for stage in stages:
        ax.text(PAD, y + ROW_STAGE / 2, stage["name"].upper(), va="center",
                fontsize=9, fontweight="bold", color=ACCENT)
        y += ROW_STAGE
        if stage.get("description"):
            ax.text(PAD, y + ROW_DESC / 2, stage["description"], va="center",
                    fontsize=6.5, color=MUTED_COLOR)
            y += ROW_DESC

        for m in stage["metrics"]:
            if m["value"] is None:
                continue
            cy = y + ROW_METRIC / 2
            ax.text(PAD + 12, cy, m["label"], va="center", fontsize=7.5, color=MUTED_COLOR)
            ax.text(width * 0.55, cy, _fmt(m["value"]), va="center", ha="right",
                    fontsize=7.5, fontweight="bold", color=TEXT_COLOR)
            if m["avg_7d"] is not None:
                direction = m.get("direction", "on_par")
                if direction == "above":
                    color, arrow = GREEN, "↑"
                elif direction == "below":
                    color, arrow = RED, "↓"
                else:
                    color, arrow = MUTED_COLOR, "→"
                ax.text(width * 0.60, cy, f"{arrow} 7d avg {_fmt(m['avg_7d'])}", va="center",
                        fontsize=6.5, color=color)
            y += ROW_METRIC

        y += ROW_GAP / 2
        ax.plot([PAD, width - PAD], [y, y], color=RULE_COLOR, linewidth=0.6)
        y += ROW_GAP / 2

    if targets:
        ax.text(PAD, y + ROW_STAGE / 2, "TARGETS", va="center", fontsize=7,
                fontweight="bold", color=MUTED_COLOR)
        y += ROW_STAGE
        for name, target in targets.items():
            ax.text(PAD + 12, y + ROW_TARGET / 2, f"{name}: {target}", va="center",
                    fontsize=6.5, color=MUTED_COLOR)
            y += ROW_TARGET

    return _finish(fig, save_path)


def _generate_empty_dashboard(date: str, save_path: str | None = None) -> bytes:
    fig, ax = plt.subplots(figsize=(6, 1.6))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis("off")
    ax.text(0.5, 0.65, f"DAILY BRIEF  {date}", ha="center", va="center",
            fontsize=11, fontweight="bold", color=HEADER_COLOR)
    ax.text(0.5, 0.3, "No funnel metrics yet. Fill in funnel.md and point DB_PATH at your numbers.",
            ha="center", va="center", fontsize=7, color=MUTED_COLOR)
    return _finish(fig, save_path)


def _finish(fig, save_path: str | None) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=BG_COLOR, edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    image_bytes = buf.read()
    if save_path:
        Path(save_path).write_bytes(image_bytes)
    return image_bytes


if __name__ == "__main__":
    sample = {
        "date": "2026-08-29",
        "currency": "EUR",
        "stages": [
            {"name": "Awareness", "description": "How people find you", "metrics": [
                {"label": "YouTube views", "value": 15234, "avg_7d": 12100.0, "direction": "above", "date": "2026-08-29"},
                {"label": "Website sessions", "value": 1820, "avg_7d": 1900.0, "direction": "below", "date": "2026-08-29"},
            ]},
            {"name": "Conversion", "description": "Prospects becoming customers", "metrics": [
                {"label": "Demo bookings", "value": 8, "avg_7d": 6.2, "direction": "above", "date": "2026-08-29"},
            ]},
            {"name": "Revenue", "description": "Money in the bank", "metrics": [
                {"label": "Revenue MTD", "value": 42500, "avg_7d": None, "direction": "on_par", "date": "2026-08-29"},
            ]},
        ],
        "targets": {"Monthly revenue": "50,000", "New customers": "10"},
    }
    out = generate_dashboard_image(sample, save_path="test_dashboard.png")
    print(f"Dashboard generated: {len(out):,} bytes -> test_dashboard.png")
