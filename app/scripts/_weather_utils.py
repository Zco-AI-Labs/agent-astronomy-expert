import asyncio
import logging
import re
import time
import urllib.parse
from typing import Any

import httpx

logger = logging.getLogger(__name__)

COORDINATES_REGEX = re.compile(
    r"^\s*([-+]?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+)?))\s*,\s*([-+]?(?:180(?:\.0+)?|(?:1[0-7]\d|[1-9]?\d)(?:\.\d+)?))\s*$"
)

# In-memory TTL caches to avoid repeated external calls and rate limits
_WEATHER_CACHE: dict[tuple, tuple[float, dict[str, Any]]] = {}
_GEOCODE_CACHE: dict[str, tuple[float, dict[str, Any] | None]] = {}
CACHE_TTL_SECONDS = 900  # 15 minutes


async def geocode_location(location_query: str | None) -> dict[str, Any] | None:
    """
    Resolves a location query (e.g., 'Denver, CO', 'Flagstaff, AZ', 'London', or '35.2,-111.6')
    into geographical coordinates and metadata using Open-Meteo's free Geocoding API.
    Returns None if location is empty, unknown, or if resolution fails (no silent fallbacks).
    Includes in-memory caching and retry with exponential backoff on transient errors.
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

    norm_key = trimmed.lower()
    cached = _GEOCODE_CACHE.get(norm_key)
    if cached:
        cached_ts, cached_val = cached
        if (time.time() - cached_ts) < CACHE_TTL_SECONDS:
            return cached_val

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(trimmed)}&count=1&language=en&format=json"
    attempts = 3
    for attempt in range(attempts):
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
                        geo_res = {
                            "name": display_name,
                            "latitude": float(top.get("latitude")),
                            "longitude": float(top.get("longitude")),
                            "timezone": top.get("timezone", "auto"),
                        }
                        _GEOCODE_CACHE[norm_key] = (time.time(), geo_res)
                        return geo_res
                    else:
                        _GEOCODE_CACHE[norm_key] = (time.time(), None)
                        return None
                elif resp.status_code in (429, 500, 502, 503, 504):
                    logger.warning(f"Geocoding API status {resp.status_code} (attempt {attempt + 1}/{attempts})")
                    if attempt < attempts - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.warning(f"Geocoding network error (attempt {attempt + 1}/{attempts}) for '{location_query}': {e}")
            if attempt < attempts - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        except Exception as e:
            logger.warning(f"Geocoding API request failed for '{location_query}': {e}")
            break

    return None


async def resolve_observing_location(
    location_query: str | None = None,
) -> dict[str, Any] | None:
    """
    Resolves observing coordinates and display name following this priority order:
    1. Explicit user-provided location_query (e.g., 'Flagstaff, AZ' or '35.19,-111.65')
    2. Active RemoteContext (user_location, userLocation, location, hub_location, coordinates)
    3. User-scoped persistent profile in Firestore / local cache (manage_stargazer_profile)
    Returns None only if all sources are completely empty/unresolved.
    """
    # 1. Explicit user-provided location argument
    if location_query and location_query.strip():
        geo = await geocode_location(location_query.strip())
        if not geo:
            return {
                "error": f"Could not resolve geographical coordinates for location '{location_query}'. Please check the spelling or provide 'lat,lon' decimal coordinates."
            }
        return {
            "name": geo["name"],
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "timezone": geo.get("timezone", "auto"),
            "source": "user_argument",
        }

    # 2. Check RemoteContext (Platform / GEAP runtime session metadata)
    try:
        import app.core.hubscape_adk
        ctx = app.core.hubscape_adk.get_context()
        raw = getattr(ctx, "raw_context", {}) or {}

        # Look for location structures either on ctx attributes (Hubscape ADK Studio / HubscapeContext) or in raw_context (GEAP Cloud runtime)
        candidate = (
            getattr(ctx, "user_location", None)
            or getattr(ctx, "location", None)
            or getattr(ctx, "workspace_location", None)
            or getattr(ctx, "hub_location", None)
            or raw.get("user_location")
            or raw.get("userLocation")
            or raw.get("location")
            or raw.get("hub_location")
            or raw.get("hubLocation")
            or raw.get("workspace_location")
            or raw.get("device_location")
            or raw.get("client_location")
        )

        if isinstance(candidate, dict) and bool(candidate):
            lat = candidate.get("latitude") or candidate.get("lat")
            lon = candidate.get("longitude") or candidate.get("lng") or candidate.get("lon")
            if lat is not None and lon is not None:
                lat_f = float(lat)
                lon_f = float(lon)
                name = (
                    candidate.get("city")
                    or candidate.get("label")
                    or candidate.get("address")
                    or candidate.get("name")
                    or f"{lat_f:.4f}°, {lon_f:.4f}°"
                )
                return {
                    "name": name,
                    "latitude": lat_f,
                    "longitude": lon_f,
                    "timezone": candidate.get("timezone", "auto"),
                    "source": "remote_context",
                }
            elif candidate.get("city") or candidate.get("address") or candidate.get("label") or candidate.get("name"):
                query_str = candidate.get("city") or candidate.get("address") or candidate.get("label") or candidate.get("name")
                geo = await geocode_location(str(query_str))
                if geo:
                    return {
                        "name": geo["name"],
                        "latitude": geo["latitude"],
                        "longitude": geo["longitude"],
                        "timezone": geo.get("timezone", "auto"),
                        "source": "remote_context",
                    }
        elif isinstance(candidate, str) and candidate.strip():
            geo = await geocode_location(candidate.strip())
            if geo:
                return {
                    "name": geo["name"],
                    "latitude": geo["latitude"],
                    "longitude": geo["longitude"],
                    "timezone": geo.get("timezone", "auto"),
                    "source": "remote_context",
                }
        elif raw.get("latitude") is not None and (raw.get("longitude") is not None or raw.get("lng") is not None):
            lat_f = float(raw["latitude"])
            lon_f = float(raw.get("longitude") or raw.get("lng"))
            return {
                "name": raw.get("city") or f"{lat_f:.4f}°, {lon_f:.4f}°",
                "latitude": lat_f,
                "longitude": lon_f,
                "timezone": raw.get("timezone", "auto"),
                "source": "remote_context",
            }
    except Exception:
        pass

    # 3. Check persistent stargazer profile
    try:
        from app.scripts.manage_stargazer_profile import manage_stargazer_profile
        saved = await manage_stargazer_profile(action="get")
        prof = saved.get("profile")
        if prof and prof.get("latitude") is not None and prof.get("longitude") is not None:
            return {
                "name": prof.get("city_name", f"{float(prof['latitude']):.2f}°, {float(prof['longitude']):.2f}°"),
                "latitude": float(prof["latitude"]),
                "longitude": float(prof["longitude"]),
                "timezone": prof.get("timezone", "auto"),
                "source": "saved_profile",
            }
    except Exception:
        pass

    return None


async def get_weather_forecast(
    latitude: float, longitude: float, date: str | None = None
) -> dict[str, Any]:
    """
    Fetches hourly meteorological conditions and daily astronomical ephemerides (sunrise, sunset,
    moonrise, moonset, moon phase) from Open-Meteo's free Forecast API for a specific date or current window.
    Includes in-memory caching (15 min TTL) and exponential backoff retries on transient errors/rate-limits (503/429).
    Does NOT return fake or hardcoded weather when the service is unreachable.
    """
    cache_key = (round(latitude, 2), round(longitude, 2), date or "current")
    cached = _WEATHER_CACHE.get(cache_key)
    if cached:
        cached_ts, cached_val = cached
        if (time.time() - cached_ts) < CACHE_TTL_SECONDS:
            return cached_val

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
    attempts = 3
    last_err = ""

    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
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

                    result = {
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
                    _WEATHER_CACHE[cache_key] = (time.time(), result)
                    return result
                elif resp.status_code in (429, 500, 502, 503, 504):
                    last_err = f"Open-Meteo weather API returned status {resp.status_code}: {resp.text[:100]}"
                    logger.warning(f"Open-Meteo transient error (attempt {attempt + 1}/{attempts}): {last_err}")
                    if attempt < attempts - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                else:
                    return {
                        "error": f"Open-Meteo weather API returned status {resp.status_code}: {resp.text[:100]}",
                        "is_available": False,
                    }
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            last_err = str(e)
            logger.warning(f"Open-Meteo network/timeout error (attempt {attempt + 1}/{attempts}): {e}")
            if attempt < attempts - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        except Exception as e:
            logger.warning(f"Open-Meteo weather API call failed: {e}")
            return {
                "error": f"Open-Meteo weather service error: {e}",
                "is_available": False,
            }

    return {
        "error": f"Open-Meteo weather service unavailable after {attempts} attempts: {last_err}",
        "is_available": False,
    }
