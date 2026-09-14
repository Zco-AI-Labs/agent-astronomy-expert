import datetime
import pytest

from app.scripts._ephemeris_utils import (
    compute_horizontal_coords,
    compute_stargazing_index,
    degrees_to_cardinal,
    get_active_meteor_showers,
    get_constellation_from_coords,
    get_moon_ephemeris,
    get_planet_coordinates,
    get_target_ephemeris,
)


def test_moon_ephemeris():
    dt = datetime.datetime(2026, 9, 11, 22, 0, tzinfo=datetime.UTC)
    moon = get_moon_ephemeris(dt, moon_phase_fraction=0.10, moonset_str="20:30")
    assert "phase_name" in moon
    assert 0 <= moon["illumination_percent"] <= 100
    assert "moonset_time" in moon
    assert "interference_level" in moon
    assert "dark_sky_window" in moon


def test_cardinal_directions():
    assert degrees_to_cardinal(0) == "North"
    assert degrees_to_cardinal(90) == "East"
    assert degrees_to_cardinal(180) == "South"
    assert degrees_to_cardinal(270) == "West"
    assert degrees_to_cardinal(135) == "Southeast"
    assert degrees_to_cardinal(45) == "Northeast"


def test_constellation_from_coords():
    # Orion: RA ~5.6h, Dec ~ -5°
    const = get_constellation_from_coords(5.6, -5.0)
    assert const == "Orion"

    # Ursa Major: RA ~11h, Dec ~ 50°
    const_um = get_constellation_from_coords(11.0, 50.0)
    assert const_um == "Ursa Major"


def test_compute_horizontal_coords():
    dt = datetime.datetime(2026, 9, 11, 22, 0, tzinfo=datetime.UTC)
    alt, az, cardinal = compute_horizontal_coords(ra_hours=18.0, dec_deg=35.0, lat_deg=35.0, lon_deg=-111.0, dt=dt)
    assert -90.0 <= alt <= 90.0
    assert 0.0 <= az <= 360.0
    assert isinstance(cardinal, str)


@pytest.mark.asyncio
async def test_planet_coordinates():
    dt = datetime.datetime(2026, 9, 11, 22, 0, tzinfo=datetime.UTC)
    for planet in ["mars", "jupiter", "saturn", "venus"]:
        ra, dec, mag, const = await get_planet_coordinates(planet, dt)
        assert 0.0 <= ra < 24.0
        assert -90.0 <= dec <= 90.0
        assert isinstance(mag, float)
        assert isinstance(const, str)


@pytest.mark.asyncio
async def test_target_ephemeris_planet_and_deep_sky():
    dt = datetime.datetime(2026, 9, 11, 22, 0, tzinfo=datetime.UTC)
    mars = await get_target_ephemeris("Mars", 39.7392, -104.9903, dt)
    assert mars["target_name"] == "Mars"
    assert "is_visible_now" in mars
    assert "altitude_degrees" in mars
    assert "cardinal_direction" in mars

    pleiades = await get_target_ephemeris("Pleiades", 39.7392, -104.9903, dt)
    assert "Pleiades" in pleiades["target_name"]
    assert "altitude_degrees" in pleiades


def test_compute_stargazing_index():
    # Pristine clear sky: 0% clouds, 0% moon, excellent seeing -> High score >= 80
    score_high, label_high = compute_stargazing_index(cloud_cover=0, moon_illumination=0, seeing_quality="Excellent")
    assert score_high >= 80
    assert "Excellent" in label_high

    # Terrible overcast sky: 100% clouds, 100% moon, poor seeing -> Low score < 40
    score_low, label_low = compute_stargazing_index(cloud_cover=100, moon_illumination=100, seeing_quality="Poor")
    assert score_low <= 40
    assert "Poor" in label_low


def test_active_meteor_showers():
    dt = datetime.datetime(2026, 8, 12, 23, 0, tzinfo=datetime.UTC)
    showers = get_active_meteor_showers(dt)
    assert len(showers) > 0
    names = [s["name"] for s in showers]
    assert any("Perseids" in n for n in names)

