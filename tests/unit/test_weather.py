import pytest

from app.scripts._weather_utils import geocode_location, get_weather_forecast


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

