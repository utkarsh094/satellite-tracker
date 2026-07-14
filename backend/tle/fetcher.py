"""
This handles fetching orbital element (GP/TLE) data from Celestrak, with local caching so we never hit their servers more often than necessary.

As CelesTrak does not update data more often than every 2 hours, and the underlying source data itself only refreshes ~3 times/day. This module enforces a configurable minimum refresh interval (see config.py) and serves cached data in between.
"""

import json
import os
import sys
from datetime import datetime, timezone
import requests

# it will allow running this file directly (python tle/fetcher.py) as well as importing it as part of the backend package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  
def _cache_path(group: str) -> str:
    """Build the local cache file path for a given group of ssatellite ."""
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.TLE_CACHE_DIR)
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{group}.json")

def _is_cache_stale(path: str) -> bool:
    """It will check if the cached file is missing or older than the refresh interval (for the refereshing)."""
    if not os.path.exists(path):
        return True
    with open(path, "r") as f:
        cached = json.load(f)
    fetched_at = datetime.fromisoformat(cached["fetched_at"])
    age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600
    return age_hours >= config.TLE_REFRESH_INTERVAL_HOURS


def fetch_group(group: str = None, force: bool = False) -> list:
    """It will return orbital element data (list of satellite dicts) for a Celestrak group, e.g. 'stations', 'active', 'starlink'.
       It will use the local cache unless it's old (or force=True), in which case it will re-downloads the data from Celestrak and updates the cache.
    """
    group = group or config.DEFAULT_GROUP
    path = _cache_path(group)
    if force or _is_cache_stale(path):
        print(f"[fetcher] Fetching fresh TLE data for group '{group}' from Celestrak...")
        url = f"{config.CELESTRAK_BASE_URL}?GROUP={group}&FORMAT=json"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"CelesTrak returned no data for group '{group}'. Check the group name.")
        cached = {
            "group": group,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "satellites": data,}
        with open(path, "w") as f:
            json.dump(cached, f, indent=2)
        print(f"[fetcher] Cached {len(data)} satellites -> {path}")
        return data
    print(f"[fetcher] Using cached TLE data for group '{group}' (still fresh).")
    with open(path, "r") as f:
        cached = json.load(f)
    return cached["satellites"]

if __name__ == "__main__":
    satellites = fetch_group()
    print(f"\nFetched {len(satellites)} satellites in group '{config.DEFAULT_GROUP}':")
    for sat in satellites[:5]:
        print(f"  - {sat['OBJECT_NAME']} (NORAD {sat['NORAD_CAT_ID']})")