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
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.hubscape_adk import resolve_mcp_tools

@pytest.mark.asyncio
async def test_resolve_mcp_tools_with_placeholders():
    # Mock RemoteContext
    context = MagicMock()
    context.get_oauth_token = AsyncMock(return_value="test_github_token")
    context.raw_context = {
        "secrets": {
            "MY_API_KEY": "super_secret_key"
        },
        "accessible_tools": {
            "github_mcp": ["read_repo", "write_repo"]
        }
    }
    
    # Mock Agent
    agent = MagicMock()
    
    # Mock a tool resembling McpToolset
    mcp_tool = MagicMock()
    mcp_tool._mcp_server_name = "github_mcp"
    mcp_tool._mcp_raw_headers = {
        "Authorization": "Bearer ${OAUTH_TOKEN:github}",
        "X-API-Key": "${MY_API_KEY}",
        "Content-Type": "application/json"
    }
    mcp_tool.connection_params = MagicMock()
    mcp_tool.connection_params.url = "https://mock-mcp-server/sse"
    
    agent.tools = [mcp_tool]
    
    # Mock McpToolset class and StreamableHTTPConnectionParams in the ADK/mcp
    mock_mcp_toolset_cls = MagicMock()
    mock_conn_params_cls = MagicMock()
    
    mock_mcp_module = MagicMock()
    mock_mcp_module.McpToolset = mock_mcp_toolset_cls
    mock_mcp_module.StreamableHTTPConnectionParams = mock_conn_params_cls
    
    modules = {
        "google.adk.tools.mcp_tool": mock_mcp_module,
        "google.adk.tools.mcp_tool.mcp_toolset": mock_mcp_module,
    }
    
    with patch.dict("sys.modules", modules):
        # Call resolve_mcp_tools
        resolved_agent = await resolve_mcp_tools(agent, context)
        
        # Verify get_oauth_token was called for github
        context.get_oauth_token.assert_called_once_with("github")
        
        # Verify McpToolset was instantiated
        mock_mcp_toolset_cls.assert_called_once()
        
        # Verify connection headers were resolved correctly
        called_args, called_kwargs = mock_conn_params_cls.call_args
        assert called_kwargs["url"] == "https://mock-mcp-server/sse"
        assert called_kwargs["headers"]["Authorization"] == "Bearer test_github_token"
        assert called_kwargs["headers"]["X-API-Key"] == "super_secret_key"
        assert called_kwargs["headers"]["Content-Type"] == "application/json"
        
        # Verify tool filtering was applied
        toolset_args, toolset_kwargs = mock_mcp_toolset_cls.call_args
        assert toolset_kwargs["tool_filter"] == ["read_repo", "write_repo"]


@pytest.mark.asyncio
async def test_resolve_mcp_tools_with_privileges():
    from unittest.mock import mock_open
    import json
    
    context = MagicMock()
    context.user_privileges = ["admin_role"]
    context.get_oauth_token = AsyncMock(return_value="token")
    context.raw_context = {}
    
    agent = MagicMock()
    mcp_tool = MagicMock()
    mcp_tool._mcp_server_name = "github_mcp"
    mcp_tool._mcp_raw_headers = {}
    mcp_tool.connection_params = MagicMock()
    mcp_tool.connection_params.url = "https://mock-mcp-server/sse"
    
    agent.tools = [mcp_tool]
    
    mock_mcp_toolset_cls = MagicMock()
    mock_sse_params_cls = MagicMock()
    mock_mcp_module = MagicMock()
    mock_mcp_module.McpToolset = mock_mcp_toolset_cls
    
    modules = {
        "google.adk.tools.mcp_tool": mock_mcp_module,
        "google.adk.tools.mcp_tool.mcp_toolset": mock_mcp_module,
        "mcp": MagicMock(SseServerParameters=mock_sse_params_cls)
    }
    
    mock_privileges = {
        "privileges": {
            "admin_role": {
                "tools": ["read_repo", "write_repo"]
            }
        }
    }
    
    with patch.dict("sys.modules", modules), \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_privileges))):
         
        resolved_agent = await resolve_mcp_tools(agent, context)
        
        toolset_args, toolset_kwargs = mock_mcp_toolset_cls.call_args
        assert toolset_kwargs["tool_filter"] == ["read_repo", "write_repo"]

