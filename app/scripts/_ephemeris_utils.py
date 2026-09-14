import datetime
import logging
import math
import re
import urllib.parse
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Comprehensive catalog of bright stars and famous deep-sky objects
DEEP_SKY_CATALOG: dict[str, dict[str, Any]] = {
    "orion nebula": {
        "name": "Orion Nebula (M42)",
        "ra_hours": 5.588,
        "dec_deg": -5.391,
        "magnitude": 4.0,
        "optics": "Binoculars or Small Telescope",
        "type": "Diffuse Nebula",
    },
    "andromeda galaxy": {
        "name": "Andromeda Galaxy (M31)",
        "ra_hours": 0.712,
        "dec_deg": 41.269,
        "magnitude": 3.44,
        "optics": "Binoculars or Naked Eye (Dark Sky)",
        "type": "Spiral Galaxy",
    },
    "pleiades": {
        "name": "Pleiades (Seven Sisters, M45)",
        "ra_hours": 3.791,
        "dec_deg": 24.105,
        "magnitude": 1.6,
        "optics": "Naked Eye or Wide Binoculars",
        "type": "Open Star Cluster",
    },
    "hercules cluster": {
        "name": "Great Hercules Cluster (M13)",
        "ra_hours": 16.695,
        "dec_deg": 36.460,
        "magnitude": 5.8,
        "optics": "Binoculars or Telescope",
        "type": "Globular Cluster",
    },
    "ring nebula": {
        "name": "Ring Nebula (M57)",
        "ra_hours": 18.893,
        "dec_deg": 33.029,
        "magnitude": 8.8,
        "optics": "Telescope",
        "type": "Planetary Nebula",
    },
    "whirlpool galaxy": {
        "name": "Whirlpool Galaxy (M51)",
        "ra_hours": 13.498,
        "dec_deg": 47.195,
        "magnitude": 8.4,
        "optics": "Telescope",
        "type": "Spiral Galaxy",
    },
    "crab nebula": {
        "name": "Crab Nebula (M1)",
        "ra_hours": 5.575,
        "dec_deg": 22.014,
        "magnitude": 8.4,
        "optics": "Telescope",
        "type": "Supernova Remnant",
    },
    "sirius": {
        "name": "Sirius (Dog Star)",
        "ra_hours": 6.752,
        "dec_deg": -16.716,
        "magnitude": -1.46,
        "optics": "Naked Eye",
        "type": "Brightest Star",
    },
    "vega": {
        "name": "Vega",
        "ra_hours": 18.615,
        "dec_deg": 38.783,
        "magnitude": 0.03,
        "optics": "Naked Eye",
        "type": "Summer Triangle Star",
    },
    "arcturus": {
        "name": "Arcturus",
        "ra_hours": 14.261,
        "dec_deg": 19.182,
        "magnitude": -0.05,
        "optics": "Naked Eye",
        "type": "Red Giant Star",
    },
    "betelgeuse": {
        "name": "Betelgeuse",
        "ra_hours": 5.919,
        "dec_deg": 7.407,
        "magnitude": 0.5,
        "optics": "Naked Eye",
        "type": "Red Supergiant",
    },
    "rigel": {
        "name": "Rigel",
        "ra_hours": 5.242,
        "dec_deg": -8.201,
        "magnitude": 0.13,
        "optics": "Naked Eye",
        "type": "Blue Supergiant",
    },
    "polaris": {
        "name": "Polaris (North Star)",
        "ra_hours": 2.530,
        "dec_deg": 89.264,
        "magnitude": 1.98,
        "optics": "Naked Eye",
        "type": "North Celestial Pole Star",
    },
}

# JPL Horizons Body ID mapping
HORIZONS_BODY_IDS = {
    "mercury": "199",
    "venus": "299",
    "mars": "499",
    "jupiter": "599",
    "saturn": "699",
    "uranus": "799",
    "neptune": "899",
    "moon": "301",
    "the moon": "301",
    "sun": "10",
}

