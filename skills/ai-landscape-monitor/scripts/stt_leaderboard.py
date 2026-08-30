"""
Voice Writer Speech Recognition Leaderboard collector.

Scrapes STT (speech-to-text) model rankings from voicewriter.io.
Metric: WER (Word Error Rate) — lower is better.
Stored as NEGATIVE elo_score so ORDER BY elo_score DESC puts best (lowest WER) first.

No API key required — public website.
Source: https://voicewriter.io/speech-recognition-leaderboard
"""

import json
import re

import requests

LEADERBOARD_URL = "https://voicewriter.io/speech-recognition-leaderboard"
CATEGORY = "speech-to-text"
SOURCE = "voice_writer"


def _parse_provider(model_name: str) -> str:
    """Extract provider from model/service name."""
    name_lower = model_name.lower()
    provider_patterns = {
        "openai": "openai", "gpt": "openai", "whisper": "openai",
        "google": "google", "gemini": "google", "chirp": "google",
        "deepgram": "deepgram", "nova": "deepgram",
        "assemblyai": "assemblyai", "assembly": "assemblyai",
        "elevenlabs": "elevenlabs", "eleven": "elevenlabs",
        "amazon": "amazon", "aws": "amazon",
        "azure": "microsoft", "microsoft": "microsoft",
        "speechmatics": "speechmatics", "rev.ai": "rev.ai",
        "nvidia": "nvidia", "canary": "nvidia", "parakeet": "nvidia",
        "gladia": "gladia", "soniox": "soniox", "groq": "groq",
    }
    for pattern, provider in provider_patterns.items():
        if pattern in name_lower:
            return provider
    return "unknown"


def _fetch_leaderboard() -> list[dict] | None:
    """Fetch and parse the Voice Writer leaderboard HTML table.

    The page is Next.js SSR with a standard HTML <table>. WER values
    use <!-- --> comment separators (e.g., "5.4<!-- -->%").
    """
    try:
        resp = requests.get(LEADERBOARD_URL, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp.raise_for_status()
        html = resp.text

        table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
        if not table_match:
            return None

        table_html = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        if len(rows) < 2:
            return None

        models = []
        rank = 0

        for row_html in rows[1:]:  # Skip header
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if len(cells) < 3:
                continue

            # Model name from <span>
            name_match = re.search(r'<span>(.*?)</span>', cells[0])
            name = name_match.group(1).strip() if name_match else re.sub(r'<[^>]+>', '', cells[0]).strip()
            if not name:
                continue

            # Mean WER — strip HTML tags and <!-- --> comments
            wer_text = re.sub(r'<[^>]+>', '', cells[1])
            wer_text = wer_text.replace('<!--', '').replace('-->', '')
            wer_match = re.search(r'([\d.]+)\s*%?', wer_text)
            if not wer_match:
                continue

            try:
                wer = float(wer_match.group(1))
            except (ValueError, TypeError):
                continue

            # Price per hour
            price_per_hour = None
            if len(cells) > 3:
                price_text = re.sub(r'<[^>]+>', '', cells[3])
                price_match = re.search(r'\$?([\d.]+)', price_text)
                if price_match:
                    try:
                        price_per_hour = float(price_match.group(1))
                    except (ValueError, TypeError):
                        pass

            # Std Dev
            std_dev = None
            if len(cells) > 2:
                std_text = re.sub(r'<[^>]+>', '', cells[2]).replace('<!--', '').replace('-->', '')
                std_match = re.search(r'([\d.]+)', std_text)
                if std_match:
                    try:
                        std_dev = float(std_match.group(1))
                    except (ValueError, TypeError):
                        pass

            rank += 1
            models.append({
                "model_id": f"voice_writer:{name}",
                "model_name": name,
                "provider": _parse_provider(name),
                "category": CATEGORY,
                "elo_score": round(-wer, 2),  # Negative so DESC sort = best first
                "quality_index": None, "speed_score": None,
                "price_input": price_per_hour, "price_output": None,
                "context_length": None,
                "rank_in_category": rank,
                "metadata": {
                    "source": SOURCE,
                    "wer_pct": wer,
                    "std_dev_pct": std_dev,
                    "price_per_hour_usd": price_per_hour,
                },
            })

        return models if models else None

    except requests.exceptions.RequestException:
        return None


def collect() -> dict:
    """Collect STT model rankings from Voice Writer Leaderboard."""
    try:
        models = _fetch_leaderboard()

        if models and len(models) >= 3:
            models.sort(key=lambda m: m["elo_score"], reverse=True)
            for i, m in enumerate(models):
                m["rank_in_category"] = i + 1

            return {"source": SOURCE, "status": "success", "data": {
                "models": models, "total_models": len(models),
            }}

        return {"source": SOURCE, "status": "skipped",
                "reason": "Could not parse leaderboard from Voice Writer (HTML structure may have changed)"}

    except Exception as e:
        return {"source": SOURCE, "status": "error", "reason": f"Unexpected error: {e}"}


if __name__ == "__main__":
    result = collect()
    if result.get("status") == "success":
        data = result["data"]
        print(f"Total STT models: {data['total_models']}")
        for m in data["models"][:15]:
            wer = m["metadata"]["wer_pct"]
            price = m["metadata"].get("price_per_hour_usd")
            price_str = f"${price:.2f}/hr" if price else "N/A"
            print(f"  #{m['rank_in_category']:2d} {m['model_name']:30s} "
                  f"({m['provider']:15s}) WER:{wer:.1f}%  {price_str}")
    else:
        print(json.dumps(result, indent=2, default=str))
