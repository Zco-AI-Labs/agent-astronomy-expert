# Backend Rules: Custom Agent Coding Standards

> [!NOTE]
> These guidelines ensure that agent logic behaves predictably and integrates safely with the Hubscape host platform under the google-adk declarative structure.

## 1. Serving Architecture & Unified HTTP Server
* **Unified Serving Lifecycle:** Hubscape agents run a unified FastAPI-based HTTP server booted from [`app/core/fast_api_app.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/fast_api_app.py), which exposes REST, A2A, and Vertex AI Reasoning Engine interfaces simultaneously.
* **No Custom Endpoint Router (`api.py` Decommissioned):** Although the runtime runs a FastAPI server, developers are strictly forbidden from placing custom FastAPI router files (like `api.py`) or manually modifying endpoints inside their custom agent logic in [`app/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app). Custom logic must be implemented solely as Python tool scripts inside [`app/scripts/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/scripts).
* **Static Assets Directory:** All static assets (HTML visual composer pages, CSS, images) must be placed in the [`app/static/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/static) folder. The platform automatically mounts this directory to `/api/agents/{agent_id}/static/`.
* **Visual IFrame Communication:** Custom frontend iframe UIs must communicate with the backend using HTML5 standard `postMessage` protocol directed at the parent window:
  ```javascript
  window.parent.postMessage({
    type: 'SUBMIT_FORM',
    actionUrl: 'agent://{tool_function_name}',
    payload: { key: value }
  }, '*');
  ```
  The platform intercepts this message, executes the corresponding Python tool script (e.g. `app/scripts/{tool_function_name}.py`) inside the agent container, and returns the response. Do not make direct HTTP calls to the agent backend from inside the iframe.

## 2. Tools & Prompts Implementation
* **Tools in `scripts/`:** Define all custom tools as standalone Python files inside the [`app/scripts/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/scripts) directory (e.g. `app/scripts/my_tool.py`). The function name inside the script must match the filename. The ADK automatically parses their signatures, docstrings, and type hints to build Gemini tool schemas.
* **Tool Registration:** Import and load these tools dynamically in [`app/agent.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/agent.py) using the [`load_local_tools()`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/load_local_tools.py) utility helper.
* **System Prompts in `SKILL.md`:** Define the agent's instructions (prompts) inside [`app/SKILL.md`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/SKILL.md). The ADK parses this markdown file dynamically at startup, automatically stripping out any YAML frontmatter.
* **Role Gating:** Enforce security gates inside tool functions using [`context.auth.has_permission`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/hubscape_adk.py#L32):
  ```python
  async def admin_only_tool(arg1: str):
      context = get_context()
      if not context.auth.has_permission("admin_only_tool"):
          return {"status": "error", "message": "Unauthorized"}
  ```
* **No Manual RemoteContext Instantiation:** Never manually instantiate [`RemoteContext`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/hubscape_adk.py#L30) or hardcode mock fallback context credentials (e.g. `user_id="dev-user-123"`) inside agent tool scripts. Tools are designed to execute solely inside active platform-managed context sessions. If you need fallback setups for local standalone testing, mock them at the test-suite level.

## 3. Package File Encapsulation
* All execution routes, prompts, and tool handlers belong strictly within the agent's package folder (e.g. [`app/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app)). Avoid placing business logic at the root level of the workspace.

## 4. Visual Widget Execution
* **Explicit show_widget Call:** To display a widget card on the companion UI when a tool executes, the tool **must explicitly call** [`context.show_widget(widget_template_id, data)`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/hubscape_adk.py#L256).
* **Do Not Rely on Dict Returns:** Simply returning `{"widget": "widget_name"}` or similar keys in the tool's output dictionary **will not** trigger widget rendering. The backend runtime requires the [`show_widget`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/hubscape_adk.py#L256) method call to append the visual action payload to the active session context's execution queue.
