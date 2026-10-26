"""Daily brief — the model call.

One function, call_model(prompt). It uses the first key it finds in
~/.claude/.env, in this order:

    OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY

Same prompt whichever it is, plain-text result back. Plain HTTP via
requests, no vendor SDKs. BRIEF_MODEL overrides the model name.
"""

from __future__ import annotations

import os

import requests

TIMEOUT_SECONDS = 300
MAX_OUTPUT_TOKENS = 16000

# (provider, key name, default model). Model names move; BRIEF_MODEL overrides.
PROVIDERS = [
    ("openai", "OPENAI_API_KEY", "gpt-5.4-mini"),
    ("anthropic", "ANTHROPIC_API_KEY", "claude-opus-5"),
    ("openrouter", "OPENROUTER_API_KEY", "anthropic/claude-sonnet-4-6"),
    ("gemini", "GEMINI_API_KEY", "gemini-2.5-flash"),
]


def pick_provider() -> tuple[str, str, str] | None:
    """(provider, key, model) for the first key present, or None."""
    for provider, key_name, default_model in PROVIDERS:
        key = os.environ.get(key_name, "").strip()
        if key:
            model = os.environ.get("BRIEF_MODEL", "").strip() or default_model
            return provider, key, model
    return None


def call_model(prompt: str, model: str | None = None) -> dict:
    """Send the prompt to whichever provider they have a key for.

    Returns {"text", "provider", "model", "input_tokens", "output_tokens"},
    or {"text": "", "error": "..."} when something went wrong.
    """
    picked = pick_provider()
    if not picked:
        return {
            "text": "",
            "error": "No model key found. Put one of OPENAI_API_KEY, ANTHROPIC_API_KEY, "
                     "OPENROUTER_API_KEY or GEMINI_API_KEY in ~/.claude/.env.",
        }
    provider, key, default_model = picked
    model = model or default_model

    try:
        if provider == "openai":
            text, usage = _chat_completions("https://api.openai.com/v1/chat/completions",
                                            {"Authorization": f"Bearer {key}"}, model, prompt)
        elif provider == "openrouter":
            text, usage = _chat_completions("https://openrouter.ai/api/v1/chat/completions",
                                            {"Authorization": f"Bearer {key}",
                                             "HTTP-Referer": "https://github.com/skyremote/skool-navaigate-install",
                                             "X-Title": "daily-brief"}, model, prompt)
        elif provider == "anthropic":
            text, usage = _anthropic_messages(key, model, prompt)
        else:
            text, usage = _gemini_generate(key, model, prompt)
    except Exception as e:  # network, HTTP, shape: one plain message, no traceback
        return {"text": "", "error": f"{provider} ({model}): {e}", "provider": provider, "model": model}

    return {"text": text, "provider": provider, "model": model,
            "input_tokens": usage[0], "output_tokens": usage[1]}


# ---------------------------------------------------------------- providers ----

def _post(url: str, headers: dict, body: dict) -> dict:
    resp = requests.post(url, headers={"Content-Type": "application/json", **headers},
                         json=body, timeout=TIMEOUT_SECONDS)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _chat_completions(url: str, headers: dict, model: str, prompt: str) -> tuple[str, tuple[int, int]]:
    """OpenAI and OpenRouter share the chat-completions shape."""
    data = _post(url, headers, {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    })
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"no choices in response: {str(data)[:300]}")
    text = (choices[0].get("message") or {}).get("content") or ""
    usage = data.get("usage") or {}
    return text.strip(), (int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0))


def _anthropic_messages(key: str, model: str, prompt: str) -> tuple[str, tuple[int, int]]:
    data = _post("https://api.anthropic.com/v1/messages", {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    }, {
        "model": model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    })
    if data.get("stop_reason") == "refusal":
        details = data.get("stop_details") or {}
        raise RuntimeError(f"the model declined: {details.get('category') or 'refusal'}")
    text = "\n".join(b.get("text", "") for b in data.get("content") or [] if b.get("type") == "text")
    usage = data.get("usage") or {}
    return text.strip(), (int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0))


def _gemini_generate(key: str, model: str, prompt: str) -> tuple[str, tuple[int, int]]:
    data = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {
        "x-goog-api-key": key,
    }, {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": MAX_OUTPUT_TOKENS},
    })
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"no candidates in response: {str(data)[:300]}")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "\n".join(p.get("text", "") for p in parts if p.get("text"))
    usage = data.get("usageMetadata") or {}
    return text.strip(), (int(usage.get("promptTokenCount") or 0), int(usage.get("candidatesTokenCount") or 0))


if __name__ == "__main__":
    picked = pick_provider()
    if picked:
        provider, key, model = picked
        print(f"Provider: {provider}  model: {model}  key: {key[:6]}...")
    else:
        print("No model key found. Add OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY "
              "or GEMINI_API_KEY to ~/.claude/.env.")