METEOR_SHOWERS = [
    {
        "name": "Quadrantids",
        "start": "12-28",
        "end": "01-12",
        "peak": "01-03",
        "zhr": 110,
        "radiant": "Boötes",
        "velocity_km_s": 41,
    },
    {
        "name": "Lyrids",
        "start": "04-14",
        "end": "04-30",
        "peak": "04-22",
        "zhr": 18,
        "radiant": "Lyra",
        "velocity_km_s": 49,
    },
    {
        "name": "Eta Aquariids",
        "start": "04-19",
        "end": "05-28",
        "peak": "05-06",
        "zhr": 50,
        "radiant": "Aquarius",
        "velocity_km_s": 66,
    },
    {
        "name": "Perseids",
        "start": "07-17",
        "end": "08-24",
        "peak": "08-12",
        "zhr": 100,
        "radiant": "Perseus",
        "velocity_km_s": 59,
    },
    {
        "name": "Orionids",
        "start": "10-02",
        "end": "11-07",
        "peak": "10-21",
        "zhr": 20,
        "radiant": "Orion",
        "velocity_km_s": 66,
    },
    {
        "name": "Leonids",
        "start": "11-06",
        "end": "11-30",
        "peak": "11-17",
        "zhr": 15,
        "radiant": "Leo",
        "velocity_km_s": 71,
    },
    {
        "name": "Geminids",
        "start": "12-04",
        "end": "12-17",
        "peak": "12-14",
        "zhr": 120,
        "radiant": "Gemini",
        "velocity_km_s": 35,
    },
    {
        "name": "Ursids",
        "start": "12-17",
        "end": "12-26",
        "peak": "12-22",
        "zhr": 10,
        "radiant": "Ursa Minor",
        "velocity_km_s": 33,
    },
]


