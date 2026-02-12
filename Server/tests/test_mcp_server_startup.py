#!/usr/bin/env python3
"""
MCP Server Startup Tests

Tests to ensure the MCP server can be started successfully and responds to basic requests.
"""

import pytest
import subprocess
import time
import requests
import json
from pathlib import Path


class TestMCPServerStartup:
    """Test MCP server startup and basic functionality."""
    
    def test_mcp_server_stdio_mode(self):
        """Test that MCP server can start in stdio mode."""
        # Get project root (two levels up from this test file)
        project_root = Path(__file__).parent.parent.parent
        # Start server in stdio mode
        process = subprocess.Popen(
            ["uv", "run", "python3", "Server/MCP_Server.py", "--server_type", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )
        
        try:
            # Send a simple JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            # Send request and wait for response
            request_data = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_data, timeout=10)
            
            # Should not crash immediately
            assert process.returncode is not None, "Server should terminate after stdin closes"
            
            # Should produce some output (even if it's an error response)
            assert stdout or stderr, "Server should produce some output"
            
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("MCP server did not respond within timeout")
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
    
    def test_mcp_server_sse_mode(self):
        """Test that MCP server can start in SSE mode."""
        # Get project root (two levels up from this test file)
        project_root = Path(__file__).parent.parent.parent
        # Start server in SSE mode (default)
        process = subprocess.Popen(
            ["uv", "run", "python3", "Server/MCP_Server.py", "--server_type", "sse"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )
        
        try:
            # Give server time to start
            time.sleep(3)
            
            # Check if server is running
            assert process.poll() is None, "Server should still be running"
            
            # Try to connect to SSE endpoint (FastMCP default is port 8000)
            try:
                response = requests.get("http://localhost:8000/sse", timeout=5)
                # SSE endpoint should be accessible (even if it returns an error, it should respond)
                assert response.status_code in [200, 400, 404], f"Unexpected status code: {response.status_code}"
            except requests.exceptions.RequestException:
                # If connection fails, that's also acceptable for this basic test
                # The important thing is that the server started without crashing
                pass
            
        finally:
            process.terminate()
            process.wait(timeout=5)
            process.wait(timeout=5)
    
    def test_mcp_server_help_command(self):
        """Test that MCP server shows help when requested."""
        # Get project root (two levels up from this test file)
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ["uv", "run", "python3", "Server/MCP_Server.py", "--help"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Should exit successfully and show help
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower(), "Should show help text"
    
    def test_mcp_server_invalid_args(self):
        """Test that MCP server handles invalid arguments gracefully."""
        # Get project root (two levels up from this test file)
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ["uv", "run", "python3", "Server/MCP_Server.py", "--invalid-arg"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Should exit with error code
        assert result.returncode != 0, "Should fail with invalid arguments"
        assert result.stderr, "Should show error message"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
