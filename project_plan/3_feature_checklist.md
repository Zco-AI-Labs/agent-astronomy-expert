## 📂 3. Feature Checklist & Interaction Modes

Breakdown of the Astronomy Expert agent's core capabilities across visual (UI) and non-visual (SMS, Voice) operational modes.

---

### Feature 1: Tonight's Night Sky & Stargazing Forecast (Main Feature)
*   **Description:** Generates a real-time stargazing report for tonight based on the user's location, combining weather visibility (cloud cover, humidity, transparency) with astronomical ephemerides (moon illumination, visible planets, constellations, and notable celestial events).
*   **Visual Interaction Mode:**
    *   *Trigger:* User asks *"What can I see in the sky tonight?"*, *"Is tonight good for stargazing?"*, or opens the Night Sky widget.
    *   *UI Rendered:* `night_sky_forecast` widget card featuring:
        *   Stargazing Index indicator (e.g., "🟢 Excellent (88/100) - Clear skies & dark moon").
        *   Weather status pill (Cloud cover %, Temperature, Seeing conditions).
        *   Moon status pill (Phase name, % illumination, rise/set time).
        *   List of prime visible targets tonight (e.g., Mars in SE, Jupiter in S, Pleiades cluster) with viewing windows and recommended optical aid.
        *   Interactive buttons: *"Target Details"*, *"Check Another Location"*, and *"Set Observing Reminder"*.
    *   *Form Actions:* Quick location change or expanding a specific target card.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Text message summarizing the stargazing condition rating, moon phase, top 2-3 bright visible planets/events, and optimal viewing hour.
    *   *Voice/Phone Flow:* Natural spoken greeting detailing sky clarity, moon interference, and which direction to look for prominent naked-eye objects.
    *   *Natural Language Parameters Extracted:* `location` (city name or lat/lon coordinates), `date_target` (defaults to tonight).
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Happy Path - Clear Sky with Visible Planets):*
        *   **GIVEN** a valid user location (e.g., Boston, MA) with < 20% cloud cover and Mars/Jupiter above the horizon after sunset.
        *   **WHEN** the user asks what they can see in the night sky tonight.
        *   **THEN** the agent calls weather and ephemeris tools, synthesizes a high stargazing rating, returns a clear summary mentioning Mars and Jupiter visibility, and renders the `night_sky_forecast` widget card.
    *   *Scenario B (Overcast / Poor Stargazing Weather):*
        *   **GIVEN** an active location forecast with > 85% overcast cloud cover.
        *   **WHEN** the user asks what they can see tonight.
        *   **THEN** the agent politely explains that heavy cloud cover will obscure celestial observations tonight, notes what is theoretically up behind the clouds, and advises checking back tomorrow night.
    *   *Scenario C (Missing Location):*
        *   **GIVEN** no saved location in the user's profile and none supplied in the prompt.
        *   **WHEN** the user asks for tonight's sky view.
        *   **THEN** the agent prompts the user for their city or zip code before running the ephemeris and weather queries.

---

### Feature 2: Celestial Object & Planet Finder
*   **Description:** Pinpoints a requested planet, bright star, constellation, or deep-sky object, delivering real-time celestial coordinates, compass direction (cardinal azimuth), altitude angle above horizon, and optical requirements.
*   **Visual Interaction Mode:**
    *   *Trigger:* User asks *"Where is Mars right now?"* or *"Can I see Saturn tonight?"*.
    *   *UI Rendered:* `celestial_target_card` showing object icon, cardinal compass direction, altitude degrees, rise/set time, and viewing tip.
    *   *Form Actions:* Button to show other nearby targets or save target to watch list.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Clean text specifying direction (e.g., "Look Southeast ~35° above the horizon between 9:00 PM and midnight").
    *   *Voice/Phone Flow:* Conversational directional instructions (e.g., "Mars is currently high in the southeastern sky, shining with an unmistakable reddish glow").
    *   *Natural Language Parameters Extracted:* `target_name` (e.g., "Mars", "Jupiter", "Orion", "Andromeda"), `location`.
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Object Visible Tonight):*
        *   **GIVEN** the requested celestial body is above the local horizon during night hours.
        *   **WHEN** the user queries its location.
        *   **THEN** the agent provides altitude, compass direction, viewing window, and optical requirements.
    *   *Scenario B (Object Below Horizon / Daytime):*
        *   **GIVEN** the requested body is below the horizon or too close to the Sun.
        *   **WHEN** the user queries its location.
        *   **THEN** the agent indicates that the object is not visible tonight and provides its next favorable viewing season or rise time.

---

### Feature 3: Astronomical Events & Sky Alerts Radar
*   **Description:** Identifies active or upcoming astronomical events including meteor shower peaks, lunar and solar eclipses, planetary conjunctions, and bright satellite/ISS flyovers.
*   **Visual Interaction Mode:**
    *   *Trigger:* User asks *"Are there any meteor showers happening?"* or *"When will the space station fly over?"*.
    *   *UI Rendered:* `sky_event_timeline` widget displaying active events, peak observation dates, expected rates (e.g., ZHR 60 meteors/hr), and dark-sky tips.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Concise alert list with event name, peak night, and radiant direction.
    *   *Voice/Phone Flow:* Natural spoken summary highlighting the most imminent event and how best to observe it.
    *   *Natural Language Parameters Extracted:* `event_type` (e.g., "meteor_shower", "iss", "eclipse", "all").
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Active Meteor Shower or Conjunction):*
        *   **GIVEN** an active event within its peak window.
        *   **WHEN** the user asks about upcoming events.
        *   **THEN** the agent details the radiant constellation, peak hours (e.g., post-midnight), and advice on avoiding moonlight interference.

---

### Feature 4: Observing Location & Optics Profile Management
*   **Description:** Allows users to set, view, or update their primary stargazing location (city/coordinates) and observing equipment (naked eye, 10x50 binoculars, 6-inch telescope) in persistent user-scoped storage.
*   **Visual Interaction Mode:**
    *   *Trigger:* User says *"Set my stargazing location to Austin, Texas"* or *"I just got an 8-inch telescope"*.
    *   *UI Rendered:* `stargazer_profile_card` widget confirming updated location and optics tier.
*   **Non-Visual Interaction Mode (SMS/Voice Fallback):**
    *   *SMS Transcript Flow:* Simple confirmation message: *"Your observing location is saved as Austin, TX (Equipment: Telescope)."*
    *   *Voice/Phone Flow:* Verbal acknowledgment of updated preferences.
    *   *Natural Language Parameters Extracted:* `city`, `optics_level` (naked_eye, binoculars, telescope).
*   **Acceptance Criteria (Given-When-Then):**
    *   *Scenario A (Save Location & Optics):*
        *   **GIVEN** user inputs new location and equipment tier.
        *   **WHEN** preference update is requested.
        *   **THEN** the agent persists these to user-scoped documents and uses them as default parameters in future queries.
