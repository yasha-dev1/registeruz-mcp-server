"""MCP Server for RegisterUZ API."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp import types
from mcp.server import Server
from pydantic import ValidationError

from .client import RegisterUZClient, RegisterUZError
from .config import get_config
from .types import (
    AccountingEntityDetail,
    AccountingEntitySearchParams,
    AnnualReportDetail,
    BaseSearchParams,
    EntityType,
    FinancialReportDetail,
    FinancialStatementDetail,
    LegalForm,
)

logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("registeruz-mcp-server")


def format_success_response(data: Any) -> List[types.TextContent]:
    """Format successful response data."""
    return [types.TextContent(
        type="text",
        text=json.dumps(data, indent=2, default=str, ensure_ascii=False)
    )]


def format_error_response(error: Exception) -> List[types.TextContent]:
    """Format error response."""
    error_message = f"Error: {type(error).__name__}: {str(error)}"
    logger.error(error_message)
    return [types.TextContent(type="text", text=error_message)]


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_accounting_entities",
            description="Search for accounting entities (companies) in Slovak business register",
            inputSchema={
                "type": "object",
                "properties": {
                    "changed_from": {
                        "type": "string",
                        "description": "Date from which to retrieve changed records (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "ico": {
                        "type": "string",
                        "description": "Company identification number (IČO)"
                    },
                    "dic": {
                        "type": "string",
                        "description": "Tax identification number (DIČ)"
                    },
                    "legal_form": {
                        "type": "string",
                        "description": "Legal form code (e.g., '112' for s.r.o., '121' for a.s.)",
                        "enum": ["112", "121", "113", "111", "301", "221"]
                    },
                    "continue_after_id": {
                        "type": "integer",
                        "description": "Continue pagination after this ID"
                    },
                    "max_records": {
                        "type": "integer",
                        "description": "Maximum records to return (1-10000)",
                        "minimum": 1,
                        "maximum": 10000
                    }
                },
                "required": ["changed_from"]
            }
        ),
        types.Tool(
            name="get_financial_statements",
            description="Get financial statement identifiers from Slovak business register",
            inputSchema={
                "type": "object",
                "properties": {
                    "changed_from": {
                        "type": "string",
                        "description": "Date from which to retrieve changed records (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "continue_after_id": {
                        "type": "integer",
                        "description": "Continue pagination after this ID"
                    },
                    "max_records": {
                        "type": "integer",
                        "description": "Maximum records to return (1-10000)",
                        "minimum": 1,
                        "maximum": 10000
                    }
                },
                "required": ["changed_from"]
            }
        ),
        types.Tool(
            name="get_financial_reports",
            description="Get financial report identifiers from Slovak business register",
            inputSchema={
                "type": "object",
                "properties": {
                    "changed_from": {
                        "type": "string",
                        "description": "Date from which to retrieve changed records (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "continue_after_id": {
                        "type": "integer",
                        "description": "Continue pagination after this ID"
                    },
                    "max_records": {
                        "type": "integer",
                        "description": "Maximum records to return (1-10000)",
                        "minimum": 1,
                        "maximum": 10000
                    }
                },
                "required": ["changed_from"]
            }
        ),
        types.Tool(
            name="get_annual_reports",
            description="Get annual report identifiers from Slovak business register",
            inputSchema={
                "type": "object",
                "properties": {
                    "changed_from": {
                        "type": "string",
                        "description": "Date from which to retrieve changed records (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "continue_after_id": {
                        "type": "integer",
                        "description": "Continue pagination after this ID"
                    },
                    "max_records": {
                        "type": "integer",
                        "description": "Maximum records to return (1-10000)",
                        "minimum": 1,
                        "maximum": 10000
                    }
                },
                "required": ["changed_from"]
            }
        ),
        types.Tool(
            name="get_templates",
            description="Get all available report templates from Slovak business register",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_remaining_count",
            description="Get count of remaining IDs for a specific entity type",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Type of entity",
                        "enum": ["uctovne-jednotky", "uctovne-zavierky", "uctovne-vykazy", "vyrocne-spravy"]
                    }
                },
                "required": ["entity_type"]
            }
        ),
        types.Tool(
            name="get_all_entity_ids",
            description="Get all IDs for an entity type with automatic pagination (use carefully for large datasets)",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Type of entity",
                        "enum": ["uctovne-jednotky", "uctovne-zavierky", "uctovne-vykazy", "vyrocne-spravy"]
                    },
                    "changed_from": {
                        "type": "string",
                        "description": "Date from which to retrieve changed records (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "max_total": {
                        "type": "integer",
                        "description": "Maximum total records to retrieve",
                        "minimum": 1
                    }
                },
                "required": ["entity_type"]
            }
        ),
        types.Tool(
            name="get_entity_suggestions",
            description="Get entity name suggestions based on a search query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term to get suggestions for (partial entity name)",
                        "minLength": 1
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_accounting_entity_detail",
            description="Get detailed information about a specific accounting entity (company)",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The accounting entity ID (max 10 digits)"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="get_financial_statement_detail",
            description="Get detailed information about a specific financial statement",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The financial statement ID (max 10 digits)"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="get_financial_report_detail",
            description="Get detailed information about a specific financial report with data content",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The financial report ID (max 10 digits)"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="get_annual_report_detail",
            description="Get detailed information about a specific annual report",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The annual report ID (max 10 digits)"
                    }
                },
                "required": ["id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    config = get_config()
    
    try:
        with RegisterUZClient(config) as client:
            if name == "search_accounting_entities":
                # Build search parameters
                params = AccountingEntitySearchParams(
                    zmenene_od=arguments["changed_from"],
                    pokracovat_za_id=arguments.get("continue_after_id"),
                    max_zaznamov=arguments.get("max_records"),
                    ico=arguments.get("ico"),
                    dic=arguments.get("dic"),
                    pravna_forma=arguments.get("legal_form")
                )
                
                # Execute search in thread pool
                result = await asyncio.to_thread(
                    client.get_accounting_entities,
                    params
                )
                
                return format_success_response({
                    "ids": result.id,
                    "has_more": result.existujeDalsieId,
                    "count": len(result.id)
                })
            
            elif name == "get_financial_statements":
                params = BaseSearchParams(
                    zmenene_od=arguments["changed_from"],
                    pokracovat_za_id=arguments.get("continue_after_id"),
                    max_zaznamov=arguments.get("max_records")
                )
                
                result = await asyncio.to_thread(
                    client.get_financial_statements,
                    params
                )
                
                return format_success_response({
                    "ids": result.id,
                    "has_more": result.existujeDalsieId,
                    "count": len(result.id)
                })
            
            elif name == "get_financial_reports":
                params = BaseSearchParams(
                    zmenene_od=arguments["changed_from"],
                    pokracovat_za_id=arguments.get("continue_after_id"),
                    max_zaznamov=arguments.get("max_records")
                )
                
                result = await asyncio.to_thread(
                    client.get_financial_reports,
                    params
                )
                
                return format_success_response({
                    "ids": result.id,
                    "has_more": result.existujeDalsieId,
                    "count": len(result.id)
                })
            
            elif name == "get_annual_reports":
                params = BaseSearchParams(
                    zmenene_od=arguments["changed_from"],
                    pokracovat_za_id=arguments.get("continue_after_id"),
                    max_zaznamov=arguments.get("max_records")
                )
                
                result = await asyncio.to_thread(
                    client.get_annual_reports,
                    params
                )
                
                return format_success_response({
                    "ids": result.id,
                    "has_more": result.existujeDalsieId,
                    "count": len(result.id)
                })
            
            elif name == "get_templates":
                result = await asyncio.to_thread(client.get_templates)
                
                # Format templates for better readability
                templates_data = []
                for template in result.sablony:
                    template_info = {
                        "id": template.id,
                    }
                    if template.nazov:
                        template_info["name"] = template.nazov
                    if template.nariadenieMF:
                        template_info["regulation"] = template.nariadenieMF
                    if template.tabulky:
                        template_info["tables_count"] = len(template.tabulky)
                    templates_data.append(template_info)
                
                return format_success_response({
                    "templates": templates_data,
                    "count": len(templates_data)
                })
            
            elif name == "get_remaining_count":
                entity_type = EntityType(arguments["entity_type"])
                
                result = await asyncio.to_thread(
                    client.get_remaining_count,
                    entity_type
                )
                
                return format_success_response({
                    "entity_type": entity_type.value,
                    "remaining_count": result.pocet
                })
            
            elif name == "get_all_entity_ids":
                entity_type = EntityType(arguments["entity_type"])
                changed_from = arguments.get("changed_from")
                max_total = arguments.get("max_total")
                
                # This operation might take a while for large datasets
                ids = await asyncio.to_thread(
                    client.get_all_ids,
                    entity_type,
                    changed_from,
                    max_total
                )
                
                return format_success_response({
                    "entity_type": entity_type.value,
                    "ids": ids,
                    "count": len(ids)
                })
            
            elif name == "get_entity_suggestions":
                query = arguments["query"]
                
                result = await asyncio.to_thread(
                    client.get_entity_suggestions,
                    query
                )
                
                return format_success_response({
                    "suggestions": result,
                    "count": len(result)
                })
            
            elif name == "get_accounting_entity_detail":
                entity_id = arguments["id"]
                
                result = await asyncio.to_thread(
                    client.get_accounting_entity_detail,
                    entity_id
                )
                
                return format_success_response(result.dict(exclude_none=True))
            
            elif name == "get_financial_statement_detail":
                statement_id = arguments["id"]
                
                result = await asyncio.to_thread(
                    client.get_financial_statement_detail,
                    statement_id
                )
                
                return format_success_response(result.dict(exclude_none=True))
            
            elif name == "get_financial_report_detail":
                report_id = arguments["id"]
                
                result = await asyncio.to_thread(
                    client.get_financial_report_detail,
                    report_id
                )
                
                return format_success_response(result.dict(exclude_none=True))
            
            elif name == "get_annual_report_detail":
                report_id = arguments["id"]
                
                result = await asyncio.to_thread(
                    client.get_annual_report_detail,
                    report_id
                )
                
                return format_success_response(result.dict(exclude_none=True))
            
            else:
                return format_error_response(
                    ValueError(f"Unknown tool: {name}")
                )
    
    except ValidationError as e:
        return format_error_response(e)
    except RegisterUZError as e:
        return format_error_response(e)
    except Exception as e:
        logger.exception(f"Unexpected error in tool {name}")
        return format_error_response(e)