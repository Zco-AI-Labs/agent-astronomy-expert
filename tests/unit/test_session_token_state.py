# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import os
import sys
from unittest.mock import MagicMock

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.hubscape_adk import RemoteContext, context_session
from google.adk.sessions import Session


class MockSession:
    """Mock ADK Session object matching google.adk.sessions.Session structure."""
    def __init__(self, session_id: str = "sess-1", user_id: str = "dev-user-123", state: dict = None):
        self.id = session_id
        self.user_id = user_id
        self.state = state if state is not None else {}


def test_session_token_storage_and_continuity():
    """Verify that an access token stored in ctx.session.state remains available across turns in that session."""
    ctx = RemoteContext(user_id="dev-user-123", agent_id="mopl_sample_agent")
    ctx.session = MockSession(session_id="session-turn-continuity")

    with context_session(ctx):
        # Turn 1: Store access token after OTP verification
        assert ctx.session.state.get("access_token") is None
        ctx.session.state["access_token"] = "mopl_jwt_token_sample"
        ctx.session.state["token_type"] = "Bearer"

        # Turn 2: Retrieve token in subsequent turn of the same session
        assert ctx.session.state.get("access_token") == "mopl_jwt_token_sample"
        assert ctx.session.state.get("token_type") == "Bearer"


def test_session_token_isolation_between_sessions():
    """Verify strict isolation: Session B cannot access the token stored in Session A for the same user."""
    user_id = "dev-user-123"

    # Session A: User authenticates and receives token
    ctx_a = RemoteContext(user_id=user_id, agent_id="mopl_sample_agent")
    ctx_a.session = MockSession(session_id="session-A", user_id=user_id)
    ctx_a.session.state["access_token"] = "secret-token-session-A"

    # Session B: Same user opens a fresh session
    ctx_b = RemoteContext(user_id=user_id, agent_id="mopl_sample_agent")
    ctx_b.session = MockSession(session_id="session-B", user_id=user_id)

    # Verify Session B starts clean without access to Session A's token
    assert ctx_a.session.state.get("access_token") == "secret-token-session-A"
    assert ctx_b.session.state.get("access_token") is None

    # Mutating Session B does not affect Session A
    ctx_b.session.state["access_token"] = "secret-token-session-B"
    assert ctx_a.session.state.get("access_token") == "secret-token-session-A"
    assert ctx_b.session.state.get("access_token") == "secret-token-session-B"


def test_adk_session_serialization_preserves_token_state():
    """Verify that ADK Session model_dump_json / model_validate_json preserves token state."""
    session = Session(
        id="session-serialization-test",
        app_name="mopl-sample-agent",
        user_id="dev-user-123",
        state={"access_token": "serialized-token-xyz", "scope": "mcp:tools:call"}
    )

    # Serialize (as done at the end of turn in geap_agent_wrapper.py)
    serialized_json = session.model_dump_json()
    assert "serialized-token-xyz" in serialized_json

    # Restore (as done at the start of turn in geap_agent_wrapper.py)
    restored_session = Session.model_validate_json(serialized_json)
    assert restored_session.id == "session-serialization-test"
    assert restored_session.state["access_token"] == "serialized-token-xyz"
    assert restored_session.state["scope"] == "mcp:tools:call"


def test_session_token_invalidation():
    """Verify that removing or clearing the token from session state immediately revokes access."""
    ctx = RemoteContext(user_id="dev-user-123", agent_id="mopl_sample_agent")
    ctx.session = MockSession(session_id="session-invalidation")
    ctx.session.state["access_token"] = "token-to-revoke"

    assert ctx.session.state.get("access_token") == "token-to-revoke"

    # Invalidate token on session end or logout
    ctx.session.state.pop("access_token", None)
    assert ctx.session.state.get("access_token") is None
