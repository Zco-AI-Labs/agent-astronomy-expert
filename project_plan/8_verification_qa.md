## 🧪 8. Verification & QA Plan

Outline of automated testing strategies, command-line runners, and manual acceptance checklists.

---

### Automated Tests
*   **Unit Tests (`tests/unit/`):**
    ```bash
    uv run pytest tests/unit -v
    ```
    *Tests weather parsing logic, astronomical coordinate calculation algorithms, stargazing score weighting, and input validation.*

*   **Integration Tests (`tests/integration/`):**
    ```bash
    uv run pytest tests/integration -v
    ```
    *Tests end-to-end tool execution against live/mocked Open-Meteo API endpoints and Firestore user-scoped preference persistence.*

*   **Code Quality & Linting:**
    ```bash
    ruff check .
    ```

*   **Agent Evaluation & Scenario Grading:**
    ```bash
    agents-cli eval generate
    agents-cli eval grade
    ```
    *Generates and grades multi-turn agent evaluation scenarios against LLM-as-judge benchmarks.*

---

### Manual Verification Checklist
1. `[ ]` **Clear Sky Forecast Flow:**
   - Execute query: *"What can I see in the night sky tonight in Denver?"*
   - Verify: Agent evaluates cloud cover (< 20%), moon phase, and identifies prominent planets (e.g., Mars, Jupiter).
   - Verify: `night_sky_forecast` widget renders with complete Lego styling and interactive buttons.
2. `[ ]` **Overcast Weather Handling:**
   - Execute query with cloudy coordinates (e.g., Seattle during heavy cloud cover).
   - Verify: Agent flags Stargazing Index as Poor, explains cloud obstruction, and provides optimistic tomorrow forecast.
3. `[ ]` **Celestial Object Finder:**
   - Query specific target: *"Where is Mars right now?"*
   - Verify: Returned altitude and cardinal azimuth match real ephemerides.
   - Verify: `celestial_target_card` renders with direction and altitude pills.
4. `[ ]` **Object Below Horizon:**
   - Query target currently beneath the horizon or obscured by the Sun.
   - Verify: Agent clearly states the target is below the horizon and provides rise time.
5. `[ ]` **Observing Profile Persistence:**
   - Set location: *"Save my observing spot as Flagstaff, AZ"*.
   - Ask follow-up without specifying city: *"What can I see tonight?"*.
   - Verify: Agent automatically uses Flagstaff coordinates from user scope.
6. `[ ]` **SMS Non-Visual Adaptation:**
   - Inspect SMS simulation responses. Verify no raw markdown asterisks, broken tables, or raw JSON payloads.
7. `[ ]` **Voice Channel Speech Quality:**
   - Verify spoken voice script: Natural conversational phrasing, no acronym confusion, and smooth phonetic descriptions.
