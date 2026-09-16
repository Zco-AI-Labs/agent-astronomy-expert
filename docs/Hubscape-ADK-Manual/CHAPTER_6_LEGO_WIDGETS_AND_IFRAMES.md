# Chapter 6: Lego Widgets & Sandboxed IFrames

Custom agents can display rich interfaces inside the companion chat UI. Simple forms are built using declarative JSON (Lego Widgets), while complex visuals (such as poster compositors or canvas editors) use custom HTML iframes.

---

## 1. Declarative Lego Widgets

Lego widgets are JSON files representing a tree of nested components. They must be saved inside:
`app/ui/widgets/<widget_name>.json`

### Data Binding Rules:
1. **Flat Keys:** The React UI parser flattens variables passed to widgets. Reference keys directly (e.g. use `{{image_url}}` rather than `{{data.image_url}}`).
2. **No Dot Notation:** Variable placeholders are parsed using the regex pattern `/\{\{\s*(\w+)\s*\}\}/g`. Because dots (`.`) are not word characters, placeholders containing dots will fail to parse and render literally in the DOM.

---

## 2. The Tri-Target Viewport Architecture

The Hubscape client provides three dedicated spatial destinations for UI widgets:

### 1. The Three Placement Targets

| Target | Viewport Location | Interaction Model | Primary Use Cases |
|---|---|---|---|
| **Inline Chat** (`target="inline"`) | Embedded directly in conversation timeline | Scrolls with messages; converts to receipt on submission | Fast data capture, receipts, surveys, confirmation dialogs |
| **Tactical Side Bar** (`target="sidebar"`) | Pinned 384px (`w-96`) dock on desktop; drawer on mobile | Persistent tab in top carousel; interactive bookmark card in chat | Live dashboards, audio/video players, task boards, editors |
| **Full-Screen App Mode** (`target="app_mode"`) | Promotes main viewport to full-screen canvas | Top toolbar + canvas + companion remote in Side Bar + companion chat | Interactive maps, full editors, data visualizers, iframe web apps |

> [!NOTE]
> **Inline Chat Form Lifecycle:** Inside inline chat, widgets follow the **Atomic Viewport Model** where one form is submitted or completed sequentially before the conversation moves forward. In the Side Bar and App Mode, widgets remain persistently active while the user continues chatting.

### 2. Viewport Lifecycle & Dismissal Options (Inline Chat)
Widgets support two core submission lifecycle paradigms, alongside instant client-side cancellation and server-driven closure:

| Lifecycle Mode | Trigger | Viewport Behavior | Confirmation / Message Display |
|---|---|---|---|
| **Optimistic Collapse** | `"closeOnClick": true` | Widget vanishes immediately (0ms) upon valid submit | Displays `submittedLabel`, `?text=...`, or `"Form submitted."` |
| **Read-Only Receipt** *(Default)* | `"closeOnClick": false` or omitted | Form locks in place into an immutable read-only receipt | Submit button converts into green status badge; inputs disabled |
| **Client Cancellation** | `actionUrl: "client://close_widget"` | Widget unmounts locally with **0 network / 0 LLM calls** | Displays `?text=...` (default: `"Form cancelled."`); purges draft cache |
| **Server Tool Closure** | `context.close_widget()` in Python | Widget unmounts after backend Python tool finishes | Displays `result_text` provided by the Python tool |

### 3. Full Button Configuration Example
```json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-4 bg-white rounded-lg border border-indigo-100 shadow-sm"
  },
  "children": [
    {
      "type": "input",
      "props": {
        "name": "org_name",
        "label": "Organization Name",
        "placeholder": "Apex Innovations",
        "required": true
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Submit Details",
        "actionUrl": "agent://{{agent_id}}/save_org_details",
        "styling": {
          "colorTheme": "indigo"
        },
        "submittedLabel": "Organization Details Submitted",
        "closeOnClick": true
      }
    },
    {
      "type": "button",
      "props": {
        "label": "Cancel",
        "actionUrl": "client://close_widget?text=Form+cancelled.",
        "styling": {
          "colorTheme": "slate"
        },
        "hideOnSubmit": true
      }
    }
  ]
}
```

### 4. Zero-Data-Loss Error Re-Hydration & Sibling Disabling
* **Client-Side Validation:** Form inputs are validated on blur and submit before any dispatch occurs, preventing bad requests from firing.
* **In-Flight Retry Buffer:** Submissions are automatically buffered in `inFlightSubmissionRef`. If an agent tool encounters a business logic error and re-renders the form, the user's previously entered input values are automatically re-hydrated.
* **Sibling Button Disabling:** When a user clicks a button, sibling buttons inside the widget are disabled/dimmed to prevent race conditions or duplicate submissions.