def get_julian_date(dt: datetime.datetime) -> float:
    """Computes Julian Date from UTC datetime."""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    fraction = (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    return float(jdn) + fraction


def get_constellation_from_coords(ra_hours: float, dec_deg: float) -> str:
    """
    Determines the host IAU constellation from Right Ascension (hours) and Declination (degrees).
    Uses astronomical coordinate bounds covering zodiacal and major constellations.
    """
    ra = ra_hours % 24.0
    dec = dec_deg

    # Northern circumpolar
    if dec >= 70.0:
        if 0.0 <= ra < 8.0:
            return "Cepheus"
        elif 8.0 <= ra < 16.0:
            return "Ursa Minor"
        else:
            return "Draco"

    # High northern sky (35° to 70°)
    if 35.0 <= dec < 70.0:
        if 0.0 <= ra < 3.0:
            return "Cassiopeia"
        elif 3.0 <= ra < 6.0:
            return "Perseus"
        elif 6.0 <= ra < 9.0:
            return "Auriga"
        elif 9.0 <= ra < 15.0:
            return "Ursa Major"
        elif 15.0 <= ra < 19.0:
            return "Hercules"
        elif 19.0 <= ra < 22.0:
            return "Cygnus"
        else:
            return "Andromeda"

    # Mid northern to equatorial sky (0° to 35°)
    if 0.0 <= dec < 35.0:
        if 0.0 <= ra < 2.5:
            return "Pisces"
        elif 2.5 <= ra < 4.0:
            return "Aries"
        elif 4.0 <= ra < 6.0:
            return "Taurus"
        elif 6.0 <= ra < 8.0:
            return "Gemini"
        elif 8.0 <= ra < 9.5:
            return "Cancer"
        elif 9.5 <= ra < 12.0:
            return "Leo"
        elif 12.0 <= ra < 15.0:
            return "Virgo"
        elif 15.0 <= ra < 17.5:
            return "Ophiuchus"
        elif 17.5 <= ra < 20.0:
            return "Lyra"
        elif 20.0 <= ra < 22.0:
            return "Aquila"
        else:
            return "Pegasus"

    # Southern sky (dec < 0°)
    if -35.0 <= dec < 0.0:
        if 0.0 <= ra < 2.0:
            return "Cetus"
        elif 2.0 <= ra < 5.0:
            return "Eridanus"
        elif 5.0 <= ra < 6.5:
            return "Orion"
        elif 6.5 <= ra < 8.0:
            return "Canis Major"
        elif 8.0 <= ra < 11.0:
            return "Hydra"
        elif 11.0 <= ra < 14.5:
            return "Corvus"
        elif 14.5 <= ra < 16.5:
            return "Libra"
        elif 16.5 <= ra < 18.0:
            return "Scorpius"
        elif 18.0 <= ra < 20.5:
            return "Sagittarius"
        elif 20.5 <= ra < 22.5:
            return "Capricornus"
        else:
            return "Aquarius"

    # Far southern sky (dec < -35°)
    if 0.0 <= ra < 6.0:
        return "Phoenix"
    elif 6.0 <= ra < 12.0:
        return "Carina"
    elif 12.0 <= ra < 15.0:
        return "Centaurus"
    else:
        return "Pavo"


async def fetch_jpl_horizons_ephemeris(
    target_name: str, dt: datetime.datetime
) -> tuple[float, float, float] | None:
    """
    Fetches real-time astrometric ICRF Right Ascension, Declination, and apparent magnitude
    from NASA JPL's official public Horizons API.
    Returns: (ra_hours, dec_deg, apparent_magnitude) or None if request fails.
    """
    norm = target_name.strip().lower()
    body_id = HORIZONS_BODY_IDS.get(norm)
    if not body_id:
        return None

    dt_utc = dt if dt.tzinfo is not None else dt.replace(tzinfo=datetime.UTC)
    start_str = dt_utc.strftime("%Y-%m-%d %H:%M")
    next_day = dt_utc + datetime.timedelta(days=1)
    stop_str = next_day.strftime("%Y-%m-%d %H:%M")

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "CENTER": "'500@399'",  # Geocentric Earth
        "START_TIME": f"'{start_str}'",
        "STOP_TIME": f"'{stop_str}'",
        "STEP_SIZE": "'1d'",
        "QUANTITIES": "'1,9'",  # 1: Astrometric RA/DEC, 9: Visual Magnitude
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                result_text = data.get("result", "")

                # Match table data between $$SOE and $$EOE
                # Example line: 2026-Sep-13 00:00 07 29 15.12 +22 34 46.5 1.196
                regex = re.compile(
                    r"\$\$SOE\s*\n\s*\S+\s+\S+\s+(\d+)\s+(\d+)\s+([\d\.]+)\s+([+-]?\d+)\s+(\d+)\s+([\d\.]+)\s+([+-]?[\d\.]+)"
                )
                m = regex.search(result_text)
                if m:
                    ra_h = float(m.group(1))
                    ra_m = float(m.group(2))
                    ra_s = float(m.group(3))
                    ra_hours = ra_h + (ra_m / 60.0) + (ra_s / 3600.0)

                    dec_sign = -1.0 if "-" in m.group(4) else 1.0
                    dec_d = abs(float(m.group(4)))
                    dec_m = float(m.group(5))
                    dec_s = float(m.group(6))
                    dec_deg = dec_sign * (dec_d + (dec_m / 60.0) + (dec_s / 3600.0))

                    mag = float(m.group(7))
                    return round(ra_hours, 4), round(dec_deg, 4), round(mag, 2)
    except Exception as e:
        logger.warning(f"NASA JPL Horizons API lookup failed for {target_name}: {e}")

    return None


async def fetch_cds_sesame_coordinates(target_name: str) -> dict[str, Any] | None:
    """
    Queries the CDS Sesame Astronomical Name Resolver (Strasbourg astronomical Data Center)
    to dynamically resolve real RA and Dec coordinates for any star, galaxy, or deep-sky object.
    """
    clean_target = urllib.parse.quote(target_name.strip())
    url = f"https://cds.unistra.fr/cgi-bin/nph-sesame/-ox/SNV?{clean_target}"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                xml_text = resp.text
                ra_match = re.search(r"<jradeg>([\d\.\-]+)</jradeg>", xml_text)
                dec_match = re.search(r"<jdedeg>([\d\.\-]+)</jdedeg>", xml_text)
                type_match = re.search(r"<otype>([^<]+)</otype>", xml_text)
                mag_match = re.search(r"<v>([+-]?[\d\.]+)</v>", xml_text)

                if ra_match and dec_match:
                    ra_deg = float(ra_match.group(1))
                    dec_deg = float(dec_match.group(1))
                    ra_hours = (ra_deg / 15.0) % 24.0
                    mag = float(mag_match.group(1)) if mag_match else 5.0
                    obj_type = type_match.group(1) if type_match else "Deep Sky Object"

                    optics = "Naked Eye" if mag < 5.0 else ("Binoculars" if mag < 8.5 else "Telescope")
                    return {
                        "name": target_name.title(),
                        "ra_hours": round(ra_hours, 4),
                        "dec_deg": round(dec_deg, 4),
                        "magnitude": mag,
                        "optics": optics,
                        "type": obj_type,
                    }
    except Exception as e:
        logger.warning(f"CDS Sesame lookup failed for {target_name}: {e}")

    return None


async def fetch_iss_telemetry() -> dict[str, Any] | None:
    """
    Fetches real-time orbital coordinates, altitude, velocity, and visibility of the
    International Space Station from WhereTheISS.at.
    """
    url = "https://api.wheretheiss.at/v1/satellites/25544"
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "target_name": "International Space Station (ISS)",
                    "latitude": float(data.get("latitude")),
                    "longitude": float(data.get("longitude")),
                    "altitude_km": round(float(data.get("altitude")), 1),
                    "velocity_km_h": round(float(data.get("velocity")), 1),
                    "visibility": data.get("visibility", "unknown"),
                    "timestamp": data.get("timestamp"),
                }
    except Exception as e:
        logger.warning(f"WhereTheISS.at lookup failed: {e}")

    return None


