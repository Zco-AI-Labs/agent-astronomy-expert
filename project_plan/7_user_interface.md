## 🎨 7. User Interface & Widgets Specification

Defines the complete Lego block UI templates used by the Astronomy Expert agent. All widgets are stored in `app/ui/widgets/` and rendered via the Hubscape ADK Generative UI engine.

---

### Widget 1: `night_sky_forecast`
*   **Purpose:** Comprehensive dashboard card displaying the nightly stargazing index, cloud cover, moon phase, and visible planetary targets.
*   **Theme Token Default:** `indigo`
*   **File Path:** `app/ui/widgets/night_sky_forecast.json`

```json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-4 p-5 bg-slate-900 border border-indigo-500/30 rounded-2xl shadow-xl text-slate-100 max-w-md w-full"
  },
  "children": [
    {
      "type": "container",
      "props": {
        "className": "flex items-center justify-between border-b border-slate-800 pb-3"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "flex items-center gap-2"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "✨ Tonight's Night Sky Forecast",
                "className": "text-base font-bold text-indigo-300"
              }
            }
          ]
        },
        {
          "type": "text",
          "props": {
            "text": "{{location_name}}",
            "className": "text-xs font-medium text-slate-400"
          }
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "flex items-center justify-between p-3.5 bg-indigo-950/40 rounded-xl border border-indigo-500/20"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Stargazing Index",
                "className": "text-xs text-slate-400 font-medium"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{stargazing_rating}} ({{stargazing_score}}/100)",
                "className": "text-lg font-bold text-emerald-400"
              }
            }
          ]
        },
        {
          "type": "text",
          "props": {
            "text": "☁️ {{cloud_cover}}% Clouds",
            "className": "text-xs font-semibold px-2.5 py-1 bg-slate-800 rounded-full text-slate-300"
          }
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "grid grid-cols-2 gap-2"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "🌙 Moon Phase",
                "className": "text-xs text-slate-400"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{moon_phase}} ({{moon_illumination}}%)",
                "className": "text-sm font-semibold text-slate-200 mt-0.5"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "Sets: {{moon_set_time}}",
                "className": "text-xs text-slate-400 mt-1"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "🔭 Prime Window",
                "className": "text-xs text-slate-400"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{prime_window}}",
                "className": "text-sm font-semibold text-amber-300 mt-0.5"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "Seeing: {{seeing_quality}}",
                "className": "text-xs text-slate-400 mt-1"
              }
            }
          ]
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "flex flex-col gap-1.5"
      },
      "children": [
        {
          "type": "text",
          "props": {
            "text": "Top Visible Objects Tonight:",
            "className": "text-xs font-semibold text-slate-400 uppercase tracking-wider"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "{{visible_targets_summary}}",
            "className": "text-sm text-slate-200 leading-relaxed p-2.5 bg-slate-800/40 rounded-lg border border-slate-800"
          }
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "flex items-center gap-2 pt-1"
      },
      "children": [
        {
          "type": "button",
          "props": {
            "label": "Track Mars",
            "actionUrl": "agent://astronomy_expert/get_celestial_body_position?target=Mars",
            "styling": {
              "colorTheme": "indigo"
            },
            "closeOnClick": false,
            "submittedLabel": "Target Selected",
            "className": "flex-1 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
          }
        },
        {
          "type": "button",
          "props": {
            "label": "Upcoming Events",
            "actionUrl": "agent://astronomy_expert/get_astronomical_events",
            "styling": {
              "colorTheme": "slate"
            },
            "closeOnClick": false,
            "submittedLabel": "Events Loaded",
            "className": "flex-1 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          }
        }
      ]
    }
  ]
}
```

---

### Widget 2: `celestial_target_card`
*   **Purpose:** Detailed orientation and coordinates card for locating a specific planet or deep-sky object.
*   **Theme Token Default:** `violet`
*   **File Path:** `app/ui/widgets/celestial_target_card.json`

