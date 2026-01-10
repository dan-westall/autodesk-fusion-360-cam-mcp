#!/usr/bin/env python3
"""
Pytest test to verify draw_cylinder function parameter passing fix
"""
import pytest
from unittest.mock import patch, MagicMock


def test_draw_cylinder_send_request_parameters():
    """Test that draw_cylinder calls send_request with correct parameters"""
    
    # Mock the functions that draw_cylinder depends on
    mock_send_request = MagicMock(return_value={"success": True})
    mock_get_endpoints = MagicMock(return_value={"draw_cylinder": "http://test/cylinder"})
    mock_get_headers = MagicMock(return_value={"Content-Type": "application/json"})
    
    with patch('tools.cad.geometry.send_request', mock_send_request), \
         patch('tools.cad.geometry.get_endpoints', mock_get_endpoints), \
         patch('tools.cad.geometry.get_headers', mock_get_headers):
        
        # Import after patching to avoid import errors
        from tools.cad.geometry import draw_cylinder
        
        # Call the function
        result = draw_cylinder(radius=5.0, height=10.0, x=0.0, y=0.0, z=0.0, plane="XY")
        
        # Verify send_request was called exactly once
        mock_send_request.assert_called_once()
        
        # Get the arguments passed to send_request
        args, kwargs = mock_send_request.call_args
        
        # Verify the correct number of arguments
        assert len(args) == 3, f"Expected 3 arguments, got {len(args)}"
        
        # Verify first argument is the endpoint
        assert args[0] == "http://test/cylinder", f"Expected endpoint URL, got {args[0]}"
        
        # Verify second argument is a dictionary (the data)
        assert isinstance(args[1], dict), f"Expected dict for data, got {type(args[1])}"
        
        # Verify the data contains expected keys
        expected_keys = {"radius", "height", "x", "y", "z", "plane"}
        assert set(args[1].keys()) == expected_keys, f"Expected keys {expected_keys}, got {set(args[1].keys())}"
        
        # Verify third argument is "POST" (not headers dict)
        assert args[2] == "POST", f"Expected 'POST' as method, got {args[2]} (type: {type(args[2])})"
        
        print("✅ Test passed: draw_cylinder calls send_request with correct parameters")


if __name__ == "__main__":
    # Run the test directly
    test_draw_cylinder_send_request_parameters()
    print("All tests passed!")
