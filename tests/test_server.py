"""Tests for TCT MCP Server functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp.shared.exceptions import McpError

from TCT.server import mcp


class TestMCPServer:
    """Test the MCP server setup and basic functionality."""
    
    def test_mcp_server_exists(self):
        """Test that the MCP server instance exists."""
        assert mcp is not None
        assert hasattr(mcp, 'name')
        assert mcp.name == "translator-toolkit"
    
    def test_mcp_server_has_tools(self):
        """Test that the MCP server has registered tools."""
        # Get list of registered tools
        tools = mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        
        # Check for expected tools
        expected_tools = [
            'name_lookup',
            'get_name_synonyms', 
            'batch_name_lookup',
            'normalize_nodes',
            'get_kp_info',
            'get_metakg_data',
            'add_custom_api_to_metakg',
            'add_plover_apis_to_metakg',
            'get_api_predicates',
            'optimize_query_for_api',
            'query_knowledge_provider',
            'parallel_query_apis',
            'trapi_query_endpoint'
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in registered tools"


class TestNameResolverTools:
    """Test name resolver MCP tools."""
    
    @patch('TCT.server.lookup')
    def test_name_lookup_success(self, mock_lookup):
        """Test successful name lookup."""
        mock_node = Mock()
        mock_node.curie = "HGNC:123"
        mock_node.label = "Test Gene"
        mock_lookup.return_value = mock_node
        
        from TCT.server import name_lookup
        result = name_lookup("test gene")
        
        assert result == mock_node
        mock_lookup.assert_called_once_with("test gene", True, False)
    
    @patch('TCT.server.lookup')
    def test_name_lookup_error(self, mock_lookup):
        """Test name lookup with error."""
        mock_lookup.side_effect = Exception("Test error")
        
        from TCT.server import name_lookup
        with pytest.raises(McpError) as exc_info:
            name_lookup("test gene")
        
        assert "Name lookup error: Test error" in str(exc_info.value)
    
    @patch('TCT.server.synonyms')
    def test_get_name_synonyms_success(self, mock_synonyms):
        """Test successful synonyms lookup."""
        mock_result = {"HGNC:123": Mock(label="Test Gene")}
        mock_synonyms.return_value = mock_result
        
        from TCT.server import get_name_synonyms
        result = get_name_synonyms("HGNC:123")
        
        assert result == mock_result
        mock_synonyms.assert_called_once_with("HGNC:123")
    
    @patch('TCT.server.synonyms')
    def test_get_name_synonyms_error(self, mock_synonyms):
        """Test synonyms lookup with error."""
        mock_synonyms.side_effect = Exception("Synonyms error")
        
        from TCT.server import get_name_synonyms
        with pytest.raises(McpError) as exc_info:
            get_name_synonyms("HGNC:123")
        
        assert "Synonyms lookup error: Synonyms error" in str(exc_info.value)
    
    @patch('TCT.server.batch_lookup')
    def test_batch_name_lookup_success(self, mock_batch_lookup):
        """Test successful batch name lookup."""
        mock_result = {"gene1": Mock(curie="HGNC:1", label="Gene 1")}
        mock_batch_lookup.return_value = mock_result
        
        from TCT.server import batch_name_lookup
        result = batch_name_lookup(["gene1", "gene2"])
        
        assert result == mock_result
        mock_batch_lookup.assert_called_once_with(["gene1", "gene2"], 25, True, False)
    
    @patch('TCT.server.batch_lookup')
    def test_batch_name_lookup_error(self, mock_batch_lookup):
        """Test batch name lookup with error."""
        mock_batch_lookup.side_effect = Exception("Batch error")
        
        from TCT.server import batch_name_lookup
        with pytest.raises(McpError) as exc_info:
            batch_name_lookup(["gene1", "gene2"])
        
        assert "Batch lookup error: Batch error" in str(exc_info.value)


class TestNodeNormalizerTools:
    """Test node normalizer MCP tools."""
    
    @patch('TCT.server.get_normalized_nodes')
    def test_normalize_nodes_success(self, mock_normalize):
        """Test successful node normalization."""
        mock_node = Mock()
        mock_node.curie = "HGNC:123"
        mock_node.label = "Test Gene"
        mock_normalize.return_value = mock_node
        
        from TCT.server import normalize_nodes
        result = normalize_nodes("HGNC:123")
        
        assert result == mock_node
        mock_normalize.assert_called_once_with("HGNC:123", False, conflate=True, drug_chemical_conflate=False)
    
    @patch('TCT.server.get_normalized_nodes')
    def test_normalize_nodes_error(self, mock_normalize):
        """Test node normalization with error."""
        mock_normalize.side_effect = Exception("Normalization error")
        
        from TCT.server import normalize_nodes
        with pytest.raises(McpError) as exc_info:
            normalize_nodes("HGNC:123")
        
        assert "Node normalization error: Normalization error" in str(exc_info.value)


class TestKPInfoTools:
    """Test knowledge provider info MCP tools."""
    
    @patch('TCT.server.get_translator_kp_info')
    def test_get_kp_info_success(self, mock_kp_info):
        """Test successful KP info retrieval."""
        import pandas as pd
        mock_df = pd.DataFrame({"api": ["test"], "url": ["http://test.com"]})
        mock_api_names = {"test": "http://test.com"}
        mock_kp_info.return_value = (mock_df, mock_api_names)
        
        from TCT.server import get_kp_info
        result = get_kp_info()
        
        assert result == (mock_df, mock_api_names)
        mock_kp_info.assert_called_once()
    
    @patch('TCT.server.get_translator_kp_info')
    def test_get_kp_info_error(self, mock_kp_info):
        """Test KP info retrieval with error."""
        mock_kp_info.side_effect = Exception("KP info error")
        
        from TCT.server import get_kp_info
        with pytest.raises(McpError) as exc_info:
            get_kp_info()
        
        assert "KP info error: KP info error" in str(exc_info.value)


class TestMetaKGTools:
    """Test meta knowledge graph MCP tools."""
    
    @patch('TCT.server.get_KP_metadata')
    def test_get_metakg_data_success(self, mock_metakg):
        """Test successful MetaKG data retrieval."""
        import pandas as pd
        mock_df = pd.DataFrame({"predicate": ["biolink:treats"]})
        mock_metakg.return_value = mock_df
        
        from TCT.server import get_metakg_data
        result = get_metakg_data({"test": "http://test.com"})
        
        assert result == mock_df
        mock_metakg.assert_called_once_with({"test": "http://test.com"})
    
    @patch('TCT.server.get_KP_metadata')
    def test_get_metakg_data_error(self, mock_metakg):
        """Test MetaKG data retrieval with error."""
        mock_metakg.side_effect = Exception("MetaKG error")
        
        from TCT.server import get_metakg_data
        with pytest.raises(McpError) as exc_info:
            get_metakg_data({"test": "http://test.com"})
        
        assert "MetaKG data error: MetaKG error" in str(exc_info.value)
    
    @patch('TCT.server.add_new_API_for_query')
    def test_add_custom_api_success(self, mock_add_api):
        """Test successful custom API addition."""
        import pandas as pd
        mock_api_names = {"existing": "http://existing.com"}
        mock_df = pd.DataFrame({"predicate": ["biolink:treats"]})
        mock_add_api.return_value = (mock_api_names, mock_df)
        
        from TCT.server import add_custom_api_to_metakg
        result = add_custom_api_to_metakg(
            mock_api_names, mock_df, "new_api", "http://new.com", 
            "biolink:treats", "Gene", "Disease"
        )
        
        assert result == (mock_api_names, mock_df)
        mock_add_api.assert_called_once_with(
            mock_api_names, mock_df, "new_api", "http://new.com",
            "biolink:treats", "Gene", "Disease"
        )
    
    @patch('TCT.server.add_plover_API')
    def test_add_plover_apis_success(self, mock_add_plover):
        """Test successful Plover APIs addition."""
        import pandas as pd
        mock_api_names = {"existing": "http://existing.com"}
        mock_df = pd.DataFrame({"predicate": ["biolink:treats"]})
        mock_add_plover.return_value = (mock_api_names, mock_df)
        
        from TCT.server import add_plover_apis_to_metakg
        result = add_plover_apis_to_metakg(mock_api_names, mock_df)
        
        assert result == (mock_api_names, mock_df)
        mock_add_plover.assert_called_once_with(mock_api_names, mock_df)


class TestQueryTools:
    """Test query MCP tools."""
    
    @patch('TCT.server.get_translator_API_predicates')
    def test_get_api_predicates_success(self, mock_predicates):
        """Test successful API predicates retrieval."""
        mock_result = ({"test": "url"}, Mock(), {"test": ["biolink:treats"]})
        mock_predicates.return_value = mock_result
        
        from TCT.server import get_api_predicates
        result = get_api_predicates()
        
        assert result == mock_result
        mock_predicates.assert_called_once()
    
    @patch('TCT.server.get_translator_API_predicates')
    def test_get_api_predicates_error(self, mock_predicates):
        """Test API predicates retrieval with error."""
        mock_predicates.side_effect = Exception("Predicates error")
        
        from TCT.server import get_api_predicates
        with pytest.raises(McpError) as exc_info:
            get_api_predicates()
        
        assert "API predicates error: Predicates error" in str(exc_info.value)
    
    @patch('TCT.server.optimize_query_json')
    def test_optimize_query_success(self, mock_optimize):
        """Test successful query optimization."""
        mock_query = {"message": {"query_graph": {}}}
        mock_optimize.return_value = mock_query
        
        from TCT.server import optimize_query_for_api
        result = optimize_query_for_api(mock_query, "test_api", {"test_api": ["biolink:treats"]})
        
        assert result == mock_query
        mock_optimize.assert_called_once_with(mock_query, "test_api", {"test_api": ["biolink:treats"]})
    
    @patch('TCT.server.optimize_query_json')
    def test_optimize_query_error(self, mock_optimize):
        """Test query optimization with error."""
        mock_optimize.side_effect = Exception("Optimization error")
        
        from TCT.server import optimize_query_for_api
        with pytest.raises(McpError) as exc_info:
            optimize_query_for_api({}, "test_api", {})
        
        assert "Query optimization error: Optimization error" in str(exc_info.value)
    
    @patch('TCT.server.query_KP')
    def test_query_knowledge_provider_success(self, mock_query):
        """Test successful knowledge provider query."""
        mock_result = {"message": {"results": []}}
        mock_query.return_value = mock_result
        
        from TCT.server import query_knowledge_provider
        result = query_knowledge_provider("test_api", {}, {"test_api": "url"}, {"test_api": ["biolink:treats"]})
        
        assert result == mock_result
        mock_query.assert_called_once_with("test_api", {}, {"test_api": "url"}, {"test_api": ["biolink:treats"]})
    
    @patch('TCT.server.query_KP')
    def test_query_knowledge_provider_error(self, mock_query):
        """Test knowledge provider query with error."""
        mock_query.side_effect = Exception("Query error")
        
        from TCT.server import query_knowledge_provider
        with pytest.raises(McpError) as exc_info:
            query_knowledge_provider("test_api", {}, {}, {})
        
        assert "KP query error: Query error" in str(exc_info.value)
    
    @patch('TCT.server.parallel_api_query')
    def test_parallel_query_apis_success(self, mock_parallel):
        """Test successful parallel API query."""
        mock_result = {"message": {"results": []}}
        mock_parallel.return_value = mock_result
        
        from TCT.server import parallel_query_apis
        result = parallel_query_apis({}, ["api1", "api2"], {"api1": "url1"}, {"api1": ["biolink:treats"]})
        
        assert result == mock_result
        mock_parallel.assert_called_once_with({}, ["api1", "api2"], {"api1": "url1"}, {"api1": ["biolink:treats"]}, 1)
    
    @patch('TCT.server.parallel_api_query')
    def test_parallel_query_apis_error(self, mock_parallel):
        """Test parallel API query with error."""
        mock_parallel.side_effect = Exception("Parallel query error")
        
        from TCT.server import parallel_query_apis
        with pytest.raises(McpError) as exc_info:
            parallel_query_apis({}, [], {}, {})
        
        assert "Parallel query error: Parallel query error" in str(exc_info.value)


class TestTRAPITools:
    """Test TRAPI MCP tools."""
    
    @patch('TCT.server.trapi_query')
    def test_trapi_query_endpoint_success(self, mock_trapi):
        """Test successful TRAPI query."""
        mock_result = {"message": {"results": []}}
        mock_trapi.return_value = mock_result
        
        from TCT.server import trapi_query_endpoint
        result = trapi_query_endpoint("http://test.com/query")
        
        assert result == mock_result
        mock_trapi.assert_called_once_with("http://test.com/query")
    
    @patch('TCT.server.trapi_query')
    def test_trapi_query_endpoint_error(self, mock_trapi):
        """Test TRAPI query with error."""
        mock_trapi.side_effect = Exception("TRAPI error")
        
        from TCT.server import trapi_query_endpoint
        with pytest.raises(McpError) as exc_info:
            trapi_query_endpoint("http://test.com/query")
        
        assert "TRAPI query error: TRAPI error" in str(exc_info.value)