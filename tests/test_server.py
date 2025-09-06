"""Simple tests for TCT MCP Server functionality."""

from TCT.server import mcp


def test_mcp_server_exists():
    """Test that MCP server instance exists and has correct name."""
    assert mcp is not None
    assert mcp.name == "translator-toolkit"


def test_mcp_server_has_tools():
    """Test that MCP server has registered tools for orchestrating agent."""
    tools = mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    
    # Verify key tools are available for agent orchestration
    expected_tools = [
        'name_lookup',
        'normalize_nodes', 
        'get_kp_info',
        'query_knowledge_provider'
    ]
    
    for tool in expected_tools:
        assert tool in tool_names, f"Tool {tool} not found - orchestrating agent won't have access"


def test_mcp_tools_callable():
    """Test that MCP tools can be called by orchestrating agent."""
    from TCT.server import name_lookup, normalize_nodes
    
    # These should be callable functions (even if they fail due to missing deps)
    assert callable(name_lookup)
    assert callable(normalize_nodes)