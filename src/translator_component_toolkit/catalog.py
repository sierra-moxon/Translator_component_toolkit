"""
Process-wide cache of the Translator reference catalog.

The foundational reference data — the map of API names to URLs, the MetaKG, and
each API's supported predicates — is slow-changing but expensive to build
(several HTTP calls over ~1000 SmartAPI specs plus per-KP metakg fetches). The
library produces all three together in :func:`translator_query.get_translator_API_predicates`,
where ``api_predicates`` is derived from the MetaKG, which is derived from
``api_names``.

Caching that bundle here lets read-path tools resolve it on demand instead of
forcing agents to fetch it and thread it back through every call. Tools keep
explicit parameters as an override; the cache is only consulted when a caller
omits them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import translator_query

# A builder returns the foundational bundle ``(api_names, metakg, api_predicates)``.
CatalogBuilder = Callable[[], tuple[dict, Any, dict]]


@dataclass(frozen=True)
class Catalog:
    """The foundational Translator reference data, built as one bundle.

    Attributes
    ----------
    api_names : dict[str, str]
        Map of API name to query URL.
    metakg : Any
        The MetaKG ``pandas.DataFrame`` (kept as ``Any`` to avoid importing
        pandas eagerly here).
    api_predicates : dict[str, list]
        Map of API name to the list of predicates it supports.
    """

    api_names: dict[str, str]
    metakg: Any
    api_predicates: dict[str, list]


_CACHE: Catalog | None = None


def _default_builder() -> tuple[dict, Any, dict]:
    return translator_query.get_translator_API_predicates()


def get_catalog(force_refresh: bool = False, builder: CatalogBuilder | None = None) -> Catalog:
    """Return the cached :class:`Catalog`, building it on first use.

    The bundle is built once via ``builder`` (defaulting to
    :func:`translator_query.get_translator_API_predicates`) and reused. Pass
    ``force_refresh=True`` to rebuild (e.g. after the upstream registry
    changes). ``builder`` is an injection seam for tests.
    """
    global _CACHE
    if _CACHE is None or force_refresh:
        build = builder or _default_builder
        api_names, metakg, api_predicates = build()
        _CACHE = Catalog(api_names, metakg, api_predicates)
    return _CACHE


def reset_cache() -> None:
    """Drop the cached catalog (primarily for tests)."""
    global _CACHE
    _CACHE = None
