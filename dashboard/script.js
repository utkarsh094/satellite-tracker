const API_BASE_URL = "http://localhost:7789";
const REFRESH_INTERVAL_MS = 1000;

let refreshTimer = null;
async function loadSatelliteList() {
  const select = document.getElementById("satelliteSelect");
  const statusEl = document.getElementById("connectionStatus");
  try {
    const response = await fetch(`${API_BASE_URL}/satellites`);
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const satellites = await response.json();
    select.innerHTML = "";
    satellites.forEach((sat) => {
      const option = document.createElement("option");
      option.value = sat.norad_id;
      option.textContent = `${sat.name} (${sat.norad_id})`;
      select.appendChild(option);});
    statusEl.textContent = "[ online ]";
    statusEl.className = "status-online";
    startTracking();} catch (err) {
    statusEl.textContent = "[ offline ]";
    statusEl.className = "status-offline";
    showError(
      `Could not reach backend at ${API_BASE_URL}. Is app.py running? (${err.message})`);}}

function startTracking() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(updateTrackingData, REFRESH_INTERVAL_MS);
  updateTrackingData();}
async function updateTrackingData() {
  const select = document.getElementById("satelliteSelect");
  const noradId = select.value;
  if (!noradId) return;
  try {
    const response = await fetch(`${API_BASE_URL}/track?sat=${noradId}`);
    const data = await response.json();
    if (!response.ok) {
      showError(data.error || "404 satellite not found");
      return;}
    hideError();
    renderData(data);
    if (data.orbitalElements) {
      renderOrbitalElements(data.orbitalElements);(
        data.orbitalElements["Inclination [deg]"],
        data.orbitalElements["Eccentricity"]);}} 
        catch (err) {
    showError(`Lost connection to backend: ${err.message}`);}}

function renderData(data) {
  set("val_norad", data["NORAD ID"]);
  set("val_name", data["Name"]);
  set("val_localtime", data["Local Time"]);
  set("val_utc", data["UTC"]);
  set("val_lat", formatDeg(data["Latitude [deg]"]));
  set("val_lon", formatDeg(data["Longitude [deg]"]));
  set("val_alt", `${data["Altitude [km]"].toFixed(2)} km`);
  set("val_speed", `${data["Speed [km/s]"].toFixed(3)} km/s`);
  set("val_az", formatDeg(data["Azimuthal [deg]"]));
  set("val_el", formatDeg(data["Elevation [deg]"]));
  const visible = data["Elevation [deg]"] > 0;
  const visEl = document.getElementById("val_visible");
  visEl.textContent = visible ? "YES" : "NO (below horizon)";
  visEl.style.color = visible ? "#008000" : "#800000";}

function renderOrbitalElements(oe) {set("oe_incl", `${oe["Inclination [deg]"].toFixed(2)}\u00B0`);
  set("oe_ecc", oe["Eccentricity"].toFixed(4));
  set("oe_raan", `${oe["RAAN [deg]"].toFixed(2)}\u00B0`);
  set("oe_mm", `${oe["Mean Motion [rev/day]"].toFixed(2)} rev/day`);
  set("oe_epoch", oe["Epoch [UTC]"]);} 

function set(id, value) {
  document.getElementById(id).textContent = value;}

function formatDeg(value) {
  return `${value.toFixed(2)}\u00B0`;}

function showError(message) {
  const box = document.getElementById("errorBox");
  box.textContent = message;
  box.style.display = "block";}

function hideError() {
  document.getElementById("errorBox").style.display = "none";}

document.getElementById("satelliteSelect").addEventListener("change", startTracking);
loadSatelliteList();