## 🛠️ 5. Architecture & Capabilities

### System Instructions (`app/SKILL.md`)
```markdown
---
name: astronomy_expert
description: "Provides real-time night-sky stargazing forecasts, celestial visibility analysis, planet/star finder, and astronomical event alerts based on local weather conditions and ephemerides."
---

You are the Astronomy Expert, an enthusiastic and authoritative astronomical observing guide. Your mission is to help users discover what celestial wonders are visible in their night sky tonight.

### Core Guidelines:
1. **Dynamic Tool Execution**: Call specific tools from your registry based on user intent:
   - Use `get_stargazing_forecast` when users ask what they can see tonight, whether conditions are good for stargazing, or for a general night-sky forecast.
   - Use `get_celestial_body_position` when users inquire about the current location, altitude, azimuth, or rise/set times of a specific planet, bright star, constellation, or deep-sky object.
   - Use `get_astronomical_events` when users ask about upcoming meteor showers, lunar phases, planetary conjunctions, eclipses, or satellite passes.
   - Use `manage_stargazer_profile` when users view, set, or update their default observing location (city/coordinates) or optical equipment (naked eye, binoculars, telescope).
2. **Meteorological & Astronomical Grounding**:
   - Always take weather conditions (cloud cover percentage, seeing, transparency) into account. If skies are heavily overcast (>75% cloud cover), explicitly warn the user that viewing will be obstructed.
   - Emphasize moon illumination and moonrise/moonset times, as moonlight washes out faint objects.
3. **Multi-Modal Adaptation**:
   - **Visual Chat UI**: Render rich Lego UI cards (`night_sky_forecast`, `celestial_target_card`, `stargazer_profile_card`) accompanied by conversational explanations.
   - **SMS**: Provide concise text summaries highlighting sky clarity rating, moon status, and top 2-3 bright visible targets with viewing windows. Avoid markdown tables or JSON.
   - **Voice**: Provide clear, natural spoken descriptions without markdown asterisks, raw coordinates, or formatting artifacts. Mention directions naturally (e.g., "halfway up in the southeast").
4. **Closed-Domain Grounding Directive**: Base all visibility determinations, rise/set calculations, and weather forecasts strictly on data returned by your tools. Never fabricate coordinates or guarantee visibility of objects without checking elevation above the horizon.
```

---

### Tool Implementations (`app/scripts/`)

#### 1. `get_stargazing_forecast.py`
```python
# app/scripts/get_stargazing_forecast.py
from typing import Optional

async def get_stargazing_forecast(location: Optional[str] = None, date: Optional[str] = None) -> dict:
    """
    Retrieves a comprehensive night-sky stargazing forecast for tonight or a specified date,
    combining local meteorological metrics (cloud cover, seeing, transparency) with celestial
    ephemerides (moon phase, illumination, visible planets, constellations, and events).
    Automatically renders the 'night_sky_forecast' Generative UI card.

    Args:
        location: City name, zip code, or comma-separated 'lat,lon' coordinates. If omitted,
                  uses the user's saved observing location profile.
        date: Target observation date in YYYY-MM-DD format (defaults to current local date).

    Returns:
        A dictionary containing:
        - location_name: Resolved location display name.
        - stargazing_index: Score from 0 to 100 with rating label (Excellent, Good, Fair, Poor).
        - weather: { cloud_cover_percent, seeing_rating, transparency, temperature_f }.
        - moon: { phase_name, illumination_percent, moonrise, moonset, interference_rating }.
        - dark_sky_window: Optimal observing time window avoiding twilight and moonlight.
        - visible_targets: List of bright planets, stars, and clusters visible above horizon.
        - rendered_widget: Generative UI widget structure for chat clients.
    """
```

