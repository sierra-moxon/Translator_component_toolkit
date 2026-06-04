"""Simple tests for TCT MCP Server functionality."""

import asyncio

from translator_component_toolkit.schema import all_names
from translator_component_toolkit.server import mcp


def _registered_tool_names():
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


def test_mcp_server_exists():
    """Test that MCP server instance exists and has correct name."""
    assert mcp is not None
    assert mcp.name == "translator-toolkit"


def test_mcp_server_ready():
    """Test that MCP server is ready for orchestrating agent access."""
    assert hasattr(mcp, "run"), "MCP server should be runnable for agents"
    assert mcp.name == "translator-toolkit", "MCP server should have correct name for agents"


def test_all_registry_tools_are_registered():
    """Every canonical name and alias in the registry is exposed as an MCP tool."""
    registered = _registered_tool_names()
    assert set(all_names()).issubset(registered)


def test_mcp_tools_accessible():
    """Canonical tool callables remain importable from the server module."""
    from translator_component_toolkit.server import lookup_name, normalize_nodes

    assert callable(lookup_name), "lookup_name tool should be accessible"
    assert callable(normalize_nodes), "normalize_nodes tool should be accessible"


def test_deprecated_alias_still_importable():
    """The deprecated alias name is still importable for backwards compatibility."""
    from translator_component_toolkit.server import name_lookup

    assert callable(name_lookup), "deprecated name_lookup alias should still be accessible"
