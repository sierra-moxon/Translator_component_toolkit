"""Tests for the registry-generated CLI."""

from click.testing import CliRunner

from translator_component_toolkit.cli import main
from translator_component_toolkit.schema import REGISTRY


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
    assert result.exit_code != 0
    assert "valid JSON" in result.output
