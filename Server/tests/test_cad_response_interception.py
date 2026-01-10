#!/usr/bin/env python3
"""
Response Interception Tests for CAD Tools Modernization.

This module contains tests to verify that response interception functionality
works correctly for modernized CAD tools.

Tests validate:
- Response interceptor can be enabled and disabled
- Interception works for both GET and POST requests
- Interceptor doesn't break normal operation
- Logging functionality works correctly
"""

import pytest
import sys
import os
import logging
import io
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from core import interceptor
from tools.cad import geometry, sketching, modeling, features


class TestCADResponseInterception:
    """Test response interception functionality for CAD tools."""
    
    def setup_method(self):
        """Set up test method."""
        # Reset interceptor state
        interceptor.set_interceptor_enabled(False)
        
        # Set up logging capture
        self.log_capture = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        self.log_handler.setLevel(logging.INFO)
        
        # Get the interceptor logger
        self.logger = logging.getLogger('core.interceptor')
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.INFO)
    
    def teardown_method(self):
        """Clean up after test method."""
        # Remove log handler
        self.logger.removeHandler(self.log_handler)
        
        # Reset interceptor state
        interceptor.set_interceptor_enabled(False)
    
    def test_interceptor_can_be_enabled_and_disabled(self):
        """Test that response interceptor can be enabled and disabled."""
        # Initially disabled
        assert not interceptor.is_interceptor_enabled()
        
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        assert interceptor.is_interceptor_enabled()
        
        # Disable interceptor
        interceptor.set_interceptor_enabled(False)
        assert not interceptor.is_interceptor_enabled()
    
    def test_interceptor_toggle_functionality(self):
        """Test interceptor toggle functionality."""
        # Initially disabled
        initial_state = interceptor.is_interceptor_enabled()
        
        # Toggle should change state
        new_state = interceptor.toggle_interceptor()
        assert interceptor.is_interceptor_enabled() != initial_state
        assert new_state == interceptor.is_interceptor_enabled()
        
        # Toggle again should return to original state
        new_state = interceptor.toggle_interceptor()
        assert interceptor.is_interceptor_enabled() == initial_state
        assert new_state == interceptor.is_interceptor_enabled()
    
    def test_intercept_response_with_disabled_interceptor(self):
        """Test that intercept_response works normally when interceptor is disabled."""
        # Ensure interceptor is disabled
        interceptor.set_interceptor_enabled(False)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        
        # Call intercept_response
        result = interceptor.intercept_response("http://test.com/endpoint", mock_response, "POST")
        
        # Should return the JSON response
        assert result == {"success": True, "data": "test"}
        
        # Should not log anything when disabled
        log_output = self.log_capture.getvalue()
        assert "INTERCEPTOR" not in log_output
    
    def test_intercept_response_with_enabled_interceptor(self):
        """Test that intercept_response logs when interceptor is enabled."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        
        # Call intercept_response
        result = interceptor.intercept_response("http://test.com/endpoint", mock_response, "POST")
        
        # Should return the JSON response
        assert result == {"success": True, "data": "test"}
        
        # Should log when enabled
        log_output = self.log_capture.getvalue()
        assert "INTERCEPTOR" in log_output
        assert "POST" in log_output
        assert "http://test.com/endpoint" in log_output
    
    def test_intercept_response_handles_json_decode_error(self):
        """Test that intercept_response handles JSON decode errors gracefully."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        # Create mock response that raises JSON decode error
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        
        # Call intercept_response - should raise the exception
        with pytest.raises(ValueError):
            interceptor.intercept_response("http://test.com/endpoint", mock_response, "GET")
        
        # Should log the error when enabled
        log_output = self.log_capture.getvalue()
        assert "INTERCEPTOR" in log_output
        assert "Failed to parse" in log_output
    
    def test_intercept_response_handles_different_http_methods(self):
        """Test that intercept_response handles different HTTP methods correctly."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"method_test": True}
        
        # Test GET method
        result_get = interceptor.intercept_response("http://test.com/get", mock_response, "GET")
        assert result_get == {"method_test": True}
        
        # Test POST method
        result_post = interceptor.intercept_response("http://test.com/post", mock_response, "POST")
        assert result_post == {"method_test": True}
        
        # Check logs contain both methods
        log_output = self.log_capture.getvalue()
        assert "GET" in log_output
        assert "POST" in log_output
    
    def test_cad_functions_use_interceptor_correctly(self):
        """Test that CAD functions call interceptor with correct parameters."""
        with patch('requests.post') as mock_post, \
             patch('core.interceptor.intercept_response') as mock_intercept:
            
            # Set up mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            mock_intercept.return_value = {"intercepted": True}
            
            # Call a CAD function
            result = geometry.draw_cylinder(radius=2.0, height=5.0, x=0.0, y=0.0, z=0.0)
            
            # Verify requests.post was called
            assert mock_post.called
            
            # Verify interceptor was called with correct parameters
            assert mock_intercept.called
            call_args = mock_intercept.call_args
            
            # Should be called with (endpoint, response, method)
            assert len(call_args[0]) == 3
            endpoint, response, method = call_args[0]
            
            # Verify parameters
            assert "draw_cylinder" in endpoint
            assert response == mock_response
            assert method == "POST"
            
            # Verify function returns interceptor result
            assert result == {"intercepted": True}
    
    def test_interceptor_with_real_cad_function_calls(self):
        """Test interceptor with real CAD function calls (mocked HTTP)."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        with patch('requests.post') as mock_post:
            # Set up mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"geometry": "created", "id": "test123"}
            mock_post.return_value = mock_response
            
            # Call multiple CAD functions
            functions_to_test = [
                (geometry.draw_cylinder, {"radius": 2.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0}),
                (geometry.draw_box, {"height_value": "3", "width_value": "4", "depth_value": "2", 
                                    "x_value": 0.0, "y_value": 0.0, "z_value": 0.0}),
                (sketching.draw2Dcircle, {"radius": 2.5, "x": 0.0, "y": 0.0, "z": 0.0}),
                (modeling.extrude, {"value": 5.0, "angle": 0.0})
            ]
            
            results = []
            for func, params in functions_to_test:
                result = func(**params)
                results.append(result)
                
                # Each result should be the mocked JSON response
                assert result == {"geometry": "created", "id": "test123"}
            
            # Verify all calls were intercepted and logged
            log_output = self.log_capture.getvalue()
            assert log_output.count("INTERCEPTOR") == len(functions_to_test)
            assert "draw_cylinder" in log_output
            assert "draw_box" in log_output or "Box" in log_output
            assert "create_circle" in log_output
            assert "extrude_last_sketch" in log_output
    
    def test_interceptor_doesnt_break_error_handling(self):
        """Test that interceptor doesn't interfere with error handling."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        with patch('requests.post') as mock_post:
            # Simulate connection error
            mock_post.side_effect = Exception("Connection failed")
            
            # Call CAD function
            result = geometry.draw_sphere(x=0.0, y=0.0, z=0.0, radius=3.0)
            
            # Should return proper error response
            assert isinstance(result, dict)
            assert result["error"] is True
            assert "Failed to draw sphere" in result["message"]
            assert result["code"] == "UNKNOWN_ERROR"
            
            # Interceptor should not have been called (due to exception)
            log_output = self.log_capture.getvalue()
            # Should not contain interceptor logs since exception occurred before interception
            assert "INTERCEPTOR" not in log_output
    
    def test_interceptor_performance_impact(self):
        """Test that interceptor has minimal performance impact."""
        import time
        
        with patch('requests.post') as mock_post:
            # Set up mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"performance": "test"}
            mock_post.return_value = mock_response
            
            # Test with interceptor disabled
            interceptor.set_interceptor_enabled(False)
            start_time = time.time()
            for _ in range(10):
                geometry.draw_cylinder(radius=1.0, height=1.0, x=0.0, y=0.0, z=0.0)
            disabled_time = time.time() - start_time
            
            # Test with interceptor enabled
            interceptor.set_interceptor_enabled(True)
            start_time = time.time()
            for _ in range(10):
                geometry.draw_cylinder(radius=1.0, height=1.0, x=0.0, y=0.0, z=0.0)
            enabled_time = time.time() - start_time
            
            # Performance impact should be reasonable for debugging (less than 200% overhead)
            # Note: JSON formatting and logging can be expensive, but this is a debugging feature
            performance_impact = (enabled_time - disabled_time) / disabled_time if disabled_time > 0 else 0
            assert performance_impact < 2.0, f"Interceptor performance impact too high: {performance_impact:.2%}"
    
    def test_interceptor_logging_format(self):
        """Test that interceptor logging uses correct format."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        with patch('requests.post') as mock_post:
            # Set up mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data", "nested": {"key": "value"}}
            mock_post.return_value = mock_response
            
            # Call CAD function
            geometry.draw_cylinder(radius=2.0, height=5.0, x=0.0, y=0.0, z=0.0)
            
            # Check log format
            log_output = self.log_capture.getvalue()
            
            # Should contain interceptor header
            assert "INTERCEPTOR" in log_output
            
            # Should contain method and endpoint
            assert "POST" in log_output
            assert "draw_cylinder" in log_output
            
            # Should contain formatted JSON
            assert '"test": "data"' in log_output
            assert '"nested"' in log_output
    
    def test_interceptor_with_large_responses(self):
        """Test that interceptor handles large responses correctly."""
        # Enable interceptor
        interceptor.set_interceptor_enabled(True)
        
        with patch('requests.post') as mock_post:
            # Create large response data
            large_data = {"data": ["item"] * 1000, "metadata": {"size": "large"}}
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = large_data
            mock_post.return_value = mock_response
            
            # Call CAD function
            result = geometry.draw_box("10", "10", "10", 0.0, 0.0, 0.0)
            
            # Should return the large data
            assert result == large_data
            
            # Should log the response (may be truncated for very large responses)
            log_output = self.log_capture.getvalue()
            assert "INTERCEPTOR" in log_output
            assert "POST" in log_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])