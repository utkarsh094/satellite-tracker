"""
it will loads cached TLE/OMM data and will use Skyfield's SGP4 method implementation to calculate a satellite's real position at a given moment in time.

This module only works with GEOCENTRIC position (relative to Earth's center) and the ground pointed directly beneath the satellite. Converting this into Az/El relative to OUR location.
"""

import json
import os
import sys
from typing import Optional
from skyfield.api import EarthSatellite, load, wgs84

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config 


def load_satellite(norad_cat_id: int, group: Optional[str] = None):
    """ A Skyfield EarthSatellite object for one satellite, identified by its NORAD catalog number, from the locally cached TLE/OMM data for a given group (defaults to config.DEFAULT_GROUP).
    It will returns None if that satellite isn't found in the cached group."""
    group = group or config.DEFAULT_GROUP
    cache_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        config.TLE_CACHE_DIR,
        f"{group}.json",)
    if not os.path.exists(cache_path):
        raise FileNotFoundError(
            f"No cached data for group '{group}'. Run tle/fetcher.py first.")
    with open(cache_path, "r") as f:
        cached = json.load(f)
    ts = load.timescale()
    for fields in cached["satellites"]:
        if int(fields["NORAD_CAT_ID"]) == norad_cat_id:
            return EarthSatellite.from_omm(ts, fields)
    return None

def get_current_position(satellite: EarthSatellite) -> dict:
    """A Skyfield EarthSatellite,it will calculate its position RIGHT NOW/ in current time and will return a plain text like: subpoint latitude/longitude/altitude, plus the epoch of the orbital data being used (so we know how "old/fresh(new)" this is).
    """
    ts = load.timescale()
    t = ts.now()
    geocentric = satellite.at(t)
    subpoint = wgs84.subpoint_of(geocentric)
    return {
        "name": satellite.name,
        "time_utc": t.utc_iso(),
        "epoch_utc": satellite.epoch.utc_iso(),
        "latitude_deg": subpoint.latitude.degrees,
        "longitude_deg": subpoint.longitude.degrees,
        "altitude_km": wgs84.height_of(geocentric).km,}

if __name__ == "__main__":
    iss = load_satellite(norad_cat_id=48274)
    if iss is None:
        print("Satellite not found in cache. Did fetcher run first?")
    else:
        position = get_current_position(iss)
        print(f"Satellite: {position['name']}")
        print(f"Current time (UTC): {position['time_utc']}")
        print(f"TLE epoch (UTC):    {position['epoch_utc']}")
        print(f"Subpoint latitude:  {position['latitude_deg']:.4f} deg")
        print(f"Subpoint longitude: {position['longitude_deg']:.4f} deg")
        print(f"Altitude:           {position['altitude_km']:.1f} km")