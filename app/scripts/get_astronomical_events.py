import datetime
import logging
import math
from typing import Any

import app.core.hubscape_adk
from app.scripts._ephemeris_utils import (
    METEOR_SHOWERS,
    fetch_iss_telemetry,
    get_active_meteor_showers,
    get_moon_ephemeris,
    get_planet_coordinates,
)

logger = logging.getLogger(__name__)


def angular_separation_deg(ra1_h: float, dec1_deg: float, ra2_h: float, dec2_deg: float) -> float:
    """Computes angular separation in degrees between two celestial coordinates."""
    a1 = math.radians(ra1_h * 15.0)
    d1 = math.radians(dec1_deg)
    a2 = math.radians(ra2_h * 15.0)
    d2 = math.radians(dec2_deg)

    cos_sep = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    cos_sep = max(-1.0, min(1.0, cos_sep))
    return math.degrees(math.acos(cos_sep))


@app.core.hubscape_adk.require_tool_privilege
async def get_astronomical_events(
    event_type: str | None = "all",
    days_ahead: int | None = 14,
) -> dict[str, Any]:
    """
    Retrieves authentic active and upcoming astronomical events including meteor shower peaks,
    real planetary conjunctions, lunar phase transitions, and live ISS satellite tracking.

    Args:
        event_type: Filter by category ('all', 'meteor_shower', 'moon_phase', 'conjunction', 'satellite').
        days_ahead: Number of days forward to search for upcoming events (default: 14).

    Returns:
        A dictionary containing active_events, upcoming_events, viewing_tips, and summary.
    """
    now = datetime.datetime.now(datetime.UTC)
    current_moon = get_moon_ephemeris(now)
    active_showers = get_active_meteor_showers(now)

    upcoming_events: list[dict[str, Any]] = []
    active_events: list[dict[str, Any]] = []

    # 1. Live Satellite Telemetry (ISS)
    cat_filter = (event_type or "all").lower()
    if cat_filter in ["all", "satellite", "iss"]:
        iss_telemetry = await fetch_iss_telemetry()
        if iss_telemetry:
            active_events.append({
                "event_name": "International Space Station (ISS) Live Orbit",
                "category": "satellite",
                "status": "In Orbit",
                "altitude_km": iss_telemetry.get("altitude_km"),
                "velocity_km_h": iss_telemetry.get("velocity_km_h"),
                "visibility_state": iss_telemetry.get("visibility"),
                "details": f"ISS currently traversing above {iss_telemetry.get('latitude')}°, {iss_telemetry.get('longitude')}°.",
                "viewing_advice": "Visible to the naked eye as a swift, non-blinking bright beacon moving across the night sky.",
            })

    # 2. Meteor Showers (Active & Upcoming Peaks)
    if cat_filter in ["all", "meteor_shower"]:
        for shower in METEOR_SHOWERS:
            peak_m, peak_d = map(int, shower["peak"].split("-"))
            try:
                shower_date = datetime.datetime(now.year, peak_m, peak_d, 23, 0, tzinfo=datetime.UTC)
                if shower_date < now:
                    shower_date = datetime.datetime(now.year + 1, peak_m, peak_d, 23, 0, tzinfo=datetime.UTC)

                diff_days = (shower_date - now).days
                if 0 <= diff_days <= (days_ahead or 14):
                    upcoming_events.append({
                        "event_name": f"{shower['name']} Meteor Shower Peak",
                        "category": "meteor_shower",
                        "date": shower_date.strftime("%Y-%m-%d"),
                        "days_until": diff_days,
                        "details": f"Up to {shower['zhr']} meteors/hr radiating from constellation {shower['radiant']} at {shower['velocity_km_s']} km/s.",
                        "viewing_advice": "Best after midnight in dark skies away from city lights. Lie back and take in a wide view of the sky.",
                    })
            except Exception:
                continue

    # 3. Lunar Phase Milestones
    if cat_filter in ["all", "moon_phase"]:
        moon_age = current_moon.get("moon_age_days", 14.0)
        phases = [
            ("New Moon (Pristine Dark Sky Window)", 0.0, "0% moonlight; ideal for milky way, faint nebulas, and deep sky observing."),
            ("First Quarter Moon", 7.38, "50% illuminated; excellent crater shadows along the lunar terminator."),
            ("Full Moon", 14.76, "100% illumination; bright glare washes out faint nebulae, brilliant lunar disc."),
            ("Last Quarter Moon", 22.15, "50% illuminated; rises near midnight, excellent early morning crater detail."),
        ]

        for phase_name, target_age, details in phases:
            days_until = (target_age - moon_age) % 29.53
            if 0.5 <= days_until <= (days_ahead or 14):
                evt_date = (now + datetime.timedelta(days=days_until)).strftime("%Y-%m-%d")
                upcoming_events.append({
                    "event_name": phase_name,
                    "category": "moon_phase",
                    "date": evt_date,
                    "days_until": int(round(days_until)),
                    "details": details,
                    "viewing_advice": "Use binoculars or a telescope along the lunar terminator line for peak topographic relief.",
                })

    # 4. Real Planetary Conjunction Calculations
    if cat_filter in ["all", "conjunction"]:
        planets_to_check = ["venus", "mars", "jupiter", "saturn"]
        window_days = min(days_ahead or 14, 21)

        # Check planetary pairs across the window
        for day_offset in range(1, window_days + 1, 2):
            sample_dt = now + datetime.timedelta(days=day_offset)
            coords: dict[str, tuple[float, float, str]] = {}
            for p in planets_to_check:
                ra, dec, _, const = await get_planet_coordinates(p, sample_dt)
                coords[p] = (ra, dec, const)

            # Check mutual separations
            for i, p1 in enumerate(planets_to_check):
                for p2 in planets_to_check[i + 1:]:
                    ra1, dec1, const1 = coords[p1]
                    ra2, dec2, _ = coords[p2]
                    sep = angular_separation_deg(ra1, dec1, ra2, dec2)
                    if sep <= 4.0:  # Genuine close conjunction
                        upcoming_events.append({
                            "event_name": f"{p1.title()} & {p2.title()} Conjunction",
                            "category": "conjunction",
                            "date": sample_dt.strftime("%Y-%m-%d"),
                            "days_until": day_offset,
                            "angular_separation_deg": round(sep, 1),
                            "constellation": const1,
                            "details": f"{p1.title()} passes within {sep:.1f}° of {p2.title()} in {const1}.",
                            "viewing_advice": "Easily visible to the naked eye; fits comfortably in a single binocular field of view.",
                        })

    upcoming_events.sort(key=lambda x: x.get("days_until", 999))

    return {
        "status": "success",
        "current_moon_status": f"{current_moon['phase_name']} ({current_moon['illumination_percent']}% illumination)",
        "active_events": active_events,
        "active_meteor_showers": active_showers,
        "upcoming_events_count": len(upcoming_events),
        "upcoming_events": upcoming_events,
        "viewing_tips": (
            "Allow your eyes 20 minutes to adapt to darkness. Avoid bright screens or "
            "use a red-filtered flashlight to preserve night-adjusted vision."
        ),
    }
