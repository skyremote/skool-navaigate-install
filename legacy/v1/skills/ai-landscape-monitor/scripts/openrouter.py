"""
OpenRouter models API collector for AI model pricing and context lengths.

Collects 400+ models with pricing, context lengths, and modality support.
Complements LMArena (quality/ELO) with definitive cost data.

Requires: OPENROUTER_API_KEY (free account at https://openrouter.ai)
API docs: https://openrouter.ai/docs
"""

import json
from collections import Counter

import requests
from config import get_env

API_URL = "https://openrouter.ai/api/v1/models"


def _infer_category(model: dict) -> str:
    """Infer the primary category from model architecture fields."""
    arch = model.get("architecture") or {}
    modality = (arch.get("modality") or "").lower()
    input_mods = [m.lower() for m in (arch.get("input_modalities") or [])]
    output_mods = [m.lower() for m in (arch.get("output_modalities") or [])]
    model_id = (model.get("id") or "").lower()

    if "image" in output_mods and "text" not in output_mods:
        return "image-generation"
    if "audio" in output_mods and "text" not in output_mods:
        return "text-to-speech"
    if "->image" in modality:
        return "image-generation"
    if "->audio" in modality:
        return "text-to-speech"
    if "->video" in modality:
        return "video-generation"
    if "audio" in input_mods and "text" in output_mods and "image" not in input_mods:
        return "speech-to-text"
    if "text" in input_mods and "text" in output_mods:
        return "text-generation"
    if "image" in input_mods and "text" in output_mods:
        return "vision"

    id_hints = {
        "stable-diffusion": "image-generation", "dall-e": "image-generation",
        "flux": "image-generation", "imagen": "image-generation",
        "tts": "text-to-speech", "whisper": "speech-to-text",
    }
    for hint, category in id_hints.items():
        if hint in model_id:
            return category

    return "text-generation"


def _normalize_model(item: dict) -> dict:
    """Normalize an OpenRouter model entry to the standard format."""
    model_id = item.get("id", "")
    name = item.get("name", model_id)
    provider = model_id.split("/")[0] if "/" in model_id else ""

    pricing = item.get("pricing") or {}
    prompt_price = pricing.get("prompt")
    completion_price = pricing.get("completion")

    try:
        price_input = float(prompt_price) * 1_000_000 if prompt_price else None
    except (ValueError, TypeError):
        price_input = None
    try:
        price_output = float(completion_price) * 1_000_000 if completion_price else None
    except (ValueError, TypeError):
        price_output = None

    return {
        "model_id": model_id,
        "model_name": name,
        "provider": provider,
        "category": _infer_category(item),
        "elo_score": None,
        "quality_index": None,
        "speed_score": None,
        "price_input": price_input,
        "price_output": price_output,
        "context_length": item.get("context_length"),
        "rank_in_category": None,
        "metadata": {
            "source": "openrouter",
            "architecture": item.get("architecture"),
            "description": (item.get("description") or "")[:500] or None,
            "top_provider": item.get("top_provider"),
            "created": item.get("created"),
        },
    }


def collect() -> dict:
    """Collect model catalog from OpenRouter API.

    Returns a standardized result dict. Skips gracefully if no API key.
    """
    api_key = get_env("OPENROUTER_API_KEY")
    if not api_key:
        return {"source": "openrouter", "status": "skipped",
                "reason": "Missing OPENROUTER_API_KEY — add it to .env (free at openrouter.ai)"}

    try:
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        resp = requests.get(API_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        models_raw = data.get("data", [])
        models = [_normalize_model(m) for m in models_raw]
        cat_counts = Counter(m["category"] for m in models)

        return {"source": "openrouter", "status": "success", "data": {
            "models": models,
            "total_models": len(models),
            "categories": dict(cat_counts),
        }}

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return {"source": "openrouter", "status": "error",
                "reason": f"OpenRouter API error (HTTP {status_code}): {e}"}
    except Exception as e:
        return {"source": "openrouter", "status": "error",
                "reason": f"Unexpected error: {e}"}


if __name__ == "__main__":
    result = collect()
    if result.get("status") == "success":
        data = result["data"]
        print(f"Total models: {data['total_models']}")
        print(f"Categories: {data['categories']}")
    else:
        print(json.dumps(result, indent=2, default=str))
