#!/usr/bin/env python3
"""
Test to verify draw_cylinder function parameter passing fix
"""
import sys
import os
sys.path.append('/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server')

# Mock the missing modules
sys.modules['requests'] = type(sys)('requests')
sys.modules['requests.RequestException'] = Exception

from unittest.mock import patch, MagicMock

def test_draw_cylinder_send_request_parameters():
    """Test that draw_cylinder calls send_request with correct parameters"""
    
    # Mock the dependencies before importing
    with patch.dict('sys.modules', {
        'core.request_handler': MagicMock(),
        'core.config': MagicMock(),
    }):
        # Mock the functions
        mock_send_request = MagicMock(return_value={"success": True})
        mock_get_endpoints = MagicMock(return_value={"draw_cylinder": "http://test/cylinder"})
        mock_get_headers = MagicMock(return_value={"Content-Type": "application/json"})
        
        with patch('tools.cad.geometry.send_request', mock_send_request), \
             patch('tools.cad.geometry.get_endpoints', mock_get_endpoints), \
             patch('tools.cad.geometry.get_headers', mock_get_headers):
            
            from tools.cad.geometry import draw_cylinder
            
            # Call the function
            result = draw_cylinder(radius=5.0, height=10.0, x=0.0, y=0.0, z=0.0, plane="XY")
            
            # Verify send_request was called
            mock_send_request.assert_called_once()
            args, kwargs = mock_send_request.call_args
            
            # Check the arguments - this should fail with current broken code
            print(f"send_request called with args: {args}")
            
            if len(args) == 3:
                if isinstance(args[2], str) and args[2] == "POST":
                    print("✅ Test passed: draw_cylinder calls send_request with correct parameters")
                    return True
                else:
                    print(f"❌ Test failed: Third argument should be 'POST', got {args[2]} (type: {type(args[2])})")
                    return False
            else:
                print(f"❌ Test failed: Expected 3 arguments, got {len(args)}")
                return False

if __name__ == "__main__":
    try:
        success = test_draw_cylinder_send_request_parameters()
        if success:
            print("All tests passed!")
        else:
            print("Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
