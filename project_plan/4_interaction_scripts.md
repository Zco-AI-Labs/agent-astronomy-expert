## 💬 4. Interaction Scripts & Conversational Flows

Provide exact transcript logs showing how users interact with the Astronomy Expert agent across visual (Chat UI) and non-visual (SMS, Voice) interfaces.

---

### Scenario 1: Tonight's Stargazing & Night Sky Forecast (Main Feature)

#### Flow A: Visual Path (Chat UI with Widgets)
*   **User:** "What will I be able to see in the night sky tonight?"
*   **Agent (Behind the Scenes):**
    1. Calls `get_user_profile` to retrieve saved coordinates (e.g., Denver, CO: `39.7392° N, 104.9903° W`).
    2. Calls `get_stargazing_weather(latitude=39.7392, longitude=-104.9903)` -> `{ cloud_cover: 12%, seeing: "good", transparency: "high" }`.
    3. Calls `get_night_sky_visibility(latitude=39.7392, longitude=-104.9903, date="2026-09-11")` -> `{ moon: { phase: "Waxing Crescent", illumination: "18%", rise: "08:15 AM", set: "09:12 PM" }, visible_planets: ["Mars", "Jupiter", "Saturn"], events: ["Perseids residual activity"] }`.
    4. Evaluates stargazing index: 88/100 (Excellent).
*   **Agent UI Rendered:** Displays Widget `night_sky_forecast` with:
    *   Header: "Tonight's Stargazing Forecast: Denver, CO"
    *   Score Badge: "🟢 Excellent Observing Conditions (88/100)"
    *   Key Metrics: Cloud Cover 12% | Moon Illumination 18% (Sets at 9:12 PM)
    *   Highlight Cards:
        *   **Mars:** Visible in SE after 9:00 PM, ~45° altitude, prominent reddish hue (Naked Eye).
        *   **Jupiter:** High in the Southern sky around 10:30 PM, Galilean moons visible with binoculars.
        *   **Dark Sky Window:** 9:15 PM onwards (optimal after moonset).
*   **Agent Message:** "Tonight looks fantastic for stargazing in Denver! Skies are mostly clear with just 12% cloud cover. The thin 18% waxing crescent moon sets early at 9:12 PM, leaving dark skies for the rest of the night. Mars will be prominent in the southeast, and Jupiter will shine brilliantly in the south."
*   **User clicks button:** "Explore Target: Jupiter"
*   **Backend Response:** Displays `celestial_target_card` with precise elevation, azimuth, and moon-transit timeline.

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "What can I see in the sky tonight in Denver?"
*   **Agent (Behind the Scenes):** Calls `get_stargazing_weather` and `get_night_sky_visibility`.
*   **Agent Text Reply:**
    "Tonight's Denver Stargazing: EXCELLENT (88/100).
    - Skies: Mostly clear (12% clouds).
    - Moon: 18% crescent, sets at 9:12 PM (dark skies afterwards).
    - Top Targets: Mars (Southeast after 9 PM), Jupiter (South after 10:30 PM, bright naked-eye).
    Reply TARGET <name> for pointing directions or HELP for options."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "What's visible in the night sky tonight?"
*   **Agent (Behind the Scenes):** Calls tools and synthesizes concise speech response.
*   **Agent Speech Reply:** "Tonight is an excellent night for stargazing in your area. Skies are mostly clear with only light cloud cover, and the crescent moon sets early around nine fifteen, leaving behind very dark skies. You will have a great view of Mars rising in the southeast after nine PM, followed by a brilliant Jupiter high in the southern sky later in the evening."

---

### Scenario 2: Finding a Specific Planet or Celestial Body

#### Flow A: Visual Path (Chat UI with Widgets)
*   **User:** "Where is Mars right now?"
*   **Agent (Behind the Scenes):**
    1. Calls `get_celestial_object_coordinates(target="Mars", latitude=39.7392, longitude=-104.9903)`.
    2. Result: `{ altitude: 42.5, azimuth: 135.0, direction: "Southeast", constellation: "Taurus", magnitude: -0.5, visible_now: true, best_window: "9:00 PM - 2:00 AM" }`.
