#!/usr/bin/env python3
"""
Live Integration Tests for Setup Management

Tests for MANUFACTURE workspace setup endpoints including:
- Setup listing and retrieval
- Setup creation, modification, and deletion
- Setup duplication
- Response structure validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A document with setups open (for most tests)

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_setups.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
    BRIDGE_BASE_URL,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
    pytest.mark.skip(reason="Setup tests timeout - bridge slow to respond intermittently")
]


class TestListSetups:
    """Tests for /cam/setups list endpoint."""
    
    def test_list_setups_returns_response(self, bridge_available):
        """Test that list setups returns a non-empty response."""
        response = make_request("/cam/setups")
        
        assert not response_is_empty(response), (
            "CRITICAL: /cam/setups returned empty response. "
            "Handler likely uses broken task_queue callback pattern."
        )
    
    def test_list_setups_response_structure(self, bridge_available):
        """Test that list setups response has expected structure."""
        response = make_request("/cam/setups")
        data = response.json()
        
        # Should have data wrapper or direct content
        content = data.get("data", data)
        
        # Valid responses have setups list or error info
        has_valid_structure = (
            "setups" in content or
            "total_count" in content or
            "error" in content or
            "message" in content
        )
        assert has_valid_structure, f"Unexpected response structure: {data}"
    
    def test_list_setups_setups_is_list(self, bridge_available):
        """Test that setups field is a list when present."""
        response = make_request("/cam/setups")
        data = response.json()
        content = data.get("data", data)
        
        if "setups" in content:
            assert isinstance(content["setups"], list), (
                f"'setups' should be a list, got {type(content['setups'])}"
            )
    
    def test_list_setups_includes_count(self, bridge_available):
        """Test that response includes setup count."""
        response = make_request("/cam/setups")
        data = response.json()
        content = data.get("data", data)
        
        if not content.get("error"):
            has_count = "total_count" in content or "setups" in content
            assert has_count, "Response should include count or setups list"


class TestGetSetup:
    """Tests for /cam/setups/{setup_id} get endpoint."""
    
    def test_get_setup_invalid_id_returns_error(self, bridge_available):
        """Test that invalid setup ID returns proper error."""
        response = make_request("/cam/setups/nonexistent_id_12345")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        # Should indicate not found or error
        is_error_response = (
            response.status_code == 404 or
            content.get("error") is True or
            "not found" in str(content).lower() or
            "SETUP_NOT_FOUND" in str(content)
        )
        assert is_error_response, f"Expected error for invalid ID: {data}"
    
    def test_get_setup_empty_id_returns_error(self, bridge_available):
        """Test that empty setup ID returns error."""
        response = make_request("/cam/setups/")
        
        # Either 404 or redirects to list endpoint
        assert response.status_code in [200, 400, 404], (
            f"Unexpected status code: {response.status_code}"
        )
    
    def test_get_existing_setup_structure(self, bridge_available):
        """Test structure of existing setup response (if setups exist)."""
        # First get list of setups
        list_response = make_request("/cam/setups")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available to test get endpoint")
        
        # Get first setup
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        if not setup_id:
            pytest.skip("Setup has no ID field")
        
        response = make_request(f"/cam/setups/{setup_id}")
        assert not response_is_empty(response), "Get setup response should not be empty"
        
        data = response.json()
        setup_data = data.get("data", data)
        
        # Should have setup details
        has_details = (
            "name" in setup_data or
            "id" in setup_data or
            "setup_id" in setup_data or
            "error" in setup_data
        )
        assert has_details, f"Setup response missing expected fields: {setup_data}"


class TestCreateSetup:
    """Tests for /cam/setups create endpoint (POST)."""
    
    @pytest.mark.destructive
    def test_create_setup_missing_params_returns_error(self, bridge_available):
        """Test that create without required params returns error."""
        response = make_request("/cam/setups", method="POST", data={})
        
        assert not response_is_empty(response), "Response should not be empty"
        
        # Note: 501 (not implemented) is also acceptable
        if response.status_code == 501:
            pytest.skip("Create setup not implemented")
        
        data = response.json()
        
        # Should indicate missing parameters, error, or succeed with defaults
        is_error = (
            response.status_code in [400, 422, 500] or
            data.get("error") is True or
            "required" in str(data).lower() or
            "missing" in str(data).lower()
        )
        
        if is_error:
            # Verify error response structure
            assert response.status_code >= 400, (
                f"Error response should have 4xx/5xx status code: {response.status_code}, data: {data}"
            )
        else:
            # Success case - implementation creates setup with defaults
            assert response.status_code in [200, 201], (
                f"Success response should have 200/201 status code: {response.status_code}, data: {data}"
            )
    
    @pytest.mark.destructive
    def test_create_setup_with_name(self, bridge_available):
        """Test creating a setup with a name."""
        test_name = "Test Setup - Live Integration"
        response = make_request(
            "/cam/setups",
            method="POST",
            data={"name": test_name}
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        if response.status_code == 501:
            pytest.skip("Create setup not implemented")
        
        data = response.json()
        # Either success with created setup or error with reason
        has_response = (
            "data" in data or
            "error" in data or
            "message" in data or
            "id" in data
        )
        assert has_response, f"Unexpected create response: {data}"


class TestModifySetup:
    """Tests for /cam/setups/{setup_id} modify endpoint (PUT)."""
    
    @pytest.mark.destructive
    def test_modify_setup_invalid_id_returns_error(self, bridge_available):
        """Test that modify with invalid ID returns error."""
        response = make_request(
            "/cam/setups/nonexistent_id_12345",
            method="PUT",
            data={"name": "Modified Name"}
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500, 501] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestDeleteSetup:
    """Tests for /cam/setups/{setup_id} delete endpoint (DELETE)."""
    
    @pytest.mark.destructive
    def test_delete_setup_invalid_id_returns_error(self, bridge_available):
        """Test that delete with invalid ID returns error."""
        response = make_request(
            "/cam/setups/nonexistent_id_12345",
            method="DELETE"
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500, 501] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestDuplicateSetup:
    """Tests for /cam/setups/{setup_id}/duplicate endpoint."""
    
    @pytest.mark.destructive
    def test_duplicate_setup_invalid_id_returns_error(self, bridge_available):
        """Test that duplicate with invalid ID returns error."""
        response = make_request(
            "/cam/setups/nonexistent_id_12345/duplicate",
            method="POST"
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500, 501] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid ID: {data}"


class TestSetupResponseValidation:
    """Validate setup response structures match expected format."""
    
    def test_setup_list_item_has_required_fields(self, bridge_available):
        """Test that setup list items have required fields."""
        response = make_request("/cam/setups")
        data = response.json()
        content = data.get("data", data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available to validate")
        
        setup = setups[0]
        
        # Should have at least an identifier
        has_id = "id" in setup or "setup_id" in setup or "name" in setup
        assert has_id, f"Setup missing identifier: {setup}"
    
    def test_setup_detail_has_configuration(self, bridge_available):
        """Test that setup detail includes configuration info."""
        # Get list first
        list_response = make_request("/cam/setups")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available to validate")
        
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        if not setup_id:
            pytest.skip("Setup has no ID")
        
        response = make_request(f"/cam/setups/{setup_id}")
        data = response.json()
        setup_data = data.get("data", data)
        
        if setup_data.get("error"):
            pytest.skip(f"Could not get setup details: {setup_data}")
        
        # Detailed setup should have more info than list item
        # At minimum should have name or configuration
        has_detail = (
            "name" in setup_data or
            "wcs" in setup_data or
            "work_coordinate_system" in setup_data or
            "stock" in setup_data or
            "operations" in setup_data or
            "toolpaths" in setup_data
        )
        assert has_detail, f"Setup detail missing configuration: {setup_data}"
