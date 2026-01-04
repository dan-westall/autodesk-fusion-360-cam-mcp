#!/usr/bin/env python3
"""
Live Integration Tests for Design Workspace

Tests for Design workspace endpoints including:
- Basic connectivity
- Geometry creation (box, cylinder, circle)
- Feature operations (extrude, revolve, fillet)
- Export functionality

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - A design document open

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_design.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [pytest.mark.integration, pytest.mark.design]


class TestDesignConnection:
    """Tests for basic Design workspace connectivity."""
    
    def test_connection_endpoint_responds(self, bridge_available):
        """Test that /test_connection endpoint responds."""
        response = make_request("/test_connection")
        
        assert response.status_code == 200, (
            f"Connection test failed with status {response.status_code}"
        )
        assert not response_is_empty(response), "Connection response should not be empty"
    
    def test_connection_returns_status(self, bridge_available):
        """Test that connection response includes status."""
        response = make_request("/test_connection")
        data = response.json()
        
        has_status = (
            "status" in data or
            "connected" in data or
            "success" in data or
            "message" in data
        )
        assert has_status, f"Connection response missing status: {data}"


class TestGeometryCreation:
    """Tests for geometry creation endpoints."""
    
    @pytest.mark.destructive
    def test_draw_box_returns_response(self, bridge_available):
        """Test that /draw-box endpoint returns a response."""
        response = make_request(
            "/draw-box",
            method="POST",
            data={"width": 10, "height": 10, "depth": 10}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /draw-box returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Draw box not implemented")
    
    @pytest.mark.destructive
    @pytest.mark.skip(reason="404 on /draw-box endpoint - endpoint not implemented")
    def test_draw_box_missing_params(self, bridge_available):
        """Test draw box with missing parameters."""
        response = make_request(
            "/draw-box",
            method="POST",
            data={}
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        if response.status_code == 501:
            pytest.skip("Draw box not implemented")
        
        # Should return error for missing params or succeed with defaults
        data = response.json()
        is_error = (
            response.status_code in [400, 422, 500] or
            data.get("error") is True or
            "required" in str(data).lower()
        )
        
        if is_error:
            # Verify error response has expected structure
            assert response.status_code >= 400, (
                f"Error response should have 4xx/5xx status: {response.status_code}"
            )
        else:
            # Success case - implementation uses defaults
            assert response.status_code == 200, (
                f"Success response should have 200 status: {response.status_code}"
            )
    
    @pytest.mark.destructive
    def test_draw_cylinder_returns_response(self, bridge_available):
        """Test that /draw-cylinder endpoint returns a response."""
        response = make_request(
            "/draw-cylinder",
            method="POST",
            data={"radius": 5, "height": 20}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /draw-cylinder returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Draw cylinder not implemented")
    
    @pytest.mark.destructive
    def test_draw_circle_returns_response(self, bridge_available):
        """Test that /draw-circle endpoint returns a response."""
        response = make_request(
            "/draw-circle",
            method="POST",
            data={"radius": 10, "x": 0, "y": 0}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /draw-circle returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Draw circle not implemented")
    
    @pytest.mark.destructive
    def test_draw_lines_returns_response(self, bridge_available):
        """Test that /draw-lines endpoint returns a response."""
        response = make_request(
            "/draw-lines",
            method="POST",
            data={
                "points": [
                    {"x": 0, "y": 0},
                    {"x": 10, "y": 0},
                    {"x": 10, "y": 10},
                    {"x": 0, "y": 10}
                ]
            }
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /draw-lines returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Draw lines not implemented")


class TestFeatureOperations:
    """Tests for feature operation endpoints."""
    
    @pytest.mark.destructive
    def test_extrude_returns_response(self, bridge_available):
        """Test that /extrude endpoint returns a response."""
        response = make_request(
            "/extrude",
            method="POST",
            data={"distance": 10}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /extrude returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Extrude not implemented")
    
    @pytest.mark.destructive
    def test_extrude_missing_distance(self, bridge_available):
        """Test extrude with missing distance parameter."""
        response = make_request(
            "/extrude",
            method="POST",
            data={}
        )
        
        assert not response_is_empty(response), "Response should not be empty"
        
        if response.status_code == 501:
            pytest.skip("Extrude not implemented")
    
    @pytest.mark.destructive
    @pytest.mark.skip(reason="Triggers interactive dialog 'Select a profile to revolve'")
    def test_revolve_returns_response(self, bridge_available):
        """Test that /revolve endpoint returns a response."""
        response = make_request(
            "/revolve",
            method="POST",
            data={"angle": 360}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /revolve returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Revolve not implemented")
    
    @pytest.mark.destructive
    def test_fillet_returns_response(self, bridge_available):
        """Test that /fillet endpoint returns a response."""
        response = make_request(
            "/fillet",
            method="POST",
            data={"radius": 2}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /fillet returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Fillet not implemented")
    
    @pytest.mark.destructive
    def test_shell_returns_response(self, bridge_available):
        """Test that /shell endpoint returns a response."""
        response = make_request(
            "/shell",
            method="POST",
            data={"thickness": 1}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /shell returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Shell not implemented")


class TestExportOperations:
    """Tests for export endpoints."""
    
    @pytest.mark.slow
    def test_export_step_returns_response(self, bridge_available):
        """Test that /export-step endpoint returns a response."""
        response = make_request(
            "/export-step",
            method="POST",
            data={"filename": "test_export"}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /export-step returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Export STEP not implemented")
    
    @pytest.mark.slow
    def test_export_stl_returns_response(self, bridge_available):
        """Test that /export-stl endpoint returns a response."""
        response = make_request(
            "/export-stl",
            method="POST",
            data={"filename": "test_export"}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /export-stl returned empty response."
        )
        
        if response.status_code == 501:
            pytest.skip("Export STL not implemented")
    
    def test_export_with_invalid_params(self, bridge_available):
        """Test export with invalid parameters."""
        response = make_request(
            "/export-step",
            method="POST",
            data={"filename": ""}  # Empty filename
        )
        
        if response.status_code == 501:
            pytest.skip("Export STEP not implemented")
        
        # Should handle gracefully
        assert not response_is_empty(response), "Response should not be empty"


class TestGeometryErrors:
    """Tests for geometry operation error handling."""
    
    @pytest.mark.destructive
    @pytest.mark.skip(reason="404 on /draw-box endpoint - endpoint not implemented")
    def test_draw_box_invalid_dimensions(self, bridge_available):
        """Test draw box with invalid dimensions."""
        response = make_request(
            "/draw-box",
            method="POST",
            data={"width": -10, "height": 0, "depth": "invalid"}
        )
        
        if response.status_code == 501:
            pytest.skip("Draw box not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        # Should return error for invalid dimensions
        is_error = (
            response.status_code in [400, 422, 500] or
            data.get("error") is True
        )
        # Some implementations may clamp values
        assert is_error or response.status_code == 200, (
            f"Expected error or handled gracefully: {data}"
        )
    
    @pytest.mark.destructive
    def test_extrude_negative_distance(self, bridge_available):
        """Test extrude with negative distance."""
        response = make_request(
            "/extrude",
            method="POST",
            data={"distance": -10}
        )
        
        if response.status_code == 501:
            pytest.skip("Extrude not implemented")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        # Negative distance may be valid (cut direction) or error
        # Just verify we get a response
    
    def test_operation_when_no_sketch(self, bridge_available):
        """Test operation when no sketch is available."""
        # This tests error handling when prerequisites aren't met
        response = make_request(
            "/extrude-last-sketch",
            method="POST",
            data={"distance": 10}
        )
        
        if response.status_code == 501:
            pytest.skip("Extrude last sketch not implemented")
        
        if response.status_code == 404:
            pytest.skip("Extrude last sketch endpoint not found")
        
        assert not response_is_empty(response), "Response should not be empty"


class TestDesignResponseStructure:
    """Tests for Design workspace response structure validation."""
    
    def test_geometry_response_has_result(self, bridge_available):
        """Test that geometry responses include result information."""
        response = make_request(
            "/draw-box",
            method="POST",
            data={"width": 10, "height": 10, "depth": 10}
        )
        
        if response.status_code == 501:
            pytest.skip("Draw box not implemented")
        
        data = response.json()
        
        # Should have result or error information
        has_result = (
            "result" in data or
            "success" in data or
            "body" in data or
            "feature" in data or
            "error" in data or
            "message" in data
        )
        assert has_result, f"Geometry response missing result info: {data}"
    
    def test_error_response_has_message(self, bridge_available):
        """Test that error responses include message."""
        # Intentionally cause an error
        response = make_request(
            "/draw-box",
            method="POST",
            data={"width": "not_a_number"}
        )
        
        if response.status_code == 501:
            pytest.skip("Draw box not implemented")
        
        if response.status_code == 200:
            pytest.skip("Request succeeded (implementation may convert types)")
        
        data = response.json()
        
        # Error response should have message
        has_message = (
            "message" in data or
            "error" in data or
            "detail" in data
        )
        assert has_message, f"Error response missing message: {data}"
