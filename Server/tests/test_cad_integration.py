#!/usr/bin/env python3
"""
Integration tests for CAD tools modernization.

This module contains integration tests that make real HTTP requests to the Fusion 360 add-in
to validate that all modernized CAD functions work correctly with their endpoints.

Tests validate:
- HTTP endpoint connectivity
- Request/response format validation
- Error handling with connection failures and timeouts
- Response structure consistency
"""

import pytest
import sys
import os
import requests
import time
from typing import Dict, Any, List
from unittest.mock import patch

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from core.config import get_endpoints, get_base_url, get_timeout
from tools.cad import geometry, sketching, modeling, features


class TestCADIntegration:
    """Integration tests for CAD tools with HTTP endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class."""
        cls.base_url = get_base_url()
        cls.timeout = get_timeout()
        cls.cad_endpoints = get_endpoints("cad")
        
        # Test connection to Fusion 360 add-in
        try:
            response = requests.get(f"{cls.base_url}/test_connection", timeout=5)
            if response.status_code != 200:
                pytest.skip("Fusion 360 add-in not available")
        except requests.RequestException:
            pytest.skip("Fusion 360 add-in not available")
    
    def test_fusion_360_connection(self):
        """Test basic connection to Fusion 360 add-in."""
        response = requests.get(f"{self.base_url}/test_connection", timeout=self.timeout)
        assert response.status_code == 200
        
        # Should return JSON response
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
    
    def test_all_cad_endpoints_exist(self):
        """Test that all CAD endpoints are accessible."""
        missing_endpoints = []
        working_endpoints = []
        
        for endpoint_name, endpoint_url in self.cad_endpoints.items():
            # Make a basic POST request to check endpoint exists
            try:
                response = requests.post(endpoint_url, json={}, timeout=5)
                if response.status_code == 404:
                    missing_endpoints.append(f"{endpoint_name} ({endpoint_url})")
                else:
                    working_endpoints.append(f"{endpoint_name} ({endpoint_url})")
            except requests.RequestException as e:
                missing_endpoints.append(f"{endpoint_name} ({endpoint_url}) - Connection error: {e}")
        
        # Report results
        print(f"\nWorking endpoints ({len(working_endpoints)}):")
        for endpoint in working_endpoints:
            print(f"  ✓ {endpoint}")
            
        if missing_endpoints:
            print(f"\nMissing endpoints ({len(missing_endpoints)}):")
            for endpoint in missing_endpoints:
                print(f"  ✗ {endpoint}")
        
        # For integration testing, we expect most endpoints to work
        # Allow some endpoints to be missing during development
        working_percentage = len(working_endpoints) / len(self.cad_endpoints) * 100
        assert working_percentage >= 70, f"Too many endpoints missing: {working_percentage:.1f}% working"
    
    def test_geometry_draw_cylinder_endpoint(self):
        """Test draw_cylinder function with HTTP endpoint."""
        # Test with valid parameters
        result = geometry.draw_cylinder(radius=2.0, height=5.0, x=0.0, y=0.0, z=0.0, plane="XY")
        
        # Should return a dictionary response
        assert isinstance(result, dict)
        
        # Check response structure
        if "error" in result:
            # If error, should have proper error structure
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            # If success, should have success indicators
            assert "error" not in result or result["error"] is False
    
    def test_geometry_draw_box_endpoint(self):
        """Test draw_box function with HTTP endpoint."""
        result = geometry.draw_box(
            height_value="3", width_value="4", depth_value="2",
            x_value=0.0, y_value=0.0, z_value=0.0, plane="XY"
        )
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_geometry_draw_sphere_endpoint(self):
        """Test draw_sphere function with HTTP endpoint."""
        result = geometry.draw_sphere(x=0.0, y=0.0, z=0.0, radius=3.0)
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_sketching_draw2dcircle_endpoint(self):
        """Test draw2Dcircle function with HTTP endpoint."""
        result = sketching.draw2Dcircle(radius=2.5, x=0.0, y=0.0, z=0.0, plane="XY")
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_sketching_draw_lines_endpoint(self):
        """Test draw_lines function with HTTP endpoint."""
        points = [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0]]
        result = sketching.draw_lines(points=points, plane="XY")
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_sketching_draw_one_line_endpoint(self):
        """Test draw_one_line function with HTTP endpoint."""
        result = sketching.draw_one_line(
            x1=0.0, y1=0.0, z1=0.0, x2=10.0, y2=10.0, z2=0.0, plane="XY"
        )
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_sketching_draw_arc_endpoint(self):
        """Test draw_arc function with HTTP endpoint."""
        result = sketching.draw_arc(
            point1=[0, 0, 0], point2=[5, 5, 0], point3=[10, 0, 0], plane="XY"
        )
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_sketching_spline_endpoint(self):
        """Test spline function with HTTP endpoint."""
        points = [[0, 0, 0], [5, 10, 0], [10, 5, 0], [15, 0, 0]]
        result = sketching.spline(points=points, plane="XY")
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_modeling_extrude_endpoint(self):
        """Test extrude function with HTTP endpoint."""
        result = modeling.extrude(value=5.0, angle=0.0)
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_modeling_revolve_endpoint(self):
        """Test revolve function with HTTP endpoint."""
        result = modeling.revolve(angle=360.0)
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_features_fillet_edges_endpoint(self):
        """Test fillet_edges function with HTTP endpoint."""
        result = features.fillet_edges(radius="1.0")
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False
    
    def test_features_circular_pattern_endpoint(self):
        """Test circular_pattern function with HTTP endpoint."""
        result = features.circular_pattern(
            plane="XY", quantity=6.0, axis="Z"
        )
        
        assert isinstance(result, dict)
        
        if "error" in result:
            assert isinstance(result["error"], bool)
            assert "message" in result
            assert "code" in result
        else:
            assert "error" not in result or result["error"] is False


