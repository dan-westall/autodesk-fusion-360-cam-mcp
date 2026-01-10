# MCP Server Development Guidelines

**Version:** 1.0  
**Last Updated:** January 6, 2026  
**Purpose:** Prevent common MCP server issues, especially with stdio transport

## Critical Rules

### 1. Never Use `print()` in MCP Server Code

**RULE**: All output must go through `logging` module, never `print()`.

**Why**: With stdio transport, stdout is the MCP JSON-RPC protocol channel. Any `print()` corrupts the protocol and causes `-32602` errors.

```python
# ❌ FORBIDDEN - corrupts stdio protocol
print("Debug info")
print(json.dumps(data))

# ✅ CORRECT - uses logging
import logging
logger = logging.getLogger(__name__)
logger.info("Debug info")
logger.info(json.dumps(data))
```

### 2. Logging Configuration for stdio

**RULE**: Configure logging to write to file and stderr, never stdout.

```python
import logging
import sys
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'mcp_server.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stderr)  # stderr is safe, stdout is not
    ]
)
```

### 3. Prefer stdio Transport Over HTTP/SSE

**RULE**: Use stdio transport for Kiro CLI agents.

**Why**: HTTP/SSE has session reconnection issues where clients may send requests before completing MCP initialization handshake.

```json
// ✅ CORRECT - stdio transport
{
  "mcpServers": {
    "FusionMCP": {
      "command": "uv",
      "args": ["--directory", "/path/to/project", "run", "python3", "Server/MCP_Server.py", "--server_type", "stdio"]
    }
  }
}

// ⚠️ AVOID - HTTP/SSE has reconnection issues
{
  "mcpServers": {
    "FusionMCP": {
      "url": "http://127.0.0.1:8000/sse",
      "type": "http"
    }
  }
}
```

### 4. Debug Interceptors Must Use Logging

**RULE**: Any debug/interceptor functionality must use the logging module.

```python
# ❌ FORBIDDEN
def log_response(data):
    print("═" * 65)
    print(json.dumps(data, indent=2))

# ✅ CORRECT
def log_response(data):
    logger.info(f"[INTERCEPTOR] Response:\n{json.dumps(data, indent=2)}")
```

### 5. Return Type Annotations

**RULE**: Always add return type annotations to MCP tools for clarity.

```python
# ✅ CORRECT - explicit return type
@mcp.tool()
def get_toolpath_details(toolpath_id: str) -> dict:
    """Get toolpath details."""
    return {"id": toolpath_id}

# ⚠️ AVOID - missing return type
@mcp.tool()
def get_toolpath_details(toolpath_id: str):
    return {"id": toolpath_id}
```

## Debugging MCP Issues

### Log File Location
```
Server/mcp_server.log
```

### Tail Logs While Testing
```bash
tail -f Server/mcp_server.log
```

### Common Error Codes

| Error | Meaning | Likely Cause |
|-------|---------|--------------|
| `-32602` | Invalid request parameters | stdout corruption or client sending malformed requests |
| `-32002` | Connection closed | Server crashed, check logs for Python errors |
| `before initialization` | Request before init complete | Client reconnection issue, use stdio transport |

## Testing Changes

After modifying MCP server code:

1. Test import: `cd Server && uv run python3 -c "from core.interceptor import *; print('OK')"`
2. Check for syntax errors in logs
3. Test with a simple tool call before complex operations

## References

- [FastMCP Documentation](https://gofastmcp.com/servers/tools)
- [Investigation: -32602 Error](./../.investigation/mcp-32602-invalid-params-error.md)