---

## 3. Targeted Agent Action Routing (`agent://<agent_id>/<action_name>`)

For buttons triggering backend tool actions, configure `actionUrl` using the targeted URI format `agent://<agent_id>/<action_name>` (e.g. `agent://sales-onboarding-agent/save_org_details`).

* **Deterministic Dispatch:** Bypasses Host LLM re-interpretation and routes straight to the owning subagent via `/action <action_name> <payload>`.
* **Query Parameters:** Query parameters in the URL (e.g. `?text=Custom+confirmation+message`) are parsed and merged into the payload automatically.

Inside a Python tool, you can process the payload and optionally trigger a programmatic close:

```python
from app.core.hubscape_adk import get_context

async def submit_and_close_form(data: str) -> dict:
    context = get_context()
    
    # 1. Process or save data...
    context.save(scope="user", collection_name="submissions", doc_id="form_1", data={"info": data})
    
    # 2. Append close directive action (optional if not using closeOnClick)
    context.close_widget(result_text="Form submitted successfully! Widget closing.")
    
    return {"status": "success"}
```

This appends the `CLOSE_AGENT_WIDGET` action directive to the response payload:
```json
{
  "type": "CLOSE_AGENT_WIDGET",
  "payload": {
    "messageId": null,
    "resultText": "Form submitted successfully! Widget closing."
  }
}
```

---

## 3.1 Zero-LLM Local Bridge Routing (`app://<action_name>`)

When building App Mode companion remotes or interactive Lego widgets, buttons can dispatch actions with **0ms latency and 0 LLM cost** using the `app://` protocol:

* **Format:** `app://<action_name>?<key>=<value>&announcement=<text>`
* **Instant Client-Side Dispatch:** Handled entirely by the client-side `useAppBridge` event bus. Updates shared application state across both the canvas stage and companion remote without invoking an agent LLM turn.
* **Automatic State Parsing:** All query parameters (e.g. `?shields=100&warp=9`) are parsed into strings, numbers, or booleans and merged into the shared application store, instantly triggering reactive re-renders in Lego containers and IFrames.
* **Chat Timeline Announcements:** Passing `?announcement=Operation+complete` posts a formatted assistant status message to the companion chat history without triggering an LLM generation. (To suppress announcements, pass `?silent=true`).
* **Domain State & Custom Banners:** Arbitrary state parameters passed via `app://` (such as `?status=active&mode=turbo`) update the shared state store instantly. Agents can render dynamic status indicators, alert banners, and telemetry gauges directly within their Lego widget trees that reactively re-render when these state keys update.

```json
{
  "type": "button",
  "props": {
    "label": "High Priority",
    "actionUrl": "app://set_priority?priority=high&announcement=Priority+updated+to+high.",
    "styling": { "colorTheme": "amber" }
  }
}
```

---

## 4. Visual Sandboxed IFrames (`iframe`)

For complex UIs requiring canvas interactions, dragging, or real-time editing, use the `iframe` Lego component to embed custom HTML files:

```json
{
  "type": "iframe",
  "props": {
    "src": "/api/agents/{{agent_id}}/static/my_widget.html",
    "className": "w-full h-[600px] border-0 rounded-xl"
  }
}
```

* **Relative Src Rule:** Always use relative platform paths (e.g. `/api/agents/{{agent_id}}/static/widget.html`) inside the `src` property. Never hardcode absolute URLs or ports (like `http://localhost:8090/...`) as they will fail when deployed to production cloud routing.

---

## 5. Bidirectional IFrame Communication & Reactive App Bridge

Because GEAP/ADK agent containers are sandboxed, iframes communicate with the parent Hubscape web client using standard HTML5 `window.parent.postMessage()` APIs.

```text
  Custom HTML (IFrame)                 Hubscape Client / Bridge                 Agent / Subsystems
------------------------               ------------------------                 ------------------
window.parent.postMessage()  ----->    Message Broker Relay         ----->      Executes Python Tool or
                                       (Security & Token Scoping)               Updates Companion Remote
IFrame Message Listener      <-----    Relays Parent Events         <-----      Toolbar Actions / State
```

### 1. Inbound Actions from the IFrame

Web applications running inside iframes can dispatch three primary message types to the parent window:

