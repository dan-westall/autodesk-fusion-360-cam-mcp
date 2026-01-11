# MCP -32602 Invalid Request Parameters Error Investigation

**Date:** January 6, 2026  
**Status:** RESOLVED  
**Root Cause:** Interceptor printing to stdout corrupted stdio MCP protocol

## Problem Statement

Multiple MCP tools (~60%) were intermittently failing with:
```
Mcp error: -32602: Invalid request parameters("")
```

Affected tools included `get_toolpath_details`, `get_tool_info`, `get_toolpath_heights`, and others.

## Symptoms

- Error was **intermittent** - tools would work, then suddenly fail
- Error occurred mid-session after successful tool calls
- MCP server logs showed: `WARNING - Failed to validate request: Received request before initialization was complete`
- Session IDs were changing mid-conversation

## Investigation Timeline

### Hypothesis 1: Missing Return Type Annotations (REJECTED)

**Theory:** FastMCP requires `-> dict` return type annotations for proper schema generation.

**Finding:** Testing showed tools with and without return types generated identical MCP schemas. Both `output_schema: None`. This was not the cause.

### Hypothesis 2: Client Sending Empty String Arguments (PARTIALLY CORRECT)

**Theory:** MCP client sending `arguments: ""` instead of `arguments: {}`.

**Finding:** The error message format `Invalid request parameters("")` suggested this, and testing confirmed that `arguments: ""` fails Pydantic validation. However, this was a symptom, not the root cause.

### Hypothesis 3: Session Initialization Race Condition (PARTIALLY CORRECT)

**Theory:** Kiro CLI reconnecting and sending requests before MCP initialization completes.

**Finding:** Logs showed new session IDs appearing with immediate `Failed to validate request: Received request before initialization was complete` errors. This pointed to a protocol corruption issue.

### Hypothesis 4: Interceptor Corrupting stdio Protocol (ROOT CAUSE)

**Theory:** The response interceptor was using `print()` to stdout, which corrupts the stdio MCP transport.

**Finding:** CONFIRMED. The interceptor module was printing debug output to stdout:

```python
# BROKEN - corrupts stdio protocol
print("═" * 65)
print(f"[INTERCEPTOR] {method} {endpoint}")
print(formatted_json)
```

With stdio transport:
- **stdout** = MCP JSON-RPC protocol messages
- **stderr** = safe for logging/debug

When the interceptor was enabled and printed to stdout, it injected non-JSON-RPC data into the protocol stream, causing the MCP SDK to fail parsing subsequent messages.

## The Fix

### 1. Changed MCP Transport Protocol (HTTP/SSE → stdio)

Switched from HTTP/SSE transport to stdio transport:

**Before (HTTP/SSE):**
```json
{
  "mcpServers": {
    "FusionMCP": {
      "url": "http://127.0.0.1:8000/sse",
      "type": "http"
    }
  }
}
```

**After (stdio):**
```json
{
  "mcpServers": {
    "FusionMCP": {
      "command": "uv",
      "args": ["--directory", "...", "run", "python3", "Server/MCP_Server.py", "--server_type", "stdio"]
    }
  }
}
```

**Why:** HTTP/SSE had session reconnection issues where Kiro would create new sessions mid-conversation without completing MCP initialization handshake. stdio is more reliable as each agent invocation gets a dedicated server process.

### 2. Fixed Interceptor stdout Corruption

Changed interceptor to use Python's `logging` module instead of `print()`:

```python
# FIXED - uses logging which goes to file/stderr
logger = logging.getLogger(__name__)

def log_response(endpoint: str, response_data: Any, method: str = "POST") -> None:
    formatted_json = json.dumps(response_data, indent=4)
    logger.info(f"[INTERCEPTOR] {method} {endpoint}\n{formatted_json}")
```

Also updated `MCP_Server.py` to log to both file and stderr:

```python
LOG_FILE = os.path.join(os.path.dirname(__file__), 'mcp_server.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stderr)
    ]
)
```

## Additional Changes

1. **Agent config updated** to use stdio transport instead of HTTP/SSE:
   ```json
   {
     "mcpServers": {
       "FusionMCP": {
         "command": "uv",
         "args": ["--directory", "...", "run", "python3", "Server/MCP_Server.py", "--server_type", "stdio"]
       }
     }
   }
   ```
   
   Previously used HTTP/SSE which had session reconnection issues:
   ```json
   {
     "mcpServers": {
       "FusionMCP": {
         "url": "http://127.0.0.1:8000/sse",
         "type": "http"
       }
     }
   }
   ```

2. **Interceptor now logs enable/disable state:**
   ```python
   def toggle_interceptor() -> bool:
       logger.info(f"Interceptor {'ENABLED' if _interceptor_enabled else 'DISABLED'}")
   ```

## Files Modified

- `Server/core/interceptor.py` - Changed from `print()` to `logger.info()`
- `Server/MCP_Server.py` - Added file logging for stdio debugging
- `.kiro/agents/fusion-360.json` - Switched to stdio transport

## Lessons Learned

1. **Never use `print()` in MCP servers using stdio transport** - it corrupts the protocol
2. **Always use `logging` module** - it can be configured to write to files or stderr
3. **HTTP/SSE transport has reconnection issues** - stdio is more reliable for agent use
4. **Intermittent errors often indicate protocol-level issues** - not application logic

## Verification

After the fix:
- Tools work consistently without `-32602` errors
- Interceptor output appears in `Server/mcp_server.log`
- No protocol corruption with stdio transport

## Related Documentation

- [FastMCP Tools Documentation](https://gofastmcp.com/servers/tools)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- Project steering: `.kiro/steering/quick-reference.md`