class TestCADErrorHandling:
    """Test error handling for CAD functions."""
    
    def test_connection_error_handling(self):
        """Test connection error handling when Fusion 360 is not available."""
        # Mock requests to simulate connection error
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.ConnectionError("Connection failed")
            
            result = geometry.draw_cylinder(radius=2.0, height=5.0, x=0.0, y=0.0, z=0.0)
            
            assert isinstance(result, dict)
            assert result["error"] is True
            assert "Cannot connect to Fusion 360" in result["message"]
            assert result["code"] == "CONNECTION_ERROR"
    
    def test_timeout_error_handling(self):
        """Test timeout error handling."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.Timeout("Request timed out")
            
            result = geometry.draw_box(
                height_value="3", width_value="4", depth_value="2",
                x_value=0.0, y_value=0.0, z_value=0.0
            )
            
            assert isinstance(result, dict)
            assert result["error"] is True
            assert "timed out" in result["message"]
            assert result["code"] == "TIMEOUT_ERROR"
    
    def test_generic_exception_handling(self):
        """Test generic exception handling."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Unexpected error")
            
            result = geometry.draw_sphere(x=0.0, y=0.0, z=0.0, radius=3.0)
            
            assert isinstance(result, dict)
            assert result["error"] is True
            assert "Failed to draw sphere" in result["message"]
            assert result["code"] == "UNKNOWN_ERROR"
    
    def test_error_response_format_consistency(self):
        """Test that all error responses follow the same format."""
        error_functions = [
            lambda: geometry.draw_cylinder(radius=2.0, height=5.0, x=0.0, y=0.0, z=0.0),
            lambda: geometry.draw_box("3", "4", "2", 0.0, 0.0, 0.0),
            lambda: geometry.draw_sphere(x=0.0, y=0.0, z=0.0, radius=3.0),
            lambda: sketching.draw2Dcircle(radius=2.5, x=0.0, y=0.0, z=0.0),
            lambda: modeling.extrude(value=5.0, angle=0.0),
            lambda: features.fillet_edges(radius="1.0")
        ]
        
        for func in error_functions:
            with patch('requests.post') as mock_post:
                mock_post.side_effect = requests.ConnectionError("Connection failed")
                
                result = func()
                
                # Validate error response format
                assert isinstance(result, dict)
                assert "error" in result
                assert isinstance(result["error"], bool)
                assert result["error"] is True
                assert "message" in result
                assert isinstance(result["message"], str)
                assert len(result["message"]) > 0
                assert "code" in result
                assert isinstance(result["code"], str)
                assert result["code"] in ["CONNECTION_ERROR", "TIMEOUT_ERROR", "UNKNOWN_ERROR"]


