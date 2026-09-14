import pytest

from app.core.hubscape_adk import RemoteContext, context_session
from app.scripts._weather_utils import (
    geocode_location,
    get_weather_forecast,
    resolve_observing_location,
)


@pytest.mark.asyncio
async def test_geocode_coordinates_input():
    # Pass explicit lat,lon string
    result = await geocode_location("35.1983, -111.6513")
    assert result is not None
    assert abs(result["latitude"] - 35.1983) < 0.001
    assert abs(result["longitude"] - (-111.6513)) < 0.001


@pytest.mark.asyncio
async def test_geocode_empty_returns_none():
    # Empty string should return None (no silent Denver fallback)
    result = await geocode_location("")
    assert result is None


@pytest.mark.asyncio
async def test_get_weather_forecast_structure():
    # Calling with known coordinates
    weather = await get_weather_forecast(39.7392, -104.9903)
    assert weather.get("is_available") is True
    assert "cloud_cover" in weather
    assert "seeing_quality" in weather
    assert "temperature_f" in weather
    assert "precipitation_probability" in weather
    assert "sunset_time" in weather
    assert "moonrise_time" in weather
    assert "moonset_time" in weather
    assert "moon_phase_fraction" in weather
    assert isinstance(weather["cloud_cover"], int)
    assert 0 <= weather["cloud_cover"] <= 100


@pytest.mark.asyncio
async def test_resolve_observing_location_remote_context_coords():
    # Verify that RemoteContext user_location coordinates are automatically used when location_query is None
    ctx = RemoteContext(
        user_id="test_user_rc",
        raw_context={
            "user_location": {
                "latitude": 42.3601,
                "longitude": -71.0589,
                "city": "Boston, MA",
            }
        },
    )
    with context_session(ctx):
        resolved = await resolve_observing_location(None)
        assert resolved is not None
        assert resolved["source"] == "remote_context"
        assert abs(resolved["latitude"] - 42.3601) < 0.001
        assert abs(resolved["longitude"] - (-71.0589)) < 0.001
        assert "Boston" in resolved["name"]


@pytest.mark.asyncio
async def test_resolve_observing_location_user_override():
    # User explicitly queries Tokyo, even though RemoteContext is set to Boston
    ctx = RemoteContext(
        user_id="test_user_rc",
        raw_context={
            "user_location": {
                "latitude": 42.3601,
                "longitude": -71.0589,
                "city": "Boston, MA",
            }
        },
    )
    with context_session(ctx):
        resolved = await resolve_observing_location("Tokyo, Japan")
        assert resolved is not None
        assert resolved["source"] == "user_argument"
        assert "Tokyo" in resolved["name"]
        # Tokyo is approx 35.68 N, 139.69 E
        assert abs(resolved["latitude"] - 35.68) < 1.0


@pytest.mark.asyncio
async def test_resolve_observing_location_direct_ctx_attribute():
    # Verify that when ctx has user_location directly as an attribute (as in Hubscape ADK Studio / HubscapeContext)
    ctx = RemoteContext(
        user_id="test_user_rc",
        raw_context={},
    )
    # Simulate HubscapeContext attribute
    ctx.user_location = {
        "label": "Boston, MA",
        "latitude": 42.3601,
        "longitude": -71.0589,
    }
    with context_session(ctx):
        resolved = await resolve_observing_location(None)
        assert resolved is not None
        assert resolved["source"] == "remote_context"
        assert resolved["name"] == "Boston, MA"
        assert abs(resolved["latitude"] - 42.3601) < 0.001
        assert abs(resolved["longitude"] - (-71.0589)) < 0.001



