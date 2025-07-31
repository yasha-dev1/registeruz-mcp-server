"""Tests for RegisterUZ MCP server."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from mcp import types
from mcp_server_registeruz.server import server, call_tool, list_tools
from mcp_server_registeruz.types import ApiResponse, TemplatesResponse, Template


class TestMCPServer:
    """Test MCP server functionality."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that all tools are listed correctly."""
        tools = await list_tools()
        
        assert len(tools) == 7
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "search_accounting_entities",
            "get_financial_statements",
            "get_financial_reports",
            "get_annual_reports",
            "get_templates",
            "get_remaining_count",
            "get_all_entity_ids"
        ]
        
        for expected in expected_tools:
            assert expected in tool_names
    
    @pytest.mark.asyncio
    async def test_search_accounting_entities_tool(self):
        """Test search_accounting_entities tool definition."""
        tools = await list_tools()
        tool = next(t for t in tools if t.name == "search_accounting_entities")
        
        assert tool.description == "Search for accounting entities (companies) in Slovak business register"
        assert "changed_from" in tool.inputSchema["properties"]
        assert "ico" in tool.inputSchema["properties"]
        assert "dic" in tool.inputSchema["properties"]
        assert "legal_form" in tool.inputSchema["properties"]
        assert tool.inputSchema["required"] == ["changed_from"]
    
    @pytest.mark.asyncio
    @patch('mcp_server_registeruz.server.RegisterUZClient')
    @patch('mcp_server_registeruz.server.get_config')
    async def test_call_tool_search_accounting_entities(self, mock_get_config, mock_client_class):
        """Test calling search_accounting_entities tool."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = ApiResponse(id=[1, 2, 3], existujeDalsieId=True)
        mock_client.get_accounting_entities.return_value = mock_response
        
        # Call tool
        arguments = {
            "changed_from": "2024-01-01",
            "ico": "12345678",
            "max_records": 10
        }
        
        result = await call_tool("search_accounting_entities", arguments)
        
        # Verify result
        assert len(result) == 1
        assert result[0].type == "text"
        
        response_data = json.loads(result[0].text)
        assert response_data["ids"] == [1, 2, 3]
        assert response_data["has_more"] is True
        assert response_data["count"] == 3
    
    @pytest.mark.asyncio
    @patch('mcp_server_registeruz.server.RegisterUZClient')
    @patch('mcp_server_registeruz.server.get_config')
    async def test_call_tool_get_templates(self, mock_get_config, mock_client_class):
        """Test calling get_templates tool."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        template = Template(
            id=1,
            nazov="Test Template",
            typ="Type A",
            verzia="1.0",
            platnost_od="2024-01-01",
            platnost_do=None
        )
        mock_response = TemplatesResponse(sablony=[template])
        mock_client.get_templates.return_value = mock_response
        
        # Call tool
        result = await call_tool("get_templates", {})
        
        # Verify result
        assert len(result) == 1
        assert result[0].type == "text"
        
        response_data = json.loads(result[0].text)
        assert len(response_data["templates"]) == 1
        assert response_data["templates"][0]["name"] == "Test Template"
        assert response_data["count"] == 1
    
    @pytest.mark.asyncio
    @patch('mcp_server_registeruz.server.RegisterUZClient')
    @patch('mcp_server_registeruz.server.get_config')
    async def test_call_tool_error_handling(self, mock_get_config, mock_client_class):
        """Test error handling in tool calls."""
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Simulate an error
        mock_client.get_financial_statements.side_effect = Exception("Test error")
        
        # Call tool
        arguments = {"changed_from": "2024-01-01"}
        result = await call_tool("get_financial_statements", arguments)
        
        # Verify error response
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Exception: Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: ValueError: Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    @patch('mcp_server_registeruz.server.RegisterUZClient')
    @patch('mcp_server_registeruz.server.get_config')
    async def test_call_tool_validation_error(self, mock_get_config, mock_client_class):
        """Test validation error handling."""
        from pydantic import ValidationError
        
        # Setup mocks
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Simulate validation error
        mock_client.get_accounting_entities.side_effect = ValidationError.from_exception_data(
            "ValidationError",
            [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
        )
        
        # Call tool
        arguments = {"changed_from": "2024-01-01"}
        result = await call_tool("search_accounting_entities", arguments)
        
        # Verify error response
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: ValidationError" in result[0].text