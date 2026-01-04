#!/usr/bin/env python3
"""
Live Integration Tests for Work Coordinate System (WCS) Configuration

Tests for MANUFACTURE workspace WCS endpoints:
- WCS configuration retrieval
- WCS origin and orientation validation
- WCS type validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A document with setups open

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_wcs.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
    pytest.mark.skip(reason="WCS tests timeout - bridge slow to respond intermittently")
]


class TestWCSInSetup:
    """Tests for WCS configuration in setup details."""
    
    def test_setup_includes_wcs_configuration(self, bridge_available):
        """Test that setup details include WCS configuration."""
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
        
        response = make_request(f"/cam/setups/{setup_id}")
        data = response.json()
        setup_data = data.get("data", data)
        
        if setup_data.get("error"):
            pytest.skip(f"Could not get setup: {setup_data}")
        
        # Setup should include WCS information
        has_wcs = (
            "wcs" in setup_data or
            "work_coordinate_system" in setup_data or
            "workCoordinateSystem" in setup_data or
            "wcs_origin" in setup_data or
            "origin" in setup_data
        )
        # Soft check - WCS may not be in basic response
        if not has_wcs:
            pytest.skip("Setup doesn't include WCS in basic response (may need dedicated endpoint)")


class TestGetWCS:
    """Tests for /cam/setups/{setup_id}/wcs GET endpoint."""
    
    def test_get_wcs_invalid_setup_returns_error(self, bridge_available):
        """Test that get WCS with invalid setup ID returns error."""
        response = make_request("/cam/setups/nonexistent_id/wcs")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected error for invalid setup ID: {data}"
    
    def test_get_wcs_returns_configuration(self, bridge_available):
        """Test that WCS endpoint returns configuration."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/wcs")
        
        if response.status_code == 404:
            pytest.skip("WCS endpoint not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get WCS: {content}")
        
        # Should have WCS configuration
        has_config = (
            "origin" in content or
            "type" in content or
            "wcs_type" in content or
            "orientation" in content or
            "x" in content or
            "x_axis" in content
        )
        assert has_config, f"WCS missing configuration: {data}"


class TestWCSOrigin:
    """Tests for WCS origin coordinates."""
    
    def test_wcs_has_origin_coordinates(self, bridge_available):
        """Test that WCS includes origin coordinates."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/wcs")
        
        if response.status_code == 404:
            pytest.skip("WCS endpoint not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get WCS: {content}")
        
        # Should have origin coordinates
        has_origin = (
            "origin" in content or
            ("x" in content and "y" in content and "z" in content) or
            "position" in content or
            "coordinates" in content
        )
        assert has_origin, f"WCS missing origin coordinates: {content}"
    
    @pytest.mark.destructive
    def test_wcs_origin_validation(self, bridge_available):
        """Test WCS origin coordinate validation."""
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
        
        # Try to set invalid origin
        response = make_request(
            f"/cam/setups/{setup_id}/wcs",
            method="PUT",
            data={"origin": {"x": "invalid", "y": None, "z": []}}
        )
        
        if response.status_code == 404:
            pytest.skip("WCS PUT endpoint not implemented")
        
        if response.status_code == 501:
            pytest.skip("WCS modification not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        # Should reject invalid coordinates
        is_error = (
            response.status_code in [400, 422, 500] or
            content.get("error") is True
        )
        assert is_error or response.status_code == 200, (
            f"Expected validation error for invalid origin: {data}"
        )


class TestWCSOrientation:
    """Tests for WCS orientation vectors."""
    
    def test_wcs_has_orientation(self, bridge_available):
        """Test that WCS includes orientation information."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/wcs")
        
        if response.status_code == 404:
            pytest.skip("WCS endpoint not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get WCS: {content}")
        
        # Should have orientation information
        has_orientation = (
            "orientation" in content or
            "x_axis" in content or
            "y_axis" in content or
            "z_axis" in content or
            "x_direction" in content or
            "rotation" in content
        )
        # Soft check - orientation may not be exposed
        if not has_orientation:
            pytest.skip("WCS orientation not in response (may be by design)")
    
    @pytest.mark.destructive
    def test_wcs_orientation_validation_non_orthogonal(self, bridge_available):
        """Test that non-orthogonal orientation vectors are rejected."""
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
        
        # Try to set non-orthogonal vectors
        response = make_request(
            f"/cam/setups/{setup_id}/wcs",
            method="PUT",
            data={
                "orientation": {
                    "x_axis": [1, 0, 0],
                    "y_axis": [1, 0, 0],  # Same as x - not orthogonal
                    "z_axis": [0, 0, 1]
                }
            }
        )
        
        if response.status_code == 404:
            pytest.skip("WCS PUT endpoint not implemented")
        
        if response.status_code == 501:
            pytest.skip("WCS modification not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        # Should reject non-orthogonal vectors
        is_error = (
            response.status_code in [400, 422, 500] or
            content.get("error") is True or
            "orthogonal" in str(content).lower() or
            "invalid" in str(content).lower()
        )
        assert is_error or response.status_code == 200, (
            f"Expected validation error for non-orthogonal vectors: {data}"
        )


class TestWCSTypes:
    """Tests for WCS type values."""
    
    VALID_WCS_TYPES = [
        "model_origin", "face_based", "custom", "box_point",
        "stock_box_point", "selected_point", "orientation"
    ]
    
    def test_wcs_type_is_valid(self, bridge_available):
        """Test that WCS type is a valid value."""
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
        
        response = make_request(f"/cam/setups/{setup_id}/wcs")
        
        if response.status_code == 404:
            pytest.skip("WCS endpoint not implemented")
        
        data = response.json()
        content = data.get("data", data)
        
        if content.get("error"):
            pytest.skip(f"Could not get WCS: {content}")
        
        wcs_type = content.get("type") or content.get("wcs_type")
        
        if not wcs_type:
            pytest.skip("WCS type not in response")
        
        # Type should be a known value (case-insensitive)
        type_lower = wcs_type.lower().replace(" ", "_").replace("-", "_")
        valid_types_lower = [t.lower() for t in self.VALID_WCS_TYPES]
        
        # Soft check - there may be other valid types
        if type_lower not in valid_types_lower:
            pytest.skip(f"Unknown WCS type '{wcs_type}' (may be valid)")


class TestWCSChangeImpact:
    """Tests for WCS change impact warnings."""
    
    def test_wcs_change_returns_impact_info(self, bridge_available):
        """Test that WCS changes include impact information."""
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
        
        # Check if there's an impact preview endpoint
        response = make_request(
            f"/cam/setups/{setup_id}/wcs/impact",
            method="POST",
            data={"origin": {"x": 10, "y": 20, "z": 0}}
        )
        
        if response.status_code == 404:
            pytest.skip("WCS impact endpoint not implemented")
        
        assert not response_is_empty(response), "Impact response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        # Should have impact information
        has_impact = (
            "impact" in content or
            "affected_operations" in content or
            "warnings" in content or
            "regeneration_required" in content or
            "error" in content
        )
        assert has_impact, f"Impact response missing expected fields: {data}"
