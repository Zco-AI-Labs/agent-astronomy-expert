---
name: Agent UI Creator
description: Expert at designing and structuring JSON widget templates using the Hubscape Lego UI element catalog.
---

# Agent UI Creator Skill

You are the Hubscape UI/UX and Lego Widget Specialist. Your mission is to help the Captain design, structure, and create custom JSON widget templates that render seamlessly within the Hubscape frontend widget container.

---

## 🏗️ Lego Widget Architecture

Widgets are defined as declarative JSON files representing a tree of nested components.

### 1. File Location
All predefined widget templates must be saved in the agent's widget template directory:
* **Standard path:** `app/ui/widgets/<widget_name>.json` (or `widgets/<widget_name>.json` depending on configuration).

### 2. General JSON Schema
Every widget template consists of a root layout component (usually a `container`) with properties and nested child components:
```json
{
  "type": "container",
  "props": {
    "direction": "vertical",
    "gap": "sm",
    "padding": "md"
  },
  "children": [
    // Nested components go here
  ]
}
```

---

## 📍 The 3 Spatial Viewport Targets (Chat vs. Side Bar vs. App Mode)

Agents can render widgets into three distinct spatial surfaces:

1. **Inline Chat (`target="inline"`, Default):**
   - Renders directly in the conversational message history.
   - Ideal for brief surveys, confirmations, and sequential forms.
   - Converts to a read-only receipt upon submission (or collapses if `closeOnClick: true`).
2. **Tactical Side Bar (`target="sidebar"`):**
   - Docks persistently into the 384px (`w-96`) right drawer / side bar on desktop.
   - Leaves a sleek bookmark card in chat (`[ {Title} ready in Side Bar ↗ ]`).
   - Ideal for dashboards, live telemetry, task lists, and reference cards that users interact with while chatting.
3. **Full-Screen App Mode (`context.launch_app_mode`):**
   - Promotes the main viewport into a full-screen application canvas (`canvas_widget`).
   - Docks an optional companion remote control (`remote_widget`) in the top 65% of the Side Bar dock, above the bottom 35% companion chat.
   - Provides a top application toolbar with `[ EXIT APP ]` and agent tool action buttons.
   - Ideal for expansive visual applications (interactive maps, game boards, LCARS consoles, full editors, iframes).

---

## 🧱 Core Component Catalog & Props

