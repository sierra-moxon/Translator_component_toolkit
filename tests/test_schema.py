"""Tests for the schema-first tool registry."""

import inspect

import pytest

from translator_component_toolkit import schema
from translator_component_toolkit.errors import InvalidParameterError
from translator_component_toolkit.schema import (
    REGISTRY,
    ParamSpec,
    ToolAnnotations,
    ToolSpec,
    all_names,
    make_signed_callable,
)

EXPECTED_NAMES = {
    "lookup_name",
    "get_synonyms",
    "lookup_names",
    "normalize_nodes",
    "get_kp_info",
    "get_metakg",
    "add_metakg_api",
    "add_plover_apis",
    "get_api_predicates",
    "optimize_query",
    "query_kp",
    "query_kps_parallel",
    "query_trapi",
}

# Canonical name -> deprecated alias kept for backwards compatibility.
EXPECTED_ALIASES = {
    "lookup_name": "name_lookup",
    "get_synonyms": "get_name_synonyms",
    "lookup_names": "batch_name_lookup",
    "get_metakg": "get_metakg_data",
    "add_metakg_api": "add_custom_api_to_metakg",
    "add_plover_apis": "add_plover_apis_to_metakg",
    "optimize_query": "optimize_query_for_api",
    "query_kp": "query_knowledge_provider",
    "query_kps_parallel": "parallel_query_apis",
    "query_trapi": "trapi_query_endpoint",
}


def test_registry_is_populated():
    assert len(REGISTRY) >= 13
    assert all(isinstance(spec, ToolSpec) for spec in REGISTRY)


def test_registry_covers_expected_tools():
    assert {spec.name for spec in REGISTRY} == EXPECTED_NAMES


def test_names_are_unique_across_canonical_and_aliases():
    names = all_names()
    assert len(names) == len(set(names)), "duplicate tool name or alias detected"


def test_canonical_names_use_verb_object_vocabulary():
    allowed_verbs = {"get", "list", "lookup", "normalize", "query", "add", "optimize"}
    for spec in REGISTRY:
        verb = spec.name.split("_", 1)[0]
        assert verb in allowed_verbs, f"{spec.name} does not start with a canonical verb"


def test_deprecated_aliases_are_preserved():
    by_name = {spec.name: spec for spec in REGISTRY}
    for canonical, alias in EXPECTED_ALIASES.items():
        assert canonical in by_name, f"missing canonical tool {canonical}"
        assert alias in by_name[canonical].aliases, f"{canonical} missing alias {alias}"


def test_every_func_is_callable():
    for spec in REGISTRY:
        assert callable(spec.func), f"{spec.name} func is not callable"


def test_every_param_is_a_paramspec_with_help():
    for spec in REGISTRY:
        for p in spec.params:
            assert isinstance(p, ParamSpec)
            assert p.help, f"{spec.name}.{p.name} is missing help text"


def test_summary_is_one_concise_line():
    for spec in REGISTRY:
        assert spec.summary
        assert "\n" not in spec.summary


def test_signed_callable_matches_paramspecs():
    for spec in REGISTRY:
        signed = make_signed_callable(spec)
        sig = inspect.signature(signed)
        assert list(sig.parameters) == [p.name for p in spec.params]
        for p in spec.params:
            param = sig.parameters[p.name]
            if p.required:
                assert param.default is inspect.Parameter.empty
            else:
                assert param.default == p.default


def test_signed_callable_binds_and_delegates():
    captured = {}

    spec = ToolSpec(
        name="demo",
        summary="demo",
        func=lambda a, b=2: captured.update(a=a, b=b),
        params=[ParamSpec("a", int, required=True, help="a"), ParamSpec("b", int, default=2, help="b")],
    )
    signed = make_signed_callable(spec)
    signed(1)
    assert captured == {"a": 1, "b": 2}


def test_paginated_tools_expose_limit_and_offset():
    for spec in REGISTRY:
        if spec.paginated:
            names = {p.name for p in spec.params}
            assert {"limit", "offset"} <= names, f"{spec.name} paginated but missing limit/offset"


def test_get_metakg_is_paginated():
    by_name = {spec.name: spec for spec in REGISTRY}
    assert by_name["get_metakg"].paginated is True


def test_get_metakg_returns_raw_when_unbounded(monkeypatch):
    import pandas as pd

    from translator_component_toolkit import schema, translator_metakg

    df = pd.DataFrame({"API": ["x", "y"], "Predicate": ["p", "q"]})
    monkeypatch.setattr(translator_metakg, "get_KP_metadata", lambda api_names: df)
    result = schema._get_metakg_data({"x": "http://x"})
    assert result is df  # unchanged shape preserves chaining


