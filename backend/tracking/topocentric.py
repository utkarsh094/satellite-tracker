import math
import os
import sys
from datetime import timedelta, timezone
from skyfield.api import load, wgs84

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  
from tracking.propagator import load_satellite  

# Fixed observer location, built it once from config.py's coordinates which are alredy coded in it.
OBSERVER = wgs84.latlon(
    config.OBSERVER_LAT_DEG,
    config.OBSERVER_LON_DEG,
    elevation_m=config.OBSERVER_ELEVATION_M,)

# Local timezone offset from UTC, used only for the LOCAL_TIME field.
LOCAL_UTC_OFFSET = timedelta(hours=5, minutes=30)

def get_tracking_data(satellite) -> dict:
    ts = load.timescale()
    t = ts.now()

    # (Az/El) and equatorial (RA/Dec) coordinate systems.
    difference = satellite - OBSERVER
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()
    # Speed of satellite and it's velocity vector (km/s).
    vx, vy, vz = satellite.at(t).velocity.km_per_s
    speed_km_s = math.sqrt(vx**2 + vy**2 + vz**2)
    # Subpoint location
    geocentric = satellite.at(t)
    subpoint = wgs84.subpoint_of(geocentric)
    orbital_altitude_km = wgs84.height_of(geocentric).km
    local_dt = t.utc_datetime().astimezone(timezone.utc) + LOCAL_UTC_OFFSET
    elevation_deg = alt.degrees
    return {
        "NORAD ID": satellite.model.satnum,
        "Name": satellite.name,
        "Local Time": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "UTC": t.utc_strftime("%Y-%m-%d %H:%M:%S"),
        "Latitude [deg]": subpoint.latitude.degrees,
        "Longitude [deg]": subpoint.longitude.degrees,
        "Altitude [km]": orbital_altitude_km,
        "Altitude [mil]": orbital_altitude_km * 0.621371,
        "Speed [km/s]": speed_km_s,
        "Speed [km/h]": speed_km_s * 3600,
        "Azimuthal [deg]": az.degrees,
        "Elevation [deg]": elevation_deg,}


if __name__ == "__main__":
    
    iss = load_satellite(norad_cat_id=25544)
    if iss is None:
        print("Satellite not found in cache. Did the fetcher run first?")
    else:
        data = get_tracking_data(iss)
        for key, value in data.items():
            if isinstance(value, float):
                print(f"{key:28s}: {value:.4f}")
            else:
                print(f"{key:28s}: {value}")