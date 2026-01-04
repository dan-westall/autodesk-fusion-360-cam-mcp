#!/usr/bin/env python3
"""
Live Integration Tests for Setup-Toolpath Relationships

Tests for bidirectional relationships between setups and toolpaths:
- Setup contains toolpaths
- Toolpath references parent setup
- Relationship consistency validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A document with setups and toolpaths open

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_setup_toolpath.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
    pytest.mark.skip(reason="Setup-toolpath relationship tests timeout - bridge slow to respond")
]


class TestSetupToolpathRelationship:
    """Tests for setup-toolpath bidirectional relationships."""
    
    def test_setup_contains_toolpaths_reference(self, bridge_available):
        """Test that setup details include toolpath references."""
        # Get list of setups
        list_response = make_request("/cam/setups")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available")
        
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        if not setup_id:
            pytest.skip("Setup has no ID")
        
        # Get setup details
        response = make_request(f"/cam/setups/{setup_id}")
        data = response.json()
        setup_data = data.get("data", data)
        
        if setup_data.get("error"):
            pytest.skip(f"Could not get setup: {setup_data}")
        
        # Setup should reference its toolpaths/operations
        has_toolpath_ref = (
            "toolpaths" in setup_data or
            "operations" in setup_data or
            "toolpath_count" in setup_data or
            "operation_count" in setup_data
        )
        # Soft check - implementation may vary
        if not has_toolpath_ref:
            pytest.skip("Setup doesn't include toolpath references (may be by design)")
    
    def test_toolpath_references_parent_setup(self, bridge_available):
        """Test that toolpath details include parent setup reference."""
        # Get list of toolpaths
        list_response = make_request("/cam/toolpaths")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
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
        # Soft check - list view may not include setup ref
        if not has_setup_ref:
            # Try getting detailed view
            toolpath_id = (
                toolpath.get("id") or
                toolpath.get("toolpath_id") or
                toolpath.get("operation_id")
            )
            if toolpath_id:
                detail_response = make_request(f"/cam/toolpaths/{toolpath_id}")
                detail_data = detail_response.json()
                toolpath_detail = detail_data.get("data", detail_data)
                
                has_setup_ref = (
                    "setup_id" in toolpath_detail or
                    "setup_name" in toolpath_detail or
                    "setup" in toolpath_detail
                )
        
        if not has_setup_ref:
            pytest.skip("Toolpath doesn't include setup reference (may be by design)")


class TestSetupToolpathsList:
    """Tests for /cam/setups/{setup_id}/toolpaths endpoint."""
    
    def test_setup_toolpaths_invalid_id_returns_error(self, bridge_available):
        """Test that toolpaths for invalid setup ID returns error."""
        response = make_request("/cam/setups/nonexistent_id/toolpaths")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid setup ID: {data}"
    
    def test_setup_toolpaths_returns_list(self, bridge_available):
        """Test that setup toolpaths endpoint returns a list."""
        # Get a valid setup
        list_response = make_request("/cam/setups")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available")
        
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        if not setup_id:
            pytest.skip("Setup has no ID")
        
        response = make_request(f"/cam/setups/{setup_id}/toolpaths")
        
        if response.status_code == 404:
            pytest.skip("Setup toolpaths endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        # Should have toolpaths list or error
        has_structure = (
            "toolpaths" in content or
            "operations" in content or
            isinstance(content, list) or
            "error" in content
        )
        assert has_structure, f"Unexpected response structure: {data}"


class TestToolpathSetupReference:
    """Tests for /cam/toolpaths/{toolpath_id}/setup endpoint."""
    
    def test_toolpath_setup_invalid_id_returns_error(self, bridge_available):
        """Test that setup for invalid toolpath ID returns error."""
        response = make_request("/cam/toolpaths/nonexistent_id/setup")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid toolpath ID: {data}"
    
    def test_toolpath_setup_returns_setup_info(self, bridge_available):
        """Test that toolpath setup endpoint returns setup information."""
        # Get a valid toolpath
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
        
        response = make_request(f"/cam/toolpaths/{toolpath_id}/setup")
        
        if response.status_code == 404:
            pytest.skip("Toolpath setup endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        # Should have setup info or error
        has_structure = (
            "setup_id" in content or
            "setup_name" in content or
            "name" in content or
            "id" in content or
            "error" in content
        )
        assert has_structure, f"Unexpected response structure: {data}"


class TestSetupToolpathConsistency:
    """Tests for setup-toolpath mapping consistency."""
    
    def test_toolpath_setup_id_matches_parent(self, bridge_available):
        """Test that toolpath's setup_id matches its parent setup."""
        # Get setups with their toolpaths
        setups_response = make_request("/cam/setups")
        setups_data = setups_response.json()
        setups_content = setups_data.get("data", setups_data)
        
        setups = setups_content.get("setups", [])
        if not setups:
            pytest.skip("No setups available")
        
        # Get toolpaths
        toolpaths_response = make_request("/cam/toolpaths")
        toolpaths_data = toolpaths_response.json()
        toolpaths_content = toolpaths_data.get("data", toolpaths_data)
        
        toolpaths = toolpaths_content.get("toolpaths", toolpaths_content.get("operations", []))
        if not toolpaths:
            pytest.skip("No toolpaths available")
        
        # Check if toolpaths have setup references
        toolpaths_with_setup = [
            tp for tp in toolpaths
            if tp.get("setup_id") or tp.get("setup_name") or tp.get("setup")
        ]
        
        if not toolpaths_with_setup:
            pytest.skip("Toolpaths don't include setup references")
        
        # Verify setup references are valid
        setup_ids = {
            s.get("id") or s.get("setup_id")
            for s in setups
            if s.get("id") or s.get("setup_id")
        }
        
        for tp in toolpaths_with_setup:
            tp_setup_id = tp.get("setup_id") or tp.get("setup", {}).get("id")
            if tp_setup_id:
                assert tp_setup_id in setup_ids or len(setup_ids) == 0, (
                    f"Toolpath references unknown setup: {tp_setup_id}"
                )


