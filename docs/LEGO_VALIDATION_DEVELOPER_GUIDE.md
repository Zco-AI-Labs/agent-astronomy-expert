# Agent Developer Guide: Lego UI Validation & Error Handling

## 🚀 Overview
The Hubscape Lego UI Widget System has been upgraded with a **Standardized Validation & Error Handling Protocol**. Agent developers no longer need ad-hoc workarounds for input validation or live-monitored task failures.

---

## ✨ What's New?

1. **Declarative Field Validation**: Validate email addresses, 10+ digit phone numbers (area code required), required fields, regex patterns, and numeric ranges.
2. **Interactive Triggers**:
   - `onBlur` (field exit): Instant red highlight & error text when leaving an invalid field.
   - `onSubmit` (button click): Full form sweep. Aborts post action and highlights failing fields if validation errors exist.
3. **Live Error Banners (`live-error-banner`)**: Standardized error alert cards for live-monitored tasks with expandable diagnostic logs and retry buttons.
4. **Python Type-Safe Builder (`lego_builder.py`)**: Pydantic models for Python agent tools.

---

## 🛠️ How to Use in JSON Templates

Add `required: true`, `validationType`, and `errorMessage` props to any `input` or `select` element:

### 📧 1. Email Field Validation
Validates RFC-5322 email formatting (`user@domain.ext`). Rejects incomplete emails on blur and submit.

```json
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
}
```

### 📞 2. Phone Number Validation (Area Code Required)
Validates that the telephone number contains at least 10 digits including area code. Rejects 7-digit local numbers.

```json
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
}
```

### 🚨 3. Live Error Banner Element (`live-error-banner`)
Renders an error card for live monitoring task failures with diagnostic expander logs and retry triggers.

```json
{
  "type": "live-error-banner",
  "props": {
    "title": "Live Monitoring Stream Interrupted",
    "message": "Connection to the external sensor array timed out.",
    "errorCode": "ERR_STREAM_TIMEOUT",
    "details": { "node_id": "sensor_04", "latency_ms": 30420, "attempt": 3 },
    "retryActionUrl": "agent://reconnect_sensor?node_id=sensor_04",
    "retryLabel": "Reconnect Sensor"
  }
}
```

---

## 🐍 How to Use in Python (`app/ui/lego_builder.py`)

Python agent developers can import `app.ui.lego_builder` to build validated widgets programmatically:

```python
from app.ui.lego_builder import create_input_widget, create_live_error_widget, LegoWidgetConfig

# 1. Create a validated Email Input
email_field = create_input_widget(
    name="email",
    label="Email Address",
    placeholder="officer@starfleet.org",
    input_type="email",
    required=True,
    validation_type="email",
    error_message="Please enter a valid email address."
)

# 2. Create a Live Error Banner
error_banner = create_live_error_widget(
    title="Sensor Connection Failed",
    message="Unable to establish streaming session.",
    error_code="ERR_SENSOR_OFFLINE",
    details={"sensor": "subspace_array_01"},
    retry_action_url="agent://retry_sensor"
)
```

---

## 📋 Catalog Summary of Validation Types

| `validationType` | Rule Description | Example Target |
|---|---|---|
| `"email"` | RFC-5322 Email Format (`@` + domain + TLD) | `user@domain.com` |
| `"phone"` / `"phone_us"` | 10+ Digit Phone Number (Area Code Required) | `(555) 019-2834` |
| `"pattern"` / `"regex"` | Regular Expression string matching | Custom regex in `pattern` |
| `"numeric"` | Number format with `min` and `max` constraints | Numbers |
| `"length"` | String length with `minLength` and `maxLength` | Passwords, codes |
