import datetime
import logging
from typing import Any

import app.core.hubscape_adk
from app.scripts._ephemeris_utils import (
    compute_stargazing_index,
    get_active_meteor_showers,
    get_moon_ephemeris,
    get_target_ephemeris,
)
from app.scripts._weather_utils import geocode_location, get_weather_forecast
from app.scripts.manage_stargazer_profile import manage_stargazer_profile

logger = logging.getLogger(__name__)


@app.core.hubscape_adk.require_tool_privilege
async def get_stargazing_forecast(
    location: str | None = None,
    date: str | None = None,
) -> dict[str, Any]:
    """
    Retrieves a comprehensive night-sky stargazing forecast for tonight or a specified date,
    combining local meteorological metrics (cloud cover, seeing, transparency) with celestial
    ephemerides (moon phase, illumination, visible planets, constellations, and events).
    Automatically renders the 'night_sky_forecast' Generative UI card.

    Args:
        location: City name, zip code, or comma-separated 'lat,lon' coordinates. If omitted,
                  uses the user's saved observing location profile.
        date: Target observation date in YYYY-MM-DD format (defaults to current date).

    Returns:
        A dictionary containing:
        - location_name: Resolved location display name.
        - stargazing_index: Score from 0 to 100 with qualitative rating label.
        - weather: { cloud_cover, seeing_quality, temperature_f, precipitation_probability }.
        - moon: { phase_name, illumination_percent, moonrise_time, moonset_time, dark_sky_window }.
        - visible_targets: List of bright planets and clusters visible above horizon tonight.
        - active_events: Active meteor showers or upcoming highlights.
        - summary: Actionable narrative recommendation for the observer.
    """
    # 1. Resolve Observing Location
    loc_display: str | None = None
    lat: float | None = None
    lon: float | None = None

    if location and location.strip():
        geo = await geocode_location(location)
        if not geo:
            return {
                "status": "error",
                "message": f"Could not resolve geographical coordinates for location '{location}'. Please check the city or provide 'lat,lon' coordinates.",
            }
        lat = geo["latitude"]
        lon = geo["longitude"]
        loc_display = geo["name"]
    else:
        # Check saved profile
        saved = await manage_stargazer_profile(action="get")
        prof = saved.get("profile")
        if prof and prof.get("latitude") is not None and prof.get("longitude") is not None:
            lat = float(prof["latitude"])
            lon = float(prof["longitude"])
            loc_display = prof.get("city_name", f"{lat:.2f}°, {lon:.2f}°")
        else:
            return {
                "status": "location_required",
                "message": (
                    "No observing location is saved in your profile. Please provide your city, "
                    "zip code, or coordinates so I can generate an accurate local stargazing forecast."
                ),
            }

    # 2. Resolve observation date
    now = datetime.datetime.now(datetime.UTC)
    target_dt = now
    date_str = None
    if date:
        try:
            parsed = datetime.datetime.strptime(date, "%Y-%m-%d")
            date_str = parsed.strftime("%Y-%m-%d")
            # Set to evening hours (22:00 UTC) for night viewing
            target_dt = datetime.datetime(parsed.year, parsed.month, parsed.day, 22, 0, tzinfo=datetime.UTC)
        except Exception:
            date_str = now.strftime("%Y-%m-%d")
    else:
        date_str = now.strftime("%Y-%m-%d")

    # 3. Fetch live weather & astronomy data from Open-Meteo
    weather = await get_weather_forecast(lat, lon, date=date_str)
    if not weather.get("is_available", True) or "error" in weather:
        return {
            "status": "error",
            "message": f"Unable to retrieve live forecast for {loc_display}: {weather.get('error', 'Weather service offline')}",
        }

    moon = get_moon_ephemeris(
        target_dt,
        moon_phase_fraction=weather.get("moon_phase_fraction"),
        moonrise_str=weather.get("moonrise_time"),
        moonset_str=weather.get("moonset_time"),
    )

    # 4. Check prime planet and deep-sky visibility
    check_objects = [
        "Venus", "Jupiter", "Mars", "Saturn", "Mercury",
        "Pleiades", "Orion Nebula", "Andromeda Galaxy", "Hercules Cluster",
        "Sirius", "Vega", "Arcturus", "Betelgeuse", "Polaris"
    ]
    visible_targets = []
    for obj in check_objects:
        eph = await get_target_ephemeris(obj, lat, lon, target_dt)
        if eph.get("is_visible_now"):
            visible_targets.append({
                "name": eph["target_name"],
                "altitude": eph["altitude_degrees"],
                "azimuth": eph["azimuth_degrees"],
                "direction": eph["cardinal_direction"],
                "constellation": eph["constellation"],
                "optics": eph["optical_aid_required"],
            })

    # Sort visible targets by altitude descending
    visible_targets.sort(key=lambda x: x["altitude"], reverse=True)

    # 5. Compute Stargazing Index Score
    cloud_cover = weather.get("cloud_cover", 0)
    illumination = moon.get("illumination_percent", 0)
    seeing = weather.get("seeing_quality", "Good (Slight Atmospheric Haze)")
    score, rating_label = compute_stargazing_index(cloud_cover, illumination, seeing)

    # 6. Active Meteor Showers
    meteor_showers = get_active_meteor_showers(target_dt)

    # 7. Compute Prime Viewing Window dynamically
    sunset_str = weather.get("sunset_time")
    moonset_str = weather.get("moonset_time")
    if cloud_cover > 75:
        prime_window = "Cloud obscured / Limited clear breaks"
    elif sunset_str:
        if moonset_str and illumination > 35:
            prime_window = f"After moonset (~{moonset_str}) until dawn"
        else:
            prime_window = f"Post-twilight (~1 hr after {sunset_str}) through midnight"
    else:
        prime_window = "Post-twilight into late night"

    targets_bullet_list = [f"{t['name']} in the {t['direction']} ({t['optics']})" for t in visible_targets[:4]]
    targets_summary = ", ".join(targets_bullet_list) if targets_bullet_list else "Seasonal star fields and asterisms"

    widget_data = {
        "location_name": loc_display,
        "stargazing_score": str(score),
        "stargazing_rating": rating_label.split(" ")[0],  # "Excellent", "Good", "Fair", "Poor"
        "cloud_cover": str(cloud_cover),
        "moon_phase": moon.get("phase_name", "Waxing Crescent"),
        "moon_illumination": str(illumination),
        "moon_set_time": moonset_str or "N/A",
        "prime_window": prime_window,
        "seeing_quality": seeing.split(" ")[0],
        "visible_targets_summary": targets_summary,
    }

    # Support direct prefix replacement in widget template
    for k, v in list(widget_data.items()):
        widget_data[f"data.{k}"] = v

    # 8. Render Lego Widget via context
    try:
        ctx = app.core.hubscape_adk.get_context()
        ctx.show_widget("night_sky_forecast", widget_data)
    except Exception as e:
        logger.debug(f"Could not render night_sky_forecast widget: {e}")

    # 9. Format narrative summary
    if weather.get("is_overcast"):
        narrative = (
            f"Overcast skies ({cloud_cover}% cloud cover) in {loc_display} will obstruct celestial viewing tonight. "
            f"Atmospheric conditions are rated {rating_label.upper()} ({score}/100). We recommend checking back on clearer nights."
        )
    else:
        moon_desc = f"{moon['phase_name']} at {illumination}% illumination"
        if moonset_str:
            moon_desc += f", setting at {moonset_str}"
        narrative = (
            f"Stargazing conditions in {loc_display} are rated {rating_label.upper()} ({score}/100) with {cloud_cover}% cloud cover. "
            f"The Moon is in its {moon_desc}. Prime observing window: {prime_window}. "
            f"Top visible celestial targets: {targets_summary}."
        )

    return {
        "status": "success",
        "location_name": loc_display,
        "stargazing_score": score,
        "stargazing_rating": rating_label,
        "weather": {
            "cloud_cover_percent": cloud_cover,
            "seeing_quality": seeing,
            "temperature_f": weather.get("temperature_f"),
            "precipitation_probability": weather.get("precipitation_probability"),
            "sunset_time": weather.get("sunset_time"),
            "sunrise_time": weather.get("sunrise_time"),
        },
        "moon": moon,
        "prime_window": prime_window,
        "visible_targets": visible_targets,
        "active_events": meteor_showers,
        "summary": narrative,
    }
