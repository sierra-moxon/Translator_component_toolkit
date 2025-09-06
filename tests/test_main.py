"""Tests for main.py MCP server entry point."""

import pytest
from unittest.mock import Mock, patch


class TestMainEntry:
    """Test the main.py entry point functionality."""
    
    @patch('main.mcp')
    def test_main_function_calls_mcp_run(self, mock_mcp):
        """Test that main() function calls mcp.run()."""
        from main import main
        
        # Mock the run method
        mock_mcp.run = Mock()
        
        # Call main function
        main()
        
        # Verify mcp.run() was called
        mock_mcp.run.assert_called_once()
    
    @patch('main.mcp')
    def test_main_entry_point(self, mock_mcp):
        """Test the main entry point when run as script."""
        # Mock the run method
        mock_mcp.run = Mock()
        
        # Import and execute the main block
        import main
        
        # Mock __name__ to be '__main__'
        with patch.object(main, '__name__', '__main__'):
            # This would normally execute main(), but we'll call it directly
            main.main()
        
        # Verify mcp.run() was called
        mock_mcp.run.assert_called_once()
    
    def test_main_imports_correctly(self):
        """Test that main.py imports the necessary components."""
        import main
        
        # Check that main has the required attributes
        assert hasattr(main, 'main'), "main.py should have a main() function"
        assert hasattr(main, 'mcp'), "main.py should import mcp from TCT.server"
        assert callable(main.main), "main() should be callable"
    
    def test_main_function_signature(self):
        """Test that main() function has the correct signature."""
        import main
        import inspect
        
        # Get the main function signature
        sig = inspect.signature(main.main)
        
        # Should have no parameters
        assert len(sig.parameters) == 0, "main() should take no parameters"
    
    @patch('main.mcp')
    def test_main_docstring(self, mock_mcp):
        """Test that main() function has proper documentation."""
        from main import main
        
        # Check that the function has a docstring
        assert main.__doc__ is not None, "main() should have a docstring"
        assert "Entry point for tct-server script" in main.__doc__, "Docstring should describe the entry point"


class TestMCPServerIntegration:
    """Test integration between main.py and the MCP server."""
    
    @patch('TCT.server.mcp')
    def test_mcp_server_accessible_from_main(self, mock_server_mcp):
        """Test that main.py can access the MCP server instance."""
        # This tests the import chain: main.py -> TCT.server.mcp
        import main
        
        # The mcp object should be available in main
        assert hasattr(main, 'mcp'), "main.py should have access to mcp server"
    
    @patch('TCT.server.mcp')
    def test_server_configuration_passed_through(self, mock_server_mcp):
        """Test that server configuration is properly passed through."""
        from main import main
        
        # Mock the run method to capture arguments
        mock_server_mcp.run = Mock()
        
        # Call main
        main()
        
        # Verify run was called with no arguments (default stdio mode)
        mock_server_mcp.run.assert_called_once_with()
    
    def test_main_module_structure(self):
        """Test the overall structure of main.py module."""
        import main
        
        # Check module-level attributes
        expected_attributes = ['main', 'mcp']
        for attr in expected_attributes:
            assert hasattr(main, attr), f"main.py should have {attr} attribute"
        
        # Check that it's a minimal wrapper
        import inspect
        
        # Get the source lines to verify it's simple
        source_lines = inspect.getsourcelines(main)[0]
        
        # Should be a small file (less than 20 lines including imports and comments)
        assert len(source_lines) < 20, "main.py should be a simple wrapper module"


class TestServerScriptIntegration:
    """Test the tct-server script integration."""
    
    def test_pyproject_toml_script_configuration(self):
        """Test that pyproject.toml correctly configures the tct-server script."""
        try:
            import tomllib
        except ImportError:
            # For Python < 3.11, use tomli
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("tomllib/tomli not available")
        
        # Read pyproject.toml
        with open('/Users/SMoxon/Documents/src/Translator_component_toolkit/pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        
        # Check that tct-server script is configured
        scripts = config.get('project', {}).get('scripts', {})
        assert 'tct-server' in scripts, "tct-server script should be configured in pyproject.toml"
        assert scripts['tct-server'] == 'main:main', "tct-server should point to main:main"
    
    @patch('main.mcp')
    def test_script_entry_point_functionality(self, mock_mcp):
        """Test that the script entry point works correctly."""
        # This simulates what happens when `tct-server` command is run
        mock_mcp.run = Mock()
        
        # Import and call main as the script would
        from main import main
        main()
        
        # Verify the server starts
        mock_mcp.run.assert_called_once()


class TestErrorHandling:
    """Test error handling in main.py."""
    
    @patch('main.mcp')
    def test_main_handles_mcp_import_error(self, mock_mcp):
        """Test behavior when MCP server import fails."""
        # This is more of a structural test since we can't easily mock import failures
        # after the module is already imported. But we can verify the import structure.
        
        import main
        
        # Verify that the import is done correctly
        assert main.mcp is not None, "MCP server should be imported successfully"
    
    @patch('main.mcp')
    def test_main_handles_run_exceptions(self, mock_mcp):
        """Test that main() handles exceptions from mcp.run()."""
        # Mock mcp.run to raise an exception
        mock_mcp.run.side_effect = Exception("Server startup error")
        
        from main import main
        
        # The function should let the exception propagate
        # (this is expected behavior for a simple entry point)
        with pytest.raises(Exception, match="Server startup error"):
            main()