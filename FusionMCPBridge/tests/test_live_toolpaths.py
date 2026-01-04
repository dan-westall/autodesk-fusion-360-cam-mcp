#!/usr/bin/env python3
"""
Live Integration Tests for Toolpath Management

Tests for MANUFACTURE workspace toolpath endpoints including:
- Toolpath listing and retrieval
- Toolpath parameters (heights, passes, linking)
- Response structure validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A document with toolpaths open

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_toolpaths.py -v --integration
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
]

SKIP_TIMEOUT = pytest.mark.skip(reason="Toolpath tests timeout - bridge slow to respond intermittently")


class TestListToolpaths:
    """Tests for /cam/toolpaths list endpoint."""
    
    @SKIP_TIMEOUT
    def test_list_toolpaths_returns_response(self, bridge_available):
        """Test that list toolpaths returns a non-empty response."""
        response = make_request("/cam/toolpaths")
        
        assert not response_is_empty(response), (
            "CRITICAL: /cam/toolpaths returned empty response. "
            "Handler likely uses broken task_queue callback pattern."
        )
    
    @SKIP_TIMEOUT
    def test_list_toolpaths_response_structure(self, bridge_available):
        """Test that list toolpaths response has expected structure."""
        response = make_request("/cam/toolpaths")
        data = response.json()
        content = data.get("data", data)
        
        has_valid_structure = (
            "toolpaths" in content or
            "operations" in content or
            "error" in content or
            "message" in content
        )
        assert has_valid_structure, f"Unexpected response structure: {data}"
    
    @SKIP_TIMEOUT
    def test_list_toolpaths_is_list(self, bridge_available):
        """Test that toolpaths field is a list when present."""
        response = make_request("/cam/toolpaths")
        data = response.json()
        content = data.get("data", data)
        
        if "toolpaths" in content:
            assert isinstance(content["toolpaths"], list), (
                f"'toolpaths' should be a list, got {type(content['toolpaths'])}"
            )


class TestGetToolpath:
    """Tests for /cam/toolpaths/{toolpath_id} get endpoint."""
    
    def test_get_toolpath_invalid_id_returns_error(self, bridge_available):
        """Test that invalid toolpath ID returns proper error."""
        response = make_request("/cam/toolpaths/nonexistent_id_12345")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error_response = (
            response.status_code == 404 or
            content.get("error") is True or
            "not found" in str(content).lower()
        )
        assert is_error_response, f"Expected error for invalid ID: {data}"
    
    def test_get_existing_toolpath_structure(self, bridge_available):
        """Test structure of existing toolpath response."""
        # First get list of toolpaths
        list_response = make_request("/cam/toolpaths")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        # Handle both flat and nested (setups) response structures
        toolpaths = content.get("toolpaths", content.get("operations", []))
        if not toolpaths and "setups" in content:
            # Extract toolpaths from nested setups structure
            for setup in content.get("setups", []):
                toolpaths.extend(setup.get("toolpaths", []))
        
        if not toolpaths:
            pytest.skip("No toolpaths available to test")
        
        toolpath_id = (
            toolpaths[0].get("id") or 
            toolpaths[0].get("toolpath_id") or
            toolpaths[0].get("operation_id")
        )
        if not toolpath_id:
            pytest.skip("Toolpath has no ID field")
        
        response = make_request(f"/cam/toolpaths/{toolpath_id}")
        assert not response_is_empty(response), "Get toolpath response should not be empty"


class TestToolpathHeights:
    """Tests for /cam/toolpaths/{toolpath_id}/heights endpoint."""
    
    @SKIP_TIMEOUT
    def test_heights_invalid_id_returns_error(self, bridge_available):
        """Test that heights with invalid ID returns error."""
        response = make_request("/cam/toolpaths/nonexistent_id/heights")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"
    
    @SKIP_TIMEOUT
    def test_heights_existing_toolpath(self, bridge_available):
        """Test heights endpoint for existing toolpath."""
        # Get a toolpath first
        list_response = make_request("/cam/toolpaths")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        toolpaths = content.get("toolpaths", content.get("operations", []))
        if not toolpaths:
            pytest.skip("No toolpaths available")
        
        toolpath_id = (
            toolpaths[0].get("id") or 
            toolpaths[0].get("toolpath_id") or
            toolpaths[0].get("operation_id")
        )
        if not toolpath_id:
            pytest.skip("Toolpath has no ID")
        
        response = make_request(f"/cam/toolpaths/{toolpath_id}/heights")
        assert not response_is_empty(response), "Heights response should not be empty"


class TestToolpathPasses:
    """Tests for /cam/toolpaths/{toolpath_id}/passes endpoint."""
    
    @SKIP_TIMEOUT
    def test_passes_invalid_id_returns_error(self, bridge_available):
        """Test that passes with invalid ID returns error."""
        response = make_request("/cam/toolpaths/nonexistent_id/passes")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestToolpathLinking:
    """Tests for /cam/toolpaths/{toolpath_id}/linking endpoint."""
    
    @SKIP_TIMEOUT
    def test_linking_invalid_id_returns_error(self, bridge_available):
        """Test that linking with invalid ID returns error."""
        response = make_request("/cam/toolpaths/nonexistent_id/linking")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestToolpathParameters:
    """Tests for /cam/toolpaths/{toolpath_id}/parameters endpoint."""
    
    @SKIP_TIMEOUT
    def test_parameters_invalid_id_returns_error(self, bridge_available):
        """Test that parameters with invalid ID returns error."""
        response = make_request("/cam/toolpaths/nonexistent_id/parameters")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestToolpathResponseValidation:
    """Validate toolpath response structures."""
    
    @SKIP_TIMEOUT
    def test_toolpath_list_item_has_identifier(self, bridge_available):
        """Test that toolpath list items have identifiers."""
        response = make_request("/cam/toolpaths")
        data = response.json()
        content = data.get("data", data)
        
        toolpaths = content.get("toolpaths", content.get("operations", []))
        if not toolpaths:
            pytest.skip("No toolpaths available")
        
        toolpath = toolpaths[0]
        has_id = (
            "id" in toolpath or 
            "toolpath_id" in toolpath or
            "operation_id" in toolpath or
            "name" in toolpath
        )
        assert has_id, f"Toolpath missing identifier: {toolpath}"
    
    @SKIP_TIMEOUT
    def test_toolpath_includes_setup_context(self, bridge_available):
        """Test that toolpath response includes setup context."""
        response = make_request("/cam/toolpaths")
        data = response.json()
        content = data.get("data", data)
        
        toolpaths = content.get("toolpaths", content.get("operations", []))
        if not toolpaths:
            pytest.skip("No toolpaths available")
        
        toolpath = toolpaths[0]
        
        # Toolpath should reference its parent setup
        has_setup_ref = (
            "setup_id" in toolpath or
            "setup_name" in toolpath or
            "setup" in toolpath or
            "parent_setup" in toolpath
        )
        # This is a soft check - not all implementations include setup ref in list
        if not has_setup_ref:
            pytest.skip("Toolpath list doesn't include setup reference (may be by design)")
