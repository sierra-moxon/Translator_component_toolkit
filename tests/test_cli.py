"""Tests for the registry-generated CLI."""

import requests
from click.testing import CliRunner

from translator_component_toolkit import name_resolver
from translator_component_toolkit.cli import main
from translator_component_toolkit.errors import InvalidParameterError
from translator_component_toolkit.io import (
    EXIT_NOT_FOUND,
    EXIT_OK,
    EXIT_UNEXPECTED,
    EXIT_UPSTREAM,
    EXIT_USAGE,
)
from translator_component_toolkit.schema import REGISTRY
from translator_component_toolkit.translator_node import TranslatorNode


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Translator Component Toolkit" in result.output


def test_expected_groups_exist():
    runner = CliRunner()
    for group in ["name", "normalize", "kp", "metakg", "query", "trapi", "server"]:
        result = runner.invoke(main, [group, "--help"])
        assert result.exit_code == 0, f"group {group} missing"


def test_every_registry_tool_has_a_command():
    runner = CliRunner()
    for spec in REGISTRY:
        command_name = spec.name.replace("_", "-")
        result = runner.invoke(main, [spec.group, command_name, "--help"])
        assert result.exit_code == 0, f"missing command {spec.group} {command_name}"
        assert command_name in result.output
        assert spec.summary.split()[0] in result.output


def test_server_start_command_exists():
    runner = CliRunner()
    result = runner.invoke(main, ["server", "start", "--help"])
    assert result.exit_code == 0
    assert "Start the MCP server" in result.output


def test_required_argument_is_enforced():
    runner = CliRunner()
    # lookup-name requires a query argument
    result = runner.invoke(main, ["name", "lookup-name"])
    assert result.exit_code != 0


def test_invalid_json_argument_is_rejected():
    runner = CliRunner()
    # get-metakg takes a JSON dict argument; pass invalid JSON
    result = runner.invoke(main, ["metakg", "get-metakg", "{not json"])
    assert result.exit_code == EXIT_USAGE
    assert "valid JSON" in result.output


def test_lookup_error_exits_not_found(monkeypatch):
    def boom(*args, **kwargs):
        raise LookupError("no match for 'ZZZ'")

    monkeypatch.setattr(name_resolver, "lookup", boom)
    runner = CliRunner()
    result = runner.invoke(main, ["name", "lookup-name", "ZZZ"])
    assert result.exit_code == EXIT_NOT_FOUND
    assert "no match" in result.stderr


def test_request_exception_exits_upstream(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.RequestException("connection refused")

    monkeypatch.setattr(name_resolver, "lookup", boom)
    runner = CliRunner()
    result = runner.invoke(main, ["name", "lookup-name", "AML"])
    assert result.exit_code == EXIT_UPSTREAM
    assert "upstream" in result.stderr


def test_unexpected_exception_exits_one(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(name_resolver, "lookup", boom)
    runner = CliRunner()
    result = runner.invoke(main, ["name", "lookup-name", "AML"])
    assert result.exit_code == EXIT_UNEXPECTED


def test_invalid_parameter_exits_usage():
    runner = CliRunner()
    # query-kp validates api_name against the (empty) api_names dict.
    result = runner.invoke(main, ["query", "query-kp", "Unknown", "{}", "{}", "{}"])
    assert result.exit_code == EXIT_USAGE


def test_data_goes_to_stdout_as_json(monkeypatch):
    node = TranslatorNode(curie="MONDO:0018874", label="acute myeloid leukemia")
    monkeypatch.setattr(name_resolver, "lookup", lambda *a, **k: node)
    runner = CliRunner()
    result = runner.invoke(main, ["name", "lookup-name", "AML"])
    assert result.exit_code == EXIT_OK
    assert '"curie": "MONDO:0018874"' in result.output


def test_no_json_flag_emits_plain_repr(monkeypatch):
    node = TranslatorNode(curie="MONDO:0018874", label="acute myeloid leukemia")
    monkeypatch.setattr(name_resolver, "lookup", lambda *a, **k: node)
    runner = CliRunner()
    result = runner.invoke(main, ["--no-json", "name", "lookup-name", "AML"])
    assert result.exit_code == EXIT_OK
    assert "MONDO:0018874" in result.output
    assert '"curie"' not in result.output


def test_invalid_parameter_error_is_importable():
    # Guards the CLI's exception mapping import.
    assert issubclass(InvalidParameterError, ValueError)
