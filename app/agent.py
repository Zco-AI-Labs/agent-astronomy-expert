import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Force regional Vertex AI routing only if no direct API keys are configured
if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    os.environ.pop("GOOGLE_GENAI_USE_ENTERPRISE", None)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("GOOGLE_API_KEY", None)
import asyncio
import importlib.util
import re
from google.adk import Agent as AdkAgent

from app.core.load_local_tools import load_local_tools

# Statically import custom script/tool modules here so the Vertex AI packaging dependency analyzer
# sees them and bundles them in the cloud deployment container/ZIP.
from app.core.system_tools import (
    consultAgent,
    discover_agents,
)

# 1. Require SKILL.md as the Single Source of Truth for metadata (name, description) and instructions
runtime_dir = os.path.dirname(os.path.abspath(__file__))
skill_md_path = os.path.join(runtime_dir, "SKILL.md")
if not os.path.exists(skill_md_path):
    raise FileNotFoundError(f"Required agent definition file missing: {skill_md_path}")

with open(skill_md_path, "r", encoding="utf-8") as f:
    skill_content = f.read()

fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_content, flags=re.DOTALL)
if not fm_match:
    raise ValueError(f"SKILL.md is missing required YAML frontmatter header (--- ... ---): {skill_md_path}")

fm_text = fm_match.group(1)
name_m = re.search(r'^name:\s*["\']?([^"\'\n]+)["\']?', fm_text, re.MULTILINE)
if not name_m:
    raise ValueError(f"SKILL.md frontmatter is missing required 'name:' field: {skill_md_path}")

desc_m = re.search(r'^description:\s*["\']?([^"\'\n]+)["\']?', fm_text, re.MULTILINE)
if not desc_m:
    raise ValueError(f"SKILL.md frontmatter is missing required 'description:' field: {skill_md_path}")

agent_name = name_m.group(1).strip().replace('-', '_')
agent_description = desc_m.group(1).strip()
system_instruction = skill_content[fm_match.end():].strip()

scripts_dir = os.path.join(runtime_dir, "scripts")
system_tools_dir = os.path.join(runtime_dir, "core", "system_tools")
tools = load_local_tools(system_tools_dir) + load_local_tools(scripts_dir)

allow_web_search = False
allow_google_maps = False

# 1. Load config from app/config.json if it exists, falling back to app/agent_config.json
agent_config_path = os.path.join(runtime_dir, "config.json")
if not os.path.exists(agent_config_path):
    agent_config_path = os.path.join(runtime_dir, "agent_config.json")
    
agent_config_data = {}
if os.path.exists(agent_config_path):
    try:
        import json
        with open(agent_config_path, "r", encoding="utf-8") as cf:
            agent_config_data = json.load(cf) or {}
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to read/parse agent config file: {e}")

# 2. Load config from deploy_config.json / config.json in root (fallback path)
config_json_path = os.path.join(os.path.dirname(runtime_dir), "deploy_config.json")
if not os.path.exists(config_json_path):
    config_json_path = os.path.join(os.path.dirname(runtime_dir), "config.json")

fallback_config_data = {}
if os.path.exists(config_json_path):
    try:
        import json
        with open(config_json_path, "r", encoding="utf-8") as cf:
            fallback_config_data = json.load(cf) or {}
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to read/parse root config file: {e}")

# Resolve search toggles (prioritizing agent_config.json keys)
if "allow_web_search" in agent_config_data or "allowWebSearch" in agent_config_data:
    allow_web_search = bool(agent_config_data.get("allow_web_search") if "allow_web_search" in agent_config_data else agent_config_data.get("allowWebSearch"))
else:
    allow_web_search = bool(fallback_config_data.get("allow_web_search") if "allow_web_search" in fallback_config_data else fallback_config_data.get("allowWebSearch", False))

if "google_search" in agent_config_data:
    allow_web_search = allow_web_search or bool(agent_config_data.get("google_search"))
elif "google_search" in fallback_config_data:
    allow_web_search = allow_web_search or bool(fallback_config_data.get("google_search"))

# Resolve maps toggles (prioritizing agent_config.json keys)
if "allow_google_maps" in agent_config_data or "allowGoogleMaps" in agent_config_data:
    allow_google_maps = bool(agent_config_data.get("allow_google_maps") if "allow_google_maps" in agent_config_data else agent_config_data.get("allowGoogleMaps"))
else:
    allow_google_maps = bool(fallback_config_data.get("allow_google_maps") if "allow_google_maps" in fallback_config_data else fallback_config_data.get("allowGoogleMaps", False))

if "google_maps" in agent_config_data:
    allow_google_maps = allow_google_maps or bool(agent_config_data.get("google_maps"))
elif "google_maps" in fallback_config_data:
    allow_google_maps = allow_google_maps or bool(fallback_config_data.get("google_maps"))

# Resolve mcp_servers key
mcp_servers = agent_config_data.get("mcp_servers") if "mcp_servers" in agent_config_data else fallback_config_data.get("mcp_servers", {})

# Load remote MCP servers statically
if mcp_servers:
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
        
        for server_name, server_config in mcp_servers.items():
            url = server_config.get("url")
            if not url:
                continue
            
            headers = server_config.get("headers")
            
            kwargs = {"url": url}
            if headers is not None:
                kwargs["headers"] = headers
                
            connection_params = StreamableHTTPConnectionParams(**kwargs)
            toolset = McpToolset(connection_params=connection_params)
            # Tag the toolset with metadata for request-time resolution/filtering
            toolset._mcp_server_name = server_name
            toolset._mcp_raw_headers = headers or {}
            
            tools.append(toolset)
    except ImportError:
        import logging
        logging.getLogger(__name__).warning("⚠️ mcp library or McpToolset not available. Skipping static MCP server loading.")

# Register built-in ADK grounding tools based on resolved toggles
if allow_web_search or allow_google_maps:
    # Vertex AI REST API requirement: Search/Grounding tools CANNOT be combined with custom function declaration tools
    tools = []
    if allow_web_search:
        try:
            from google.adk.tools import google_search
            tools.append(google_search)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to import google_search tool: {e}")
    if allow_google_maps:
        try:
            from google.adk.tools import google_maps_grounding
            tools.append(google_maps_grounding)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to import google_maps_grounding tool: {e}")

from app.app_utils.vertex_gemini import get_model

root_agent = AdkAgent(
    model=get_model("gemini-2.5-flash"),
    name=agent_name,
    description=agent_description,
    instruction=system_instruction,
    tools=tools
)

from app.core.geap_agent_wrapper import GEAPAgentWrapper

# Singleton instance used as the serialization target
agent_app = GEAPAgentWrapper(root_agent)

from google.adk.apps import App
app = App(
    root_agent=root_agent,
    name="app",
)