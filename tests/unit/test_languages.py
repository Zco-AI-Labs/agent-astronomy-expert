import pytest
from app.core.hubscape_adk import RemoteContext, context_session
import app.core.hubscape_adk as hubscape_adk
from app.core.load_local_tools import load_local_tools


def test_remote_context_get_supported_languages_all():
    ctx = RemoteContext(user_id="test_user", agent_id="test_agent")
    langs = ctx.get_supported_languages()
    assert len(langs) == 57
    codes = {l["code"] for l in langs}
    assert "client" in codes
    assert "en" in codes
    assert "es" in codes
    assert "is" in codes


def test_remote_context_get_supported_languages_voice():
    ctx = RemoteContext(user_id="test_user", agent_id="test_agent")
    voice_langs = ctx.get_supported_languages(capability="voice")
    # 1 client auto-detect + 30 voice-ready languages = 31
    assert len(voice_langs) == 31
    for lang in voice_langs:
        assert lang["voice_supported"] is True

    codes = {l["code"] for l in voice_langs}
    assert "en" in codes
    assert "es" in codes
    assert "ja" in codes
    # Text-only languages should not be included
    assert "is" not in codes
    assert "tl" not in codes
    assert "ur" not in codes


def test_remote_context_get_language():
    ctx = RemoteContext(user_id="test_user", agent_id="test_agent")
    
    # Test valid voice language
    en = ctx.get_language("en")
    assert en is not None
    assert en["code"] == "en"
    assert en["name"] == "English"
    assert en["voice_supported"] is True

    # Test valid text-only language
    icelandic = ctx.get_language("is")
    assert icelandic is not None
    assert icelandic["code"] == "is"
    assert icelandic["name"] == "Icelandic"
    assert icelandic["voice_supported"] is False

    # Test case insensitivity and whitespace trimming
    es = ctx.get_language("  ES  ")
    assert es is not None
    assert es["code"] == "es"
    assert es["name"] == "Spanish"

    # Test invalid / empty code
    assert ctx.get_language("nonexistent_language_code") is None
    assert ctx.get_language("") is None
    assert ctx.get_language(None) is None


def test_module_level_helpers_with_and_without_session():
    # Outside context session
    all_langs = hubscape_adk.get_supported_languages()
    assert len(all_langs) == 57
    voice_langs = hubscape_adk.get_supported_languages(capability="voice")
    assert len(voice_langs) == 31
    assert hubscape_adk.get_language("fr")["name"] == "French"

    # Inside context session
    ctx = RemoteContext(user_id="session_user", agent_id="session_agent")
    with context_session(ctx):
        assert len(hubscape_adk.get_supported_languages()) == 57
        assert len(hubscape_adk.get_supported_languages(capability="voice")) == 31
        assert hubscape_adk.get_language("de")["name"] == "German"


def test_no_system_tool_registered_for_languages():
    """Verify that language discovery was NOT registered as an agent system tool."""
    import os
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "app"))
    system_tools_dir = os.path.join(app_dir, "core", "system_tools")
    scripts_dir = os.path.join(app_dir, "scripts")
    tools = load_local_tools(system_tools_dir) + load_local_tools(scripts_dir)
    tool_names = [getattr(t, "__name__", str(t)) for t in tools]
    assert "get_supported_languages" not in tool_names
    assert "get_language" not in tool_names

