# Satellite Position Tracker

A self-hosted satellite tracking system: fetches live orbital data (TLEs), computes real-time Azimuth/Elevation for a fixed ground location using SGP4.

This is being built incrementally, day by day. See `docs/PRD.md` for the
full project rationale and `docs/ARCHITECTURE.md` for the system design.
(Above part will be added later , the project progress)

## TLE fetcher

`backend/tle/fetcher.py` downloads orbital element data from
[Celestrak](https://celestrak.org) and caches it locally, refreshing at most once every `TLE_REFRESH_INTERVAL_HOURS` (set in `config.py`) to respect Celestrak's fair-use limits.

### Setup

```bash
cd backend
pip install -r requirements.txt
```

### Run

```bash
python3 tle/fetcher.py
```

First run downloads and caches data for the group set in
`config.DEFAULT_GROUP` (default: `stations`). Running it again immediately will just reuse the cache instead of re-downloading.

Edit `config.py` to set your own observer latitude/longitude/elevation before later stages (Az/El calculation depends on this).
