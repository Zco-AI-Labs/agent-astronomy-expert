import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent

def test_astronomy_expert_stargazing_flow():
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="captain_raj", app_name="astronomy_test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="astronomy_test")

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text="What will I be able to see in the night sky tonight in Denver?")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="captain_raj",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events) > 0

    full_text = ""
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_text += part.text

    assert len(full_text) > 0
    # Verify the response mentions key stargazing elements
    lower_text = full_text.lower()
    assert any(term in lower_text for term in ["moon", "mars", "sky", "cloud", "denver", "stargaz"])
