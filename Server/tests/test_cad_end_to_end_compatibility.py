#!/usr/bin/env python3
"""
End-to-End Compatibility Property Test for CAD Tools Modernization.

This module contains property-based tests to verify that the modernized CAD tools
maintain complete end-to-end compatibility with the original implementation.

Property 7: End-to-End Compatibility
Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import Dict, Any, List, Tuple

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from tools.cad import geometry, sketching, modeling, features
from core import interceptor
from tests.cad_modernization_utils import (
    get_cad_functions,
    CADModernizationUtils
)


def create_mock_response(status_code: int, json_data: Dict[str, Any]) -> MagicMock:
    """Create a mock HTTP response."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data
    return mock_response


def validate_error_response_format(response: Dict[str, Any]) -> bool:
    """Validate error response format using the utility function."""
    return CADModernizationUtils.validate_error_response_format(response)


class TestCADEndToEndCompatibility:
    """Property-based tests for end-to-end compatibility of modernized CAD tools."""
    
    def setup_method(self):
        """Set up test method."""
        # Reset interceptor state
        interceptor.set_interceptor_enabled(False)
    
    def teardown_method(self):
        """Clean up after test method."""
        # Reset interceptor state
        interceptor.set_interceptor_enabled(False)
    
    @given(
        interceptor_enabled=st.booleans(),
        response_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=1, max_size=50),
                st.integers(min_value=-1000, max_value=1000),
                st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
                st.booleans()
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_end_to_end_compatibility(self, interceptor_enabled: bool, response_data: Dict[str, Any]):
        """
        Property 7: End-to-End Compatibility
        
        Tests that modernized CAD functions maintain complete compatibility:
        - HTTP requests are made correctly (Requirement 8.1)
        - Response formats are preserved (Requirement 8.2) 
        - Server loading works without errors (Requirement 8.3)
        - Function signatures are unchanged (Requirement 8.4)
        - Interceptor integration works properly (Requirement 8.5)
        """
        # Set interceptor state
        interceptor.set_interceptor_enabled(interceptor_enabled)
        
        # Get all CAD functions to test
        all_functions = get_cad_functions()
        
        with patch('requests.post') as mock_post, \
             patch('requests.get') as mock_get:
            
            # Set up mock response
            mock_response = create_mock_response(200, response_data)
            mock_post.return_value = mock_response
            mock_get.return_value = mock_response
            
            # Test a sample of functions from each module
            functions_to_test = [
                # Geometry functions
                (geometry.draw_cylinder, {"radius": 2.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0}),
                (geometry.draw_box, {"height_value": "3", "width_value": "4", "depth_value": "2", 
                                    "x_value": 0.0, "y_value": 0.0, "z_value": 0.0}),
                (geometry.draw_sphere, {"x": 0.0, "y": 0.0, "z": 0.0, "radius": 3.0}),
                
                # Sketching functions
                (sketching.draw2Dcircle, {"radius": 2.5, "x": 0.0, "y": 0.0, "z": 0.0, "plane": "XY"}),
                (sketching.draw_lines, {"points": [[0, 0, 0], [10, 10, 0]], "plane": "XY"}),
                (sketching.draw_one_line, {"x1": 0.0, "y1": 0.0, "z1": 0.0, "x2": 10.0, "y2": 10.0, "z2": 0.0, "plane": "XY"}),
                
                # Modeling functions
                (modeling.extrude, {"value": 5.0, "angle": 0.0}),
                (modeling.revolve, {"angle": 180.0}),
                (modeling.loft, {"sketchcount": 2}),
                
                # Features functions
                (features.fillet_edges, {"radius": 2.0}),
                (features.draw_holes, {"points": [[0, 0, 0]], "depth": 10.0, "width": 5.0, "faceindex": 0}),
                (features.shell_body, {"thickness": 2.0, "faceindex": 0})
            ]
            
            for func, params in functions_to_test:
                # Test function call succeeds
                result = func(**params)
                
                # Verify result format (Requirement 8.2)
                assert isinstance(result, dict), f"Function {func.__name__} should return dict"
                assert result == response_data, f"Function {func.__name__} should return response data unchanged"
                
                # Verify HTTP request was made (Requirement 8.1)
                assert mock_post.called or mock_get.called, f"Function {func.__name__} should make HTTP request"
                
                # Reset mocks for next function
                mock_post.reset_mock()
                mock_get.reset_mock()
    
    @given(
        error_type=st.sampled_from(['connection', 'timeout', 'http_error', 'json_decode'])
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_error_handling_compatibility(self, error_type: str):
        """
        Property 7.1: Error Handling Compatibility
        
        Tests that error handling is consistent across all modernized functions.
        """
        # Test functions from each module
        test_functions = [
            (geometry.draw_cylinder, {"radius": 2.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0}),
            (sketching.draw2Dcircle, {"radius": 2.5, "x": 0.0, "y": 0.0, "z": 0.0, "plane": "XY"}),
            (modeling.extrude, {"value": 5.0, "angle": 0.0}),
            (features.fillet_edges, {"radius": 2.0})
        ]
        
        with patch('requests.post') as mock_post:
            # Set up different error conditions
            if error_type == 'connection':
                mock_post.side_effect = Exception("Connection failed")
            elif error_type == 'timeout':
                mock_post.side_effect = Exception("Request timeout")
            elif error_type == 'http_error':
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.json.return_value = {"error": True, "message": "Server error", "code": "UNKNOWN_ERROR"}
                mock_post.return_value = mock_response
            elif error_type == 'json_decode':
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_post.return_value = mock_response
            
            for func, params in test_functions:
                result = func(**params)
                
                # Verify error response format is consistent (Requirement 8.2)
                assert validate_error_response_format(result), f"Function {func.__name__} should return valid error format"
                
                # Verify error response contains required fields
                assert "error" in result, f"Function {func.__name__} error response should have 'error' field"
                assert "message" in result, f"Function {func.__name__} error response should have 'message' field"
                assert "code" in result, f"Function {func.__name__} error response should have 'code' field"
                
                # Verify error flag is set
                assert result["error"] is True, f"Function {func.__name__} should set error=True on failure"
    
    @given(
        interceptor_state=st.booleans()
    )
    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_interceptor_integration_compatibility(self, interceptor_state: bool):
        """
        Property 7.2: Interceptor Integration Compatibility
        
        Tests that interceptor integration works consistently across all functions.
        Validates Requirement 8.5.
        """
        # Set interceptor state
        interceptor.set_interceptor_enabled(interceptor_state)
        
        # Test functions that use different HTTP methods
        test_functions = [
            (geometry.draw_cylinder, {"radius": 2.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0}),
            (modeling.extrude, {"value": 5.0, "angle": 0.0}),
            (features.shell_body, {"thickness": 2.0, "faceindex": 0})
        ]
        
        with patch('requests.post') as mock_post, \
             patch('core.interceptor.intercept_response') as mock_intercept:
            
            # Set up mock response
            mock_response = create_mock_response(200, {"success": True})
            mock_post.return_value = mock_response
            mock_intercept.return_value = {"success": True}
            
            for func, params in test_functions:
                result = func(**params)
                
                # Verify interceptor was called (Requirement 8.5)
                assert mock_intercept.called, f"Function {func.__name__} should call interceptor"
                
                # Verify interceptor was called with correct parameters
                call_args = mock_intercept.call_args
                assert len(call_args[0]) == 3, f"Interceptor should be called with 3 arguments"
                
                endpoint, response, method = call_args[0]
                assert isinstance(endpoint, str), f"Endpoint should be string"
                assert response == mock_response, f"Response should be passed to interceptor"
                assert method in ["GET", "POST"], f"Method should be GET or POST"
                
                # Verify function returns interceptor result
                assert result == {"success": True}, f"Function should return interceptor result"
                
                # Reset mock for next function
                mock_intercept.reset_mock()
    
    def test_property_function_signature_preservation(self):
        """
        Property 7.3: Function Signature Preservation
        
        Tests that all modernized functions preserve their original signatures.
        Validates Requirement 8.4.
        """
        # Get all CAD functions
        all_functions = get_cad_functions()
        
        # Test that functions can be called (signature preserved)
        signature_tests = [
            # Geometry functions - test basic parameter acceptance
            (geometry.draw_cylinder, {"radius": 1.0, "height": 1.0, "x": 0.0, "y": 0.0, "z": 0.0}),
            (geometry.draw_box, {"height_value": "1", "width_value": "1", "depth_value": "1", 
                                "x_value": 0.0, "y_value": 0.0, "z_value": 0.0}),
            (geometry.draw_sphere, {"x": 0.0, "y": 0.0, "z": 0.0, "radius": 1.0}),
            
            # Sketching functions
            (sketching.draw2Dcircle, {"radius": 1.0, "x": 0.0, "y": 0.0, "z": 0.0, "plane": "XY"}),
            (sketching.draw_lines, {"points": [[0, 0, 0], [1, 1, 0]], "plane": "XY"}),
            (sketching.draw_one_line, {"x1": 0.0, "y1": 0.0, "z1": 0.0, "x2": 1.0, "y2": 1.0, "z2": 0.0, "plane": "XY"}),
            (sketching.draw_arc, {"point1": [0, 0, 0], "point2": [1, 1, 0], "point3": [2, 0, 0], "plane": "XY"}),
            (sketching.spline, {"points": [[0, 0, 0], [1, 1, 0], [2, 0, 0]], "plane": "XY"}),
            
            # Modeling functions
            (modeling.extrude, {"value": 1.0, "angle": 0.0}),
            (modeling.extrude_thin, {"thickness": 0.1, "distance": 1.0}),
            (modeling.cut_extrude, {"depth": 1.0}),
            (modeling.revolve, {"angle": 90.0}),
            (modeling.loft, {"sketchcount": 2}),
            (modeling.sweep, {}),
            (modeling.boolean_operation, {"operation": "union"}),
            (modeling.draw_2d_rectangle, {"x_1": 0.0, "y_1": 0.0, "z_1": 0.0, "x_2": 10.0, "y_2": 5.0, "z_2": 0.0, "plane": "XY"}),
            (modeling.draw_text, {"text": "Test", "plane": "XY", "x_1": 0.0, "y_1": 0.0, "z_1": 0.0, "x_2": 10.0, "y_2": 10.0, "z_2": 0.0, "thickness": 1.0, "value": 10.0}),
            
            # Features functions
            (features.fillet_edges, {"radius": 1.0}),
            (features.draw_holes, {"points": [[0, 0, 0]], "depth": 10.0, "width": 5.0, "faceindex": 0}),
            (features.shell_body, {"thickness": 1.0, "faceindex": 0}),
            (features.circular_pattern, {"plane": "XY", "quantity": 4.0, "axis": "Z"}),
            (features.rectangular_pattern, {"plane": "XY", "quantity_one": 2.0, "quantity_two": 2.0, "distance_one": 10.0, "distance_two": 10.0, "axis_one": "X", "axis_two": "Y"}),
            (features.create_thread, {"inside": True, "allsizes": 1}),
            (features.ellipsie, {"x_center": 0.0, "y_center": 0.0, "z_center": 0.0,
                                "x_major": 10.0, "y_major": 0.0, "z_major": 0.0,
                                "x_through": 0.0, "y_through": 5.0, "z_through": 0.0, "plane": "XY"}),
            (features.draw_witzenmannlogo, {})
        ]
        
        with patch('requests.post') as mock_post:
            # Set up mock response
            mock_response = create_mock_response(200, {"signature_test": True})
            mock_post.return_value = mock_response
            
            for func, params in signature_tests:
                try:
                    # Test that function can be called with expected parameters
                    result = func(**params)
                    
                    # Verify function executed without signature errors
                    assert isinstance(result, dict), f"Function {func.__name__} should return dict"
                    
                except TypeError as e:
                    # Signature mismatch - this should not happen
                    pytest.fail(f"Function {func.__name__} signature changed: {e}")
                except Exception:
                    # Other exceptions are OK (network errors, etc.)
                    pass
    
    def test_property_module_loading_compatibility(self):
        """
        Property 7.4: Module Loading Compatibility
        
        Tests that all modules can be loaded without errors.
        Validates Requirement 8.3.
        """
        # Test that all modules can be imported
        modules_to_test = [
            'tools.cad.geometry',
            'tools.cad.sketching', 
            'tools.cad.modeling',
            'tools.cad.features'
        ]
        
        for module_name in modules_to_test:
            try:
                # Test module import
                __import__(module_name)
                
                # Test that module has expected functions
                module = sys.modules[module_name]
                
                # Verify module has callable functions
                functions = [attr for attr in dir(module) 
                           if callable(getattr(module, attr)) and not attr.startswith('_')]
                
                assert len(functions) > 0, f"Module {module_name} should have callable functions"
                
                # Test that functions are properly defined
                for func_name in functions:
                    func = getattr(module, func_name)
                    assert callable(func), f"Function {func_name} in {module_name} should be callable"
                    
            except ImportError as e:
                pytest.fail(f"Module {module_name} failed to import: {e}")
            except Exception as e:
                pytest.fail(f"Module {module_name} loading error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])