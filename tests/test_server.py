"""Simple tests for TCT MCP Server functionality."""

import asyncio

from translator_component_toolkit.schema import REGISTRY, all_names
from translator_component_toolkit.server import mcp


def _registered_tool_names():
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


def _registered_tools_by_name():
    return {t.name: t for t in asyncio.run(mcp.list_tools())}


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


def test_registered_tools_carry_annotations():
    """Each canonical tool exposes the behavioral hints declared in the registry."""
    registered = _registered_tools_by_name()
    for spec in REGISTRY:
        tool = registered[spec.name]
        assert tool.annotations is not None, f"{spec.name} missing annotations"
        assert tool.annotations.readOnlyHint is spec.annotations.read_only
        assert tool.annotations.destructiveHint is spec.annotations.destructive
        assert tool.annotations.idempotentHint is spec.annotations.idempotent
        assert tool.annotations.openWorldHint is spec.annotations.open_world


def test_aliases_inherit_canonical_annotations():
    """A deprecated alias is registered with the same hints as its canonical tool."""
    registered = _registered_tools_by_name()
    for spec in REGISTRY:
        for alias in spec.aliases:
            assert registered[alias].annotations.readOnlyHint is spec.annotations.read_only
            assert registered[alias].annotations.openWorldHint is spec.annotations.open_world