```json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-3 p-4 bg-slate-900 border border-violet-500/30 rounded-xl shadow-lg text-slate-100 max-w-sm w-full"
  },
  "children": [
    {
      "type": "container",
      "props": {
        "className": "flex items-center justify-between border-b border-slate-800 pb-2"
      },
      "children": [
        {
          "type": "text",
          "props": {
            "text": "🪐 {{target_name}}",
            "className": "text-base font-bold text-violet-300"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "{{visibility_status}}",
            "className": "text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/30"
          }
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "grid grid-cols-2 gap-2"
      },
      "children": [
        {
          "type": "container",
          "props": {
            "className": "p-2.5 bg-slate-800/50 rounded-lg flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Direction",
                "className": "text-xs text-slate-400"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{cardinal_direction}} ({{azimuth_degrees}}°)",
                "className": "text-sm font-semibold text-slate-100"
              }
            }
          ]
        },
        {
          "type": "container",
          "props": {
            "className": "p-2.5 bg-slate-800/50 rounded-lg flex flex-col"
          },
          "children": [
            {
              "type": "text",
              "props": {
                "text": "Altitude Angle",
                "className": "text-xs text-slate-400"
              }
            },
            {
              "type": "text",
              "props": {
                "text": "{{altitude_degrees}}° Above Horizon",
                "className": "text-sm font-semibold text-slate-100"
              }
            }
          ]
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "flex items-center justify-between text-xs text-slate-300 p-2 bg-slate-800/30 rounded-lg"
      },
      "children": [
        {
          "type": "text",
          "props": {
            "text": "Constellation: {{constellation}}",
            "className": "font-medium"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "Optics: {{optical_aid_required}}",
            "className": "font-medium text-amber-300"
          }
        }
      ]
    },
    {
      "type": "button",
      "props": {
        "label": "Close",
        "actionUrl": "client://close_widget",
        "closeOnClick": true,
        "submittedLabel": "Dismissed",
        "className": "w-full py-1.5 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
      }
    }
  ]
}
```

---

### Widget 3: `stargazer_profile_card`
*   **Purpose:** Profile management card displaying saved coordinates and observing optics tier.
*   **Theme Token Default:** `emerald`
*   **File Path:** `app/ui/widgets/stargazer_profile_card.json`

```json
{
  "type": "container",
  "props": {
    "className": "flex flex-col gap-3 p-4 bg-slate-900 border border-emerald-500/30 rounded-xl shadow-lg text-slate-100 max-w-sm w-full"
  },
  "children": [
    {
      "type": "container",
      "props": {
        "className": "flex items-center justify-between border-b border-slate-800 pb-2"
      },
      "children": [
        {
          "type": "text",
          "props": {
            "text": "🔭 Stargazer Profile",
            "className": "text-base font-bold text-emerald-300"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "Saved",
            "className": "text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300"
          }
        }
      ]
    },
    {
      "type": "container",
      "props": {
        "className": "flex flex-col gap-1.5 text-xs text-slate-300"
      },
      "children": [
        {
          "type": "text",
          "props": {
            "text": "📍 Location: {{city_name}} ({{latitude}}°, {{longitude}}°)",
            "className": "font-medium"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "🔍 Observing Gear: {{optics_tier_label}}",
            "className": "font-medium"
          }
        },
        {
          "type": "text",
          "props": {
            "text": "🌌 Dark-Sky Rating: {{dark_sky_desc}}",
            "className": "text-slate-400"
          }
        }
      ]
    },
    {
      "type": "button",
      "props": {
        "label": "Update Location",
        "actionUrl": "agent://astronomy_expert/manage_stargazer_profile?action=set",
        "styling": {
          "colorTheme": "emerald"
        },
        "closeOnClick": false,
        "submittedLabel": "Settings Opened",
        "className": "w-full py-1.5 text-xs font-semibold rounded bg-emerald-700 hover:bg-emerald-600 text-white transition-colors"
      }
    }
  ]
}
```
