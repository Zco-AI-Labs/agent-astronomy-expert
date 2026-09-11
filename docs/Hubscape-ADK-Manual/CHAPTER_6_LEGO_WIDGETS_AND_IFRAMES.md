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

## 2. The Atomic Viewport Model & Widget Lifecycle

The Hubscape UI operates under the **Atomic Viewport Model** for all interactive widgets and forms:

### 1. The Single Active Widget Principle
> [!IMPORTANT]
> **Only ONE interactive widget or form can be active in the viewport at a time.**
> When an agent calls `context.show_widget()` (or returns a UI payload from a tool), the newly emitted widget mounts as the singular active interactive component in the viewport. When designing agent workflows, guide users through focused, sequential steps rather than expecting concurrent multi-form interactions.

### 2. Viewport Lifecycle & Dismissal Options
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

## 5. Bidirectional IFrame Communication

Because GEAP/ADK agent containers are sandboxed, iframes cannot directly send HTTP requests (`fetch` or `Axios`) to custom agent API routes. Instead, they communicate using standard HTML5 browser messages:

```text
  Custom HTML (IFrame)                 Hubscape Chat UI                     Agent Container
------------------------               ----------------                     ---------------
window.parent.postMessage()  ----->    Intercepts Submit       ----->       Executes Python Tool
                                       Sends HTTP POST                      (e.g., generate_qr)
IFrame Message Listener      <-----    Returns tool response   <-----       Returns JSON Dict
```

### 1. Sending an Action from inside the IFrame
When the user clicks a button inside your HTML page, post a message containing the tool name and payload arguments to the parent window:
```javascript
// Extract dynamic agent ID from window pathname
const pathParts = window.location.pathname.split('/');
const agentId = ((pathParts[2] === 'plugins' || pathParts[2] === 'agents') && pathParts[3]) ? pathParts[3] : 'my_agent';

window.parent.postMessage({
  type: 'SUBMIT_FORM',
  actionUrl: `agent://${agentId}/my_backend_tool`,
  payload: { param1: 'value1' }
}, '*');
```

### 2. Processing the Response
The parent Hubscape container captures this request, executes the corresponding Python tool script (e.g., `app/scripts/my_backend_tool.py`), and posts the tool's JSON output back to the iframe. Listen for this response in your HTML JavaScript:
```javascript
window.addEventListener('message', (event) => {
  const data = event.data;
  if (data && data.type === 'TOOL_RESPONSE') {
    console.log("Received data from Python script:", data.payload);
    // Update HTML DOM visually
  }
});
```

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
