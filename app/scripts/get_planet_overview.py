import logging
import re
from typing import Any

import app.core.hubscape_adk

logger = logging.getLogger(__name__)

PLANETARY_DATABASE: dict[str, dict[str, Any]] = {
    "mars": {
        "name": "Mars",
        "emoji": "🔴",
        "tagline": "The Red Planet",
        "category": "Terrestrial Planet",
        "distance_from_sun": "227.9M km (1.52 AU)",
        "diameter": "6,779 km",
        "day_length": "24h 37m",
        "orbital_period": "687 Earth Days",
        "moons_count": "2 (Phobos & Deimos)",
        "avg_temperature": "-63°C (-81°F)",
        "atmosphere": "95% Carbon Dioxide, 2.6% Nitrogen, 1.9% Argon",
        "key_feature": "Home to Olympus Mons, the tallest volcano in the Solar System, and Valles Marineris canyon.",
        "observing_tip": "Visible to the naked eye with an unmistakable rusty amber glow. A small telescope reveals polar ice caps.",
        "scale_percentage": 53,
    },
    "jupiter": {
        "name": "Jupiter",
        "emoji": "🪐",
        "tagline": "The Giant Planet",
        "category": "Gas Giant",
        "distance_from_sun": "778.5M km (5.20 AU)",
        "diameter": "139,820 km",
        "day_length": "9h 56m",
        "orbital_period": "11.86 Earth Years",
        "moons_count": "95 (Io, Europa, Ganymede, Callisto)",
        "avg_temperature": "-110°C (-166°F)",
        "atmosphere": "90% Hydrogen, 10% Helium with trace methane and ammonia",
        "key_feature": "The Great Red Spot, an enormous storm larger than Earth raging for over 300 years.",
        "observing_tip": "Brilliant in the night sky. Ordinary binoculars easily show the four bright Galilean moons.",
        "scale_percentage": 100,
    },
    "saturn": {
        "name": "Saturn",
        "emoji": "🪐",
        "tagline": "The Ringed Jewel",
        "category": "Gas Giant",
        "distance_from_sun": "1.43B km (9.58 AU)",
        "diameter": "116,460 km",
        "day_length": "10h 33m",
        "orbital_period": "29.4 Earth Years",
        "moons_count": "146 (Titan, Enceladus, Mimas)",
        "avg_temperature": "-140°C (-220°F)",
        "atmosphere": "96% Hydrogen, 3% Helium with methane and ice crystals",
        "key_feature": "Spectacular ring system spanning 282,000 km, composed predominantly of billions of water-ice chunks.",
        "observing_tip": "Golden steady glow to the naked eye. Any small telescope (25x+) clearly resolves its iconic rings and moon Titan.",
        "scale_percentage": 83,
    },
    "venus": {
        "name": "Venus",
        "emoji": "✨",
        "tagline": "The Morning & Evening Star",
        "category": "Terrestrial Planet",
        "distance_from_sun": "108.2M km (0.72 AU)",
        "diameter": "12,104 km",
        "day_length": "243 Earth Days (Retrograde)",
        "orbital_period": "225 Earth Days",
        "moons_count": "0",
        "avg_temperature": "465°C (869°F)",
        "atmosphere": "96.5% Carbon Dioxide with thick clouds of sulfuric acid",
        "key_feature": "Hottest planet in the Solar System due to runaway greenhouse effect, spins backward relative to most planets.",
        "observing_tip": "The third brightest natural object in the sky after the Sun and Moon. Exhibits phases like the Moon in telescopes.",
        "scale_percentage": 95,
    },
    "mercury": {
        "name": "Mercury",
        "emoji": "🪨",
        "tagline": "The Swift Planet",
        "category": "Terrestrial Planet",
        "distance_from_sun": "57.9M km (0.39 AU)",
        "diameter": "4,879 km",
        "day_length": "59 Earth Days",
        "orbital_period": "88 Earth Days",
        "moons_count": "0",
        "avg_temperature": "-180°C to 430°C",
        "atmosphere": "Exosphere containing oxygen, sodium, hydrogen, helium, potassium",
        "key_feature": "Heavily cratered surface resembling our Moon, shortest orbital year of any planet.",
        "observing_tip": "Always near the Sun; best spotted low on the horizon during civil or nautical twilight just before dawn or after dusk.",
        "scale_percentage": 38,
    },
    "uranus": {
        "name": "Uranus",
        "emoji": "🌀",
        "tagline": "The Sideways Ice Giant",
        "category": "Ice Giant",
        "distance_from_sun": "2.87B km (19.2 AU)",
        "diameter": "50,724 km",
        "day_length": "17h 14m",
        "orbital_period": "84 Earth Years",
        "moons_count": "28 (Titania, Oberon, Miranda)",
        "avg_temperature": "-195°C (-319°F)",
        "atmosphere": "82.5% Hydrogen, 15.2% Helium, 2.3% Methane",
        "key_feature": "Extreme axial tilt of 98°, effectively rotating on its side as it orbits the Sun.",
        "observing_tip": "Faint pale cyan disk in moderate amateur telescopes under dark, clear skies.",
        "scale_percentage": 40,
    },
    "neptune": {
        "name": "Neptune",
        "emoji": "🌊",
        "tagline": "The Distant Blue Giant",
        "category": "Ice Giant",
        "distance_from_sun": "4.50B km (30.1 AU)",
        "diameter": "49,244 km",
        "day_length": "16h 6m",
        "orbital_period": "165 Earth Years",
        "moons_count": "16 (Triton, Proteus)",
        "avg_temperature": "-200°C (-328°F)",
        "atmosphere": "Hydrogen, Helium, and Methane yielding a deep azure coloration",
        "key_feature": "Strongest supersonic winds in the solar system, reaching over 2,100 km/h (1,300 mph).",
        "observing_tip": "Appears as a faint 8th-magnitude deep blue dot requiring binoculars or a telescope to distinguish from background stars.",
        "scale_percentage": 39,
    },
    "moon": {
        "name": "The Moon",
        "emoji": "🌕",
        "tagline": "Earth's Natural Satellite",
        "category": "Natural Satellite",
        "distance_from_sun": "149.6M km (from Sun) / 384,400 km (from Earth)",
        "diameter": "3,474 km",
        "day_length": "27.3 Earth Days (Tidally Locked)",
        "orbital_period": "27.3 Earth Days",
        "moons_count": "N/A",
        "avg_temperature": "-130°C to 120°C",
        "atmosphere": "Extremely tenuous exosphere (helium, neon, hydrogen)",
        "key_feature": "Covered in impact craters, ancient basaltic lava plains (maria), and towering highland mountains.",
        "observing_tip": "Best viewed along the terminator (day/night shadow line) where shadows dramatically accentuate crater depth.",
        "scale_percentage": 27,
    },
}


