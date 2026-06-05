"""
Output serialization for agent-facing surfaces.

Tool results are a mix of dataclasses (``TranslatorNode``), pandas
``DataFrame``s, tuples, dicts, and lists. :func:`serialize` normalizes any of
these into JSON-safe Python primitives so the CLI (and other callers) can emit
a single, predictable shape regardless of which library function produced it.
"""

from __future__ import annotations

import dataclasses
from typing import Any

# Exit codes for the CLI output contract. Documented here so the CLI and its
# tests share one source of truth.
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NOT_FOUND = 3
EXIT_UPSTREAM = 4
EXIT_UNEXPECTED = 1


def _is_dataframe(obj: Any) -> bool:
    """True if ``obj`` is a pandas DataFrame, without importing pandas eagerly."""
    cls = type(obj)
    return cls.__module__.startswith("pandas") and cls.__name__ == "DataFrame"


def serialize(obj: Any) -> Any:
    """Recursively convert ``obj`` into JSON-safe primitives.

    - dataclass instances -> ``dataclasses.asdict`` (recursively serialized)
    - pandas ``DataFrame`` -> list of record dicts
    - tuples -> lists
    - dicts -> dicts with serialized values (keys coerced to ``str``)
    - lists/sets -> lists of serialized items
    - primitives (``str``/``int``/``float``/``bool``/``None``) -> unchanged
    - anything else -> ``str(obj)`` as a last resort
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: serialize(v) for k, v in dataclasses.asdict(obj).items()}

    if _is_dataframe(obj):
        return obj.to_dict(orient="records")

    if isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [serialize(v) for v in obj]

    return str(obj)


def paginate(items: Any, limit: int | None = None, offset: int = 0) -> dict[str, Any]:
    """Wrap a list-style result in a bounded response envelope.

    The result is serialized, coerced to a list, then sliced by ``offset`` and
    ``limit``. The envelope makes truncation explicit so an agent knows whether
    to fetch more:

    ``{"data": [...], "total": N, "returned": k, "truncated": bool,
    "next_offset": int | None}``

    A ``limit`` of ``None`` returns everything from ``offset`` onward.
    """
    serialized = serialize(items)
    if not isinstance(serialized, list):
        serialized = [serialized]

    total = len(serialized)
    start = max(offset, 0)
    page = serialized[start:] if limit is None else serialized[start:start + limit]
    returned = len(page)
    consumed = start + returned
    truncated = consumed < total
    return {
        "data": page,
        "total": total,
        "returned": returned,
        "truncated": truncated,
        "next_offset": consumed if truncated else None,
    }
