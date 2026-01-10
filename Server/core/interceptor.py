"""
Request Interceptor Module

Provides state management and logging functionality for intercepting
HTTP responses between the MCP Server and Fusion 360 Add-In.

Requirements: 1.1, 1.4, 4.1, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3
"""

import json
import sys
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

# Global interceptor state - defaults to False (disabled)
_interceptor_enabled: bool = False


def is_interceptor_enabled() -> bool:
    """
    Check if the interceptor is currently enabled.
    
    Returns:
        bool: True if interceptor is enabled, False otherwise
    """
    return _interceptor_enabled


def set_interceptor_enabled(enabled: bool) -> None:
    """
    Enable or disable the interceptor at runtime.
    
    Args:
        enabled: True to enable interceptor, False to disable
    """
    global _interceptor_enabled
    _interceptor_enabled = enabled
    logger.info(f"Interceptor {'ENABLED' if enabled else 'DISABLED'}")


def toggle_interceptor() -> bool:
    """
    Toggle the interceptor state and return the new state.
    
    Returns:
        bool: The new state after toggling (True if now enabled, False if now disabled)
    """
    global _interceptor_enabled
    _interceptor_enabled = not _interceptor_enabled
    logger.info(f"Interceptor {'ENABLED' if _interceptor_enabled else 'DISABLED'}")
    return _interceptor_enabled


def log_response(endpoint: str, response_data: Any, method: str = "POST") -> None:
    """
    Log an HTTP response to the log file with formatted output.
    
    Args:
        endpoint: The URL that was called
        response_data: The response data (dict, list, or raw)
        method: HTTP method used (POST/GET), defaults to "POST"
    """
    try:
        if isinstance(response_data, (dict, list)):
            formatted_json = json.dumps(response_data, indent=4)
        elif isinstance(response_data, str):
            parsed = json.loads(response_data)
            formatted_json = json.dumps(parsed, indent=4)
        else:
            formatted_json = json.dumps(response_data, indent=4)
    except (json.JSONDecodeError, TypeError) as e:
        formatted_json = f"[ERROR] Failed to parse: {e}\nRaw: {str(response_data)[:500]}"
    
    logger.info(f"[INTERCEPTOR] {method} {endpoint}\n{formatted_json}")


def intercept_response(endpoint: str, response: requests.Response, method: str = "POST") -> Any:
    """
    Process a response, optionally logging it, and return the JSON data.
    
    Checks if the interceptor is enabled and logs the response if so.
    Parses and returns the JSON response data unchanged.
    
    Args:
        endpoint: The URL that was called
        response: The requests.Response object
        method: HTTP method used (POST/GET), defaults to "POST"
        
    Returns:
        The parsed JSON response data
        
    Requirements: 3.1, 3.2, 3.3
    """
    # Parse JSON response data
    try:
        response_data = response.json()
    except (json.JSONDecodeError, ValueError):
        # If JSON parsing fails, log error if interceptor enabled and re-raise
        if is_interceptor_enabled():
            log_response(endpoint, f"Failed to parse: {response.text}", method)
        raise
    
    # Log response if interceptor is enabled
    if is_interceptor_enabled():
        log_response(endpoint, response_data, method)
    
    # Return the parsed data unchanged
    return response_data