#### A. Backend Tool Execution (`SUBMIT_FORM`)
Triggers an agent tool execution without reloading the page:
```javascript
window.parent.postMessage({
  type: 'SUBMIT_FORM',
  actionUrl: `agent://${agentId}/my_backend_tool`,
  payload: { flight_id: 'UA101', altitude: 32000 }
}, '*');
```

#### B. Direct Chat Timeline Broadcast (`POST_CHAT`)
Publishes an event or announcement directly into the user's active conversation history. The platform locks attribution to the app's title and `subsystem: 'app_event'` to prevent identity spoofing:
```javascript
window.parent.postMessage({
  type: 'HUBSCAPE_APP_BRIDGE',
  action: 'POST_CHAT',
  payload: {
    text: '🚨 Waypoint deviation detected: Route updated to NAV-4.',
    senderName: 'Flight Radar'
  }
}, '*');
```

#### C. Inter-Widget State Synchronization (`UPDATE_STATE` & `BROADCAST`)
Synchronizes state in real time with a companion remote widget docked in the Side Bar:
```javascript
// Synchronize shared data store with companion remote widget
window.parent.postMessage({
  type: 'HUBSCAPE_APP_BRIDGE',
  action: 'UPDATE_STATE',
  payload: { zoom: 12, layer: 'satellite' }
}, '*');

// Broadcast custom named event across the bridge
window.parent.postMessage({
  type: 'HUBSCAPE_APP_BRIDGE',
  action: 'BROADCAST',
  eventType: 'RADAR_SWEEP_COMPLETE',
  payload: { targetsFound: 4 }
}, '*');
```

### 2. Outbound Events from Hubscape to the IFrame
When the user triggers a toolbar action button or interacts with a companion remote widget in the Side Bar dock, the parent platform broadcasts a `HUBSCAPE_APP_BRIDGE` event into all active iframes:

```javascript
window.addEventListener('message', (event) => {
  const data = event.data;
  if (data && data.type === 'HUBSCAPE_APP_BRIDGE') {
    const { type, payload } = data.detail;
    if (type === 'TOOLBAR_ACTION') {
      console.log("Toolbar action clicked:", payload.id);
    } else if (type === 'STATE_UPDATE') {
      console.log("Companion remote updated state:", payload);
    }
  } else if (data && data.type === 'TOOL_RESPONSE') {
    console.log("Received backend tool response:", data.payload);
  }
});
```

### 3. Security Token Scoping & Context Injection
The platform inspects iframe `src` URLs to enforce strict domain boundaries:
* **Internal/Relative URLs (`/api/...`, same-origin):** The client injects query parameters `?authToken=...&hubId=...&orgId=...` and passes them via `data-auth-token`.
* **External Third-Party URLs (`https://...`):** Sensitive platform `authToken` values are strictly **withheld**. Only sanitized context identifiers (`hubId`, `orgId`) are provided.

---

## 6. Declarative Field Validation

Lego form inputs (`input`, `select`, `choice-picker`) support standardized declarative validation.

### Validation Properties:
* `required` (boolean | string): Ensures field is non-empty. Optional custom error string.
* `validationType` (string): Built-in format validator: `"email"`, `"phone"` (10+ digits, area code required), `"pattern"`, `"numeric"`, `"length"`.
* `pattern` (string): Custom Regular Expression string.
* `errorMessage` (string): Custom error message override displayed under field.

### Validation Example:
```json
{
  "type": "input",
  "props": {
    "name": "user_email",
    "label": "Email Address",
    "required": true,
    "validationType": "email",
    "errorMessage": "Valid structured email address required (e.g. officer@starfleet.org)."
  }
}
```

---

## 7. Live Error Banners (`live-error-banner`)

For live-monitored tasks or background streams, render a `live-error-banner` element to provide diagnostic feedback and retry buttons:

```json
{
  "type": "live-error-banner",
  "props": {
    "title": "Stream Process Error",
    "message": "Connection to the monitoring array timed out.",
    "errorCode": "ERR_TIMEOUT",
    "details": { "sensor_id": "array_01", "latency_ms": 30000 },
    "retryActionUrl": "agent://reconnect_sensor",
    "retryLabel": "Reconnect Sensor"
  }
}
```

---

## 8. Complete Component Catalog & Parameters Reference

For a complete reference guide detailing all 25 supported Lego UI elements (such as `container`, `text`, `table`, `tabs`, `flow-chart`, and more), complete with parameters, default values, behavior descriptions, and JSON examples for each, please refer to the:

👉 **[Hubscape ADK UI Elements Catalog (UI_ELEMENTS.md)](../UI_ELEMENTS.md)**

---

[Next Chapter: OAuth Integration & Hubscape ADK API](CHAPTER_7_OAUTH_INTEGRATION_AND_ADK_API.md) | [Previous Chapter: Sandbox Emulation](CHAPTER_5_SANDBOX_EMULATION.md)
