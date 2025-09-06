"""Tests for TCT CLI functionality."""

import json
import tempfile
from unittest.mock import Mock, patch
from click.testing import CliRunner
import pytest

from TCT.cli import main


class TestCLI:
    """Test the CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_main_command_help(self):
        """Test that the main command shows help."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Translator Component Toolkit' in result.output
    
    def test_main_command_version(self):
        """Test that the main command shows version."""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
    
    def test_name_group_help(self):
        """Test name subcommand group help."""
        result = self.runner.invoke(main, ['name', '--help'])
        assert result.exit_code == 0
        assert 'Name resolution and lookup commands' in result.output
    
    def test_normalize_group_help(self):
        """Test normalize subcommand group help."""
        result = self.runner.invoke(main, ['normalize', '--help'])
        assert result.exit_code == 0
        assert 'Node normalization commands' in result.output
    
    def test_kp_group_help(self):
        """Test kp subcommand group help."""
        result = self.runner.invoke(main, ['kp', '--help'])
        assert result.exit_code == 0
        assert 'Knowledge Provider information commands' in result.output
    
    def test_metakg_group_help(self):
        """Test metakg subcommand group help."""
        result = self.runner.invoke(main, ['metakg', '--help'])
        assert result.exit_code == 0
        assert 'Meta knowledge graph commands' in result.output
    
    def test_query_group_help(self):
        """Test query subcommand group help."""
        result = self.runner.invoke(main, ['query', '--help'])
        assert result.exit_code == 0
        assert 'Query orchestration commands' in result.output
    
    def test_server_group_help(self):
        """Test server subcommand group help."""
        result = self.runner.invoke(main, ['server', '--help'])
        assert result.exit_code == 0
        assert 'MCP server commands' in result.output


class TestNameCommands:
    """Test name resolution CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.lookup')
    def test_name_lookup_simple(self, mock_lookup):
        """Test name lookup command with simple output."""
        mock_node = Mock()
        mock_node.curie = "HGNC:123"
        mock_node.label = "Test Gene"
        mock_lookup.return_value = mock_node
        
        result = self.runner.invoke(main, ['name', 'lookup', 'test gene', '--format', 'simple'])
        assert result.exit_code == 0
        assert "HGNC:123: Test Gene" in result.output
        mock_lookup.assert_called_once_with('test gene', return_top_response=True, return_synonyms=False)
    
    @patch('TCT.cli.lookup')
    def test_name_lookup_json(self, mock_lookup):
        """Test name lookup command with JSON output."""
        mock_node = Mock()
        mock_node.to_dict.return_value = {"curie": "HGNC:123", "label": "Test Gene"}
        mock_lookup.return_value = mock_node
        
        result = self.runner.invoke(main, ['name', 'lookup', 'test gene'])
        assert result.exit_code == 0
        mock_lookup.assert_called_once_with('test gene', return_top_response=True, return_synonyms=False)
    
    @patch('TCT.cli.lookup')
    def test_name_lookup_error(self, mock_lookup):
        """Test name lookup command with error."""
        mock_lookup.side_effect = Exception("Test error")
        
        result = self.runner.invoke(main, ['name', 'lookup', 'test gene'])
        assert result.exit_code == 1
        assert "Error: Test error" in result.output
    
    @patch('TCT.cli.synonyms')
    def test_synonyms_command(self, mock_synonyms):
        """Test synonyms command."""
        mock_synonyms.return_value = {"HGNC:123": Mock(label="Test Gene")}
        
        result = self.runner.invoke(main, ['name', 'synonyms', 'HGNC:123'])
        assert result.exit_code == 0
        mock_synonyms.assert_called_once_with('HGNC:123')
    
    @patch('TCT.cli.batch_lookup')
    def test_batch_command(self, mock_batch_lookup):
        """Test batch lookup command."""
        mock_batch_lookup.return_value = {"gene1": Mock(curie="HGNC:1", label="Gene 1")}
        
        result = self.runner.invoke(main, ['name', 'batch', 'gene1', 'gene2'])
        assert result.exit_code == 0
        mock_batch_lookup.assert_called_once_with(['gene1', 'gene2'], size=25, return_top_response=True, return_synonyms=False)


class TestNormalizeCommands:
    """Test node normalization CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.get_normalized_nodes')
    def test_normalize_nodes_command(self, mock_normalize):
        """Test normalize nodes command."""
        mock_node = Mock()
        mock_node.curie = "HGNC:123"
        mock_node.label = "Test Gene"
        mock_normalize.return_value = mock_node
        
        result = self.runner.invoke(main, ['normalize', 'nodes', 'HGNC:123'])
        assert result.exit_code == 0
        mock_normalize.assert_called_once_with('HGNC:123', return_equivalent_identifiers=False, conflate=True, drug_chemical_conflate=False)


