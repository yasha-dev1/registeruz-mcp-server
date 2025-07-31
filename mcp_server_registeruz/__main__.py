"""Entry point for RegisterUZ MCP Server."""

import asyncio
import logging
import os
import sys

from mcp.server.stdio import stdio_server

from .server import server

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)


async def main():
    """Run the MCP server using stdio transport."""
    logger.info("Starting RegisterUZ MCP Server...")
    logger.info("Transport: stdio (standard input/output)")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized on stdio transport, ready to handle requests")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def run():
    """Entry point for the script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass


if __name__ == "__main__":
    run()