"""Shared fixtures for the test suite."""

import pandas as pd
import pytest

from translator_component_toolkit import catalog


@pytest.fixture(autouse=True)
def reset_catalog():
    """Keep the process-wide catalog cache from leaking across tests."""
    catalog.reset_cache()
    yield
    catalog.reset_cache()


@pytest.fixture
def sample_bundle():
    """A small foundational bundle: (api_names, metakg, api_predicates)."""
    api_names = {"API X": "http://x"}
    metakg = pd.DataFrame({"API": ["API X"], "Predicate": ["biolink:related_to"]})
    api_predicates = {"API X": ["biolink:related_to"]}
    return api_names, metakg, api_predicates


@pytest.fixture
def seeded_catalog(sample_bundle):
    """Seed the cache with a known catalog so tools resolve from it offline."""
    api_names, metakg, api_predicates = sample_bundle
    cat = catalog.Catalog(api_names=api_names, metakg=metakg, api_predicates=api_predicates)
    catalog._CACHE = cat
    return cat


@pytest.fixture
def empty_catalog():
    """Seed the cache with an empty catalog (no known APIs/predicates)."""
    cat = catalog.Catalog(api_names={}, metakg=pd.DataFrame(), api_predicates={})
    catalog._CACHE = cat
    return cat
