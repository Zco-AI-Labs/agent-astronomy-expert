import datetime
import logging
from typing import Any

import app.core.hubscape_adk
from app.scripts._ephemeris_utils import fetch_iss_telemetry, get_target_ephemeris
from app.scripts._weather_utils import geocode_location, resolve_observing_location
from app.scripts.manage_stargazer_profile import manage_stargazer_profile

logger = logging.getLogger(__name__)


@app.core.hubscape_adk.require_tool_privilege
async def get_celestial_body_position(
    target: str,
    location: str | None = None,
    date: str | None = None,
    time: str | None = None,
) -> dict[str, Any]:
    """
    Calculates the real-time horizontal coordinates (altitude angle and compass azimuth),
    current visibility status, and viewing window for a specific celestial body or satellite.
    Automatically renders the 'celestial_target_card' Generative UI card.

    Args:
        target: Name of the celestial body (e.g., 'Mars', 'Jupiter', 'Saturn', 'Venus',
                'Moon', 'Orion Nebula', 'Andromeda Galaxy', 'ISS', 'Sirius', 'Pleiades').
        location: Observing location (city name, zip code, or 'lat,lon'). Defaults to saved profile.
        date: Target observation date in YYYY-MM-DD format (defaults to current date).
        time: Target observation time in HH:MM format (defaults to current time).

    Returns:
        A dictionary containing:
        - target_name: Standardized celestial object name.
        - is_visible_now: Boolean indicating if object is currently above horizon.
        - altitude_degrees: Elevation angle above the horizon (-90° to +90°).
        - azimuth_degrees: Compass bearing in degrees (0° to 360°).
        - cardinal_direction: Human-readable direction (e.g., 'Southeast', 'South-Southwest').
        - constellation: Constellation currently hosting the object.
        - apparent_magnitude: Visual brightness rating.
        - best_viewing_window: Time window when object is highest in dark sky.
        - optical_aid_required: 'Naked Eye', 'Binoculars', or 'Telescope'.
        - pointing_instructions: Clear narrative describing how to find the object in the sky.
    """
    # 1. Special Handling: International Space Station (ISS) Satellite
    target_clean = target.strip().lower()
    if target_clean in ["iss", "space station", "international space station"]:
        iss_data = await fetch_iss_telemetry()
        if iss_data:
            return {
                "status": "success",
                "target_name": "International Space Station (ISS)",
                "type": "Low Earth Orbit Satellite",
                "is_visible_now": iss_data.get("visibility") == "daylight",
                "current_latitude": iss_data.get("latitude"),
                "current_longitude": iss_data.get("longitude"),
                "altitude_km": iss_data.get("altitude_km"),
                "velocity_km_h": iss_data.get("velocity_km_h"),
                "visibility_condition": iss_data.get("visibility"),
                "optical_aid_required": "Naked Eye (Fast-Moving Bright Light)",
                "pointing_instructions": (
                    f"The ISS is currently cruising at {iss_data.get('altitude_km')} km altitude "
                    f"at {iss_data.get('velocity_km_h')} km/h above coordinates "
                    f"({iss_data.get('latitude')}°, {iss_data.get('longitude')}°)."
                ),
            }

    # 2. Resolve Observing Location (User Arg -> RemoteContext -> Stargazer Profile)
    loc_info = await resolve_observing_location(location)
    if not loc_info:
        return {
            "status": "location_required",
            "message": (
                "No observing location was provided in your query or detected in your active session context. "
                "Please specify your city, zip code, or coordinates so I can determine where this object is in your sky."
            ),
        }
    if "error" in loc_info:
        return {
            "status": "error",
            "message": loc_info["error"],
        }

    lat = loc_info["latitude"]
    lon = loc_info["longitude"]
    loc_display = loc_info["name"]

    # 3. Resolve Target Datetime
    now = datetime.datetime.now(datetime.UTC)
    target_dt = now
    if date or time:
        d_part = date if date else now.strftime("%Y-%m-%d")
        t_part = time if time else "22:00"
        try:
            parsed = datetime.datetime.strptime(f"{d_part} {t_part}", "%Y-%m-%d %H:%M")
            target_dt = parsed.replace(tzinfo=datetime.UTC)
        except Exception:
            target_dt = now

    # 4. Fetch Live Ephemeris & Compute Coordinates
    eph = await get_target_ephemeris(target, lat, lon, target_dt)
    if eph.get("error"):
        return {
            "status": "not_found",
            "message": eph["error"],
        }

    alt = eph["altitude_degrees"]
    az = eph["azimuth_degrees"]
    cardinal = eph["cardinal_direction"]
    constellation = eph.get("constellation", "Known Constellation")
    is_visible = eph["is_visible_now"]
    target_name = eph["target_name"]
    optics = eph["optical_aid_required"]

    # 5. Formulate Pointing Instructions
    if is_visible:
        if alt > 60:
            height_desc = "nearly straight overhead near zenith"
        elif alt > 30:
            height_desc = f"about halfway up from the horizon (~{int(alt)}°)"
        else:
            height_desc = f"low above the horizon (~{int(alt)}°)"
        pointing = f"Look toward the {cardinal}, {height_desc} in the constellation {constellation}."
    else:
        pointing = (
            f"{target_name} is currently below your local horizon ({alt}° altitude). "
            f"It will rise in the {cardinal} later during its celestial transit."
        )

    # 6. Render Generative UI Widget
    widget_data = {
        "target_name": target_name,
        "visibility_status": "Visible Now" if is_visible else "Below Horizon",
        "cardinal_direction": cardinal,
        "azimuth_degrees": str(int(az)),
        "altitude_degrees": str(int(alt)),
        "constellation": constellation,
        "optical_aid_required": optics,
    }
    for k, v in list(widget_data.items()):
        widget_data[f"data.{k}"] = v

    try:
        ctx = app.core.hubscape_adk.get_context()
        ctx.show_widget("celestial_target_card", widget_data)
    except Exception as e:
        logger.debug(f"Could not render celestial_target_card widget: {e}")

    return {
        "status": "success",
        "target_name": target_name,
        "is_visible_now": is_visible,
        "visibility_status": widget_data["visibility_status"],
        "altitude_degrees": alt,
        "azimuth_degrees": az,
        "cardinal_direction": cardinal,
        "constellation": constellation,
        "apparent_magnitude": eph.get("apparent_magnitude"),
        "optical_aid_required": optics,
        "best_viewing_window": eph.get("best_viewing_window"),
        "pointing_instructions": pointing,
        "observing_location": loc_display,
        "observation_time_utc": target_dt.strftime("%Y-%m-%d %H:%M UTC"),
    }
