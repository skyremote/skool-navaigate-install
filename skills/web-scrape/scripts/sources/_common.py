"""Shared helpers for the research sources (Reddit, Academic, Substack, Supadata).

Mirrors webscrape.py conventions: REST over `requests`, keys (when any) read
from ~/.claude/.env, clean stderr exits, a --json flag for raw output. Reddit,
Academic and Substack need NO API keys (Reddit can use COMPOSIO_API_KEY for its
managed path); Supadata is paid and reads SUPADATA_API_KEY. The only env value
used here is OPENALEX_EMAIL (OpenAlex polite pool), which falls back to a safe
default; per-source keys are read in each source's own module.
"""
import json
import os
import sys
import time
import warnings
from pathlib import Path

# Quiet the LibreSSL/urllib3 NotOpenSSLWarning the system Python emits, matching
# webscrape.py, so it doesn't pollute the output the agent reads.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run: python3 -m pip install --user requests")

# Polite-pool default for OpenAlex/Unpaywall. Override via OPENALEX_EMAIL in
# ~/.claude/.env. Never a secret — just an identifier for the public API.
DEFAULT_POLITE_EMAIL = "research@navaigate.dev"

# Path to the Firecrawl/Exa helper, used by sources that need real web search
# or JS rendering (Substack discovery, Academic full-text). We shell out to it
# rather than re-implement Firecrawl/Exa here, so there is one place keys live.
WEBSCRAPE = Path(__file__).resolve().parent.parent / "webscrape.py"


def load_env():
    """Populate os.environ from ~/.claude/.env without overriding real env vars."""
    env_path = Path.home() / ".claude" / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def polite_email():
    """Email for OpenAlex/Unpaywall polite pool. Safe default if unset."""
    load_env()
    return os.environ.get("OPENALEX_EMAIL", "").strip() or DEFAULT_POLITE_EMAIL


class RateLimiter:
    """Minimum interval between requests, enforced per instance."""

    def __init__(self, min_interval):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self):
        elapsed = time.time() - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.time()

    def mark(self):
        self._last = time.time()


def emit(data, as_json):
    """Print a structured payload as raw JSON, or hand back to a human view."""
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def die(msg):
    sys.exit(msg)
