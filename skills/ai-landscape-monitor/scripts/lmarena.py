"""
LMArena (Chatbot Arena) ELO scores collector.

Scrapes live leaderboard data from arena.ai for 8 categories:
  text, code, vision, text-to-image, image-edit, search, text-to-video, image-to-video

No API key required — public website.
Source: https://arena.ai/leaderboard
"""

import json
import re
from collections import Counter

import requests

BASE_URL = "https://arena.ai/leaderboard"

# All 8 LMArena categories — matches arena.ai URL slugs
CATEGORIES = [
    "text",
    "code",
    "vision",
    "text-to-image",
    "image-edit",
    "search",
    "text-to-video",
    "image-to-video",
]


def _parse_provider(model_name: str, organization: str | None = None) -> str:
    """Get provider from organization field, falling back to name patterns."""
    if organization:
        org_lower = organization.lower()
        org_map = {
            "anthropic": "anthropic", "openai": "openai", "google": "google",
            "xai": "xai", "meta": "meta", "mistral": "mistral", "cohere": "cohere",
            "alibaba": "alibaba", "microsoft": "microsoft", "amazon": "amazon",
            "deepseek": "deepseek", "bytedance": "bytedance", "stability": "stability",
            "black forest": "black-forest-labs", "midjourney": "midjourney",
            "ideogram": "ideogram", "recraft": "recraft", "tencent": "tencent",
        }
        for pattern, provider in org_map.items():
            if pattern in org_lower:
                return provider

    # Fallback to model name patterns
    name_lower = model_name.lower()
    name_patterns = {
        "claude": "anthropic", "gpt-": "openai", "chatgpt": "openai",
        "o1-": "openai", "o3-": "openai", "o4-": "openai",
        "gemini": "google", "gemma": "google", "imagen": "google", "veo-": "google",
        "grok": "xai", "deepseek": "deepseek", "llama": "meta",
        "mistral": "mistral", "mixtral": "mistral", "command": "cohere",
        "qwen": "alibaba", "phi-": "microsoft", "nova-": "amazon",
        "dall-e": "openai", "gpt-image": "openai",
        "stable-diffusion": "stability", "flux": "black-forest-labs",
        "midjourney": "midjourney", "ideogram": "ideogram", "recraft": "recraft",
        "sora": "openai", "kling": "kuaishou",
    }
    for pattern, provider in name_patterns.items():
        if pattern in name_lower:
            return provider
    return organization or "unknown"


def _fetch_leaderboard(category: str) -> list[dict] | None:
    """Fetch leaderboard entries for a single category from arena.ai.

    The data is embedded in the HTML as escaped JSON inside Next.js
    self.__next_f.push() chunks. We find the "entries" array and parse it.
    """
    url = f"{BASE_URL}/{category}"
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    text = resp.text

    # Find the entries array in the Next.js SSR data
    pos = text.find("entries")
    if pos < 0:
        return None

    bracket_start = text.find("[", pos)
    if bracket_start < 0:
        return None

    # Extract chunk and unescape the JSON (HTML contains literal \")
    chunk = text[bracket_start:bracket_start + 500000]
    unescaped = chunk.replace(chr(92) + chr(34), chr(34))

    # Find the matching closing ]
    bracket_depth = 0
    end = 0
    for j, c in enumerate(unescaped):
        if c == "[":
            bracket_depth += 1
        elif c == "]":
            bracket_depth -= 1
            if bracket_depth == 0:
                end = j + 1
                break

    if end == 0:
        return None

    return json.loads(unescaped[:end])


def collect() -> dict:
    """Collect ELO scores from all 8 LMArena leaderboard categories.

    Returns a standardized result dict with status, source, and data.
    """
    try:
        all_models = []
        errors = []

        for category in CATEGORIES:
            try:
                entries = _fetch_leaderboard(category)
                if entries is None:
                    errors.append(f"{category}: no entries found")
                    continue

                for entry in entries:
                    rating = entry.get("rating")
                    if not rating or rating <= 0:
                        continue

                    model_name = entry.get("modelDisplayName", "")
                    organization = entry.get("modelOrganization")

                    all_models.append({
                        "model_id": f"lmarena:{model_name}",
                        "model_name": model_name,
                        "provider": _parse_provider(model_name, organization),
                        "category": category,
                        "elo_score": round(rating, 1),
                        "quality_index": None,
                        "speed_score": None,
                        "price_input": None,
                        "price_output": None,
                        "context_length": None,
                        "rank_in_category": entry.get("rank"),
                        "metadata": {
                            "source": "lmarena",
                            "organization": organization,
                            "votes": entry.get("votes"),
                            "rating_upper": entry.get("ratingUpper"),
                            "rating_lower": entry.get("ratingLower"),
                            "license": entry.get("license"),
                            "model_url": entry.get("modelUrl"),
                        },
                    })

            except requests.exceptions.HTTPError as e:
                errors.append(f"{category}: HTTP {e.response.status_code if e.response else 'error'}")
            except Exception as e:
                errors.append(f"{category}: {e}")

        if not all_models:
            return {"source": "lmarena", "status": "error",
                    "reason": f"No models collected. Errors: {'; '.join(errors)}"}

        cat_counts = Counter(m["category"] for m in all_models)
        result_data = {
            "models": all_models,
            "total_models": len(all_models),
            "categories": dict(cat_counts),
        }
        if errors:
            result_data["errors"] = errors

        return {"source": "lmarena", "status": "success", "data": result_data}

    except Exception as e:
        return {"source": "lmarena", "status": "error", "reason": f"Unexpected error: {e}"}


if __name__ == "__main__":
    result = collect()
    if result.get("status") == "success":
        data = result["data"]
        print(f"Total models: {data.get('total_models')}")
        print(f"Categories: {data.get('categories')}")
        if data.get("errors"):
            print(f"Errors: {data['errors']}")
        print()
        for cat in CATEGORIES:
            cat_models = [m for m in data["models"] if m["category"] == cat]
            if cat_models:
                top = cat_models[0]
                print(f"  {cat:20s}: #{top['rank_in_category']} {top['model_name']} "
                      f"({top['provider']}) ELO:{top['elo_score']}")
    else:
        print(json.dumps(result, indent=2, default=str))
