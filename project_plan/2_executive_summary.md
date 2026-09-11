## 🎯 2. Executive Summary

### Core Objective
The Astronomy Expert agent helps stargazers, amateur astronomers, and casual night-sky observers discover what celestial objects are visible in their night sky tonight. Stargazing heavily depends on two dynamic factors:
1. **Local Meteorological Conditions:** Cloud cover percentage, seeing conditions, humidity, and transparency.
2. **Real-time Astronomical Ephemerides:** Moon phase & illumination percentage, planetary visibility windows (altitude/azimuth above the horizon), meteor shower activity, and bright satellite/ISS flyovers.

The agent analyzes local conditions and ephemerides to deliver an actionable stargazing forecast—telling users what they can see (e.g., "Mars will be visible in the southeast after 9 PM, with a 15% waxing crescent moon and clear skies"), when to look, what equipment is recommended (naked eye, binoculars, telescope), and how weather impacts their viewing window.

### High-Level Success Criteria
*   **Accurate Night Sky Synthesis:** Combines local cloud cover/weather data and planetary ephemerides into a synthesized "Stargazing Index" (e.g., Excellent, Good, Fair, Poor).
*   **Actionable Visibility Guidance:** Explicitly details visible planets, moon phase/illumination, constellations, and transient events (meteor showers, ISS passes) with directional bearings (e.g., "high in the South-East") and time windows.
*   **Multi-Modal Adaptability:**
    *   **Visual Web UI:** Renders an interactive "Tonight's Night Sky Forecast" widget card with observation ratings, celestial target pills, and viewing advice.
    *   **SMS:** Produces concise, clean, bulleted text summaries without markdown formatting errors or raw JSON.
    *   **Voice/Phone:** Provides natural, conversational spoken summaries suitable for voice assistants without acronym clutter or markdown symbols.
*   **User Location & Preferences Memory:** Stores preferred observing locations (city or lat/lon) and available optics (naked eye, binoculars, telescope) in user scope so users don't need to re-enter coordinates repeatedly.