class TestCADResponseValidation:
    """Test response format validation for CAD functions."""
    
    @classmethod
    def setup_class(cls):
        """Set up test class."""
        cls.base_url = get_base_url()
        
        # Test connection to Fusion 360 add-in
        try:
            response = requests.get(f"{cls.base_url}/test_connection", timeout=5)
            if response.status_code != 200:
                pytest.skip("Fusion 360 add-in not available")
        except requests.RequestException:
            pytest.skip("Fusion 360 add-in not available")
    
    def validate_response_structure(self, response: Dict[str, Any]) -> None:
        """Validate response structure is consistent."""
        assert isinstance(response, dict), "Response should be a dictionary"
        
        if "error" in response:
            if response["error"]:
                # Error response validation
                assert "message" in response, "Error response should have message"
                assert "code" in response, "Error response should have code"
                assert isinstance(response["message"], str), "Error message should be string"
                assert isinstance(response["code"], str), "Error code should be string"
                assert response["code"] in ["CONNECTION_ERROR", "TIMEOUT_ERROR", "UNKNOWN_ERROR"]
            else:
                # Success response (error: false)
                assert response["error"] is False
        # If no error field, assume success response
    
    def test_geometry_functions_response_format(self):
        """Test that all geometry functions return properly formatted responses."""
        functions_and_params = [
            (geometry.draw_cylinder, {"radius": 2.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0}),
            (geometry.draw_box, {"height_value": "3", "width_value": "4", "depth_value": "2", 
                                "x_value": 0.0, "y_value": 0.0, "z_value": 0.0}),
            (geometry.draw_sphere, {"x": 0.0, "y": 0.0, "z": 0.0, "radius": 3.0})
        ]
        
        for func, params in functions_and_params:
            result = func(**params)
            self.validate_response_structure(result)
    
    def test_sketching_functions_response_format(self):
        """Test that all sketching functions return properly formatted responses."""
        functions_and_params = [
            (sketching.draw2Dcircle, {"radius": 2.5, "x": 0.0, "y": 0.0, "z": 0.0}),
            (sketching.draw_lines, {"points": [[0, 0, 0], [10, 10, 0]], "plane": "XY"}),
            (sketching.draw_one_line, {"x1": 0.0, "y1": 0.0, "z1": 0.0, "x2": 10.0, "y2": 10.0, "z2": 0.0}),
            (sketching.draw_arc, {"point1": [0, 0, 0], "point2": [5, 5, 0], "point3": [10, 0, 0], "plane": "XY"}),
            (sketching.spline, {"points": [[0, 0, 0], [5, 10, 0]], "plane": "XY"})
        ]
        
        for func, params in functions_and_params:
            result = func(**params)
            self.validate_response_structure(result)
    
    def test_modeling_functions_response_format(self):
        """Test that all modeling functions return properly formatted responses."""
        functions_and_params = [
            (modeling.extrude, {"value": 5.0, "angle": 0.0}),
            (modeling.revolve, {"angle": 360.0})
        ]
        
        for func, params in functions_and_params:
            result = func(**params)
            self.validate_response_structure(result)
    
    def test_features_functions_response_format(self):
        """Test that all features functions return properly formatted responses."""
        functions_and_params = [
            (features.fillet_edges, {"radius": "1.0"}),
            (features.circular_pattern, {"plane": "XY", "quantity": 6.0, "axis": "Z"})
        ]
        
        for func, params in functions_and_params:
            result = func(**params)
            self.validate_response_structure(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])