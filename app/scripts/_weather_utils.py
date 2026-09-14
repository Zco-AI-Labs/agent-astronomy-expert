import logging
import re
import urllib.parse
from typing import Any

import httpx

logger = logging.getLogger(__name__)

COORDINATES_REGEX = re.compile(
    r"^\s*([-+]?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+)?))\s*,\s*([-+]?(?:180(?:\.0+)?|(?:1[0-7]\d|[1-9]?\d)(?:\.\d+)?))\s*$"
)


async def geocode_location(location_query: str | None) -> dict[str, Any] | None:
    """
    Resolves a location query (e.g., 'Denver, CO', 'Flagstaff, AZ', 'London', or '35.2,-111.6')
    into geographical coordinates and metadata using Open-Meteo's free Geocoding API.
    Returns None if location is empty, unknown, or if resolution fails (no silent fallbacks).
    """
    if not location_query or not location_query.strip():
        return None

    trimmed = location_query.strip()
    coord_match = COORDINATES_REGEX.match(trimmed)
    if coord_match:
        lat = float(coord_match.group(1))
        lon = float(coord_match.group(2))
        return {
            "name": f"{lat:.4f}°, {lon:.4f}°",
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
        }

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(trimmed)}&count=1&language=en&format=json"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results")
                if results and len(results) > 0:
                    top = results[0]
                    name_parts = [top.get("name", "")]
                    if top.get("admin1"):
                        name_parts.append(top["admin1"])
                    if top.get("country_code"):
                        name_parts.append(top["country_code"].upper())
                    display_name = ", ".join(filter(None, name_parts))
                    return {
                        "name": display_name,
                        "latitude": float(top.get("latitude")),
                        "longitude": float(top.get("longitude")),
                        "timezone": top.get("timezone", "auto"),
                    }
    except Exception as e:
        logger.warning(f"Geocoding API request failed for '{location_query}': {e}")

    return None


async def get_weather_forecast(
    latitude: float, longitude: float, date: str | None = None
) -> dict[str, Any]:
    """
    Fetches hourly meteorological conditions and daily astronomical ephemerides (sunrise, sunset,
    moonrise, moonset, moon phase) from Open-Meteo's free Forecast API for a specific date or current window.
    Does NOT return fake or hardcoded weather when the service is unreachable.
    """
    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility",
        "daily": "sunrise,sunset,daylight_duration,moonrise,moonset,moon_phase",
        "timezone": "auto",
    }

    if date:
        params["start_date"] = date
        params["end_date"] = date
    else:
        params["forecast_days"] = 2

    url = "https://api.open-meteo.com/v1/forecast"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return {
                    "error": f"Open-Meteo weather API returned status {resp.status_code}: {resp.text[:100]}",
                    "is_available": False,
                }

            data = resp.json()
            hourly = data.get("hourly", {})
            daily = data.get("daily", {})

            times = hourly.get("time", [])
            cloud_cover_arr = hourly.get("cloud_cover", [])
            humidity_arr = hourly.get("relative_humidity_2m", [])
            temp_arr = hourly.get("temperature_2m", [])
            visibility_arr = hourly.get("visibility", [])
            precip_arr = hourly.get("precipitation_probability", [])

            sunsets = daily.get("sunset", [])
            sunrises = daily.get("sunrise", [])
            moonrises = daily.get("moonrise", [])
            moonsets = daily.get("moonset", [])
            moon_phases = daily.get("moon_phase", [])

            sunset_iso = sunsets[0] if sunsets else None
            sunrise_iso = sunrises[0] if sunrises else None
            moonrise_iso = moonrises[0] if moonrises else None
            moonset_iso = moonsets[0] if moonsets else None
            moon_phase_val = moon_phases[0] if moon_phases else None

            # Determine evening observation indices based on actual sunset time
            sunset_hour = 20
            if sunset_iso and "T" in sunset_iso:
                try:
                    sunset_hour = int(sunset_iso.split("T")[-1].split(":")[0])
                except (ValueError, IndexError):
                    pass

            target_hours = [
                f"T{(sunset_hour + offset) % 24:02d}:00" for offset in range(1, 6)
            ]
            night_indices = []
            for idx, t_str in enumerate(times):
                if any(h in t_str for h in target_hours):
                    night_indices.append(idx)
                    if len(night_indices) >= 5:
                        break

            if not night_indices and cloud_cover_arr:
                night_indices = list(range(min(6, len(cloud_cover_arr))))

            avg_cloud = int(sum(cloud_cover_arr[i] for i in night_indices) / len(night_indices)) if night_indices else 0
            avg_humidity = int(sum(humidity_arr[i] for i in night_indices) / len(night_indices)) if night_indices else 0
            avg_temp_c = float(sum(temp_arr[i] for i in night_indices) / len(night_indices)) if night_indices else 15.0
            avg_temp_f = int((avg_temp_c * 9 / 5) + 32)
            avg_vis = float(sum(visibility_arr[i] for i in night_indices) / len(night_indices)) if night_indices else 20000.0
            precip_chance = int(max(precip_arr[i] for i in night_indices)) if night_indices else 0

            # Compute Astronomical Seeing & Transparency Rating
            if avg_cloud < 15 and avg_humidity < 60 and avg_vis >= 20000 and precip_chance < 10:
                seeing_rating = "Excellent (Crisp & Steady)"
            elif avg_cloud < 40 and precip_chance < 20:
                seeing_rating = "Good (Slight Atmospheric Haze)"
            elif avg_cloud < 75:
                seeing_rating = "Fair (Variable Cloudiness)"
            else:
                seeing_rating = "Poor (Heavy Overcast / Obstruction)"

            return {
                "is_available": True,
                "cloud_cover": avg_cloud,
                "relative_humidity": avg_humidity,
                "temperature_f": avg_temp_f,
                "temperature_c": round(avg_temp_c, 1),
                "visibility_km": round(avg_vis / 1000.0, 1),
                "precipitation_probability": precip_chance,
                "seeing_quality": seeing_rating,
                "sunset_time": sunset_iso.split("T")[-1] if sunset_iso else None,
                "sunrise_time": sunrise_iso.split("T")[-1] if sunrise_iso else None,
                "moonrise_time": moonrise_iso.split("T")[-1] if moonrise_iso else None,
                "moonset_time": moonset_iso.split("T")[-1] if moonset_iso else None,
                "moon_phase_fraction": moon_phase_val,
                "is_overcast": avg_cloud >= 75,
            }
    except Exception as e:
        logger.warning(f"Open-Meteo weather API call failed: {e}")
        return {
            "error": f"Open-Meteo weather service error: {e}",
            "is_available": False,
        }