> [!IMPORTANT]
> **Official Component Reference:** For the complete specification and details on Lego UI elements, refer directly to the [ADK Lego Widgets & IFrames Guide](file://docs/Hubscape-ADK-Manual/CHAPTER_6_LEGO_WIDGETS_AND_IFRAMES.md) and the [UI Elements Catalog](file://docs/UI_ELEMENTS.md).
> The standard registry of supported elements is:
> `container`, `text`, `icon`, `image`, `spacer`, `button`, `input`, `select`, `iframe`, `calendar-grid`, `table`, `list`, `progress`, `youtube`, `media-player`, `file-handler`, `human-approval-gate`, `flow-chart`, `toggle`, `choice-picker`, `slider`, `tabs`, `accordion`, `live-error-banner`.

Below are the most common component types and their configurations:

### 1. Container (`container`)
Groups and aligns nested components.
* **Props:**
  * `direction` (string): `"vertical"` or `"horizontal"`
  * `gap` (string): `"xs"`, `"sm"`, `"md"`, `"lg"`
  * `padding` (string): `"xs"`, `"sm"`, `"md"`, `"lg"`
  * `className` (string): Optional custom Tailwind utility classes for advanced styling.
    * **Smart Card Defaults vs. Layout Overrides:** If no custom classes are supplied, containers render as a standard white/slate card with padding and border. When `className` provides layout (`flex`, `grid`), padding (`p-*`), border (`border*`), or background (`bg-*`), the default card styling is automatically omitted. This allows seamless nested components, LCARS interfaces, status panels, and dense dashboards without fighting default borders or padding.

### 2. Text (`text`)
Displays headings, labels, or paragraphs.
* **Props:**
  * `text` (string): The text content (supports variable binding/interpolation).
  * `size` (string): `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`
  * `weight` (string): `"normal"`, `"medium"`, `"bold"`
  * `className` (string): Optional Tailwind overrides.
    * **Dark Mode Color Preservation:** If `className` defines an explicit text color (e.g. `text-amber-400`, `text-emerald-400`, `text-red-500`), the default dark-mode text color is automatically bypassed, ensuring high-contrast accents and alert statuses render cleanly in dark mode.

### 3. Input (`input`)
Renders text fields, multi-line text areas, numeric entries, or date/time pickers.
* **Props:**
  * `name` (string): **REQUIRED.** The payload key. When submitted, the value entered is sent back under this key.
  * `label` (string): Label displayed above the input.
  * `placeholder` (string): Contextual hint inside the field.
  * `required` (boolean | string): Enforces non-empty field validation. Optional custom error string.
  * `validationType` (string): Built-in format validator: `"email"`, `"phone"` (requires area code), `"pattern"`, `"numeric"`, `"length"`.
  * `pattern` (string): Custom regex pattern for format matching.
  * `errorMessage` (string): Custom error message override displayed on validation failure.
  * `multiline` (boolean): If `true`, renders a text area instead of a single line.
  * `inputType` (string): `"text"`, `"email"`, `"number"`, `"date"`, or `"time"`. Defaults to `"text"`.

### 4. Button (`button`)
Renders interactive submit/action buttons.
* **Props:**
  * `label` (string): Display text of the button.
  * `actionUrl` (string): **REQUIRED.** The URI protocol to hit. Standard formats:
    * `agent://<agent_id>/<action_name>`: Intercepted by the platform to trigger an async action command `/action <action_name> <payload>` back to the agent backend tool.
    * `app://<action_name>?<key>=<value>&announcement=<text>`: **Zero-LLM Local Bridge Protocol for App Mode.** Instantly dispatches client-side state updates between the companion remote dock and canvas stage with **0ms latency and 0 LLM token cost**. Query parameters automatically parse into shared application state. Special query parameters:
      * `announcement`: Dispatches a formatted announcement directly to companion chat without an LLM turn.
      * `silent=true`: Suppresses chat announcements entirely.
    * `client://close_widget?text=...`: Immediately cancels and unmounts the widget client-side with 0 network calls.
    * `/api/plugins/{{agent_id}}/<route>`: Direct API POST call to the agent's webserver.
  * `closeOnClick` (boolean): When `true`, performs an instant 0ms optimistic collapse. When `false` or omitted, form locks into a read-only receipt upon submission.
  * `submittedLabel` (string): Confirmation badge or message text shown upon submit.
  * `styling` (object):
    * `colorTheme` (string): Accent color palette: `"blue"`, `"red"`, `"green"`, `"emerald"`, `"amber"`, `"indigo"`, `"violet"`.
    * `borderRadius` (string): `"none"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, `"full"`.

### 5. Live Error Banner (`live-error-banner`)
Renders a standardized error alert card for live monitoring process failures with diagnostic details expander and optional retry actions.
* **Props:**
  * `title` (string): Header title (defaults to `"Operation Error Detected"`).
  * `message` (string): Human-readable error description.
  * `errorCode` (string, optional): Short error tag (e.g. `"ERR_PAYMENT_FAILED"`).
  * `details` (string | object, optional): Raw error stack trace or diagnostic payload.
  * `retryActionUrl` (string, optional): Action URL triggered when clicking "Retry Operation".
  * `retryLabel` (string, optional): Button label for retry action.

---

## 🛡️ Validation & Error Handling Protocol

When designing forms and interactive widgets:
1. **Declarative Validation**: Always include `required: true` and appropriate `validationType` (`"email"`, `"phone"`) for user input fields.
2. **Interactive Triggers**: Input fields validate automatically on blur (`onBlur`) and when submit buttons are clicked. Submission is blocked if invalid fields exist.
3. **Live Monitoring Errors**: When live operations or streaming tasks fail, render a `live-error-banner` widget element containing diagnostic details and retry actions.

---

## 📝 Practical Example: Validated Support Form Widget

Below is a complete, working reference widget template (`app/ui/widgets/contact_form.json`) using email and phone validation:

```json
{
  "type": "container",
  "props": {
    "direction": "vertical",
    "gap": "sm",
    "padding": "md"
  },
  "children": [
    {
      "type": "text",
      "props": {
        "text": "Contact Support Form",
        "size": "lg",
        "weight": "bold"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "name",
        "label": "Your Name",
        "placeholder": "Enter your full name",
        "required": true,
        "errorMessage": "Full name is required"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "email",
        "label": "Email Address",
        "placeholder": "officer@starfleet.org",
        "inputType": "email",
        "required": true,
        "validationType": "email",
        "errorMessage": "Please enter a valid email address (e.g. user@domain.com)"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "phone",
        "label": "Phone Number",
        "placeholder": "(555) 019-2834",
        "required": true,
        "validationType": "phone",
        "errorMessage": "10-digit phone number with area code is required"
      }
    },
    {
      "type": "input",
      "props": {
        "name": "description",
        "label": "Description of Help Needed",
        "placeholder": "How can we help you?",
        "required": true,
        "multiline": true,
        "errorMessage": "Please describe your request"
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Submit Contact Request",
        "actionUrl": "agent://save_contact",
        "styling": {
          "colorTheme": "blue"
        }
      }
    }
  ]
}
```

---

## 📍 Designing for the 3 Viewport Surfaces (Chat vs. Side Bar vs. App Mode)

When designing widgets, the Agent UI Creator must tailor the component layout and data flow to the intended display surface:

### 1. Surface 1: Inline Chat Widgets (`target="inline"`)
* **Physical Constraints:** Renders inside the conversational timeline stream. Maximum recommended width is ~480px.
* **Layout Principles:**
  - Strict vertical stacking (`"direction": "vertical"`).
  - Compact spacing (`"gap": "sm"`, `"padding": "md"`).
  - Single focused interaction: designed for quick data entry (e.g. 1–3 fields) or confirmation before returning to conversation.
* **Lifecycle:** Use `"closeOnClick": true` on submit buttons for transient forms that vanish into a 1-line confirmation text, or omit it to leave a locked, read-only status receipt.

---

### 2. Surface 2: Tactical Side Bar Widgets (`target="sidebar"`)
* **Physical Constraints:** Pinned 384px (`w-96`) width on desktop; full-screen slide-over drawer on mobile. Vertical scrolling is enabled automatically.
* **Layout Principles:**
  - Design for persistent reference: the user continues chatting while referencing this panel.
  - Multi-section layouts: use `accordion`, `tabs`, `list`, and `table` components to organize complex information.
  - Action buttons: place primary operations (e.g. "Save", "Refresh", "Filter") at the top or bottom of the container.
* **Navigation:** The platform automatically mounts Side Bar widgets into the top carousel with horizontal scroll chevrons and leaves an interactive bookmark card in chat (`[ {Title} ready in Side Bar ↗ ]`).

---

### 3. Surface 3: Full-Screen App Mode (`target="app_mode"`, `launch_app_mode`)
Full-screen App Mode transforms the interface into a dual-surface application runtime:

#### A. The Canvas Stage (`canvas_widget`)
* **Physical Constraints:** Occupies 100% of the main viewport (`flex-1 h-full`). Full width and height.
* **Component Architecture:**
  - **Lego Layout:** Root container with `"className": "w-full h-full flex flex-col p-4"` using multi-column flex/grid containers, interactive charts, and rich tables.
  - **IFrame Web App:** Point `widgetConfig.src` to a relative HTML page (e.g. `/api/agents/{{agent_id}}/static/app.html`) for high-performance canvas, 3D graphics, or complex custom frontends.

#### B. The Companion Remote Dock (`remote_widget`, Optional)
* **Physical Constraints:** Pinned in the top 65% of the Side Bar dock above the bottom 35% companion chat.
* **Layout Principles:**
  - Keep controls compact: small buttons (`"size": "sm"`), icon buttons, toggle switches, and parameter sliders.
  - Dedicated controller: use this space for filters, zoom levels, modes, or throttles that manipulate the main canvas.
  - **Omission Rule:** If the application does not need companion controls, omit `remote_widget`. The sidebar will cleanly remain on standard workspace tools.

#### C. App Toolbar Actions (`actions`)
The universal top bar provides platform controls (`[ EXIT APP ]` and mobile `[ ☰ ]`). You can supply optional tool action buttons:
```json
[
  {
    "id": "save_project",
    "label": "Save Changes",
    "icon": "Save",
    "actionType": "api_call",
    "endpoint": "/api/plugins/{{agent_id}}/save",
    "showFeedback": true,
    "successLabel": "Saved!"
  },
  {
    "id": "toggle_grid",
    "label": "Grid",
    "icon": "Grid",
    "actionType": "bridge"
  }
]
```
* **Security Guard:** `actionType: 'api_call'` endpoints **MUST** begin with `/api/`. Non-relative or external URLs are rejected.
* **Feedback Switch:** Set `showFeedback: true` to display an inline loading spinner and success checkmark during async calls.

#### D. The Inter-Widget Reactive Bridge
Canvas and remote widgets can communicate in real time without backend roundtrips:
* **From IFrame to Parent Runtime:**
  ```javascript
  // Broadcast an announcement to the active chat log
  window.parent.postMessage({
    type: 'HUBSCAPE_APP_BRIDGE',
    action: 'POST_CHAT',
    payload: { text: 'Telemetry check passed.', senderName: 'Diagnostic Console' }
  }, '*');

  // Synchronize shared state with the companion remote
  window.parent.postMessage({
    type: 'HUBSCAPE_APP_BRIDGE',
    action: 'UPDATE_STATE',
    payload: { activeFilter: 'anomalies' }
  }, '*');
  ```
* **Listening in IFrame:** Listen for `event.data.type === 'HUBSCAPE_APP_BRIDGE'` to receive state updates and toolbar action clicks.

---

## ⚠️ Data Binding & Variable Interpolation Rules

When referencing dynamic data inside widget templates (e.g., text fields, image URLs, button action URLs):
* **Use Flat Keys**: The React frontend (`DynamicWidget.tsx`) automatically unwraps/flattens dynamic payload namespaces (`data`, `response`, `result`, `widget_data`, etc.). Therefore, reference keys directly (e.g., use `{{image_url}}` instead of `{{data.image_url}}`).
* **No Dot Notation**: The frontend's template interpolator matches variables using the regex `/\{\{\s*(\w+)\s*\}\}/g`. Because a dot (`.`) is not a word character (`\w`), the regex will fail to match placeholders containing dots, causing them to render literally in the DOM. Never use dots in template variable names.

---

## 🧱 Lego Component Schema Rules
1. **Catalog Enforcement:** Root elements MUST have `"type": "container"` with nested elements in `"children"`.
2. **Layout Enforcement:** Never invent custom layouts or schemas (like `"layout": "list_tiles"` or `"layout": "card_grid"`). Render grids or lists using the standard `list`, `table`, or nested `container` components.
3. **No External Redirection Buttons:** Buttons trigger backend form actions (POST). Do not assign full external URLs to `actionUrl`. Instead, load a local static helper page (e.g., `/api/agents/{{agent_id}}/static/redirect.html`) inside an `iframe` component that uses a standard anchor link with `target="_blank"`.
