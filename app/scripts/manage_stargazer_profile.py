import logging
from typing import Any

import app.core.hubscape_adk
from app.scripts._weather_utils import geocode_location

logger = logging.getLogger(__name__)

import logging
from typing import Any

import app.core.hubscape_adk
from app.scripts._weather_utils import geocode_location

logger = logging.getLogger(__name__)

# In-memory fallback for local development or testing without cloud Firestore (starts empty)
_LOCAL_FALLBACK_PROFILE: dict[str, Any] = {}


@app.core.hubscape_adk.require_tool_privilege
async def manage_stargazer_profile(
    action: str = "get",
    location: str | None = None,
    optics_tier: str | None = None,
) -> dict[str, Any]:
    """
    Manages the user's personal observing profile in user-scoped storage,
    including primary observing location, geocoordinates, and optics equipment tier.
    Automatically displays the 'stargazer_profile_card' Generative UI widget when profile is configured.

    Args:
        action: Operation to perform ('get' to retrieve existing profile, 'set' to update).
        location: City name (e.g., 'Flagstaff, AZ', 'Boston, MA'), zip code, or 'lat,lon' coordinates.
        optics_tier: Observing gear ('naked_eye', 'binoculars', 'telescope').

    Returns:
        A dictionary containing the profile status, coordinates, optics, and rendered widget metadata.
    """
    global _LOCAL_FALLBACK_PROFILE
    ctx = None

    try:
        ctx = app.core.hubscape_adk.get_context()
    except Exception:
        pass

    profile = _LOCAL_FALLBACK_PROFILE.copy()

    # Attempt to load from user-scoped Firestore
    if ctx is not None:
        try:
            saved_doc = ctx.get("user", "stargazer_profiles", "preferences")
            if saved_doc and isinstance(saved_doc, dict):
                profile.update(saved_doc)
        except Exception as e:
            logger.debug(f"Could not load profile from Firestore: {e}. Using local cache.")

    if action.lower() == "set":
        if location:
            geo = await geocode_location(location)
            if not geo:
                return {
                    "status": "error",
                    "action": "set",
                    "message": f"Could not resolve geographical coordinates for '{location}'. Please check the spelling or provide 'lat,lon' decimal coordinates.",
                }
            profile["city_name"] = geo["name"]
            profile["latitude"] = geo["latitude"]
            profile["longitude"] = geo["longitude"]
            profile["timezone"] = geo.get("timezone", "auto")

        if optics_tier:
            tier_clean = optics_tier.lower().replace(" ", "_")
            if "telescope" in tier_clean:
                profile["optics_tier"] = "telescope"
                profile["optics_tier_label"] = "Telescope (Deep Sky & High Magnification)"
            elif "binocular" in tier_clean:
                profile["optics_tier"] = "binoculars"
                profile["optics_tier_label"] = "Binoculars (Wide Field & Clusters)"
            else:
                profile["optics_tier"] = "naked_eye"
                profile["optics_tier_label"] = "Naked Eye"
        elif "optics_tier" not in profile:
            profile["optics_tier"] = "naked_eye"
            profile["optics_tier_label"] = "Naked Eye"

        if "dark_sky_desc" not in profile:
            profile["dark_sky_desc"] = "Observing Site Configured"

        _LOCAL_FALLBACK_PROFILE.update(profile)

        # Persist to user-scoped Firestore if client available
        if ctx is not None:
            try:
                ctx.save("user", "stargazer_profiles", "preferences", profile)
            except Exception as e:
                logger.debug(f"Could not save profile to Firestore: {e}")

        # Prepare widget template data
        widget_data = {
            "city_name": profile.get("city_name", "Observing Site"),
            "latitude": f"{profile.get('latitude', 0.0):.2f}",
            "longitude": f"{profile.get('longitude', 0.0):.2f}",
            "optics_tier_label": profile.get("optics_tier_label", "Naked Eye"),
            "dark_sky_desc": profile.get("dark_sky_desc", "Observing Site"),
        }
        for k, v in list(widget_data.items()):
            widget_data[f"data.{k}"] = v

        if ctx is not None:
            try:
                ctx.show_widget("stargazer_profile_card", widget_data)
            except Exception as e:
                logger.debug(f"Could not render profile widget: {e}")

        return {
            "status": "success",
            "action": "set",
            "profile": profile,
            "message": f"Observing location is set to {profile.get('city_name')} (Optics: {profile.get('optics_tier_label')}).",
        }

    # Action is 'get'
    if not profile or not profile.get("city_name"):
        return {
            "status": "not_set",
            "action": "get",
            "profile": None,
            "message": "No observing location has been saved to your profile yet. Please provide your city or coordinates.",
        }

    widget_data = {
        "city_name": profile.get("city_name", "Observing Site"),
        "latitude": f"{profile.get('latitude', 0.0):.2f}",
        "longitude": f"{profile.get('longitude', 0.0):.2f}",
        "optics_tier_label": profile.get("optics_tier_label", "Naked Eye"),
        "dark_sky_desc": profile.get("dark_sky_desc", "Observing Site"),
    }
    for k, v in list(widget_data.items()):
        widget_data[f"data.{k}"] = v

    if ctx is not None:
        try:
            ctx.show_widget("stargazer_profile_card", widget_data)
        except Exception as e:
            logger.debug(f"Could not render profile widget: {e}")

    return {
        "status": "success",
        "action": "get",
        "profile": profile,
        "message": f"Observing location is set to {profile.get('city_name')} (Optics: {profile.get('optics_tier_label')}).",
    }
