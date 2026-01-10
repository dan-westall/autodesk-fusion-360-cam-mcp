"""
CAM Height Parameter Tools

This module contains tools for height parameter management:
- get_toolpath_heights: Get toolpath height parameters
"""

import logging
import requests
from mcp.server.fastmcp import FastMCP
from core.config import get_endpoints, get_timeout
from core import interceptor

# Get the MCP instance from the main server
# This will be injected by the module loader
mcp = None

def register_tools(mcp_instance: FastMCP):
    """Register height parameter tools with the MCP server."""
    global mcp
    mcp = mcp_instance
    
    # Register all tools in this module
    mcp.tool()(get_toolpath_heights)

def get_toolpath_heights(toolpath_id: str) -> dict:
    """
    Get detailed height information for a specific CAM toolpath.
    
    Use this tool after list_toolpaths_with_heights() or list_cam_toolpaths() to
    inspect comprehensive height parameters for a specific manufacturing operation.
    You need the toolpath_id from the response of list_toolpaths_with_heights.
    
    Returns complete height parameters including:
    - Clearance height: Safe travel height above all obstacles
    - Retract height: Height for rapid positioning moves
    - Feed height: Height where feed rate begins
    - Top height: Upper material boundary for the operation
    - Bottom height: Lower material boundary for the operation
    
    Each parameter contains: value, unit, expression, type, editability and constraints.
    
    IMPORTANT: The toolpath_id must exactly match the one returned by list_toolpaths_with_heights.
    If the toolpath doesn't exist, you'll get a TOOLPATH_NOT_FOUND error.
    
    Example request:
    {
        "toolpath_id": "op_001"
    }
    
    Example response:
    {
        "toolpath_id": "op_001",
        "toolpath_name": "Adaptive1",
        "heights": {
            "clearance_height": {
                "value": 25.0,
                "unit": "mm",
                "expression": "stockTop + 5mm",
                "type": "numeric",
                "editable": true,
                "min_value": null,
                "max_value": null
            },
            "retract_height": {
                "value": 15.0,
                "unit": "mm",
                "expression": "stockTop",
                "type": "numeric",
                "editable": true,
                "min_value": null,
                "max_value": null
            },
            "feed_height": {
                "value": 2.0,
                "unit": "mm",
                "expression": "stockTop - 3mm",
                "type": "numeric",
                "editable": true,
                "min_value": null,
                "max_value": null
            },
            "top_height": {
                "value": 0.0,
                "unit": "mm",
                "expression": "stockTop",
                "type": "numeric",
                "editable": true,
                "min_value": null,
                "max_value": null
            },
            "bottom_height": {
                "value": -10.0,
                "unit": "mm",
                "expression": "stockTop - 10mm",
                "type": "numeric",
                "editable": true,
                "min_value": null,
                "max_value": null
            }
        }
    }
    
    Possible errors:
    - TOOLPATH_NOT_FOUND: The toolpath_id doesn't exist
    - CAM_NOT_AVAILABLE: No MANUFACTURE workspace or CAM data available
    - CONNECTION_ERROR: Connection to Fusion 360 failed
    
    Typical use cases: Detailed analysis of height parameters, verification of safety heights,
    preparation for height modifications, collision avoidance.
    
    Requirements: 2.2, 3.1, 3.2, 3.3, 3.4
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_toolpath_heights']}/{toolpath_id}/heights"
        response = requests.get(endpoint, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "GET")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running and you are in the MANUFACTURE workspace.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy processing CAM operations.",
            "code": "TIMEOUT_ERROR"
        }
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            return {
                "error": True,
                "message": f"Toolpath with ID '{toolpath_id}' not found. Ensure you have CAM setups with generated toolpaths.",
                "code": "TOOLPATH_NOT_FOUND"
            }
        else:
            logging.error("Get toolpath heights failed: %s", e)
            return {
                "error": True,
                "message": f"Failed to retrieve toolpath heights: {str(e)}. Ensure you are in the MANUFACTURE workspace.",
                "code": "UNKNOWN_ERROR"
            }
    except Exception as e:
        logging.error("Get toolpath heights failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to retrieve toolpath heights: {str(e)}. Ensure you are in the MANUFACTURE workspace.",
            "code": "UNKNOWN_ERROR"
        }