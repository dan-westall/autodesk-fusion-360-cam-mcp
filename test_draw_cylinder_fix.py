#!/usr/bin/env python3
"""
Test to verify draw_cylinder function parameter passing fix
"""
import sys
import os
sys.path.append('/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server')

from unittest.mock import patch, MagicMock
from tools.cad.geometry import draw_cylinder

def test_draw_cylinder_send_request_parameters():
    """Test that draw_cylinder calls send_request with correct parameters"""
    
    # Mock the dependencies
    with patch('tools.cad.geometry.get_endpoints') as mock_endpoints, \
         patch('tools.cad.geometry.get_headers') as mock_headers, \
         patch('tools.cad.geometry.send_request') as mock_send_request:
        
        # Setup mocks
        mock_endpoints.return_value = {"draw_cylinder": "http://test/cylinder"}
        mock_headers.return_value = {"Content-Type": "application/json"}
        mock_send_request.return_value = {"success": True}
        
        # Call the function
        result = draw_cylinder(radius=5.0, height=10.0, x=0.0, y=0.0, z=0.0, plane="XY")
        
        # Verify send_request was called with correct parameters
        mock_send_request.assert_called_once()
        args, kwargs = mock_send_request.call_args
        
        # Check the arguments
        assert len(args) == 3, f"Expected 3 arguments, got {len(args)}"
        assert args[0] == "http://test/cylinder", f"Expected endpoint, got {args[0]}"
        assert isinstance(args[1], dict), f"Expected dict for data, got {type(args[1])}"
        assert args[2] == "POST", f"Expected 'POST' as method, got {args[2]}"
        
        print("✅ Test passed: draw_cylinder calls send_request with correct parameters")
        return True

if __name__ == "__main__":
    try:
        test_draw_cylinder_send_request_parameters()
        print("All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
