import pytest
import asyncio
from unittest.mock import MagicMock
from app.core import hubscape_adk

class DummySession:
    def __init__(self, state=None):
        self.state = state or {}

@pytest.mark.asyncio
async def test_require_oauth_async_authenticated():
    context = hubscape_adk.RemoteContext(
        user_id="user-123",
        agent_id="custom-agent",
        hub_id="hub-456"
    )
    context.session = DummySession(state={"tokens": {"mopl": {"access_token": "valid_token_123"}}})

    executed = False

    @hubscape_adk.require_oauth("mopl")
    async def sample_tool():
        nonlocal executed
        executed = True
        return {"status": "success", "data": "widget_rendered"}

    with hubscape_adk.context_session(context):
        result = await sample_tool()
        assert executed is True
        assert result == {"status": "success", "data": "widget_rendered"}
        assert len(context.actions) == 0

@pytest.mark.asyncio
async def test_require_oauth_async_unauthenticated():
    context = hubscape_adk.RemoteContext(
        user_id="user-123",
        agent_id="custom-agent",
        hub_id="hub-456"
    )
    # Empty session tokens
    context.session = DummySession(state={"tokens": {}})

    executed = False

    @hubscape_adk.require_oauth("mopl")
    async def sample_tool():
        nonlocal executed
        executed = True
        return {"status": "success", "data": "widget_rendered"}

    with hubscape_adk.context_session(context):
        result = await sample_tool()
        # Execution of the tool body must be blocked
        assert executed is False
        # Must return the oauth challenge
        assert result.get("status") == "error"
        assert result.get("error_type") == "AUTH_REQUIRED"
        assert result.get("system_action", {}).get("type") == "TRIGGER_OAUTH"
        # Must register the TRIGGER_OAUTH action in context.actions
        assert len(context.actions) == 1
        assert context.actions[0]["type"] == "TRIGGER_OAUTH"
        assert context.actions[0]["payload"]["provider"] == "mopl"

def test_require_oauth_sync_authenticated():
    context = hubscape_adk.RemoteContext(
        user_id="user-123",
        agent_id="custom-agent",
        hub_id="hub-456"
    )
    context.session = DummySession(state={"tokens": {"github": {"access_token": "gh_valid_token"}}})

    executed = False

    @hubscape_adk.require_oauth("github")
    def sync_sample_tool():
        nonlocal executed
        executed = True
        return {"status": "success", "message": "Done"}

    with hubscape_adk.context_session(context):
        result = sync_sample_tool()
        assert executed is True
        assert result["status"] == "success"
        assert len(context.actions) == 0

def test_require_oauth_sync_unauthenticated():
    context = hubscape_adk.RemoteContext(
        user_id="user-123",
        agent_id="custom-agent",
        hub_id="hub-456"
    )
    context.session = DummySession(state={"tokens": {}})

    executed = False

    @hubscape_adk.require_oauth("github")
    def sync_sample_tool():
        nonlocal executed
        executed = True
        return {"status": "success", "message": "Done"}

    with hubscape_adk.context_session(context):
        result = sync_sample_tool()
        assert executed is False
        assert result.get("status") == "error"
        assert result.get("error_type") == "AUTH_REQUIRED"
        assert len(context.actions) == 1
        assert context.actions[0]["type"] == "TRIGGER_OAUTH"
        assert context.actions[0]["payload"]["provider"] == "github"

@pytest.mark.asyncio
async def test_require_oauth_sync_inside_running_event_loop():
    """Verifies that a sync tool executes safely when called from an existing running event loop."""
    context = hubscape_adk.RemoteContext(
        user_id="user-123",
        agent_id="custom-agent",
        hub_id="hub-456"
    )
    context.session = DummySession(state={"tokens": {"mopl": {"access_token": "token_inside_loop"}}})

    executed = False

    @hubscape_adk.require_oauth("mopl")
    def sync_tool_called_in_async_context():
        nonlocal executed
        executed = True
        return {"status": "success"}

    with hubscape_adk.context_session(context):
        # We are inside an async test function (running loop active)
        result = sync_tool_called_in_async_context()
        assert executed is True
        assert result == {"status": "success"}
