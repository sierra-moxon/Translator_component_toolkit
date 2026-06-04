"""
Command-line interface for the Translator Component Toolkit.

The CLI is generated from the schema-first :data:`schema.REGISTRY`, so it
mirrors the MCP tool surface by construction: every tool becomes a subcommand
under a group derived from ``ToolSpec.group``. Scalar required parameters are
positional arguments; optional parameters are options; complex parameters
(dicts/lists) are passed as JSON strings.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import click
import requests

from .errors import InvalidParameterError
from .io import (
    EXIT_NOT_FOUND,
    EXIT_UNEXPECTED,
    EXIT_UPSTREAM,
    EXIT_USAGE,
    serialize,
)
from .schema import REGISTRY, ParamSpec, ToolSpec, make_signed_callable


def _is_option(p: ParamSpec) -> bool:
    """Optional params and booleans become Click options; required scalars are arguments."""
    return p.type is bool or not p.required


def _is_json_param(p: ParamSpec) -> bool:
    """True if the parameter should be supplied as a JSON string on the CLI."""
    return p.type not in (str, int, float, bool)


def _dest(p: ParamSpec) -> str:
    return "param_" + p.name if _is_option(p) else p.name


def _json_callback(ctx, param, value):
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise click.BadParameter(f"{param.name} must be valid JSON: {e}") from e


def _echo_result(result: Any, as_json: bool) -> None:
    """Write a normalized tool result to stdout.

    ``serialize`` flattens dataclasses/DataFrames/tuples into JSON-safe
    primitives. With ``--json`` (the default) the result is emitted as JSON;
    with ``--no-json`` the serialized structure is printed in its Python repr
    for quick human scanning.
    """
    normalized = serialize(result)
    if as_json:
        click.echo(json.dumps(normalized, indent=2, default=str))
    else:
        click.echo(str(normalized))


def _build_command(spec: ToolSpec) -> click.Command:
    callable_ = make_signed_callable(spec)
    decorators = []

    for p in spec.params:
        flag = p.name.replace("_", "-")
        if p.type is bool:
            decorators.append(
                click.option(f"--{flag}/--no-{flag}", _dest(p), default=p.default, help=p.help)
            )
        elif _is_json_param(p):
            if p.required:
                decorators.append(click.argument(p.name, callback=_json_callback))
            else:
                decorators.append(
                    click.option(f"--{flag}", _dest(p), callback=_json_callback, default=None, help=p.help)
                )
        else:
            click_type = {int: int, float: float}.get(p.type, str)
            if p.required:
                decorators.append(click.argument(p.name, type=click_type))
            else:
                decorators.append(
                    click.option(f"--{flag}", _dest(p), type=click_type, default=p.default, help=p.help)
                )

    @click.pass_context
    def callback(ctx, **kwargs):
        # Map click destinations back to the spec parameter names.
        call_kwargs = {p.name: kwargs.get(_dest(p)) for p in spec.params}
        as_json = ctx.obj.get("json", True) if ctx.obj else True
        try:
            result = callable_(**call_kwargs)
        except InvalidParameterError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(EXIT_USAGE)
        except LookupError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(EXIT_NOT_FOUND)
        except requests.RequestException as e:
            click.echo(f"Error: upstream request failed: {e}", err=True)
            sys.exit(EXIT_UPSTREAM)
        except Exception as e:  # noqa: BLE001 - surfaced to the user
            click.echo(f"Error: {e}", err=True)
            sys.exit(EXIT_UNEXPECTED)
        _echo_result(result, as_json)

    command_name = spec.name.replace("_", "-")
    cmd = click.command(name=command_name, help=spec.summary)(callback)
    for decorator in reversed(decorators):
        cmd = decorator(cmd)
    return cmd


@click.group()
@click.version_option()
@click.option("--json/--no-json", "as_json", default=True,
              help="Emit machine-readable JSON to stdout (default) or a plain repr.")
@click.pass_context
def main(ctx, as_json: bool):
    """Translator Component Toolkit - biomedical knowledge graph tools.

    Data is written to stdout; diagnostics go to stderr. Exit codes: 0 success,
    2 usage/invalid parameter, 3 not found, 4 upstream API error, 1 unexpected.
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json


# Build one group per ToolSpec.group and attach generated commands.
_GROUP_HELP = {
    "name": "Name resolution and lookup commands.",
    "normalize": "Node normalization commands.",
    "kp": "Knowledge Provider information commands.",
    "metakg": "Meta knowledge graph commands.",
    "query": "Query orchestration commands.",
    "trapi": "TRAPI protocol commands.",
}

_groups: dict[str, click.Group] = {}
for _spec in REGISTRY:
    if _spec.group not in _groups:
        grp = click.Group(name=_spec.group, help=_GROUP_HELP.get(_spec.group, f"{_spec.group} commands."))
        _groups[_spec.group] = grp
        main.add_command(grp)
    _groups[_spec.group].add_command(_build_command(_spec))


@main.group()
def server():
    """MCP server commands."""


@server.command()
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio")
@click.option("--port", default=8000, help="Port for HTTP transport.")
def start(transport: str, port: int):
    """Start the MCP server."""
    from .server import mcp

    if transport == "http":
        mcp.run(transport="http", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
