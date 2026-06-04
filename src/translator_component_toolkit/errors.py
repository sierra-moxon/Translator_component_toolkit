"""
Error mapping for agent-facing surfaces.

The MCP server previously collapsed every exception into ``INTERNAL_ERROR``,
which hides the real cause and offers no guidance. This module maps Python
exception types to appropriate MCP error codes and produces messages that
*teach* (e.g. enumerating valid values) so an agent can correct its call.
"""

from __future__ import annotations

import requests
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData

# Cap enumerated choices so a teaching message stays bounded.
MAX_LISTED_CHOICES = 20


class InvalidParameterError(ValueError):
    """Raised for invalid user input; maps to MCP ``INVALID_PARAMS``."""


def format_choices(valid: list[str], limit: int = MAX_LISTED_CHOICES) -> str:
    """Render a bounded, comma-separated list of valid values."""
    listed = list(valid)
    head = listed[:limit]
    suffix = "" if len(listed) <= limit else f", ... (+{len(listed) - limit} more)"
    return ", ".join(repr(v) for v in head) + suffix


def validate_choice(value: str, valid, param_name: str) -> None:
    """Raise :class:`InvalidParameterError` enumerating valid values on mismatch."""
    valid_list = list(valid)
    if value not in valid_list:
        raise InvalidParameterError(
            f"{param_name} {value!r} is not valid. Must be one of: {format_choices(valid_list)}"
        )


def to_mcp_error(exc: Exception, tool_name: str) -> McpError:
    """Map a raised exception to an :class:`McpError` with a teaching message.

    - ``InvalidParameterError`` / ``LookupError`` -> ``INVALID_PARAMS``
    - ``requests.RequestException`` -> ``INTERNAL_ERROR`` (upstream/API failure)
    - anything else -> ``INTERNAL_ERROR``
    """
    if isinstance(exc, (InvalidParameterError, LookupError)):
        return McpError(ErrorData(code=INVALID_PARAMS, message=f"{tool_name}: {exc}"))

    if isinstance(exc, requests.RequestException):
        status = None
        response = getattr(exc, "response", None)
        if response is not None:
            status = getattr(response, "status_code", None)
        detail = f" (HTTP {status})" if status is not None else ""
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f"{tool_name}: upstream API error{detail}: {exc}"))

    return McpError(ErrorData(code=INTERNAL_ERROR, message=f"{tool_name}: {exc}"))