*   **Agent UI Rendered:** Displays Widget `celestial_target_card` with a compass direction dial pointing Southeast, 42° altitude arc, and magnitude rating.
*   **Agent Message:** "Mars is currently 42° above the horizon in the Southeast, nestled in the constellation Taurus. It has an apparent magnitude of -0.5, making it easily visible as a bright reddish beacon to the naked eye."

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Where is Mars?"
*   **Agent (Behind the Scenes):** Calls `get_celestial_object_coordinates`.
*   **Agent Text Reply:** "Mars is currently visible in the Southeast at an altitude of 42 degrees in the constellation Taurus. Look for its bright reddish steady glow. Best viewing is between 9:00 PM and 2:00 AM."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "Where should I look to spot Mars tonight?"
*   **Agent (Behind the Scenes):** Calls `get_celestial_object_coordinates`.
*   **Agent Speech Reply:** "To spot Mars, face toward the southeast and look about halfway up from the horizon. You will see a distinct, bright reddish light that shines steadily without twinkling. It will be easily visible to the naked eye until about two in the morning."

---

### Scenario 3: Overcast / Poor Weather Fallback

#### Flow A: Visual Path (Chat UI with Widgets)
*   **User:** "Can I stargaze tonight from Seattle?"
*   **Agent (Behind the Scenes):**
    1. Calls `get_stargazing_weather(latitude=47.6062, longitude=-122.3321)` -> `{ cloud_cover: 94%, condition: "Overcast / Rain showers", visibility_rating: "Poor" }`.
*   **Agent UI Rendered:** Displays `night_sky_forecast` with a warning banner: "🔴 Poor Observing Conditions (15/100) - Overcast & Rain".
*   **Agent Message:** "Unfortunately, stargazing from Seattle will not be favorable tonight. Thick overcast clouds with 94% coverage and scattered rain will obstruct the night sky. While Jupiter and Saturn are theoretically above the horizon, visibility from the ground will be near zero. Tomorrow's forecast shows clearer skies developing after midnight."

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Sky tonight in Seattle?"
*   **Agent Text Reply:** "Seattle Stargazing: POOR (15/100). Thick cloud cover (94%) and rain will block visibility tonight. Consider checking back tomorrow night when conditions are expected to improve."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "How does the night sky look in Seattle tonight?"
*   **Agent Speech Reply:** "I am afraid conditions are poor for stargazing in Seattle tonight. Dense cloud cover of ninety-four percent and rain showers will block the sky completely. Tomorrow night looks much more promising."

---

### Scenario 4: Setting Observing Location & Equipment Preferences

#### Flow A: Visual Path (Chat UI with Widgets)
*   **User:** "Save my observing spot as Flagstaff, Arizona, and I use an 8-inch Dobsonian telescope."
*   **Agent (Behind the Scenes):**
    1. Calls `geocode_location(query="Flagstaff, Arizona")` -> `{ lat: 35.1983, lon: -111.6513, timezone: "America/Phoenix" }`.
    2. Calls `save_user_profile(latitude=35.1983, longitude=-111.6513, city="Flagstaff, AZ", equipment="8-inch Dobsonian telescope")`.
*   **Agent UI Rendered:** Displays `stargazer_profile_card` showing verified Dark-Sky city coordinates and telescope optical profile.
*   **Agent Message:** "Your observing profile has been updated! Your primary location is set to Flagstaff, AZ (Bortle Class 2-3 Dark Sky), and your optics preference is set to an 8-inch Dobsonian telescope. I will tailor upcoming targets to include deep-sky objects visible through your scope."

#### Flow B: Non-Visual SMS Path (No-UI, Text Only)
*   **User (SMS):** "Set location Flagstaff AZ and equipment telescope"
*   **Agent Text Reply:** "Location saved as Flagstaff, AZ with telescope optics profile. Future stargazing forecasts will automatically use these settings."

#### Flow C: Non-Visual Voice Path (No-UI, Spoken Phone Call)
*   **User (Voice):** "Please update my stargazing location to Flagstaff, Arizona, and note that I have an eight-inch telescope."
*   **Agent Speech Reply:** "I have updated your profile. Your observing location is now Flagstaff, Arizona, and I have noted your eight-inch telescope. I will recommend deep-sky clusters and nebulae suitable for your telescope in future forecasts."
