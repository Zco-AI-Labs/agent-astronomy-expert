# Primary Directive: Custom Agent AI Constitution

> [!IMPORTANT]
> This file is the **HIGHEST AUTHORITY** inside this custom agent repository. 
> Any AI coding assistant or agent modifying this codebase must strictly adhere to these directives.

## 1. Scope Containment & Pure Agent Principle
To ensure clean deployment and ingestion by the Hubscape platform, this repository follows the **Pure Agent Principle**:
* Only modify the core files accepted by the GitOps ingestion pipeline:
  * Root level:
    * [`deploy_config.json`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/deploy_config.json) (Metadata, RBAC permissions, UI settings, Secrets declarations)
    * [`pyproject.toml`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/pyproject.toml) (Package configuration and python dependency listings)
    * [`agents-cli-manifest.yaml`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/agents-cli-manifest.yaml) (Agent engine manifest details)
  * [`app/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app) package folder:
    * [`app/__init__.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/__init__.py) (Standard initialization exposing the `root_agent`)
    * [`app/agent.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/agent.py) (LlmAgent and app wrapper setup)
    * [`app/config.json`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/config.json) (Agent configurations: MCP servers, OAuth configuration, and search/maps toggles)
    * [`app/SKILL.md`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/SKILL.md) (Contains LLM instructions/prompts)
    * [`app/scripts/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/scripts) (Contains standalone Python tool scripts)
    * [`app/static/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/static) (Contains local static HTML/CSS/images/iframes)
    * [`app/ui/widgets/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/ui/widgets) (Contains custom Lego UI JSON widgets)
    * [`app/app_utils/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/app_utils) (Central shared platform utilities and telemetry configurations)
    * [`app/core/`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core) (Core template runtime wrapper engines)
* Do **NOT** commit, modify, or reference any local sandbox test files (`local_db.json`, `.env`, `.agent/`, or virtual environment folders) in your production logic.

## 2. Model Context Protocol (MCP) & Agent-to-Agent (A2A) Connections
Custom agents must route all external connections and tool calls through the standardized platform interfaces:
* **Standard MCP Servers (Direct Model Tooling):** Register remote MCP servers in [`app/config.json`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/config.json) under `mcp_servers` with the `openid_configuration` and dynamic headers (e.g. `"${OAUTH_TOKEN:provider}"`). In [`app/agent.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/agent.py), load these servers statically using `McpToolset` so that the tools are auto-discovered, whitelisted, and presented directly to the Gemini LLM.
* **Programmatic MCP Calls:** When manually calling tools from whitelisted `mcp_servers` in custom Python logic, load the configuration dynamically and invoke them by registering them in the static toolset or calling backend methods directly. Note that `context.mcp` does not exist on the [`RemoteContext`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/hubscape_adk.py#L30) object.
* **A2A Outbound Calls:** When invoking tools on another agent, use the programmatic client handler rather than context properties. Import and instantiate [`RemoteA2aAgent`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/system_tools/consultAgent.py#L124) from `google.adk.agents.remote_a2a_agent` and execute its `run_async()` method, as modeled in [`consultAgent.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/core/system_tools/consultAgent.py).

## 3. Database Scoping & Index-Free Queries
* **Scoping Helper Paths:** Always read and write to Firestore collections using platform-provided scope context helper methods on `context` (e.g. `context.save()`, `context.get()`, `context.list()`, `context.delete()`).
* **NO Custom Indexes:** You are strictly forbidden from writing query code that requires custom composite index definitions. All database searches must use in-memory sorting or denormalized composite keys to guarantee full compliance with the platform's **Index-Free Database Query Guidelines**.

## 4. Platform Secrets Vault Fallback
* Never hardcode API keys, tokens, or credentials in files.
* Retrieve all external credentials using the sandbox-safe fallback pattern:
  ```python
  api_key = context.raw_context.get("secrets", {}).get("KEY_NAME") or os.environ.get("KEY_NAME")
  ```

## 5. Event Logging & Telemetry
* Telemetry and trace logging are managed automatically at the platform level via OpenTelemetry and Vertex AI instrumentation configured in [`app/app_utils/telemetry.py`](file:///Users/rajvekeria/Documents/GitHub/hubscape-agent-template/app/app_utils/telemetry.py).
* All calls made to a paid external API or provider (e.g. Stripe, Twilio, Google AI) must utilize standard Python logging (`logging.info` or `logging.error`) with structured context or details so they can be captured by the platform's trace/log collection pipeline. Log both successes and failures to maintain billing audit integrity.
