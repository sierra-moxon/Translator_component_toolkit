"""Simple tests for TCT CLI functionality."""

from click.testing import CliRunner
from TCT.cli import main


def test_cli_help():
    """Test that CLI shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Translator Component Toolkit' in result.output

def test_cli_groups_exist():
    """Test that all CLI command groups exist."""
    runner = CliRunner()

    groups = ['name', 'normalize', 'kp', 'metakg', 'query', 'server']
    for group in groups:
        result = runner.invoke(main, [group, '--help'])
        assert result.exit_code == 0


def test_server_command_exists():
    """Test that server start command exists."""
    runner = CliRunner()
    result = runner.invoke(main, ['server', 'start', '--help'])
    assert result.exit_code == 0
    assert 'Start the MCP server' in result.output
