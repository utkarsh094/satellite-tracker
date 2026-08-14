import os
import sys
from math import degrees, pi
from tracking.propagator import load_satellite 
from flask import Blueprint, jsonify, request
from tracking.topocentric import get_tracking_data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  
from tle.fetcher import fetch_group 
  
api = Blueprint("api", __name__)
@api.route("/satellites", methods=["GET"])
def satellites():
    group = request.args.get("group", config.DEFAULT_GROUP)
    try:
        raw = fetch_group(group)
    except Exception as e:
        return jsonify({"error": f"Could not load satellite list: {e}"}), 500
    result = [
        {"name": sat["OBJECT_NAME"], "norad_id": int(sat["NORAD_CAT_ID"])}
        for sat in raw]
    return jsonify(result)

@api.route("/track", methods=["GET"])
def track():
    sat_param = request.args.get("sat")
    group = request.args.get("group", config.DEFAULT_GROUP)
    if sat_param is None:
        return jsonify({"error": "Missing required query parameter: sat"}), 400
    try:
        norad_id = int(sat_param)
    except ValueError:
        return jsonify({"error": f"'sat' must be a NORAD catalog number, got: {sat_param}"}), 400
    satellite = load_satellite(norad_id, group=group)
    if satellite is None:
        return jsonify({"error": f"Satellite {norad_id} not found in group '{group}'"}), 404
    data = get_tracking_data(satellite)
    m = satellite.model
    data["orbitalElements"] = {
    "Inclination [deg]": round(float(degrees(m.inclo)), 4),
    "Eccentricity": round(float(m.ecco), 8),
    "RAAN [deg]": round(float(degrees(m.nodeo)), 4),
    "Mean Motion [rev/day]": round(float(m.no_kozai) * 720 / pi, 8),
    "Epoch [UTC]": satellite.epoch.utc_datetime().strftime("%Y-%m-%dT%H:%M:%S.%f"),}
    return jsonify(data)