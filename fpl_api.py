"""
fpl_api.py - Gets data from the official (free, no login needed) FPL API.

Two endpoints do most of the work:
  bootstrap-static -> every player, team and gameweek
  fixtures         -> every match, with a difficulty rating (1 = easy, 5 = hard)

We save a copy to disk ("cache") so we don't hit the API on every page load.
If the internet isn't available, we fall back to the small sample data in sample_data/.
"""
import json
import time
from pathlib import Path

import requests

BASE_URL = "https://fantasy.premierleague.com/api"
HERE = Path(__file__).parent
CACHE_DIR = HERE / "cache"
SAMPLE_DIR = HERE / "sample_data"
CACHE_SECONDS = 60 * 60  # refresh at most once an hour


def _get_json(endpoint: str, cache_name: str) -> dict | list:
    """Return JSON from cache if fresh, otherwise from the API, otherwise sample data."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / cache_name

    # 1. Fresh cache?
    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < CACHE_SECONDS:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    # 2. Live API
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", timeout=10,
                            headers={"User-Agent": "fpl-guide-student-project"})
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        return data
    except requests.RequestException as err:
        print(f"[fpl_api] Couldn't reach FPL API ({err}). Using sample data.")

    # 3. Sample data fallback
    return json.loads((SAMPLE_DIR / cache_name).read_text(encoding="utf-8"))


def get_bootstrap() -> dict:
    return _get_json("bootstrap-static/", "bootstrap.json")


def get_fixtures() -> list:
    return _get_json("fixtures/?future=1", "fixtures.json")