def normalize_planet_key(name: str | None) -> str:
    if not name:
        return "mars"
    cleaned = re.sub(r"(?i)(the|planet|celestial|body|tell|me|about|info|show)", "", name).strip().lower()
    for key in PLANETARY_DATABASE:
        if key in cleaned:
            return key
    return "mars"


@app.core.hubscape_adk.require_tool_privilege
async def get_planet_overview(
    planet_name: str | None = "Mars",
) -> dict[str, Any]:
    """Provides a self-contained, interactive educational spotlight and observational
    overview for any solar system planet or major body (e.g. Mars, Jupiter, Saturn, Venus,
    Mercury, Uranus, Neptune, Moon).

    Does NOT require user location or external weather API calls. Renders an interactive
    Lego widget spotlight card containing key stats, scale progress, expandable details,
    an observation preference picker, and follow-up celestial actions.

    Args:
        planet_name: Name of the planet or body (e.g. 'Mars', 'Jupiter', 'Saturn', 'Venus', 'Moon').

    Returns:
        A dictionary of authentic planetary data and observation insights.
    """
    key = normalize_planet_key(planet_name)
    info = PLANETARY_DATABASE.get(key, PLANETARY_DATABASE["mars"])

    widget_data = {
        "planet_name": info["name"],
        "planet_emoji": info["emoji"],
        "tagline": info["tagline"],
        "category": info["category"],
        "distance_from_sun": info["distance_from_sun"],
        "diameter": info["diameter"],
        "day_length": info["day_length"],
        "orbital_period": info["orbital_period"],
        "moons_count": info["moons_count"],
        "avg_temperature": info["avg_temperature"],
        "atmosphere": info["atmosphere"],
        "key_feature": info["key_feature"],
        "observing_tip": info["observing_tip"],
        "scale_percentage": str(info["scale_percentage"]),
    }

    # Add data. prefixes for dynamic widget interpolation
    for k, v in list(widget_data.items()):
        widget_data[f"data.{k}"] = v

    # Render Generative UI Widget
    try:
        ctx = app.core.hubscape_adk.get_context()
        if ctx is not None:
            ctx.show_widget("planet_spotlight_card", widget_data)
    except Exception as e:
        logger.debug(f"Could not render planet_spotlight_card widget: {e}")

    return {
        "status": "success",
        "planet_name": info["name"],
        "tagline": info["tagline"],
        "category": info["category"],
        "distance_from_sun": info["distance_from_sun"],
        "diameter": info["diameter"],
        "day_length": info["day_length"],
        "orbital_period": info["orbital_period"],
        "moons_count": info["moons_count"],
        "avg_temperature": info["avg_temperature"],
        "atmosphere": info["atmosphere"],
        "key_feature": info["key_feature"],
        "observing_tip": info["observing_tip"],
        "scale_percentage": info["scale_percentage"],
        "offline_ready": True,
    }
