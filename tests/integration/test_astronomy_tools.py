import pytest

from app.scripts.get_astronomical_events import get_astronomical_events
from app.scripts.get_celestial_body_position import get_celestial_body_position
from app.scripts.get_stargazing_forecast import get_stargazing_forecast
from app.scripts.manage_stargazer_profile import manage_stargazer_profile


@pytest.mark.asyncio
async def test_manage_stargazer_profile_flow():
    # 1. Update location and optics
    set_res = await manage_stargazer_profile(action="set", location="Flagstaff, AZ", optics_tier="telescope")
    assert set_res["status"] == "success"
    assert "Flagstaff" in set_res["profile"]["city_name"]
    assert set_res["profile"]["optics_tier"] == "telescope"

    # 2. Retrieve profile
    get_res = await manage_stargazer_profile(action="get")
    assert get_res["status"] == "success"
    assert "Flagstaff" in get_res["profile"]["city_name"]


@pytest.mark.asyncio
async def test_get_stargazing_forecast_tool():
    forecast = await get_stargazing_forecast(location="Denver, CO", date="2026-09-11")
    assert forecast["status"] == "success"
    assert "stargazing_score" in forecast
    assert 0 <= forecast["stargazing_score"] <= 100
    assert "stargazing_rating" in forecast
    assert "weather" in forecast
    assert "moon" in forecast
    assert "visible_targets" in forecast
    assert "summary" in forecast


@pytest.mark.asyncio
async def test_get_celestial_body_position_tool():
    mars = await get_celestial_body_position(target="Mars", location="Flagstaff, AZ")
    assert mars["status"] == "success"
    assert mars["target_name"] == "Mars"
    assert "altitude_degrees" in mars
    assert "cardinal_direction" in mars
    assert "constellation" in mars
    assert "optical_aid_required" in mars
    assert "pointing_instructions" in mars


@pytest.mark.asyncio
async def test_get_celestial_body_position_with_date_time():
    jupiter = await get_celestial_body_position(
        target="Jupiter", location="Flagstaff, AZ", date="2026-09-15", time="23:30"
    )
    assert jupiter["status"] == "success"
    assert "Jupiter" in jupiter["target_name"]
    assert "2026-09-15 23:30" in jupiter["observation_time_utc"]


@pytest.mark.asyncio
async def test_iss_tracking_tool():
    iss = await get_celestial_body_position(target="ISS")
    assert iss["status"] == "success"
    assert "International Space Station" in iss["target_name"]
    assert "altitude_km" in iss
    assert "velocity_km_h" in iss


@pytest.mark.asyncio
async def test_get_astronomical_events_tool():
    events = await get_astronomical_events(event_type="all", days_ahead=30)
    assert events["status"] == "success"
    assert "current_moon_status" in events
    assert "active_meteor_showers" in events
    assert "upcoming_events" in events
    assert "viewing_tips" in events