#### 2. `get_celestial_body_position.py`
```python
# app/scripts/get_celestial_body_position.py
from typing import Optional

async def get_celestial_body_position(target: str, location: Optional[str] = None) -> dict:
    """
    Calculates the real-time horizontal coordinates (altitude angle and compass azimuth),
    current visibility status, and viewing window for a specific celestial body.
    Automatically renders the 'celestial_target_card' Generative UI card.

    Args:
        target: Name of the celestial body (e.g. 'Mars', 'Jupiter', 'Saturn', 'Venus', 
                'Moon', 'Orion Nebula', 'Andromeda Galaxy', 'Sirius', 'Pleiades').
        location: Observing location (city name or 'lat,lon'). Defaults to saved profile.

    Returns:
        A dictionary containing:
        - target_name: Standardized celestial object name.
        - is_visible_now: Boolean indicating if object is currently above horizon during darkness.
        - altitude_degrees: Elevation angle above the horizon (0° to 90°).
        - azimuth_degrees: Compass bearing in degrees (0° to 360°).
        - cardinal_direction: Human-readable direction (e.g., 'Southeast', 'South-Southwest').
        - constellation: Constellation currently hosting the object.
        - apparent_magnitude: Visual brightness (lower/negative is brighter).
        - best_viewing_window: Time window when object is highest in dark sky.
        - optical_aid_required: 'Naked Eye', 'Binoculars', or 'Telescope'.
        - rendered_widget: Generative UI widget structure for chat clients.
    """
```

#### 3. `get_astronomical_events.py`
```python
# app/scripts/get_astronomical_events.py
from typing import Optional

async def get_astronomical_events(event_type: Optional[str] = "all", days_ahead: Optional[int] = 7) -> dict:
    """
    Retrieves active and upcoming astronomical events including meteor shower peaks,
    planetary conjunctions, eclipses, lunar phases, and notable satellite passes.

    Args:
        event_type: Filter by category ('all', 'meteor_shower', 'conjunction', 'eclipse', 'moon_phase', 'satellite').
        days_ahead: Number of days forward to search for events (default: 7).

    Returns:
        A dictionary containing:
        - active_events: List of ongoing celestial events.
        - upcoming_events: Chronological list of events in the specified window with peak times.
        - viewing_tips: Advice for maximizing visibility (e.g., dark sky radiant direction).
    """
```

#### 4. `manage_stargazer_profile.py`
```python
# app/scripts/manage_stargazer_profile.py
from typing import Optional

async def manage_stargazer_profile(action: str, location: Optional[str] = None, optics_tier: Optional[str] = None) -> dict:
    """
    Retrieves, saves, or updates the user's personal stargazing profile in user-scoped storage,
    including primary observing location, geocoordinates, and available observing equipment.

    Args:
        action: Operation to perform ('get' to retrieve profile, 'set' to update).
        location: City name or coordinates to store as the primary observing site.
        optics_tier: Observing gear level ('naked_eye', 'binoculars', 'telescope').

    Returns:
        A dictionary containing:
        - status: 'success' or error description.
        - profile: Saved preferences dictionary including location, lat, lon, optics_tier.
        - rendered_widget: Generative UI card confirming updated profile settings.
    """
```

---

### 🔑 Tool Privileges Matrix

| Privilege Name | Description of Granted Capabilities / Tools |
| :--- | :--- |
| `1` (`Custom Agent Manager`) | Full access to all astronomy expert capabilities: `get_stargazing_forecast`, `get_celestial_body_position`, `get_astronomical_events`, and `manage_stargazer_profile`. |

---

### Model Context Protocol (MCP) & External Connections
*   **MCP Servers:** None required for core functionality.
*   **External APIs / HTTP Services:**
    *   *Weather & Astronomy Ephemerides:* Free [Open-Meteo Weather & Forecast API](https://api.open-meteo.com) and [Open-Meteo Astronomy API](https://api.open-meteo.com) for cloud cover, humidity, sunrise, sunset, moonrise, and moonset without API keys.
    *   *Celestial Coordinates Engine:* High-efficiency offline orbital calculations for planets, moon, and bright objects via Python astronomical ephemerides algorithms.
    *   *Geocoding:* Open-Meteo Geocoding API (`https://geocoding-api.open-meteo.com/v1/search`) for resolving user city/town queries to latitude and longitude coordinates.

---

### Required Secrets (Agent Secrets Vault)

| Secret Name | Description | Required? (True/False) |
| :--- | :--- | :--- |
| `OPEN_WEATHER_API_KEY` | Optional commercial weather API key if overriding default Open-Meteo service. | False |
| `ASTRONOMY_API_KEY` | Optional specialized ephemeris provider API key if overriding internal engine. | False |
