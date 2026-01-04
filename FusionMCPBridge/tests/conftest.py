# conftest.py - Shared fixtures for live integration tests
"""
Shared pytest fixtures and configuration for Fusion 360 MCP Bridge integration tests.

These fixtures provide:
- Bridge availability checking
- Workspace requirement markers
- Test categorization
- Command-line option for enabling integration tests

Helper functions (make_request, response_is_empty, etc.) are in helpers.py.

Usage:
    # Run unit tests only (integration tests skipped by default)
    uv run pytest FusionMCPBridge/tests/ -v
    
    # Run integration tests (requires Fusion 360 running)
    uv run pytest FusionMCPBridge/tests/ -v --integration
    
    # Run only smoke tests
    uv run pytest FusionMCPBridge/tests/ -v --integration -m "smoke"
    
    # Skip destructive tests
    uv run pytest FusionMCPBridge/tests/ -v --integration -m "not destructive"
"""

import pytest
import requests
from typing import Dict
from dataclasses import dataclass
from enum import Enum

# Import helpers for use in fixtures
from .helpers import (
    BRIDGE_BASE_URL,
    DEFAULT_TIMEOUT,
    is_bridge_running,
    make_request,
    response_is_empty,
)

# Re-export for backward compatibility (though tests should import from helpers)
__all__ = [
    'BRIDGE_BASE_URL',
    'DEFAULT_TIMEOUT',
    'is_bridge_running',
    'make_request',
    'response_is_empty',
    'WorkspaceCategory',
    'EndpointDefinition',
    'ENDPOINTS',
    'get_endpoints_by_category',
    'get_manufacture_endpoints',
]


class WorkspaceCategory(Enum):
    """Fusion 360 workspace categories for test organization."""
    DESIGN = "design"
    MANUFACTURE = "manufacture"
    SYSTEM = "system"


@dataclass
class EndpointDefinition:
    """Definition of an HTTP endpoint for testing."""
    path: str
    method: str = "GET"
    category: WorkspaceCategory = WorkspaceCategory.SYSTEM
    requires_cam: bool = False
    requires_design: bool = False
    description: str = ""
    expected_fields: tuple = ()
    
    @property
    def full_url(self) -> str:
        return f"{BRIDGE_BASE_URL}{self.path}"


# ============================================================================
# Endpoint Registry - All known endpoints for parameterized testing
# ============================================================================

ENDPOINTS = {
    # =========================================================================
    # System endpoints
    # =========================================================================
    "test_connection": EndpointDefinition(
        path="/test_connection",
        method="GET",
        category=WorkspaceCategory.SYSTEM,
        description="Test bridge connectivity",
        expected_fields=("status",)
    ),
    
    # =========================================================================
    # MANUFACTURE workspace - Setups
    # =========================================================================
    "list_setups": EndpointDefinition(
        path="/cam/setups",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="List all setups",
        expected_fields=("setups",)
    ),
    "get_setup": EndpointDefinition(
        path="/cam/setups/{setup_id}",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get setup details",
        expected_fields=("name", "id")
    ),
    "create_setup": EndpointDefinition(
        path="/cam/setups",
        method="POST",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Create new setup",
        expected_fields=("id",)
    ),
    
    # =========================================================================
    # MANUFACTURE workspace - Toolpaths
    # =========================================================================
    "list_toolpaths": EndpointDefinition(
        path="/cam/toolpaths",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="List all toolpaths",
        expected_fields=("toolpaths",)
    ),
    "get_toolpath": EndpointDefinition(
        path="/cam/toolpaths/{toolpath_id}",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get toolpath details",
        expected_fields=("name", "id")
    ),
    "get_toolpath_heights": EndpointDefinition(
        path="/cam/toolpaths/{toolpath_id}/heights",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get toolpath height parameters",
        expected_fields=()
    ),
    "get_toolpath_passes": EndpointDefinition(
        path="/cam/toolpaths/{toolpath_id}/passes",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get toolpath pass parameters",
        expected_fields=()
    ),
    "get_toolpath_linking": EndpointDefinition(
        path="/cam/toolpaths/{toolpath_id}/linking",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get toolpath linking parameters",
        expected_fields=()
    ),
    
    # =========================================================================
    # MANUFACTURE workspace - Operations
    # =========================================================================
    "get_operation_tool": EndpointDefinition(
        path="/cam/operations/{operation_id}/tool",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get operation tool assignment",
        expected_fields=()
    ),
    "get_operation_heights": EndpointDefinition(
        path="/cam/operations/{operation_id}/heights",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get operation height parameters",
        expected_fields=()
    ),
    "get_operation_passes": EndpointDefinition(
        path="/cam/operations/{operation_id}/passes",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get operation pass parameters",
        expected_fields=()
    ),
    "get_operation_linking": EndpointDefinition(
        path="/cam/operations/{operation_id}/linking",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get operation linking parameters",
        expected_fields=()
    ),
    
    # =========================================================================
    # MANUFACTURE workspace - Tool Libraries
    # =========================================================================
    "list_tool_libraries": EndpointDefinition(
        path="/tool-libraries",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="List tool libraries",
        expected_fields=("libraries",)
    ),
    "get_tool_library": EndpointDefinition(
        path="/tool-libraries/{library_id}",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Get tool library details",
        expected_fields=()
    ),
    "list_library_tools": EndpointDefinition(
        path="/tool-libraries/tools",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="List tools in libraries",
        expected_fields=()
    ),
    "search_tools": EndpointDefinition(
        path="/tool-libraries/search",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="Search tools in libraries",
        expected_fields=()
    ),
    
    # =========================================================================
    # MANUFACTURE workspace - Tools in Use
    # =========================================================================
    "list_tools": EndpointDefinition(
        path="/cam/tools",
        method="GET",
        category=WorkspaceCategory.MANUFACTURE,
        requires_cam=True,
        description="List tools in use",
        expected_fields=("tools",)
    ),
    
    # =========================================================================
    # Design workspace - Geometry
    # =========================================================================
    "draw_box": EndpointDefinition(
        path="/draw-box",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Draw a box",
        expected_fields=()
    ),
    "draw_cylinder": EndpointDefinition(
        path="/draw-cylinder",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Draw a cylinder",
        expected_fields=()
    ),
    "draw_circle": EndpointDefinition(
        path="/draw-circle",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Draw a circle",
        expected_fields=()
    ),
    "draw_lines": EndpointDefinition(
        path="/draw-lines",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Draw lines",
        expected_fields=()
    ),
    
    # =========================================================================
    # Design workspace - Features
    # =========================================================================
    "extrude": EndpointDefinition(
        path="/extrude",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Extrude a profile",
        expected_fields=()
    ),
    "revolve": EndpointDefinition(
        path="/revolve",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Revolve a profile",
        expected_fields=()
    ),
    "fillet": EndpointDefinition(
        path="/fillet",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Add fillet to edges",
        expected_fields=()
    ),
    "shell": EndpointDefinition(
        path="/shell",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Shell a body",
        expected_fields=()
    ),
    
    # =========================================================================
    # Design workspace - Export
    # =========================================================================
    "export_step": EndpointDefinition(
        path="/export-step",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Export as STEP file",
        expected_fields=()
    ),
    "export_stl": EndpointDefinition(
        path="/export-stl",
        method="POST",
        category=WorkspaceCategory.DESIGN,
        requires_design=True,
        description="Export as STL file",
        expected_fields=()
    ),
}


