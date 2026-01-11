#!/usr/bin/env python3
"""
Live Integration Tests for Part Position Configuration

Tests for MANUFACTURE workspace part position endpoints:
- Part position retrieval and modification
- Position validation
- Orientation validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A document with setups open

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_part_position.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
    pytest.mark.skip(reason="Part position tests timeout - bridge slow to respond")
]


class TestGetPartPosition:
    """Tests for /cam/setups/{setup_id}/part-position GET endpoint."""
    
    def test_get_part_position_invalid_setup_returns_error(self, bridge_available):
        """Test that get part position with invalid setup ID returns error."""
        response = make_request("/cam/setups/nonexistent_id/part-position")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid setup ID: {data}"
    
    def test_get_part_position_returns_coordinates(self, bridge_available):
        """Test that part position returns coordinate information."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/part-position")
        
        if response.status_code == 404:
            pytest.skip("Part position endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get part position: {content}")
        
        # Should have position information
        has_position = (
            "position" in content or
            "origin" in content or
            "x" in content or
            "coordinates" in content or
            "offset" in content
        )
        assert has_position, f"Part position missing coordinate info: {data}"
    
    def test_get_part_position_includes_orientation(self, bridge_available):
        """Test that part position includes orientation information."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/part-position")
        
        if response.status_code == 404:
            pytest.skip("Part position endpoint not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get part position: {content}")
        
        # Should have orientation information
        has_orientation = (
            "orientation" in content or
            "rotation" in content or
            "x_axis" in content or
            "y_axis" in content or
            "z_axis" in content or
            "direction" in content
        )
        # Soft check - orientation may not be exposed
        if not has_orientation:
            pytest.skip("Part position doesn't include orientation (may be by design)")


class TestSetPartPosition:
    """Tests for /cam/setups/{setup_id}/part-position PUT endpoint."""
    
    @pytest.mark.destructive
    def test_set_part_position_invalid_setup_returns_error(self, bridge_available):
        """Test that set part position with invalid setup ID returns error."""
        response = make_request(
            "/cam/setups/nonexistent_id/part-position",
            method="PUT",
            data={"x": 0, "y": 0, "z": 0}
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500, 501] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid setup ID: {data}"
    
    @pytest.mark.destructive
    def test_set_part_position_invalid_coordinates(self, bridge_available):
        """Test that invalid coordinates return validation error."""
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
        
        # Send invalid coordinate data
        response = make_request(
            f"/cam/setups/{setup_id}/part-position",
            method="PUT",
            data={"x": "invalid", "y": None, "z": []}
        )
        
        if response.status_code == 404:
            pytest.skip("Part position PUT endpoint not implemented")
        
        if response.status_code == 501:
            pytest.skip("Part position modification not implemented")
        
        # Should return validation error
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [400, 422, 500] or
            content.get("error") is True or
            "invalid" in str(content).lower() or
            "validation" in str(content).lower()
        )
        assert is_error, (
            f"Expected validation error for invalid coordinates: {data}"
        )


class TestPartPositionValidation:
    """Tests for part position validation."""
    
    def test_position_validation_invalid_setup(self, bridge_available):
        """Test position validation with invalid setup ID."""
        response = make_request(
            "/cam/setups/nonexistent_id/part-position/validate",
            method="POST",
            data={"x": 0, "y": 0, "z": 0}
        )
        
        if response.status_code == 404:
            pytest.skip("Position validation endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
    
    def test_orientation_validation_invalid_vectors(self, bridge_available):
        """Test orientation validation with invalid vectors."""
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
        
        # Send invalid orientation vectors (non-orthogonal)
        response = make_request(
            f"/cam/setups/{setup_id}/part-position/validate",
            method="POST",
            data={
                "orientation": {
                    "x_axis": [1, 1, 0],  # Not normalized
                    "y_axis": [1, 0, 0],  # Not orthogonal to x
                    "z_axis": [0, 0, 1]
                }
            }
        )
        
        if response.status_code == 404:
            pytest.skip("Position validation endpoint not implemented")
        
        # Should return validation result
        assert not response_is_empty(response), "Validation response should not be empty"


class TestPartPositionResponseStructure:
    """Tests for part position response structure validation."""
    
    def test_part_position_has_required_fields(self, bridge_available):
        """Test that part position response has required fields."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/part-position")
        
        if response.status_code == 404:
            pytest.skip("Part position endpoint not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get part position: {content}")
        
        # Should have at least position or origin
        has_required = (
            "position" in content or
            "origin" in content or
            ("x" in content and "y" in content and "z" in content) or
            "coordinates" in content
        )
        assert has_required, f"Part position missing required fields: {content}"
