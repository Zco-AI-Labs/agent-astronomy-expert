## 🎨 7. User Interface & Widgets Specification
Define the Lego block UI layouts or templates used by the agent. Refer to `docs/Hubscape-Agent-Template-Guide/CHAPTER_6_LEGO_WIDGETS_AND_IFRAMES.md` for standard elements.

### Widget 1: `<!-- widget_template_id -->`
*   **Type:** `<!-- month-view calendar, list card, detail card, form, etc. -->`
*   **Theme Token Default:** `<!-- blue / red / green / emerald / amber / indigo / violet -->`
*   **Layout JSON Structure:**
```json
// app/ui/widgets/widget_template_id.json
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
```
