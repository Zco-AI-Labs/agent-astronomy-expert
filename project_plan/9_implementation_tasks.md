## 📋 9. Implementation Tasks

This checklist maps the precise, step-by-step coding and configuration tasks required to implement the Astronomy Expert agent. Mark tasks as `[ ]` (unstarted), `[/]` (in progress), or `[x]` (completed) during implementation.

---

### Phase 1: Configuration & Agent Identity
- [ ] Update `app/SKILL.md` frontmatter and system prompt:
  - Set `name: astronomy_expert`.
  - Set `description: "Provides real-time night-sky stargazing forecasts, celestial visibility analysis, planet/star finder, and astronomical event alerts based on local weather conditions and ephemerides."`.
  - Paste full prompt guidelines, persona definition, multi-modal formatting instructions, and closed-domain grounding directive.
- [ ] Configure `app/privileges.json`:
  - Register privilege `1` with title `Custom Agent Manager` granting access to `get_stargazing_forecast`, `get_celestial_body_position`, `get_astronomical_events`, and `manage_stargazer_profile`.
- [ ] Confirm dependencies in `pyproject.toml` (verify `httpx` and standard math/datetime utilities are active).

---

### Phase 2: Core Astronomy & Meteorological Engines (`app/scripts/`)
- [ ] Create `app/scripts/_weather_utils.py`:
  - Implement async client for Open-Meteo Weather API (`api.open-meteo.com/v1/forecast`).
  - Extract cloud cover (low, mid, high), 2m temperature, relative humidity, and precipitation probability.
  - Compute a combined Seeing & Transparency Index.
- [ ] Create `app/scripts/_ephemeris_utils.py`:
  - Implement calculations for solar twilight (sunset, dusk, astronomical twilight), moon phase, percentage illumination, and moonrise/moonset.
  - Implement horizontal coordinate algorithms (altitude angle and compass azimuth) for the 7 primary naked-eye planets (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune) and prominent bright stars / deep-sky objects (Orion Nebula, Pleiades, Andromeda Galaxy).
  - Implement stargazing index scoring algorithm (0-100) weighting cloud cover (50%), moon illumination/presence (30%), and seeing/transparency (20%).
- [ ] Implement `app/scripts/get_stargazing_forecast.py`:
  - Validate location (resolving via profile or geocoding).
  - Fetch weather and ephemeris data concurrently using `asyncio.gather`.
  - Synthesize stargazing score and construct the `night_sky_forecast` widget payload.
- [ ] Implement `app/scripts/get_celestial_body_position.py`:
  - Resolve requested target object name.
  - Calculate instantaneous altitude and azimuth.
  - Format cardinal compass direction and optical equipment recommendation.
  - Construct `celestial_target_card` widget payload.
- [ ] Implement `app/scripts/get_astronomical_events.py`:
  - Retrieve active meteor showers (with peak rates and radiant directions), lunar phases, and conjunctions.
- [ ] Implement `app/scripts/manage_stargazer_profile.py`:
  - Use `app.core.hubscape_adk.get_context()` to access `user` scope document: `platform_users/{user_id}/agent_data/astronomy_expert/stargazer_profiles/preferences`.
  - Handle `get` and `set` actions with optimistic locking version increments.
  - Construct `stargazer_profile_card` widget payload.

---

### Phase 3: Lego UI Widget Templates (`app/ui/widgets/`)
- [ ] Scaffold directory `app/ui/widgets/` if not present.
- [ ] Create `app/ui/widgets/night_sky_forecast.json` using the complete Lego block schema from Section 7.
- [ ] Create `app/ui/widgets/celestial_target_card.json` using the complete Lego block schema from Section 7.
- [ ] Create `app/ui/widgets/stargazer_profile_card.json` using the complete Lego block schema from Section 7.

---

### Phase 4: Verification & Automated Testing
- [ ] Create `tests/unit/test_ephemeris.py`:
  - Unit tests for altitude/azimuth computation accuracy.
  - Unit tests for moon phase and illumination percentage calculation.
  - Unit tests for stargazing index score computation under various cloud cover and moon conditions.
- [ ] Create `tests/unit/test_weather.py`:
  - Unit tests for Open-Meteo response parser with mock payloads.
- [ ] Create `tests/integration/test_astronomy_tools.py`:
  - Integration tests verifying all 4 tools execute and return valid schema dictionaries with rendered widgets.
- [ ] Run test suite: `uv run pytest tests/unit tests/integration -v`.
- [ ] Run code quality checks: `ruff check .`.

---

### Phase 5: Interactive Simulation & Delivery
- [ ] Verify interactive conversational flows in `agents-cli playground`.
- [ ] Test multi-modal fallbacks: SMS plain-text output and Voice natural phonetic phrasing.
- [ ] Update `walkthrough.md` with test results and validation proof.