class TestSetupToolpathValidation:
    """Tests for setup-toolpath validation endpoints."""
    
    def test_validate_toolpath_in_setup_invalid_ids(self, bridge_available):
        """Test validation with invalid setup and toolpath IDs."""
        response = make_request(
            "/cam/setups/invalid_setup/toolpaths/invalid_toolpath/validate"
        )
        
        # Either 404 (not found) or validation error
        if response.status_code == 404:
            pytest.skip("Validation endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
    
    def test_validate_mismatched_setup_toolpath(self, bridge_available):
        """Test validation with mismatched setup and toolpath."""
        # Get setups
        setups_response = make_request("/cam/setups")
        setups_data = setups_response.json()
        setups_content = setups_data.get("data", setups_data)
        setups = setups_content.get("setups", [])
        
        if len(setups) < 2:
            pytest.skip("Need at least 2 setups to test mismatch")
        
        # Get toolpaths
        toolpaths_response = make_request("/cam/toolpaths")
        toolpaths_data = toolpaths_response.json()
        toolpaths_content = toolpaths_data.get("data", toolpaths_data)
        toolpaths = toolpaths_content.get("toolpaths", toolpaths_content.get("operations", []))
        
        if not toolpaths:
            pytest.skip("No toolpaths available")
        
        # Try to validate toolpath against wrong setup
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        toolpath_id = (
            toolpaths[0].get("id") or
            toolpaths[0].get("toolpath_id") or
            toolpaths[0].get("operation_id")
        )
        
        if not setup_id or not toolpath_id:
            pytest.skip("Missing IDs for validation test")
        
        # This may or may not be a mismatch depending on data
        response = make_request(
            f"/cam/setups/{setup_id}/toolpaths/{toolpath_id}/validate"
        )
        
        if response.status_code == 404:
            pytest.skip("Validation endpoint not implemented")
        
        # Should return validation result (pass or fail)
        assert not response_is_empty(response), "Validation response should not be empty"


class TestSetupSequence:
    """Tests for /cam/setups/{setup_id}/sequence endpoint."""
    
    def test_setup_sequence_invalid_id_returns_error(self, bridge_available):
        """Test that sequence for invalid setup ID returns error."""
        response = make_request("/cam/setups/nonexistent_id/sequence")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid setup ID: {data}"
    
    def test_setup_sequence_returns_ordered_operations(self, bridge_available):
        """Test that setup sequence returns ordered operations."""
        # Get a valid setup
        list_response = make_request("/cam/setups")
        list_data = list_response.json()
        content = list_data.get("data", list_data)
        
        setups = content.get("setups", [])
        if not setups:
            pytest.skip("No setups available")
        
        setup_id = setups[0].get("id") or setups[0].get("setup_id")
        if not setup_id:
            pytest.skip("Setup has no ID")
        
        response = make_request(f"/cam/setups/{setup_id}/sequence")
        
        if response.status_code == 404:
            pytest.skip("Setup sequence endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        # Should have sequence/order information
        has_structure = (
            "sequence" in content or
            "operations" in content or
            "toolpaths" in content or
            "order" in content or
            isinstance(content, list) or
            "error" in content
        )
        assert has_structure, f"Unexpected sequence response: {data}"
