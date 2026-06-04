"""
Network configuration for agent-facing HTTP calls.

A single, configurable default timeout (in seconds) applied to every outbound
``requests`` call in the agent-facing modules. Without a timeout a hung upstream
blocks a tool call forever; for an agent that looks like a stuck session with no
error to react to. Override the value with the ``TCT_HTTP_TIMEOUT`` environment
variable.
"""

from __future__ import annotations

import os

DEFAULT_HTTP_TIMEOUT = 30.0
"""Seconds to wait on an outbound HTTP call before giving up."""

_ENV_VAR = "TCT_HTTP_TIMEOUT"


def http_timeout() -> float:
    """Return the configured HTTP timeout in seconds.

    Reads ``TCT_HTTP_TIMEOUT`` when set to a positive number; otherwise falls
    back to :data:`DEFAULT_HTTP_TIMEOUT`. A missing, unparsable, or
    non-positive value is treated as "use the default" so a bad env var can
    never disable timeouts.
    """
    raw = os.environ.get(_ENV_VAR)
    if raw is None:
        return DEFAULT_HTTP_TIMEOUT
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_HTTP_TIMEOUT
    return value if value > 0 else DEFAULT_HTTP_TIMEOUT