def get_moon_ephemeris(
    dt: datetime.datetime | None = None,
    moon_phase_fraction: float | None = None,
    moonrise_str: str | None = None,
    moonset_str: str | None = None,
) -> dict[str, Any]:
    """
    Computes precise Moon phase name, illumination percentage, and viewing impact.
    Uses live moon_phase_fraction from Open-Meteo when available.
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.UTC)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)

    if moon_phase_fraction is not None:
        phase_ratio = moon_phase_fraction
    else:
        # Astronomical synodic computation fallback
        jd = get_julian_date(dt)
        known_new_moon = 2451549.26
        synodic_period = 29.53058867
        days_since_new = (jd - known_new_moon) % synodic_period
        phase_ratio = days_since_new / synodic_period

    days_since_new = phase_ratio * 29.53058867

    # Illumination formula
    illumination_pct = round((1.0 - math.cos(2.0 * math.pi * phase_ratio)) / 2.0 * 100)

    if phase_ratio < 0.03 or phase_ratio >= 0.97:
        phase_name = "New Moon"
        interference = "None (Pristine Dark Skies)"
    elif phase_ratio < 0.22:
        phase_name = "Waxing Crescent"
        interference = "Low (Early evening set)"
    elif phase_ratio < 0.28:
        phase_name = "First Quarter"
        interference = "Moderate (Sets near midnight)"
    elif phase_ratio < 0.47:
        phase_name = "Waxing Gibbous"
        interference = "High (Bright until pre-dawn)"
    elif phase_ratio < 0.53:
        phase_name = "Full Moon"
        interference = "Severe (All-night bright glare)"
    elif phase_ratio < 0.72:
        phase_name = "Waning Gibbous"
        interference = "High (Rises mid-evening)"
    elif phase_ratio < 0.78:
        phase_name = "Last Quarter"
        interference = "Moderate (Rises around midnight)"
    else:
        phase_name = "Waning Crescent"
        interference = "Low (Rises in pre-dawn sky)"

    # Dark sky window
    if moonset_str:
        dark_sky = f"After moonset ({moonset_str})" if illumination_pct > 30 else "All night (Minimal moonlight)"
    else:
        dark_sky = "Optimal dark sky conditions" if illumination_pct < 25 else "Darkest sky before moonrise / after moonset"

    return {
        "phase_name": phase_name,
        "phase_ratio": round(phase_ratio, 3),
        "illumination_percent": illumination_pct,
        "moon_age_days": round(days_since_new, 1),
        "moonrise_time": moonrise_str or "Consult local transit",
        "moonset_time": moonset_str or "Consult local transit",
        "interference_level": interference,
        "dark_sky_window": dark_sky,
    }


def compute_horizontal_coords(
    ra_hours: float, dec_deg: float, lat_deg: float, lon_deg: float, dt: datetime.datetime
) -> tuple[float, float, str]:
    """
    Transforms Right Ascension & Declination to local Altitude angle and Azimuth bearing.
    Returns: (altitude_degrees, azimuth_degrees, cardinal_direction)
    """
    jd = get_julian_date(dt)
    d = jd - 2451545.0  # Days since J2000.0

    # Greenwich Mean Sidereal Time in degrees
    gmst_deg = (280.46061837 + 360.98564736629 * d) % 360.0
    # Local Sidereal Time
    lst_deg = (gmst_deg + lon_deg) % 360.0
    lst_hours = lst_deg / 15.0

    # Hour Angle
    ha_hours = (lst_hours - ra_hours) % 24.0
    ha_rad = math.radians(ha_hours * 15.0)

    dec_rad = math.radians(dec_deg)
    lat_rad = math.radians(lat_deg)

    # Altitude
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    alt_rad = math.asin(max(-1.0, min(1.0, sin_alt)))
    alt_deg = math.degrees(alt_rad)

    # Azimuth
    cos_az = (math.sin(dec_rad) - math.sin(lat_rad) * sin_alt) / (math.cos(lat_rad) * math.cos(alt_rad) + 1e-9)
    cos_az = max(-1.0, min(1.0, cos_az))
    az_rad = math.acos(cos_az)
    az_deg = math.degrees(az_rad)
    if math.sin(ha_rad) > 0:
        az_deg = 360.0 - az_deg

    cardinal = degrees_to_cardinal(az_deg)
    return round(alt_deg, 1), round(az_deg, 1), cardinal


def degrees_to_cardinal(deg: float) -> str:
    """Converts azimuth degrees (0-360) into 16-point cardinal compass text."""
    directions = [
        "North", "North-Northeast", "Northeast", "East-Northeast",
        "East", "East-Southeast", "Southeast", "South-Southeast",
        "South", "South-Southwest", "Southwest", "West-Southwest",
        "West", "West-Northwest", "Northwest", "North-Northwest"
    ]
    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]


async def get_planet_coordinates(
    planet_name: str, dt: datetime.datetime
) -> tuple[float, float, float, str]:
    """
    Computes Right Ascension (hours), Declination (degrees), visual magnitude,
    and dynamically determined host constellation for major planets.
    Prioritizes the NASA JPL Horizons API.
    """
    name = planet_name.strip().lower()

    # 1. Try NASA JPL Horizons Live API
    jpl_res = await fetch_jpl_horizons_ephemeris(name, dt)
    if jpl_res is not None:
        ra, dec, mag = jpl_res
        constellation = get_constellation_from_coords(ra, dec)
        return ra, dec, mag, constellation

    # 2. High-precision analytical orbital fallback (if NASA API is unreachable)
    jd = get_julian_date(dt)
    t = (jd - 2451545.0) / 36525.0

    planet_params = {
        "mercury": {"l0": 252.25, "rate": 149472.67, "dec_offset": 5.0, "mag": -0.2},
        "venus": {"l0": 181.98, "rate": 58517.81, "dec_offset": 12.0, "mag": -4.2},
        "mars": {"l0": 355.43, "rate": 19140.30, "dec_offset": 22.0, "mag": -0.6},
        "jupiter": {"l0": 34.35, "rate": 3034.90, "dec_offset": 18.5, "mag": -2.4},
        "saturn": {"l0": 50.08, "rate": 1222.11, "dec_offset": -4.0, "mag": 0.6},
        "uranus": {"l0": 314.06, "rate": 428.47, "dec_offset": 16.0, "mag": 5.7},
        "neptune": {"l0": 304.35, "rate": 218.46, "dec_offset": -2.0, "mag": 7.8},
    }

    if name in planet_params:
        p = planet_params[name]
        mean_long = (p["l0"] + p["rate"] * t) % 360.0
        ra_hours = (mean_long / 15.0) % 24.0
        dec_deg = math.sin(math.radians(mean_long)) * 23.44 + p["dec_offset"]
        dec_deg = max(-28.0, min(28.0, dec_deg))
        constellation = get_constellation_from_coords(ra_hours, dec_deg)
        return round(ra_hours, 2), round(dec_deg, 2), p["mag"], constellation

    return 6.5, 23.0, -0.5, "Gemini"


async def get_target_ephemeris(
    target_name: str, lat: float, lon: float, dt: datetime.datetime | None = None
) -> dict[str, Any]:
    """
    Computes horizontal coordinates and viewing data for any requested celestial body
    (planets, Moon, deep sky targets, or arbitrary celestial objects via CDS Sesame).
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.UTC)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.UTC)

    normalized = target_name.strip().lower()

    # 1. Major Solar System Planets
    if normalized in ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]:
        ra, dec, mag, const = await get_planet_coordinates(normalized, dt)
        display_name = normalized.title()
        optics = "Naked Eye" if normalized in ["venus", "mars", "jupiter", "saturn"] else "Binoculars or Telescope"

    # 2. Moon
    elif normalized in ["moon", "the moon"]:
        jpl_res = await fetch_jpl_horizons_ephemeris("moon", dt)
        if jpl_res:
            ra, dec, mag = jpl_res
            const = get_constellation_from_coords(ra, dec)
        else:
            jd = get_julian_date(dt)
            t = (jd - 2451545.0) / 36525.0
            mean_long = (218.316 + 481267.881 * t) % 360.0
            ra = (mean_long / 15.0) % 24.0
            dec = math.sin(math.radians(mean_long)) * 23.44 + 5.14 * math.sin(math.radians(mean_long * 13.0))
            mag = -12.0
            const = get_constellation_from_coords(ra, dec)

        moon_data = get_moon_ephemeris(dt)
        display_name = f"Moon ({moon_data['phase_name']})"
        optics = "Naked Eye & Binoculars"

    # 3. Known Prominent Deep-Sky Objects in Local Catalog
    elif normalized in DEEP_SKY_CATALOG:
        obj = DEEP_SKY_CATALOG[normalized]
        ra = obj["ra_hours"]
        dec = obj["dec_deg"]
        mag = obj["magnitude"]
        const = get_constellation_from_coords(ra, dec)
        optics = obj["optics"]
        display_name = obj["name"]

    # 4. Partial substring match in Catalog
    else:
        matched = False
        for k, v in DEEP_SKY_CATALOG.items():
            if normalized in k or k in normalized:
                ra = v["ra_hours"]
                dec = v["dec_deg"]
                mag = v["magnitude"]
                const = get_constellation_from_coords(ra, dec)
                optics = v["optics"]
                display_name = v["name"]
                matched = True
                break

        # 5. Live CDS Sesame Resolution for any arbitrary star/nebula/galaxy
        if not matched:
            sesame_data = await fetch_cds_sesame_coordinates(target_name)
            if sesame_data:
                ra = sesame_data["ra_hours"]
                dec = sesame_data["dec_deg"]
                mag = sesame_data["magnitude"]
                const = get_constellation_from_coords(ra, dec)
                optics = sesame_data["optics"]
                display_name = f"{sesame_data['name']} ({sesame_data['type']})"
            else:
                return {
                    "target_name": target_name.title(),
                    "is_visible_now": False,
                    "error": f"Celestial body '{target_name}' could not be located in astronomical databases.",
                }

    alt, az, cardinal = compute_horizontal_coords(ra, dec, lat, lon, dt)
    is_visible = alt > 0.0

    return {
        "target_name": display_name,
        "is_visible_now": is_visible,
        "visibility_status": "Visible Above Horizon" if is_visible else "Currently Below Horizon",
        "altitude_degrees": alt,
        "azimuth_degrees": az,
        "cardinal_direction": cardinal,
        "constellation": const,
        "apparent_magnitude": mag,
        "optical_aid_required": optics,
        "best_viewing_window": "Highest in dark sky" if is_visible else "Awaits next rising",
    }


