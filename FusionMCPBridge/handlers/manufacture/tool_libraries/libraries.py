# Tool Libraries Handler
# Handles tool library listing and management operations

import adsk.core
import adsk.cam
from typing import Dict, Any, Optional
import logging

# Import core components
from ....core.task_queue import task_queue, TaskPriority
from ....core.router import request_router

# Set up logging
logger = logging.getLogger(__name__)

def handle_list_libraries(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    List available tool library files.
    
    NOTE: This is a READ-ONLY operation - calls impl directly without task_queue.
    The task_queue callback pattern doesn't work for HTTP handlers.
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data
        
    Returns:
        Response with tool libraries list or error information
    """
    try:
        # Import tool library functions
        from ....tool_library import list_tool_libraries
        
        # READ-ONLY: Call function directly (no task_queue needed)
        result = list_tool_libraries()
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_list_libraries: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }

def handle_get_library_info(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed information about a specific tool library.
    
    NOTE: This is a READ-ONLY operation - calls impl directly without task_queue.
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data (should contain library_id)
        
    Returns:
        Response with library information or error
    """
    try:
        library_id = data.get("library_id")
        if not library_id:
            return {
                "status": 400,
                "error": True,
                "message": "library_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        # READ-ONLY: Call function directly (no task_queue needed)
        from ....tool_library import get_library_info
        result = get_library_info(library_id)
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_get_library_info: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }

def handle_load_library(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load a tool library for access.
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data (should contain library_path or library_id)
        
    Returns:
        Response confirming library load or error
    """
    try:
        library_path = data.get("library_path")
        library_id = data.get("library_id")
        
        if not library_path and not library_id:
            return {
                "status": 400,
                "error": True,
                "message": "Either library_path or library_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        # For now, return not implemented as this requires additional CAM API research
        return {
            "status": 501,
            "error": True,
            "message": "Tool library loading not yet implemented - requires additional CAM API research",
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_load_library: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }

def handle_validate_library_access(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate access to tool libraries and check permissions.
    
    NOTE: This is a READ-ONLY operation - calls impl directly without task_queue.
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data
        
    Returns:
        Response with validation results or error
    """
    try:
        # READ-ONLY: Call function directly (no task_queue needed)
        from ....tool_library import validate_tool_library_access
        result = validate_tool_library_access()
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_validate_library_access: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }

# Register handlers with the router
def register_handlers():
    """Register all tool library handlers with the request router"""
    try:
        request_router.register_handler(
            "/tool-libraries",
            handle_list_libraries,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.tool_libraries.libraries"
        )
        
        request_router.register_handler(
            "/tool-libraries/{library_id}",
            handle_get_library_info,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.tool_libraries.libraries"
        )
        
        request_router.register_handler(
            "/tool-libraries/load",
            handle_load_library,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.tool_libraries.libraries"
        )
        
        request_router.register_handler(
            "/tool-libraries/validate-access",
            handle_validate_library_access,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.tool_libraries.libraries"
        )
        
        logger.info("Registered tool library handlers")
        
    except Exception as e:
        logger.error(f"Error registering tool library handlers: {str(e)}")

# Auto-register handlers when module is imported
register_handlers()