## 🎨 7. User Interface & Widgets Specification
Define the UI layouts, templates, and full-screen applications used by the agent. Refer to `docs/UI_ELEMENTS.md` and `docs/Hubscape-ADK-Manual/CHAPTER_6_LEGO_WIDGETS_AND_IFRAMES.md` for standard elements and viewport targets.

### Widget 1: `<!-- widget_template_id -->`
*   **Target Viewport Destination:** `<!-- inline | sidebar | app_mode -->`
*   **Type / Archetype:** `<!-- inline form, task card, persistent sidebar dashboard, or full-screen app -->`
*   **Theme Token Default:** `<!-- emerald / brand / blue / amber / indigo / violet -->`

#### A. If Inline Chat (`target="inline"`) or Side Bar (`target="sidebar"`):
*   **Template Path:** `app/ui/widgets/<!-- widget_template_id -->.json`
*   **Layout JSON Structure:**
```json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4"
  },
  "children": [
    // ... Children configurations
  ]
}
```

#### B. If App Mode (`target="app_mode"`):
*   **App Identifier (`app_id`):** `<!-- snake_case_app_id -->`
*   **App Title & Icon:** `<!-- Title: e.g. "Flight Planner", Icon: "Command" -->`
*   **Canvas Widget (`canvas_widget`):** `<!-- Lego layout JSON or iframe URL -->`
*   **Companion Remote Widget (`remote_widget`, Optional):** `<!-- Top 65% sidebar dock controls (omit if none) -->`
*   **Toolbar Actions (`actions`, Optional):**
    ```json
    [
      {
        "id": "save",
        "label": "Save",
        "icon": "Save",
        "actionType": "api_call",
        "endpoint": "/api/plugins/{{agent_id}}/save",
        "showFeedback": true
      }
    ]
    ```
