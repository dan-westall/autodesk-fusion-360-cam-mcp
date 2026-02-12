#!/usr/bin/env python3
"""
Minimal MCP Server Entry Point

This is the main entry point for the modular Fusion 360 MCP Server.
It delegates all functionality to the core modular components while
maintaining the same FastMCP interface and command-line arguments.

Architecture:
- Tools: Automatically discovered and registered via @mcp.tool() decorators
- Prompts: Automatically registered via @mcp.prompt() decorators during import
- Modules: Dynamically loaded from tools/ directory with graceful error handling

The server uses FastMCP's native decorator-based registration system,
eliminating the need for custom registry classes or manual registration logic.
"""

import os
import urllib3
import argparse
import logging
import sys

# Disable SSL warnings and proxy for localhost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'

# Import core components
# ruff: noqa: E402 - imports after environment setup is intentional
from core.server import create_server
from core.loader import (
    set_mcp_instance, 
    load_all_modules, 
    get_health_status, 
    get_error_report,
    set_error_recovery
)
from core.config import validate_configuration
from core.request_handler import initialize_request_handler

# Import prompts module to trigger automatic decorator registration
# When this module is imported, Python executes the @mcp.prompt() decorators
# in templates.py, which automatically register all prompt templates with the
# FastMCP server instance. No manual registration is required.
from prompts import templates  # noqa: F401 - imported for side effects

# Configure logging - write to file for stdio debugging
LOG_FILE = os.path.join(os.path.dirname(__file__), 'mcp_server.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stderr)  # stderr doesn't interfere with stdio
    ]
)
logger = logging.getLogger(__name__)


def initialize_server():
    """
    Initialize the modular MCP server.
    
    This function:
    1. Validates configuration
    2. Creates the FastMCP server instance
    3. Initializes the request handler
    4. Loads all tool modules (tools are auto-registered via @mcp.tool() decorators)
    5. Provides comprehensive error reporting
    
    Automatic Prompt Registration:
    Prompts are automatically registered when the prompts.templates module is
    imported at the top of this file. Python executes the @mcp.prompt() decorators
    during module import, which registers all prompt templates with the FastMCP
    server instance. This decorator-based approach eliminates the need for manual
    prompt registration or custom registry systems.
    
    Returns:
        FastMCP: Configured server instance ready to run
    """
    logger.info("=== Initializing Modular Fusion 360 MCP Server ===")
    
    try:
        # Step 1: Validate configuration
        logger.info("Step 1: Validating configuration...")
        if not validate_configuration():
            logger.error("Configuration validation failed")
            sys.exit(1)
        logger.info("✓ Configuration validation passed")
        
        # Step 2: Create FastMCP server instance
        logger.info("Step 2: Creating FastMCP server instance...")
        mcp = create_server()
        logger.info("✓ FastMCP server instance created")
        
        # Step 3: Initialize request handler
        logger.info("Step 3: Initializing request handler...")
        initialize_request_handler()
        logger.info("✓ Request handler initialized")
        
        # Step 4: Set MCP instance for module loader
        logger.info("Step 4: Configuring module loader...")
        set_mcp_instance(mcp)
        set_error_recovery(True)  # Enable graceful degradation
        logger.info("✓ Module loader configured")
        
        # Step 5: Load all modules
        logger.info("Step 5: Loading tool and prompt modules...")
        loaded_modules = load_all_modules()
        
        # Count successful loads
        successful_modules = [m for m in loaded_modules.values() if m.loaded]
        failed_modules = [m for m in loaded_modules.values() if not m.loaded]
        
        logger.info(f"✓ Module loading complete: {len(successful_modules)} successful, {len(failed_modules)} failed")
        
        # Step 6: Health check and error reporting
        logger.info("Step 6: Performing health check...")
        health_status = get_health_status()
        logger.info(f"✓ System health: {health_status['health']}")
        
        if health_status['health'] in ['POOR', 'CRITICAL']:
            logger.warning("System health is degraded. Generating error report...")
            error_report = get_error_report()
            logger.warning(f"Total errors: {error_report['total_errors']}")
            
            # Log suggestions for common issues
            if error_report['suggestions']:
                logger.warning("Suggestions:")
                for suggestion in error_report['suggestions']:
                    logger.warning(f"  - {suggestion}")
        
        # Step 7: Log final statistics
        logger.info("=== Server Initialization Complete ===")
        logger.info(f"Loaded modules: {health_status['loaded_modules']}")
        logger.info(f"Failed modules: {health_status['failed_modules']}")
        logger.info(f"Categories: {', '.join(health_status['categories'])}")
        logger.info("Server ready to accept connections")
        
        return mcp
        
    except Exception as e:
        logger.error(f"Critical error during server initialization: {e}")
        logger.error("Server initialization failed")
        sys.exit(1)


def main():
    """
    Main entry point for the MCP server.
    
    Handles command-line arguments and starts the server with the
    specified transport type (SSE or stdio).
    """
    # Parse command-line arguments (maintaining backward compatibility)
    parser = argparse.ArgumentParser(
        description="Modular Fusion 360 MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python MCP_Server.py --server_type sse    # Start with SSE transport (default)
  python MCP_Server.py --server_type stdio  # Start with stdio transport
        """
    )
    parser.add_argument(
        "--server_type", 
        type=str, 
        default="sse", 
        choices=["sse", "stdio"],
        help="Transport type for MCP communication (default: sse)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting MCP server with transport: {args.server_type}")
    
    # Initialize the modular server
    mcp = initialize_server()
    
    # Start the server with the specified transport
    try:
        logger.info(f"Starting FastMCP server with {args.server_type} transport...")
        mcp.run(transport=args.server_type)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()