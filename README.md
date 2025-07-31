# RegisterUZ MCP Server

An MCP (Model Context Protocol) server for accessing the Slovak Business Register (Register účtovných závierok) API. This server provides AI assistants with tools to search and retrieve business information from the Slovak public register.

## Features

- 🔍 Search for accounting entities (companies) by IČO, DIČ, or legal form
- 📊 Retrieve financial statements, reports, and annual reports
- 📑 Access report templates
- 🔄 Automatic pagination support for large datasets
- ⚡ Async operations for optimal performance
- 🛡️ Comprehensive error handling and validation

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/registeruz-mcp-server.git
cd registeruz-mcp-server

# Install dependencies
pip install -e .
```

### Using pip

```bash
pip install mcp-server-registeruz
```

## Configuration

The server can be configured using environment variables. Copy `.env.example` to `.env` and adjust the values:

```bash
cp .env.example .env
```

Available configuration options:

- `REGISTERUZ_BASE_URL` - Base URL for RegisterUZ API (default: https://www.registeruz.sk/cruz-public/api)
- `REGISTERUZ_TIMEOUT` - Request timeout in seconds (default: 30)
- `REGISTERUZ_MAX_RECORDS` - Maximum records per request (default: 1000, max: 10000)
- `REGISTERUZ_DEFAULT_FROM_DATE` - Default date for initial data fetch (default: 2000-01-01)
- `LOG_LEVEL` - Logging level (default: INFO)

## Usage

### Running the Server

```bash
# Using the installed package
mcp-server-registeruz

# Or using Python module
python -m mcp_server_registeruz
```

### Integration with Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "registeruz": {
      "command": "mcp-server-registeruz",
      "env": {
        "REGISTERUZ_TIMEOUT": "60",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Available Tools

### 1. `search_accounting_entities`

Search for companies in the Slovak business register.

**Parameters:**
- `changed_from` (required): Date from which to retrieve changed records (YYYY-MM-DD)
- `ico`: Company identification number (IČO)
- `dic`: Tax identification number (DIČ)
- `legal_form`: Legal form code (e.g., '112' for s.r.o., '121' for a.s.)
- `continue_after_id`: Continue pagination after this ID
- `max_records`: Maximum records to return (1-10000)

**Example:**
```json
{
  "changed_from": "2024-01-01",
  "legal_form": "112",
  "max_records": 100
}
```

### 2. `get_financial_statements`

Retrieve financial statement identifiers.

**Parameters:**
- `changed_from` (required): Date from which to retrieve changed records (YYYY-MM-DD)
- `continue_after_id`: Continue pagination after this ID
- `max_records`: Maximum records to return (1-10000)

### 3. `get_financial_reports`

Retrieve financial report identifiers.

**Parameters:**
- Same as `get_financial_statements`

### 4. `get_annual_reports`

Retrieve annual report identifiers.

**Parameters:**
- Same as `get_financial_statements`

### 5. `get_templates`

Get all available report templates.

**Parameters:** None

### 6. `get_remaining_count`

Get count of remaining IDs for a specific entity type.

**Parameters:**
- `entity_type` (required): Type of entity (uctovne-jednotky, uctovne-zavierky, uctovne-vykazy, vyrocne-spravy)

### 7. `get_all_entity_ids`

Get all IDs for an entity type with automatic pagination (use carefully for large datasets).

**Parameters:**
- `entity_type` (required): Type of entity
- `changed_from`: Date from which to retrieve changed records (YYYY-MM-DD)
- `max_total`: Maximum total records to retrieve

## Legal Forms

Common legal form codes in Slovakia:
- `112` - s.r.o. (Limited liability company)
- `121` - a.s. (Joint stock company)
- `113` - k.s. (Limited partnership)
- `111` - v.o.s. (General partnership)
- `301` - SE (European company)
- `221` - Družstvo (Cooperative)

## API Information

This MCP server connects to the public RÚZ (Register účtovných závierok) API provided by the Slovak government. The API is free to use and doesn't require authentication.

### Rate Limits

The API documentation doesn't specify rate limits, but the server implements:
- Configurable request timeout
- Maximum records per request (up to 10,000)
- Automatic pagination for large datasets

### Data License

The data is provided under CC0 Public Domain license.

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/registeruz-mcp-server.git
cd registeruz-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=mcp_server_registeruz

# Run linting
ruff check .

# Run type checking
mypy mcp_server_registeruz
```

### Project Structure

```
registeruz-mcp-server/
├── mcp_server_registeruz/
│   ├── __init__.py
│   ├── __main__.py       # Entry point
│   ├── server.py         # MCP server implementation
│   ├── client.py         # RegisterUZ API client
│   ├── config.py         # Configuration management
│   └── types.py          # Type definitions
├── tests/
│   ├── test_client.py
│   └── test_server.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .env.example
```

## Troubleshooting

### Common Issues

1. **Connection timeouts**
   - Increase `REGISTERUZ_TIMEOUT` in your environment
   - Check your internet connection

2. **Invalid date format**
   - Ensure dates are in YYYY-MM-DD format
   - Valid example: 2024-01-01

3. **Large data requests**
   - Use pagination with `continue_after_id`
   - Reduce `max_records` parameter
   - Consider using `get_all_entity_ids` with `max_total` limit

### Debugging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
mcp-server-registeruz
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Slovak government for providing the public RÚZ API
- Anthropic for the MCP protocol specification
- The MCP community for examples and best practices

## Links

- [RÚZ API Documentation](https://www.registeruz.sk/cruz-public/home/api)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [Slovak Business Register](https://www.registeruz.sk)
