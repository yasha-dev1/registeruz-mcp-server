"""HTTP client for RegisterUZ API."""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import httpx
from httpx import HTTPError, Response

from .config import RegisterUZConfig
from .types import (
    AccountingEntityDetail,
    AccountingEntitySearchParams,
    AnnualReportDetail,
    ApiResponse,
    BaseSearchParams,
    EntityType,
    FinancialReportDetail,
    FinancialStatementDetail,
    RemainingCountResponse,
    TemplatesResponse,
)

logger = logging.getLogger(__name__)


class RegisterUZError(Exception):
    """Base exception for RegisterUZ API errors."""
    pass


class RegisterUZAPIError(RegisterUZError):
    """API request failed."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RegisterUZClient:
    """Client for interacting with RegisterUZ API."""
    
    def __init__(self, config: Optional[RegisterUZConfig] = None):
        """Initialize the RegisterUZ client.
        
        Args:
            config: Configuration object. If None, will use default config.
        """
        self.config = config or RegisterUZConfig()
        self.base_url = str(self.config.base_url)
        
        # Configure httpx client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.config.timeout),
            headers={
                "Accept": "application/json",
                "User-Agent": "RegisterUZ-MCP-Server/0.1.0"
            }
        )
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close client."""
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def _handle_response(self, response: Response) -> Dict[str, Any]:
        """Handle API response and raise exceptions for errors.
        
        Args:
            response: HTTP response from the API
            
        Returns:
            Parsed JSON response
            
        Raises:
            RegisterUZAPIError: If the API returns an error
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise RegisterUZAPIError(
                f"API request failed: {e}",
                status_code=e.response.status_code
            )
        
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise RegisterUZAPIError(f"Invalid JSON response: {e}")
    
    def _build_params(self, params: BaseSearchParams) -> Dict[str, Any]:
        """Build query parameters from Pydantic model.
        
        Args:
            params: Search parameters
            
        Returns:
            Dictionary of query parameters
        """
        query_params = {"zmenene-od": params.zmenene_od}
        
        if params.pokracovat_za_id is not None:
            query_params["pokracovat-za-id"] = params.pokracovat_za_id
        
        if params.max_zaznamov is not None:
            query_params["max-zaznamov"] = params.max_zaznamov
        
        return query_params
    
    def get_accounting_entities(
        self,
        params: AccountingEntitySearchParams
    ) -> ApiResponse:
        """Get accounting entity identifiers.
        
        Args:
            params: Search parameters
            
        Returns:
            API response with entity IDs
        """
        query_params = self._build_params(params)
        
        # Add entity-specific parameters
        if params.ico:
            query_params["ico"] = params.ico
        if params.dic:
            query_params["dic"] = params.dic
        if params.pravna_forma:
            query_params["pravna-forma"] = (
                params.pravna_forma.value 
                if hasattr(params.pravna_forma, 'value') 
                else params.pravna_forma
            )
        
        try:
            response = self.client.get("/uctovne-jednotky", params=query_params)
            data = self._handle_response(response)
            return ApiResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get accounting entities: {e}")
            raise RegisterUZAPIError(f"Failed to get accounting entities: {e}")
    
    def get_financial_statements(
        self,
        params: BaseSearchParams
    ) -> ApiResponse:
        """Get financial statement identifiers.
        
        Args:
            params: Search parameters
            
        Returns:
            API response with statement IDs
        """
        query_params = self._build_params(params)
        
        try:
            response = self.client.get("/uctovne-zavierky", params=query_params)
            data = self._handle_response(response)
            return ApiResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get financial statements: {e}")
            raise RegisterUZAPIError(f"Failed to get financial statements: {e}")
    
    def get_financial_reports(
        self,
        params: BaseSearchParams
    ) -> ApiResponse:
        """Get financial report identifiers.
        
        Args:
            params: Search parameters
            
        Returns:
            API response with report IDs
        """
        query_params = self._build_params(params)
        
        try:
            response = self.client.get("/uctovne-vykazy", params=query_params)
            data = self._handle_response(response)
            return ApiResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get financial reports: {e}")
            raise RegisterUZAPIError(f"Failed to get financial reports: {e}")
    
    def get_annual_reports(
        self,
        params: BaseSearchParams
    ) -> ApiResponse:
        """Get annual report identifiers.
        
        Args:
            params: Search parameters
            
        Returns:
            API response with report IDs
        """
        query_params = self._build_params(params)
        
        try:
            response = self.client.get("/vyrocne-spravy", params=query_params)
            data = self._handle_response(response)
            return ApiResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get annual reports: {e}")
            raise RegisterUZAPIError(f"Failed to get annual reports: {e}")
    
    def get_remaining_count(
        self,
        entity_type: EntityType
    ) -> RemainingCountResponse:
        """Get count of remaining IDs for entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Response with remaining count
        """
        try:
            response = self.client.get(f"/zostavajuce-id/{entity_type.value}")
            data = self._handle_response(response)
            return RemainingCountResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get remaining count: {e}")
            raise RegisterUZAPIError(f"Failed to get remaining count: {e}")
    
    def get_templates(self) -> TemplatesResponse:
        """Get all report templates.
        
        Returns:
            Response with template list
        """
        try:
            response = self.client.get("/sablony")
            data = self._handle_response(response)
            return TemplatesResponse(**data)
        except HTTPError as e:
            logger.error(f"Failed to get templates: {e}")
            raise RegisterUZAPIError(f"Failed to get templates: {e}")
    
    def get_all_ids(
        self,
        entity_type: EntityType,
        from_date: Optional[str] = None,
        max_total: Optional[int] = None
    ) -> List[int]:
        """Get all IDs for an entity type with automatic pagination.
        
        Args:
            entity_type: Type of entity to fetch
            from_date: Date from which to retrieve changed records
            max_total: Maximum total records to retrieve (None for all)
            
        Returns:
            List of all entity IDs
        """
        from_date = from_date or self.config.default_from_date
        all_ids: List[int] = []
        continue_after_id: Optional[int] = None
        
        while True:
            # Prepare parameters based on entity type
            if entity_type == EntityType.UCTOVNE_JEDNOTKY:
                params = AccountingEntitySearchParams(
                    zmenene_od=from_date,
                    pokracovat_za_id=continue_after_id,
                    max_zaznamov=self.config.max_records
                )
                response = self.get_accounting_entities(params)
            else:
                params = BaseSearchParams(
                    zmenene_od=from_date,
                    pokracovat_za_id=continue_after_id,
                    max_zaznamov=self.config.max_records
                )
                
                if entity_type == EntityType.UCTOVNE_ZAVIERKY:
                    response = self.get_financial_statements(params)
                elif entity_type == EntityType.UCTOVNE_VYKAZY:
                    response = self.get_financial_reports(params)
                elif entity_type == EntityType.VYROCNE_SPRAVY:
                    response = self.get_annual_reports(params)
                else:
                    raise ValueError(f"Unknown entity type: {entity_type}")
            
            all_ids.extend(response.id)
            
            # Check if we've reached the limit
            if max_total and len(all_ids) >= max_total:
                all_ids = all_ids[:max_total]
                break
            
            # Check if there are more records
            if not response.existujeDalsieId or not response.id:
                break
            
            # Set up for next iteration
            continue_after_id = response.id[-1]
        
        return all_ids
    
    def get_entity_suggestions(self, query: str) -> List[str]:
        """Get entity name suggestions based on a search query.
        
        Args:
            query: The search term to get suggestions for
            
        Returns:
            List of entity name suggestions
        """
        try:
            # Use a different base URL for the suggestion endpoint
            suggestion_url = "https://www.registeruz.sk/cruz-public/domain/suggestion/search"
            
            # Create a separate request since this uses a different base URL
            response = httpx.get(
                suggestion_url,
                params={"query": query},
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "Accept": "application/json",
                    "User-Agent": "RegisterUZ-MCP-Server/0.1.0"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract suggestions from the response
            # The API might return a list of objects with suggestion text
            # Adjust based on actual API response structure
            if isinstance(data, list):
                return [item if isinstance(item, str) else str(item) for item in data]
            elif isinstance(data, dict) and "suggestions" in data:
                return data["suggestions"]
            else:
                # Fallback: try to extract meaningful data
                return [str(data)]
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise RegisterUZAPIError(
                f"Failed to get entity suggestions: {e}",
                status_code=e.response.status_code
            )
        except Exception as e:
            logger.error(f"Failed to get entity suggestions: {e}")
            raise RegisterUZAPIError(f"Failed to get entity suggestions: {e}")
    
    def get_accounting_entity_detail(self, entity_id: int) -> AccountingEntityDetail:
        """Get detailed information about an accounting entity.
        
        Args:
            entity_id: The accounting entity ID
            
        Returns:
            Detailed entity information
        """
        try:
            response = self.client.get(
                "/uctovna-jednotka",
                params={"id": entity_id}
            )
            data = self._handle_response(response)
            return AccountingEntityDetail(**data)
        except HTTPError as e:
            logger.error(f"Failed to get accounting entity detail: {e}")
            raise RegisterUZAPIError(f"Failed to get accounting entity detail: {e}")
    
    def get_financial_statement_detail(self, statement_id: int) -> FinancialStatementDetail:
        """Get detailed information about a financial statement.
        
        Args:
            statement_id: The financial statement ID
            
        Returns:
            Detailed statement information
        """
        try:
            response = self.client.get(
                "/uctovna-zavierka",
                params={"id": statement_id}
            )
            data = self._handle_response(response)
            return FinancialStatementDetail(**data)
        except HTTPError as e:
            logger.error(f"Failed to get financial statement detail: {e}")
            raise RegisterUZAPIError(f"Failed to get financial statement detail: {e}")
    
    def get_financial_report_detail(self, report_id: int) -> FinancialReportDetail:
        """Get detailed information about a financial report.
        
        Args:
            report_id: The financial report ID
            
        Returns:
            Detailed report information including content
        """
        try:
            response = self.client.get(
                "/uctovny-vykaz",
                params={"id": report_id}
            )
            data = self._handle_response(response)
            return FinancialReportDetail(**data)
        except HTTPError as e:
            logger.error(f"Failed to get financial report detail: {e}")
            raise RegisterUZAPIError(f"Failed to get financial report detail: {e}")
    
    def get_annual_report_detail(self, report_id: int) -> AnnualReportDetail:
        """Get detailed information about an annual report.
        
        Args:
            report_id: The annual report ID
            
        Returns:
            Detailed annual report information
        """
        try:
            response = self.client.get(
                "/vyrocna-sprava",
                params={"id": report_id}
            )
            data = self._handle_response(response)
            return AnnualReportDetail(**data)
        except HTTPError as e:
            logger.error(f"Failed to get annual report detail: {e}")
            raise RegisterUZAPIError(f"Failed to get annual report detail: {e}")