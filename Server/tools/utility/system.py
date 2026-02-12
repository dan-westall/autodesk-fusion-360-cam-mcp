"""
Utility System Tools

This module contains system operation tools:
- test_connection: Test connection to Fusion 360
- delete_all: Delete all objects in current session
- undo: Undo last operation
- move_latest_body: Move the latest body
"""

import logging
from mcp.server.fastmcp import FastMCP
from core.request_handler import send_request
from core.config import get_endpoints, get_headers

def register_tools(mcp_instance: FastMCP):
    """Register system tools with the MCP server."""
    # Register all tools in this module
    mcp_instance.tool()(test_connection)
    mcp_instance.tool()(delete_all)
    mcp_instance.tool()(undo)
    mcp_instance.tool()(move_latest_body)

def test_connection():
    """Test connection to Fusion 360 server."""
    try:
        endpoint = get_endpoints("utility")["test_connection"]
        return send_request(endpoint, {})
    except Exception as e:
        logging.exception("Test connection failed")
        raise

def delete_all():
    """Delete all objects in the current Fusion 360 session."""
    try:
        endpoint = get_endpoints("utility")["delete_everything"]
        return send_request(endpoint, {})
    except Exception as e:
        logging.exception("Delete failed")
        raise

def undo():
    """Undo the last operation."""
    try:
        endpoint = get_endpoints("utility")["undo"]
        return send_request(endpoint, {})
    except Exception as e:
        logging.exception("Undo failed")
        raise

def move_latest_body(x : float,y:float,z:float):
    """
    Move the latest body in Fusion 360 in x, y, and z directions.
    
    This tool is useful for positioning manufactured parts or adjusting
    CAM setup geometry after creation.
    """
    endpoint = get_endpoints("utility")["move_body"]
    payload = {
        "x": x,
        "y": y,
        "z": z
    }
    return send_request(endpoint, payload)