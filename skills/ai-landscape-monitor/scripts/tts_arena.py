"""
TTS Arena V2 leaderboard collector.

Scrapes TTS model rankings (ELO-based, blind A/B human preference voting).
No API key required — public HuggingFace Spaces page.

Source: https://tts-agi-tts-arena-v2.hf.space/leaderboard
Category: text-to-speech
"""

import json
import re

import requests

LEADERBOARD_URL = "https://tts-agi-tts-arena-v2.hf.space/leaderboard"
CATEGORY = "text-to-speech"
SOURCE = "tts_arena"


def _parse_provider(model_name: str) -> str:
    """Extract provider from model name."""
    name_lower = model_name.lower()
    provider_patterns = {
        "elevenlabs": "elevenlabs", "eleven ": "elevenlabs",
        "openai": "openai", "gpt-4o": "openai",
        "hume": "hume", "octave": "hume",
        "google": "google", "cartesia": "cartesia", "sonic": "cartesia",
        "deepgram": "deepgram", "aura": "deepgram",
        "playht": "playht", "play.ht": "playht",
        "sesame": "sesame", "kokoro": "kokoro",
        "vocu": "vocu", "minimax": "minimax",
        "fish": "fish-audio", "speechify": "speechify",
    }
    for pattern, provider in provider_patterns.items():
        if pattern in name_lower:
            return provider
    return "unknown"


def _fetch_leaderboard() -> list[dict] | None:
    """Fetch leaderboard data from the TTS Arena V2 /leaderboard page.

    Parses structured HTML divs with class names:
    model-name-link, elo-score, rank, win-rate, total-votes
    """
    try:
        resp = requests.get(LEADERBOARD_URL, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp.raise_for_status()
        text = resp.text

        # Try full pattern first (rank + name + win-rate + votes + elo)
        full_entries = re.findall(
            r'class="rank">#?(\d+)</div>.*?'
            r'class="model-name-link">(.*?)</a>.*?'
            r'class="win-rate">(\d+)%</div>.*?'
            r'class="total-votes">([\d,]+)</div>.*?'
            r'class="elo-score">([\d,.]+)</div>',
            text, re.DOTALL
        )

        models = []

        if full_entries:
            for rank_str, name, win_rate, votes_str, elo_str in full_entries:
                name = name.strip()
                try:
                    elo = float(elo_str.replace(',', ''))
                    rank = int(rank_str)
                    votes = int(votes_str.replace(',', ''))
                    win_pct = int(win_rate)
                except (ValueError, TypeError):
                    continue

                if not name or elo <= 0:
                    continue

                models.append({
                    "model_id": f"tts_arena:{name}",
                    "model_name": name,
                    "provider": _parse_provider(name),
                    "category": CATEGORY,
                    "elo_score": round(elo, 1),
                    "quality_index": None, "speed_score": None,
                    "price_input": None, "price_output": None,
                    "context_length": None,
                    "rank_in_category": rank,
                    "metadata": {"source": SOURCE, "votes": votes, "win_rate_pct": win_pct},
                })
        else:
            # Fallback: simpler name+elo pattern
            entries = re.findall(
                r'class="model-name-link">(.*?)</a>.*?class="elo-score">([\d,.]+)',
                text, re.DOTALL
            )
            for i, (name, elo_str) in enumerate(entries):
                name = name.strip()
                try:
                    elo = float(elo_str.replace(',', ''))
                except (ValueError, TypeError):
                    continue
                if not name or elo <= 0:
                    continue

                models.append({
                    "model_id": f"tts_arena:{name}",
                    "model_name": name,
                    "provider": _parse_provider(name),
                    "category": CATEGORY,
                    "elo_score": round(elo, 1),
                    "quality_index": None, "speed_score": None,
                    "price_input": None, "price_output": None,
                    "context_length": None,
                    "rank_in_category": i + 1,
                    "metadata": {"source": SOURCE},
                })

        return models if models else None

    except requests.exceptions.RequestException:
        return None


def collect() -> dict:
    """Collect TTS model rankings from TTS Arena V2."""
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
                "reason": "Could not extract leaderboard from TTS Arena (HTML structure may have changed)"}

    except Exception as e:
        return {"source": SOURCE, "status": "error", "reason": f"Unexpected error: {e}"}


if __name__ == "__main__":
    result = collect()
    if result.get("status") == "success":
        data = result["data"]
        print(f"Total TTS models: {data['total_models']}")
        for m in data["models"][:10]:
            votes = m["metadata"].get("votes", "?")
            win = m["metadata"].get("win_rate_pct", "?")
            print(f"  #{m['rank_in_category']:2d} {m['model_name']:30s} "
                  f"({m['provider']:15s}) ELO:{m['elo_score']:.0f}  Win:{win}%  Votes:{votes}")
    else:
        print(json.dumps(result, indent=2, default=str))
