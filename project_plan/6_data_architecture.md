## 💾 6. Data Architecture & DB Schemas

All persistence strictly adheres to the standard Hubscape ADK scoping paths:
*   **User Scope:** `platform_users/{user_id}/agent_data/astronomy_expert/{collection_name}`
*   **Hub Scope:** `organizations/{org_id}/hubs/{hub_id}/agent_data/astronomy_expert/{collection_name}`
*   **Org Scope:** `organizations/{org_id}/agent_data/astronomy_expert/{collection_name}`

---

### Collection 1: `stargazer_profiles`
Stores the user's saved stargazing configuration, default observing coordinates, and optics equipment tier.

*   **Scope:** `user`
*   **Path:** `platform_users/{user_id}/agent_data/astronomy_expert/stargazer_profiles/preferences`
*   **Document ID Format:** Fixed singleton document `preferences` per user.

#### Fields Table
| Field Name | Type | Description | Mandatory / Optional |
| :--- | :--- | :--- | :--- |
| `id` | `String` | Identifier duplicated in document (`preferences`) | Mandatory |
| `created_at` | `Timestamp` | ISO-8601 UTC creation timestamp (auto-injected) | Mandatory |
| `created_by` | `String` | User ID who created the record (auto-injected) | Mandatory |
| `updated_at` | `Timestamp` | ISO-8601 UTC last update timestamp (auto-injected) | Mandatory |
| `updated_by` | `String` | User ID who modified the record (auto-injected) | Mandatory |
| `version` | `Integer` | Optimistic locking document version counter | Mandatory |
| `city_name` | `String` | Display city/region name (e.g., "Denver, CO", "Flagstaff, AZ") | Mandatory |
| `latitude` | `Float` | Observing latitude coordinate in decimal degrees | Mandatory |
| `longitude` | `Float` | Observing longitude coordinate in decimal degrees | Mandatory |
| `timezone` | `String` | Local IANA timezone identifier (e.g., "America/Denver") | Mandatory |
| `optics_tier` | `String` | User's observing equipment (`naked_eye`, `binoculars`, `telescope`) | Mandatory |
| `equipment_details` | `String` | Specific gear notes (e.g., "8-inch Dobsonian", "10x50 Binoculars") | Optional |
| `bortle_class` | `Integer` | Dark-sky rating from 1 (pristine dark sky) to 9 (inner city) | Optional |
| `favorite_targets` | `List[String]` | Array of favorite celestial bodies or constellations to track | Optional |

---

### Collection 2: `observing_logs`
Stores personal observation journal entries and target sightings recorded by the user.

*   **Scope:** `user`
*   **Path:** `platform_users/{user_id}/agent_data/astronomy_expert/observing_logs/{doc_id}`
*   **Document ID Format:** `obs_{timestamp}_{random_suffix}` (e.g., `obs_1726056000_a8f2`)

#### Fields Table
| Field Name | Type | Description | Mandatory / Optional |
| :--- | :--- | :--- | :--- |
| `id` | `String` | Document ID duplicated in payload | Mandatory |
| `created_at` | `Timestamp` | ISO-8601 UTC creation timestamp | Mandatory |
| `created_by` | `String` | Injected user ID | Mandatory |
| `updated_at` | `Timestamp` | ISO-8601 UTC update timestamp | Mandatory |
| `updated_by` | `String` | Injected user ID | Mandatory |
| `version` | `Integer` | Version counter | Mandatory |
| `target_name` | `String` | Celestial body observed (e.g., "Jupiter", "Orion Nebula") | Mandatory |
| `session_date` | `String` | Date of observing session (YYYY-MM-DD) | Mandatory |
| `location_name` | `String` | Location where observation took place | Mandatory |
| `seeing_rating` | `String` | Quality rating of observing conditions (`poor`, `fair`, `good`, `excellent`) | Optional |
| `notes` | `String` | User observation notes (e.g., "Great view of Great Red Spot") | Optional |
| `optics_used` | `String` | Equipment utilized during the session | Optional |
