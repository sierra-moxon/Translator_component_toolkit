"""
Schema-first tool registry for the Translator Component Toolkit.

This module is the single source of truth for every agent-facing operation.
The MCP server (and, in later work, the CLI) are generated from ``REGISTRY``
rather than hand-wrapping library functions per surface, so names, parameters,
and descriptions stay in lockstep across surfaces.

A :class:`ToolSpec` describes one operation: its canonical name, a one-line
summary, its parameters (:class:`ParamSpec`), the adapter callable that invokes
the underlying library function, optional deprecated aliases, and a command
group used to organize the CLI.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import name_resolver, node_normalizer, translator_kpinfo, translator_metakg, translator_query, trapi
from .errors import validate_choice


@dataclass(frozen=True)
class ParamSpec:
    """One parameter of a tool.

    Attributes
    ----------
    name : str
        Parameter name as exposed on every surface.
    type : Any
        Python type annotation used to build the MCP/CLI schema.
    required : bool
        Whether the parameter must be supplied.
    default : Any
        Default value when ``required`` is False.
    help : str
        Human/agent-facing description.
    choices : list | None
        Enumerated valid values, if the parameter is constrained.
    """

    name: str
    type: Any = Any
    required: bool = False
    default: Any = None
    help: str = ""
    choices: list[Any] | None = None


@dataclass(frozen=True)
class ToolSpec:
    """One agent-facing operation.

    Attributes
    ----------
    name : str
        Canonical tool name.
    summary : str
        One-line description shown to humans and agents.
    func : Callable
        Adapter that accepts the ``ParamSpec`` names as keyword arguments and
        delegates to the underlying library function.
    params : list[ParamSpec]
        Ordered parameter specifications.
    aliases : list[str]
        Deprecated alternative names kept for backwards compatibility.
    group : str
        CLI command group (e.g. ``name``, ``query``).
    output_hint : str | None
        Optional note about the return shape.
    """

    name: str
    summary: str
    func: Callable[..., Any]
    params: list[ParamSpec] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    group: str = "misc"
    output_hint: str | None = None


def make_signed_callable(spec: ToolSpec) -> Callable[..., Any]:
    """Build a callable whose signature/annotations match ``spec``.

    FastMCP and Click both introspect ``inspect.signature``; constructing a
    wrapper with an explicit ``__signature__`` lets a single registry entry
    drive both surfaces without duplicating parameter declarations.
    """
    parameters = []
    annotations: dict[str, Any] = {}
    for p in spec.params:
        annotations[p.name] = p.type
        default = inspect.Parameter.empty if p.required else p.default
        parameters.append(
            inspect.Parameter(
                p.name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=p.type,
            )
        )
    signature = inspect.Signature(parameters)
    func = spec.func

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return func(**bound.arguments)

    wrapper.__name__ = spec.name
    wrapper.__qualname__ = spec.name
    wrapper.__doc__ = spec.summary
    wrapper.__signature__ = signature  # type: ignore[attr-defined]
    wrapper.__annotations__ = {**annotations, "return": Any}
    return wrapper


# ---------------------------------------------------------------------------
# Adapters: each accepts ParamSpec-named kwargs and delegates to the library,
# isolating the library's notebook-style parameter names from the public API.
# ---------------------------------------------------------------------------

def _name_lookup(query: str, return_top_response: bool = True, return_synonyms: bool = False) -> Any:
    return name_resolver.lookup(query, return_top_response, return_synonyms)


def _get_name_synonyms(query: str) -> Any:
    return name_resolver.synonyms(query)


def _batch_name_lookup(strings: list[str], size: int = 25, return_top_response: bool = True,
                       return_synonyms: bool = False) -> Any:
    return name_resolver.batch_lookup(strings, size, return_top_response, return_synonyms)


def _normalize_nodes(query: str, return_equivalent_identifiers: bool = False, conflate: bool = True,
                     drug_chemical_conflate: bool = False) -> Any:
    return node_normalizer.get_normalized_nodes(
        query, return_equivalent_identifiers, conflate=conflate, drug_chemical_conflate=drug_chemical_conflate
    )


def _get_kp_info() -> Any:
    return translator_kpinfo.get_translator_kp_info()


def _get_metakg_data(api_names: dict) -> Any:
    return translator_metakg.get_KP_metadata(api_names)


def _add_custom_api_to_metakg(api_names: dict, metakg_df: Any, new_api_name: str, new_api_url: str,
                              new_api_predicate: str, new_api_subject: str, new_api_object: str) -> Any:
    return translator_metakg.add_new_API_for_query(
        api_names, metakg_df, new_api_name, new_api_url, new_api_predicate, new_api_subject, new_api_object
    )


def _add_plover_apis_to_metakg(api_names: dict, metakg_df: Any) -> Any:
    return translator_metakg.add_plover_API(api_names, metakg_df)


def _get_api_predicates() -> Any:
    return translator_query.get_translator_API_predicates()


def _optimize_query_for_api(query_json: dict, api_name: str, api_predicates: dict) -> Any:
    validate_choice(api_name, api_predicates.keys(), "api_name")
    return translator_query.optimize_query_json(query_json, api_name, api_predicates)


def _query_knowledge_provider(api_name: str, query_json: dict, api_names: dict, api_predicates: dict) -> Any:
    validate_choice(api_name, api_names.keys(), "api_name")
    return translator_query.query_KP(api_name, query_json, api_names, api_predicates)


def _parallel_query_apis(query_json: dict, selected_apis: list[str], api_names: dict, api_predicates: dict,
                         max_workers: int = 1) -> Any:
    return translator_query.parallel_api_query(query_json, selected_apis, api_names, api_predicates, max_workers)


def _trapi_query_endpoint(url: str, query: dict) -> Any:
    return trapi.query(url, query)


# ---------------------------------------------------------------------------
# Registry: the single source of truth.
# ---------------------------------------------------------------------------

REGISTRY: list[ToolSpec] = [
    ToolSpec(
        name="lookup_name",
        aliases=["name_lookup"],
        summary="Look up a name/term and return normalized TranslatorNode information.",
        func=_name_lookup,
        group="name",
        params=[
            ParamSpec("query", str, required=True, help="Query string to look up."),
            ParamSpec("return_top_response", bool, default=True,
                      help="Return only the top response (True) or all responses (False)."),
            ParamSpec("return_synonyms", bool, default=False, help="Include synonyms in the result."),
        ],
        output_hint="TranslatorNode or list[TranslatorNode]",
    ),
    ToolSpec(
        name="get_synonyms",
        aliases=["get_name_synonyms"],
        summary="Get synonyms for a given CURIE.",
        func=_get_name_synonyms,
        group="name",
        params=[ParamSpec("query", str, required=True, help="CURIE to get synonyms for.")],
        output_hint="dict[curie, TranslatorNode]",
    ),
    ToolSpec(
        name="lookup_names",
        aliases=["batch_name_lookup"],
        summary="Batch look up multiple names/terms and return normalized TranslatorNode information.",
        func=_batch_name_lookup,
        group="name",
        params=[
            ParamSpec("strings", list[str], required=True, help="List of query strings."),
            ParamSpec("size", int, default=25, help="Chunking size for batch processing."),
            ParamSpec("return_top_response", bool, default=True, help="Return only the top response per string."),
            ParamSpec("return_synonyms", bool, default=False, help="Include synonyms in the results."),
        ],
        output_hint="dict[str, TranslatorNode]",
    ),
    ToolSpec(
        name="normalize_nodes",
        summary="Normalize node CURIEs using the Node Normalizer API.",
        func=_normalize_nodes,
        group="normalize",
        params=[
            ParamSpec("query", str, required=True, help="CURIE string or list of CURIEs to normalize."),
            ParamSpec("return_equivalent_identifiers", bool, default=False,
                      help="Whether to return equivalent identifiers."),
            ParamSpec("conflate", bool, default=True, help="Enable gene-protein conflation."),
            ParamSpec("drug_chemical_conflate", bool, default=False, help="Enable drug-chemical conflation."),
        ],
        output_hint="TranslatorNode or dict[curie, TranslatorNode]",
    ),
    ToolSpec(
        name="get_kp_info",
        summary="Get SmartAPI Translator Knowledge Provider information.",
        func=_get_kp_info,
        group="kp",
        output_hint="tuple[DataFrame, dict[name, url]]",
    ),
    ToolSpec(
        name="get_metakg",
        aliases=["get_metakg_data"],
        summary="Get MetaKG metadata (predicates, subjects, objects) for Knowledge Providers.",
        func=_get_metakg_data,
        group="metakg",
        params=[ParamSpec("api_names", dict, required=True, help="Dictionary mapping API names to URLs.")],
        output_hint="DataFrame",
    ),
    ToolSpec(
        name="add_metakg_api",
        aliases=["add_custom_api_to_metakg"],
        summary="Add a custom API to the knowledge graph metadata.",
        func=_add_custom_api_to_metakg,
        group="metakg",
        params=[
            ParamSpec("api_names", dict, required=True, help="Current API names dictionary."),
            ParamSpec("metakg_df", Any, required=True, help="Current MetaKG DataFrame."),
            ParamSpec("new_api_name", str, required=True, help="Name of the new API."),
            ParamSpec("new_api_url", str, required=True, help="URL of the new API."),
            ParamSpec("new_api_predicate", str, required=True, help="Predicate for the new API."),
            ParamSpec("new_api_subject", str, required=True, help="Subject type for the new API."),
            ParamSpec("new_api_object", str, required=True, help="Object type for the new API."),
        ],
        output_hint="tuple[dict, DataFrame]",
    ),
    ToolSpec(
        name="add_plover_apis",
        aliases=["add_plover_apis_to_metakg"],
        summary="Add Plover APIs (CATRAX team APIs) to the knowledge graph metadata.",
        func=_add_plover_apis_to_metakg,
        group="metakg",
        params=[
            ParamSpec("api_names", dict, required=True, help="Current API names dictionary."),
            ParamSpec("metakg_df", Any, required=True, help="Current MetaKG DataFrame."),
        ],
        output_hint="tuple[dict, DataFrame]",
    ),
    ToolSpec(
        name="get_api_predicates",
        summary="Get the predicates supported by each Translator API.",
        func=_get_api_predicates,
        group="query",
        output_hint="tuple[dict, DataFrame, dict]",
    ),
    ToolSpec(
        name="optimize_query",
        aliases=["optimize_query_for_api"],
        summary="Remove predicates from a TRAPI query that the selected API does not support.",
        func=_optimize_query_for_api,
        group="query",
        params=[
            ParamSpec("query_json", dict, required=True, help="TRAPI 1.5.0 format query."),
            ParamSpec("api_name", str, required=True, help="Name of the API to query."),
            ParamSpec("api_predicates", dict, required=True, help="Dictionary of API names to their predicates."),
        ],
        output_hint="dict (modified query)",
    ),
    ToolSpec(
        name="query_kp",
        aliases=["query_knowledge_provider"],
        summary="Query an individual Knowledge Provider API with a TRAPI 1.5.0 query.",
        func=_query_knowledge_provider,
        group="query",
        params=[
            ParamSpec("api_name", str, required=True, help="Name of the API to query."),
            ParamSpec("query_json", dict, required=True, help="TRAPI 1.5.0 format query."),
            ParamSpec("api_names", dict, required=True, help="Dictionary mapping API names to URLs."),
            ParamSpec("api_predicates", dict, required=True, help="Dictionary of API names to their predicates."),
        ],
        output_hint="dict (knowledge graph) or None",
    ),
    ToolSpec(
        name="query_kps_parallel",
        aliases=["parallel_query_apis"],
        summary="Query multiple APIs in parallel and merge results into a single knowledge graph.",
        func=_parallel_query_apis,
        group="query",
        params=[
            ParamSpec("query_json", dict, required=True, help="TRAPI 1.5.0 format query."),
            ParamSpec("selected_apis", list[str], required=True, help="List of API names to query."),
            ParamSpec("api_names", dict, required=True, help="Dictionary mapping API names to URLs."),
            ParamSpec("api_predicates", dict, required=True, help="Dictionary of API names to their predicates."),
            ParamSpec("max_workers", int, default=1, help="Number of parallel workers."),
        ],
        output_hint="dict (merged knowledge graph)",
    ),
    ToolSpec(
        name="query_trapi",
        aliases=["trapi_query_endpoint"],
        summary="Query a TRAPI endpoint with a TRAPI query and return the result message.",
        func=_trapi_query_endpoint,
        group="trapi",
        params=[
            ParamSpec("url", str, required=True, help="URL of the TRAPI endpoint."),
            ParamSpec("query", dict, required=True, help="TRAPI query dict (e.g. from trapi.build_query)."),
        ],
        output_hint="dict (result message) or None",
    ),
]


def all_names() -> list[str]:
    """Return every canonical name plus alias registered in ``REGISTRY``."""
    names: list[str] = []
    for spec in REGISTRY:
        names.append(spec.name)
        names.extend(spec.aliases)
    return names
