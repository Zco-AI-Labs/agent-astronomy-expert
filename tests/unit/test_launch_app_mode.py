import pytest
from app.core.hubscape_adk import RemoteContext

def test_launch_app_mode_payload():
    ctx = RemoteContext(user_id="user_123", agent_id="flight_agent")
    
    canvas_widget = {
        "widgetId": "flight_map",
        "widgetConfig": {
            "type": "container",
            "children": [{"type": "text", "text": "Live Map"}]
        },
        "data": {"flightId": "UA101"}
    }
    
    remote_widget = {
        "widgetId": "flight_controls",
        "widgetConfig": {
            "type": "container",
            "children": [{"type": "button", "label": "Reroute"}]
        }
    }
    
    actions = [
        {
            "id": "save_route",
            "label": "Save Route",
            "icon": "Save",
            "actionType": "api_call",
            "endpoint": "/api/flights/save",
            "showFeedback": True
        }
    ]
    
    res = ctx.launch_app_mode(
        app_id="flight_tracker",
        canvas_widget=canvas_widget,
        remote_widget=remote_widget,
        title="Tactical Flight Tracker",
        icon="Command",
        actions=actions
    )
    
    assert res["status"] == "success"
    assert res["directive"] == "execute_host_tool"
    assert res["target_tool"] == "openAgentWidget"
    assert res["parameters"]["target"] == "app_mode"
    assert res["parameters"]["widgetId"] == "flight_tracker"
    
    app_config = res["parameters"]["appConfig"]
    assert app_config["appId"] == "flight_tracker"
    assert app_config["title"] == "Tactical Flight Tracker"
    assert app_config["icon"] == "Command"
    assert app_config["canvasWidget"] == canvas_widget
    assert app_config["remoteWidget"] == remote_widget
    assert app_config["actions"] == actions
    
    # Check registered action
    assert len(ctx.actions) == 1
    assert ctx.actions[0]["type"] == "OPEN_AGENT_WIDGET"
    assert ctx.actions[0]["payload"]["target"] == "app_mode"
    assert ctx.actions[0]["payload"]["appConfig"] == app_config

def test_launch_app_mode_optional_fields():
    ctx = RemoteContext(user_id="user_456")
    
    canvas_widget = {"widgetConfig": {"type": "iframe", "src": "/embed/dashboard"}}
    
    res = ctx.launch_app_mode(
        app_id="minimal_app",
        canvas_widget=canvas_widget
    )
    
    app_config = res["parameters"]["appConfig"]
    assert app_config["appId"] == "minimal_app"
    assert "remoteWidget" not in app_config
    assert "title" not in app_config
    assert "icon" not in app_config
    assert "actions" not in app_config
    assert app_config["canvasWidget"] == canvas_widget
