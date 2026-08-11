"""
Central configuration for the satellite tracker backend.
Edit OBSERVER_* to your actual ground station location before running anything.
"""
import os
from dotenv import load_dotenv
load_dotenv()
# Observer location (used for Az/El calculations)
# one defauld location is already set init.
# after upadated cod eit eill reaf from .env file environment.
OBSERVER_LAT_DEG = float(os.environ.get("OBSERVER_LAT_DEG"))
OBSERVER_LON_DEG = float(os.environ.get("OBSERVER_LON_DEG"))
OBSERVER_ELEVATION_M = float(os.environ.get("OBSERVER_ELEVATION_M"))  # this is in meters; above sea level (approx)

# Celestrak site TLE fetch settings 
CELESTRAK_BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

# Which satellite group to fetch by default for the dashboard picker.
# See https://celestrak.org/NORAD/elements/ for all available group names.
# Examples: "active", "stations", "starlink", "gps-ops", "weather", "amateur", "visual"
DEFAULT_GROUP = "stations"

# CelesTrak only update data every 2 hours, not more than that.
# underlying source data is only refreshed ~3 times/day.
# Refreshing more often than this will  wastes requests and can get us rate-limited.
TLE_REFRESH_INTERVAL_HOURS = 6

# Where cached TLE data is stored locally (relative to backend/ folder)
TLE_CACHE_DIR = "tle/cache"
# API server settings
API_HOST = "0.0.0.0"
API_PORT = int(os.environ.get("PORT", 7789))