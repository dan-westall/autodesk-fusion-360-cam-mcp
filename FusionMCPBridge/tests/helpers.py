"""
Shared helper functions for Fusion 360 MCP Bridge integration tests.

This module contains utility functions that can be imported by test files.
Fixtures remain in conftest.py (auto-loaded by pytest).
"""

import requests
from typing import Dict, Any, Optional

# Bridge configuration
BRIDGE_BASE_URL = "http://localhost:5001"
DEBUGGER_URL = "http://localhost:5002"
DEFAULT_TIMEOUT = 1  # seconds - bridge is fast (Python wrapper around C++ core)


def is_bridge_running() -> bool:
    """
    Check if the Fusion 360 MCP Bridge is running and accessible.
    
    Uses the FusionMCPBridgeDebugger on port 5002 to check status,
    as the main bridge on port 5001 may be blocked by interactive operations.
    """
    try:
        # Use debugger endpoint - more reliable than test_connection
        response = requests.get(
            f"{DEBUGGER_URL}/addon/status",
            timeout=10  # Longer timeout for status check
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "running" and data.get("isValid", False)
        return False
    except requests.exceptions.RequestException:
        return False


def make_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> requests.Response:
    """
    Make an HTTP request to the bridge.
    
    Args:
        endpoint: The endpoint path (e.g., "/cam/setups")
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Optional JSON data for POST/PUT requests
        timeout: Request timeout in seconds
        
    Returns:
        requests.Response object
    """
    url = f"{BRIDGE_BASE_URL}{endpoint}"
    
    if method.upper() == "GET":
        return requests.get(url, timeout=timeout)
    elif method.upper() == "POST":
        return requests.post(url, json=data or {}, timeout=timeout)
    elif method.upper() == "PUT":
        return requests.put(url, json=data or {}, timeout=timeout)
    elif method.upper() == "DELETE":
        return requests.delete(url, timeout=timeout)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


def response_is_empty(response: requests.Response) -> bool:
    """
    Check if a response is empty (the task_queue bug symptom).
    
    Returns True if:
    - Response body is empty string
    - Response body is empty JSON object {}
    - Response body is {"data": {}}
    """
    try:
        if not response.text or response.text.strip() == "":
            return True
        
        json_data = response.json()
        
        # Empty object
        if json_data == {}:
            return True
        
        # Empty data field
        if isinstance(json_data, dict) and json_data.get("data") == {}:
            return True
        
        return False
    except (ValueError, requests.exceptions.JSONDecodeError):
        return response.text.strip() == ""