def get_endpoints_by_category(category: WorkspaceCategory) -> Dict[str, EndpointDefinition]:
    """Get all endpoints for a specific workspace category."""
    return {k: v for k, v in ENDPOINTS.items() if v.category == category}


def get_manufacture_endpoints() -> Dict[str, EndpointDefinition]:
    """Get all endpoints that require MANUFACTURE workspace."""
    return {k: v for k, v in ENDPOINTS.items() if v.requires_cam}


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def bridge_available():
    """
    Session-scoped fixture that checks if the bridge is available.
    
    Skips all tests in the session if the bridge is not running.
    """
    if not is_bridge_running():
        pytest.skip("Fusion 360 MCP Bridge is not running on localhost:5001")
    return True


@pytest.fixture
def manufacture_workspace_required(bridge_available):
    """
    Fixture that marks tests requiring the MANUFACTURE workspace.
    
    Tests using this fixture will be skipped if MANUFACTURE workspace
    is not active or no setup data is available.
    """
    # Try to access a MANUFACTURE workspace endpoint to verify availability
    try:
        response = make_request("/cam/setups")
        if response.status_code != 200:
            pytest.skip("MANUFACTURE workspace not active or no setup data available")
        
        data = response.json()
        if data.get("error") and "MANUFACTURE" in data.get("message", "").upper():
            pytest.skip("MANUFACTURE workspace not active")
    except requests.exceptions.RequestException:
        pytest.skip("Could not verify MANUFACTURE workspace availability")
    
    return True


@pytest.fixture
def design_document_required(bridge_available):
    """
    Fixture that marks tests requiring an open design document.
    
    Tests using this fixture will be skipped if no design is open.
    """
    try:
        response = make_request("/test_connection")
        if response.status_code != 200:
            pytest.skip("No design document open")
    except requests.exceptions.RequestException:
        pytest.skip("Could not verify design document availability")
    
    return True


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires Fusion 360 to be running)"
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require --integration flag and running Fusion 360)"
    )
    config.addinivalue_line(
        "markers", "live: marks tests as live integration tests (alias for integration)"
    )
    config.addinivalue_line(
        "markers", "smoke: marks tests as smoke tests (quick validation)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests that take > 5 seconds"
    )
    config.addinivalue_line(
        "markers", "destructive: marks tests that modify Fusion 360 state"
    )
    config.addinivalue_line(
        "markers", "manufacture: marks tests requiring MANUFACTURE workspace"
    )
    config.addinivalue_line(
        "markers", "design: marks tests requiring Design workspace"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag is provided."""
    if config.getoption("--integration"):
        # --integration given: run integration tests
        return
    
    skip_integration = pytest.mark.skip(
        reason="Integration tests require --integration flag (and Fusion 360 running)"
    )
    
    for item in items:
        if "integration" in item.keywords or "live" in item.keywords:
            item.add_marker(skip_integration)
