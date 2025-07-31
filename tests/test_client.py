"""Tests for RegisterUZ API client."""

import pytest
from unittest.mock import Mock, patch
import httpx

from mcp_server_registeruz.client import (
    RegisterUZClient,
    RegisterUZError,
    RegisterUZAPIError,
)
from mcp_server_registeruz.config import RegisterUZConfig
from mcp_server_registeruz.types import (
    AccountingEntitySearchParams,
    ApiResponse,
    BaseSearchParams,
    EntityType,
    RemainingCountResponse,
    TemplatesResponse,
)


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return RegisterUZConfig(
        base_url="https://api.test.com",
        timeout=10,
        max_records=100,
        default_from_date="2020-01-01"
    )


@pytest.fixture
def client(mock_config):
    """Create a client instance with mocked configuration."""
    return RegisterUZClient(mock_config)


class TestRegisterUZClient:
    """Test RegisterUZ client functionality."""
    
    def test_client_initialization(self, mock_config):
        """Test client initialization."""
        client = RegisterUZClient(mock_config)
        assert client.base_url == "https://api.test.com"
        assert client.config.timeout == 10
        assert client.config.max_records == 100
    
    def test_client_context_manager(self, mock_config):
        """Test client works as context manager."""
        with RegisterUZClient(mock_config) as client:
            assert isinstance(client, RegisterUZClient)
    
    @patch.object(httpx.Client, 'get')
    def test_get_accounting_entities_success(self, mock_get, client):
        """Test successful retrieval of accounting entities."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": [1, 2, 3],
            "existujeDalsieId": True
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        params = AccountingEntitySearchParams(
            zmenene_od="2024-01-01",
            ico="12345678",
            max_zaznamov=10
        )
        
        result = client.get_accounting_entities(params)
        
        assert isinstance(result, ApiResponse)
        assert result.id == [1, 2, 3]
        assert result.existujeDalsieId is True
        
        # Check correct parameters were passed
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/uctovne-jednotky"
        assert call_args[1]["params"]["zmenene-od"] == "2024-01-01"
        assert call_args[1]["params"]["ico"] == "12345678"
        assert call_args[1]["params"]["max-zaznamov"] == 10
    
    @patch.object(httpx.Client, 'get')
    def test_get_financial_statements_success(self, mock_get, client):
        """Test successful retrieval of financial statements."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": [10, 20, 30],
            "existujeDalsieId": False
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        params = BaseSearchParams(zmenene_od="2024-01-01")
        result = client.get_financial_statements(params)
        
        assert isinstance(result, ApiResponse)
        assert result.id == [10, 20, 30]
        assert result.existujeDalsieId is False
    
    @patch.object(httpx.Client, 'get')
    def test_get_templates_success(self, mock_get, client):
        """Test successful retrieval of templates."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sablony": [
                {
                    "id": 1,
                    "nazov": "Template 1",
                    "typ": "Type A",
                    "verzia": "1.0",
                    "platnost_od": "2024-01-01",
                    "platnost_do": None
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = client.get_templates()
        
        assert isinstance(result, TemplatesResponse)
        assert len(result.sablony) == 1
        assert result.sablony[0].nazov == "Template 1"
    
    @patch.object(httpx.Client, 'get')
    def test_get_remaining_count_success(self, mock_get, client):
        """Test successful retrieval of remaining count."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pocet": 1000}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = client.get_remaining_count(EntityType.UCTOVNE_JEDNOTKY)
        
        assert isinstance(result, RemainingCountResponse)
        assert result.pocet == 1000
    
    @patch.object(httpx.Client, 'get')
    def test_api_error_handling(self, mock_get, client):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=mock_response
        )
        mock_get.return_value = mock_response
        
        params = BaseSearchParams(zmenene_od="2024-01-01")
        
        with pytest.raises(RegisterUZAPIError) as exc_info:
            client.get_financial_statements(params)
        
        assert "API request failed" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    @patch.object(httpx.Client, 'get')
    def test_json_decode_error(self, mock_get, client):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        params = BaseSearchParams(zmenene_od="2024-01-01")
        
        with pytest.raises(RegisterUZAPIError) as exc_info:
            client.get_financial_statements(params)
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch.object(httpx.Client, 'get')
    def test_get_all_ids_pagination(self, mock_get, client):
        """Test automatic pagination in get_all_ids."""
        # First response
        response1 = Mock()
        response1.status_code = 200
        response1.json.return_value = {
            "id": [1, 2, 3],
            "existujeDalsieId": True
        }
        response1.raise_for_status = Mock()
        
        # Second response
        response2 = Mock()
        response2.status_code = 200
        response2.json.return_value = {
            "id": [4, 5],
            "existujeDalsieId": False
        }
        response2.raise_for_status = Mock()
        
        mock_get.side_effect = [response1, response2]
        
        result = client.get_all_ids(
            EntityType.UCTOVNE_JEDNOTKY,
            from_date="2024-01-01"
        )
        
        assert result == [1, 2, 3, 4, 5]
        assert mock_get.call_count == 2
        
        # Check second call has continue_after_id
        second_call = mock_get.call_args_list[1]
        assert second_call[1]["params"]["pokracovat-za-id"] == 3
    
    @patch.object(httpx.Client, 'get')
    def test_get_all_ids_with_limit(self, mock_get, client):
        """Test get_all_ids respects max_total limit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": [1, 2, 3, 4, 5],
            "existujeDalsieId": True
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = client.get_all_ids(
            EntityType.UCTOVNE_JEDNOTKY,
            from_date="2024-01-01",
            max_total=3
        )
        
        assert result == [1, 2, 3]
        assert mock_get.call_count == 1