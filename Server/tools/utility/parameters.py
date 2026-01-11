"""
Utility Parameter Management Tools

This module contains parameter management tools:
- count: Count parameters in current model
- list_parameters: List all parameters in current model
- change_parameter: Change parameter value
"""

import logging
from mcp.server.fastmcp import FastMCP
from core.request_handler import send_request
from core.config import get_endpoints, get_headers

# Get the MCP instance from the main server
# This will be injected by the module loader
mcp = None

def register_tools(mcp_instance: FastMCP):
    """Register parameter management tools with the MCP server."""
    global mcp
    mcp = mcp_instance
    
    # Register all tools in this module
    mcp.tool()(count)
    mcp.tool()(list_parameters)
    mcp.tool()(change_parameter)

def count():
    """Count parameters in the current manufacturing model."""
    try:
        endpoint = get_endpoints("utility")["count_parameters"]
        return send_request(endpoint, {})
    except Exception as e:
        logging.exception("Count failed")
        raise

def list_parameters():
    """List all parameters in the current manufacturing model."""
    try:
        endpoint = get_endpoints("utility")["list_parameters"]
        return send_request(endpoint, {})
    except Exception as e:
        logging.exception("List parameters failed")
        raise

def change_parameter(name: str, value: str):
    """Change the value of a parameter in the manufacturing model."""
    try:
        endpoint = get_endpoints("utility")["change_parameter"]
        payload = {
            "name": name,
            "value": value
        }
        return send_request(endpoint, payload)
    except Exception as e:
        logging.exception("Change parameter failed")
        raise