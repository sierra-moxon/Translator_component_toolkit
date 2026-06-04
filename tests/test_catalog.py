"""Tests for the process-wide reference catalog cache."""

from unittest.mock import Mock

from translator_component_toolkit import catalog


def test_get_catalog_builds_once_and_caches(sample_bundle):
    builder = Mock(return_value=sample_bundle)

    first = catalog.get_catalog(builder=builder)
    second = catalog.get_catalog(builder=builder)

    assert builder.call_count == 1  # built once, then served from cache
    assert first is second
    assert first.api_names == {"API X": "http://x"}
    assert first.api_predicates == {"API X": ["biolink:related_to"]}


def test_force_refresh_rebuilds(sample_bundle):
    builder = Mock(return_value=sample_bundle)

    catalog.get_catalog(builder=builder)
    catalog.get_catalog(builder=builder, force_refresh=True)

    assert builder.call_count == 2


def test_reset_cache_clears(sample_bundle):
    builder = Mock(return_value=sample_bundle)
    catalog.get_catalog(builder=builder)

    catalog.reset_cache()

    assert catalog._CACHE is None