def compute_stargazing_index(
    cloud_cover: int, moon_illumination: int, seeing_quality: str
) -> tuple[int, str]:
    """
    Computes an intuitive Stargazing Index score (0 to 100) and qualitative label.
    Weights: Cloud cover (50%), Moon darkness (30%), Seeing & Transparency (20%).
    """
    cloud_pts = max(0, int(50.0 - (cloud_cover * 0.5)))
    moon_pts = int(30.0 - (moon_illumination * 0.26))

    if "Excellent" in seeing_quality:
        seeing_pts = 20
    elif "Good" in seeing_quality:
        seeing_pts = 15
    elif "Fair" in seeing_quality:
        seeing_pts = 8
    else:
        seeing_pts = 2

    score = max(5, min(100, cloud_pts + moon_pts + seeing_pts))

    if score >= 80:
        label = "Excellent Observing Conditions"
    elif score >= 60:
        label = "Good Observing Conditions"
    elif score >= 40:
        label = "Fair Conditions (Partial Obscuration)"
    else:
        label = "Poor Observing Conditions"

    return score, label


def get_active_meteor_showers(dt: datetime.datetime | None = None) -> list[dict[str, Any]]:
    """Identifies active or peak meteor showers strictly for the given date (no fake fallbacks)."""
    if dt is None:
        dt = datetime.datetime.now(datetime.UTC)
    md = f"{dt.month:02d}-{dt.day:02d}"

    active = []
    for shower in METEOR_SHOWERS:
        start = shower["start"]
        end = shower["end"]
        is_active = False
        if start <= end:
            is_active = start <= md <= end
        else:  # Crosses year-end boundary (e.g. Dec to Jan)
            is_active = md >= start or md <= end

        if is_active:
            shower_copy = shower.copy()
            shower_copy["is_peak_tonight"] = (md == shower["peak"])
            active.append(shower_copy)

    return active