def test_get_metakg_returns_envelope_when_limited(monkeypatch):
    import pandas as pd

    from translator_component_toolkit import schema, translator_metakg

    df = pd.DataFrame({"API": ["x", "y", "z"]})
    monkeypatch.setattr(translator_metakg, "get_KP_metadata", lambda api_names: df)
    result = schema._get_metakg_data({"x": "http://x"}, limit=2)
    assert result["total"] == 3
    assert result["returned"] == 2
    assert result["truncated"] is True
    assert result["next_offset"] == 2


# ---------------------------------------------------------------------------
# Read-path reshape: catalog-derivable params are optional (issue #16).
# ---------------------------------------------------------------------------

CATALOG_OPTIONAL = {
    "get_metakg": {"api_names"},
    "optimize_query": {"api_predicates"},
    "query_kp": {"api_names", "api_predicates"},
    "query_kps_parallel": {"api_names", "api_predicates"},
}


def _query_with_predicates(predicates):
    """Minimal TRAPI query carrying the given edge predicates."""
    return {"message": {"query_graph": {"edges": {"e00": {"predicates": list(predicates)}}}}}


def test_catalog_derivable_params_are_optional():
    by_name = {spec.name: spec for spec in REGISTRY}
    for tool, optional_params in CATALOG_OPTIONAL.items():
        params = {p.name: p for p in by_name[tool].params}
        for name in optional_params:
            assert not params[name].required, f"{tool}.{name} should be optional"
            assert params[name].default is None, f"{tool}.{name} should default to None"


def test_get_metakg_uses_catalog_when_api_names_omitted(seeded_catalog):
    result = schema._get_metakg_data()  # no api_names -> cached MetaKG
    assert result is seeded_catalog.metakg


def test_optimize_query_resolves_predicates_from_catalog(seeded_catalog):
    # api_predicates omitted -> resolved from the catalog; the supported
    # predicate is kept and the unsupported one is dropped.
    query = _query_with_predicates(["biolink:related_to", "biolink:unsupported"])
    result = schema._optimize_query_for_api(query, "API X")
    assert result["message"]["query_graph"]["edges"]["e00"]["predicates"] == ["biolink:related_to"]


def test_optimize_query_unknown_api_validates_against_catalog(seeded_catalog):
    query = _query_with_predicates(["biolink:related_to"])
    with pytest.raises(InvalidParameterError):
        schema._optimize_query_for_api(query, "Unknown API")


def test_query_kp_resolves_api_names_from_catalog(empty_catalog):
    # api_names omitted -> resolved from the (empty) catalog, so validation of
    # an unknown api_name fails before any network call is attempted.
    with pytest.raises(InvalidParameterError):
        schema._query_knowledge_provider("Unknown", {})


def test_query_kp_explicit_api_names_override_catalog(seeded_catalog):
    # Explicit (empty) api_names are used instead of the seeded catalog, so the
    # known "API X" is rejected.
    with pytest.raises(InvalidParameterError):
        schema._query_knowledge_provider("API X", {}, api_names={})


# ---------------------------------------------------------------------------
# MCP tool annotations (issue #21).
# ---------------------------------------------------------------------------

# Tools whose work is purely local (no external service). Everything else in the
# registry reaches out to the network.
LOCAL_ONLY_TOOLS = {"optimize_query", "add_metakg_api"}


def test_every_tool_has_annotations():
    for spec in REGISTRY:
        assert isinstance(spec.annotations, ToolAnnotations)


def test_all_tools_are_read_only_and_non_destructive():
    for spec in REGISTRY:
        assert spec.annotations.read_only is True, f"{spec.name} should be read-only"
        assert spec.annotations.destructive is False, f"{spec.name} should be non-destructive"
        assert spec.annotations.idempotent is True, f"{spec.name} should be idempotent"


def test_open_world_matches_network_reach():
    for spec in REGISTRY:
        expected = spec.name not in LOCAL_ONLY_TOOLS
        assert spec.annotations.open_world is expected, f"{spec.name} open_world should be {expected}"


def test_to_mcp_renders_spec_hint_keys():
    annotations = ToolAnnotations(read_only=True, destructive=False, idempotent=True, open_world=False)
    assert annotations.to_mcp() == {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }


def test_tool_annotations_defaults_match_mcp_defaults():
    # MCP assumes a tool is writable, destructive, non-idempotent, open-world
    # unless told otherwise.
    defaults = ToolAnnotations()
    assert defaults.to_mcp() == {
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
