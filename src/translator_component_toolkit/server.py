"""
Translator Component Toolkit MCP Server

This server provides access to biomedical translator tools including:
- Name resolution and lookup
- Node normalization
- Knowledge provider information
- Meta knowledge graph operations
- Query orchestration
- TRAPI protocol support

Tools are generated from the schema-first registry in :mod:`schema`, so the MCP
surface stays in lockstep with the library (and, later, the CLI).
"""

from fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR

from .schema import REGISTRY, ToolSpec, make_signed_callable

# Create unified MCP server
mcp = FastMCP("translator-toolkit")


def _register(spec: ToolSpec) -> None:
    """Register one tool (and its aliases) on the MCP server from a ToolSpec."""
    base = make_signed_callable(spec)

    def wrap(name: str, description: str):
        signed = make_signed_callable(spec)

        def tool_fn(*args, **kwargs):
            try:
                return signed(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 - surfaced to MCP client
                raise McpError(ErrorData(INTERNAL_ERROR, f"{name} error: {str(e)}")) from e

        tool_fn.__name__ = name
        tool_fn.__qualname__ = name
        tool_fn.__doc__ = description
        tool_fn.__signature__ = signed.__signature__  # type: ignore[attr-defined]
        tool_fn.__annotations__ = dict(signed.__annotations__)
        mcp.tool(name=name, description=description)(tool_fn)

    wrap(spec.name, spec.summary)
    for alias in spec.aliases:
        wrap(alias, f"Deprecated alias for `{spec.name}`. {spec.summary}")

    # keep module attributes so `from .server import lookup_name` (and the
    # deprecated `name_lookup` alias) still work for direct importers
    globals()[spec.name] = base
    for alias in spec.aliases:
        globals()[alias] = base


for _spec in REGISTRY:
    _register(_spec)
