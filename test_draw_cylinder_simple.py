#!/usr/bin/env python3
"""
Simple test to verify draw_cylinder fix
"""
import sys
import os

# Add the Server directory to Python path
sys.path.insert(0, '/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server')

def test_draw_cylinder_fix():
    """Test that draw_cylinder function has the correct send_request call"""
    
    # Read the source code
    with open('/Users/bsport/projects/fustion360-mcp/Autodesk-Fusion-360-MCP-Server/Server/tools/cad/geometry.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find draw_cylinder function
    in_draw_cylinder = False
    for i, line in enumerate(lines):
        if 'def draw_cylinder' in line:
            in_draw_cylinder = True
            print(f"Found draw_cylinder function at line {i+1}")
            continue
            
        if in_draw_cylinder:
            # Look for the send_request call
            if 'return send_request(' in line:
                print(f"Line {i+1}: {line.strip()}")
                
                if 'headers)' in line:
                    print("❌ BROKEN: Still passing headers as third parameter")
                    return False
                elif '"POST")' in line:
                    print("✅ FIXED: Now passing 'POST' as third parameter")
                    return True
                else:
                    print("❓ UNKNOWN: Unexpected send_request call format")
                    return False
            
            # Stop when we reach the next function
            if line.strip().startswith('def ') and 'draw_cylinder' not in line:
                break
    
    print("❌ ERROR: Could not find send_request call in draw_cylinder")
    return False

if __name__ == "__main__":
    print("Testing draw_cylinder fix...")
    success = test_draw_cylinder_fix()
    
    if success:
        print("\n✅ Test PASSED: draw_cylinder is fixed!")
        sys.exit(0)
    else:
        print("\n❌ Test FAILED: draw_cylinder is still broken!")
        sys.exit(1)