class TestKPCommands:
    """Test knowledge provider CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.get_translator_kp_info')
    def test_kp_info_command(self, mock_kp_info):
        """Test KP info command."""
        import pandas as pd
        mock_df = pd.DataFrame({"api": ["test"], "url": ["http://test.com"]})
        mock_kp_info.return_value = (mock_df, {"test": "http://test.com"})
        
        result = self.runner.invoke(main, ['kp', 'info'])
        assert result.exit_code == 0


class TestMetaKGCommands:
    """Test meta knowledge graph CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.get_translator_kp_info')
    @patch('TCT.cli.get_KP_metadata')
    def test_metakg_data_command(self, mock_metakg, mock_kp_info):
        """Test metakg data command."""
        import pandas as pd
        mock_kp_info.return_value = (None, {"test": "http://test.com"})
        mock_metakg.return_value = pd.DataFrame({"predicate": ["biolink:treats"]})
        
        result = self.runner.invoke(main, ['metakg', 'data'])
        assert result.exit_code == 0


class TestQueryCommands:
    """Test query CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.get_translator_API_predicates')
    def test_query_predicates_command(self, mock_predicates):
        """Test query predicates command."""
        mock_predicates.return_value = (None, None, {"test_api": ["biolink:treats"]})
        
        result = self.runner.invoke(main, ['query', 'predicates'])
        assert result.exit_code == 0
    
    @patch('TCT.cli.get_translator_API_predicates')
    @patch('TCT.cli.optimize_query_json')
    def test_query_optimize_command(self, mock_optimize, mock_predicates):
        """Test query optimize command."""
        mock_predicates.return_value = (None, None, {"test_api": ["biolink:treats"]})
        mock_optimize.return_value = {"message": {"query_graph": {}}}
        
        query = {"message": {"query_graph": {"edges": {}}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(query, f)
            query_file = f.name
        
        result = self.runner.invoke(main, ['query', 'optimize', query_file, 'test_api'])
        assert result.exit_code == 0
    
    @patch('TCT.cli.get_translator_kp_info')
    @patch('TCT.cli.get_translator_API_predicates') 
    @patch('TCT.cli.query_KP')
    def test_query_single_command(self, mock_query, mock_predicates, mock_kp_info):
        """Test query single command."""
        mock_kp_info.return_value = (None, {"test_api": "http://test.com"})
        mock_predicates.return_value = (None, None, {"test_api": ["biolink:treats"]})
        mock_query.return_value = {"message": {"results": []}}
        
        query = {"message": {"query_graph": {"edges": {}}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(query, f)
            query_file = f.name
        
        result = self.runner.invoke(main, ['query', 'single', query_file, 'test_api'])
        assert result.exit_code == 0


class TestServerCommands:
    """Test MCP server CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('TCT.cli.mcp')
    def test_server_start_stdio(self, mock_mcp):
        """Test server start with stdio transport."""
        # Mock the run method to avoid actually starting the server
        mock_mcp.run = Mock()
        
        result = self.runner.invoke(main, ['server', 'start'])
        assert result.exit_code == 0
        mock_mcp.run.assert_called_once_with()
    
    @patch('TCT.cli.mcp')
    def test_server_start_http(self, mock_mcp):
        """Test server start with HTTP transport."""
        # Mock the run method to avoid actually starting the server
        mock_mcp.run = Mock()
        
        result = self.runner.invoke(main, ['server', 'start', '--transport', 'http', '--port', '9000'])
        assert result.exit_code == 0
        mock_mcp.run.assert_called_once_with(transport='http', port=9000)


class TestUtilityFunctions:
    """Test CLI utility functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_print_json_with_to_dict(self):
        """Test print_json with object having to_dict method."""
        from TCT.cli import print_json
        from unittest.mock import patch
        
        mock_obj = Mock()
        mock_obj.to_dict.return_value = {"test": "data"}
        
        with patch('TCT.cli.click.echo') as mock_echo:
            print_json(mock_obj)
            mock_echo.assert_called_once()
    
    def test_print_json_with_dataframe(self):
        """Test print_json with pandas DataFrame."""
        from TCT.cli import print_json
        from unittest.mock import patch
        import pandas as pd
        
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        
        with patch('TCT.cli.click.echo') as mock_echo:
            print_json(df)
            mock_echo.assert_called_once()
    
    def test_print_json_with_dict(self):
        """Test print_json with regular dictionary."""
        from TCT.cli import print_json
        from unittest.mock import patch
        
        data = {"test": "data", "number": 123}
        
        with patch('TCT.cli.click.echo') as mock_echo:
            print_json(data)
            mock_echo.assert_called_once()