"""Tests for the schema-first tool registry."""

import inspect

from translator_component_toolkit.schema import (
    REGISTRY,
    ParamSpec,
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
