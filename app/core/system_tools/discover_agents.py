import logging
import app.core.hubscape_adk

logger = logging.getLogger(__name__)

@app.core.hubscape_adk.require_tool_privilege
def discover_agents(query: str = None) -> list:
    """
    Search and discover registered A2A subagents whitelisted for the active user session.
    
    Args:
        query: Optional search keyword to filter agents by name or description.
    """
    try:
        ctx = app.core.hubscape_adk.get_context()
        return ctx.get_available_agents(query)
    except Exception as e:
        logger.error(f"Error in discover_agents: {e}", exc_info=True)
        return [{"error": f"Failed to search registry: {str(e)}"}]