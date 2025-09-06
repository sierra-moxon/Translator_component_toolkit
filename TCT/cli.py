"""
Command Line Interface for Translator Component Toolkit

This CLI provides command-line access to all TCT functionality including:
- Name resolution and lookup
- Node normalization 
- Knowledge provider information
- Meta knowledge graph operations
- Query orchestration
- TRAPI protocol support
"""

import json
import sys

import click
import pandas as pd

from .name_resolver import lookup, synonyms, batch_lookup
from .node_normalizer import get_normalized_nodes
from .translator_kpinfo import get_translator_kp_info
from .translator_metakg import get_KP_metadata
from .translator_query import get_translator_API_predicates, optimize_query_json, query_KP, parallel_api_query


def print_json(data):
    """Helper to print JSON data nicely"""
    if hasattr(data, 'to_dict'):
        click.echo(json.dumps(data.to_dict(), indent=2))
    elif isinstance(data, pd.DataFrame):
        click.echo(data.to_json(indent=2))
    else:
        click.echo(json.dumps(data, indent=2, default=str))


@click.group()
@click.version_option()
def main():
    """Translator Component Toolkit - Biomedical knowledge graph tools"""
    pass


@main.group()
def name():
    """Name resolution and lookup commands"""
    pass


@name.command()
@click.argument('query')
@click.option('--top-only/--all', default=True, help='Return only top response or all responses')
@click.option('--synonyms/--no-synonyms', default=False, help='Include synonyms in results')
@click.option('--format', 'output_format', type=click.Choice(['json', 'simple']), default='json')
def lookup_cmd(query: str, top_only: bool, synonyms: bool, output_format: str):
    """Look up a name/term and return normalized TranslatorNode information"""
    try:
        result = lookup(query, return_top_response=top_only, return_synonyms=synonyms)
        if output_format == 'simple':
            if isinstance(result, list):
                for item in result:
                    click.echo(f"{item.curie}: {item.label}")
            else:
                click.echo(f"{result.curie}: {result.label}")
        else:
            print_json(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@name.command()
@click.argument('curie')
@click.option('--format', 'output_format', type=click.Choice(['json', 'simple']), default='json')
def synonyms_cmd(curie: str, output_format: str):
    """Get synonyms for a given CURIE"""
    try:
        result = synonyms(curie)
        if output_format == 'simple':
            for k, v in result.items():
                click.echo(f"{k}: {v.label}")
        else:
            print_json(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@name.command()
@click.argument('strings', nargs=-1, required=True)
@click.option('--size', default=25, help='Chunking size for batch processing')
@click.option('--top-only/--all', default=True, help='Return only top response or all responses')
@click.option('--synonyms/--no-synonyms', default=False, help='Include synonyms in results')
@click.option('--format', 'output_format', type=click.Choice(['json', 'simple']), default='json')
def batch(strings: tuple, size: int, top_only: bool, synonyms: bool, output_format: str):
    """Batch lookup multiple names/terms"""
    try:
        result = batch_lookup(list(strings), size=size, return_top_response=top_only, return_synonyms=synonyms)
        if output_format == 'simple':
            for query, nodes in result.items():
                if isinstance(nodes, list):
                    for node in nodes:
                        click.echo(f"{query} -> {node.curie}: {node.label}")
                else:
                    click.echo(f"{query} -> {nodes.curie}: {nodes.label}")
        else:
            print_json(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def normalize():
    """Node normalization commands"""
    pass


@normalize.command()
@click.argument('curie')
@click.option('--equivalent-ids/--no-equivalent-ids', default=False, help='Return equivalent identifiers')
@click.option('--conflate/--no-conflate', default=True, help='Enable gene-protein conflation')
@click.option('--drug-chemical-conflate/--no-drug-chemical-conflate', default=False, help='Enable drug-chemical conflation')
@click.option('--format', 'output_format', type=click.Choice(['json', 'simple']), default='json')
def nodes(curie: str, equivalent_ids: bool, conflate: bool, drug_chemical_conflate: bool, output_format: str):
    """Normalize node CURIEs using the Node Normalizer API"""
    try:
        result = get_normalized_nodes(curie, return_equivalent_identifiers=equivalent_ids, 
                                      conflate=conflate, drug_chemical_conflate=drug_chemical_conflate)
        if output_format == 'simple':
            if isinstance(result, dict):
                for k, v in result.items():
                    click.echo(f"{k} -> {v.curie}: {v.label}")
            else:
                click.echo(f"{result.curie}: {result.label}")
        else:
            print_json(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def kp():
    """Knowledge Provider information commands"""
    pass


@kp.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv', 'table']), default='table')
def info(output_format: str):
    """Get SmartAPI Translator Knowledge Provider information"""
    try:
        df, api_names = get_translator_kp_info()
        if output_format == 'csv':
            click.echo(df.to_csv(index=False))
        elif output_format == 'json':
            click.echo(df.to_json(indent=2))
        else:
            click.echo(df.to_string(index=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def metakg():
    """Meta knowledge graph commands"""
    pass


@metakg.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv', 'table']), default='table')
def data(output_format: str):
    """Get metadata for Knowledge Providers"""
    try:
        _, api_names = get_translator_kp_info()
        df = get_KP_metadata(api_names)
        if output_format == 'csv':
            click.echo(df.to_csv(index=False))
        elif output_format == 'json':
            click.echo(df.to_json(indent=2))
        else:
            click.echo(df.to_string(index=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def query():
    """Query orchestration commands"""
    pass


@query.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='json')
def predicates(output_format: str):
    """Get the predicates supported by each Translator API"""
    try:
        api_names, metakg_df, api_predicates = get_translator_API_predicates()
        if output_format == 'table':
            for api, preds in api_predicates.items():
                click.echo(f"\n{api}:")
                for pred in preds:
                    click.echo(f"  {pred}")
        else:
            print_json(api_predicates)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.argument('query_file', type=click.File('r'))
@click.argument('api_name')
@click.option('--output', '-o', type=click.File('w'), default='-')
def optimize(query_file, api_name: str, output):
    """Optimize a query JSON by removing unsupported predicates"""
    try:
        query_json = json.load(query_file)
        _, _, api_predicates = get_translator_API_predicates()
        result = optimize_query_json(query_json, api_name, api_predicates)
        json.dump(result, output, indent=2)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.argument('query_file', type=click.File('r'))
@click.argument('api_name')
@click.option('--output', '-o', type=click.File('w'), default='-')
def single(query_file, api_name: str, output):
    """Query an individual Knowledge Provider API"""
    try:
        query_json = json.load(query_file)
        _, api_names = get_translator_kp_info()
        _, _, api_predicates = get_translator_API_predicates()
        result = query_KP(api_name, query_json, api_names, api_predicates)
        json.dump(result, output, indent=2)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@query.command()
@click.argument('query_file', type=click.File('r'))
@click.argument('apis', nargs=-1, required=True)
@click.option('--workers', default=1, help='Number of parallel workers')
@click.option('--output', '-o', type=click.File('w'), default='-')
def parallel(query_file, apis: tuple, workers: int, output):
    """Query multiple APIs in parallel and merge results"""
    try:
        query_json = json.load(query_file)
        _, api_names = get_translator_kp_info()
        _, _, api_predicates = get_translator_API_predicates()
        result = parallel_api_query(query_json, list(apis), api_names, api_predicates, max_workers=workers)
        json.dump(result, output, indent=2)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def server():
    """MCP server commands"""
    pass


@server.command()
@click.option('--transport', type=click.Choice(['stdio', 'http']), default='stdio')
@click.option('--port', default=8000, help='Port for HTTP transport')
def start(transport: str, port: int):
    """Start the MCP server"""
    from .server import mcp
    if transport == 'http':
        mcp.run(transport='http', port=port)
    else:
        mcp.run()


if __name__ == '__main__':
    main()