#!/usr/bin/env python3
"""
Pytest version of draw_cylinder fix test
"""
# import pytest  # Only needed when running with pytest command
import os

def test_draw_cylinder_send_request_fix():
    """Test that draw_cylinder function calls send_request with correct parameters"""
    
    # Read the source code
    geometry_file = '/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server/tools/cad/geometry.py'
    
    with open(geometry_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find draw_cylinder function and its send_request call
    in_draw_cylinder = False
    send_request_line = None
    
    for i, line in enumerate(lines):
        if 'def draw_cylinder' in line:
            in_draw_cylinder = True
            continue
            
        if in_draw_cylinder:
            if 'return send_request(' in line:
                send_request_line = line.strip()
                break
            # Stop when we reach the next function
            if line.strip().startswith('def ') and 'draw_cylinder' not in line:
                break
    
    # Assertions
    assert send_request_line is not None, "Could not find send_request call in draw_cylinder function"
    
    # The line should contain "POST" as third parameter, not "headers"
    assert '"POST")' in send_request_line, f"Expected 'POST' as third parameter, got: {send_request_line}"
    assert 'headers)' not in send_request_line, f"Still passing headers as third parameter: {send_request_line}"
    
    print(f"✅ draw_cylinder correctly calls: {send_request_line}")


def test_draw_sphere_still_broken():
    """Test that draw_sphere is still broken (to verify our test works)"""
    
    # Read the source code
    geometry_file = '/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server/tools/cad/geometry.py'
    
    with open(geometry_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find draw_sphere function and its send_request call
    in_draw_sphere = False
    send_request_line = None
    
    for i, line in enumerate(lines):
        if 'def draw_sphere' in line:
            in_draw_sphere = True
            continue
            
        if in_draw_sphere:
            if 'return send_request(' in line:
                send_request_line = line.strip()
                break
            # Stop when we reach the next function or end of function
            if (line.strip().startswith('def ') and 'draw_sphere' not in line) or \
               (line.strip() == '' and i > 0 and lines[i-1].strip() == ''):
                break
    
    # Assertions - draw_sphere should still be broken
    assert send_request_line is not None, "Could not find send_request call in draw_sphere function"
    assert 'headers)' in send_request_line, f"Expected draw_sphere to still be broken with headers parameter: {send_request_line}"
    
    print(f"✅ draw_sphere is still broken (as expected): {send_request_line}")


if __name__ == "__main__":
    # Run tests directly without pytest
    print("Running draw_cylinder fix test...")
    test_draw_cylinder_send_request_fix()
    
    print("\nRunning draw_sphere broken test...")
    test_draw_sphere_still_broken()
    
    print("\n✅ All tests passed!")
