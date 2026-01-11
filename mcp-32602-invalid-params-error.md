# MCP Error -32602: Invalid Request Parameters

## Summary

The -32602 error indicates "Invalid request parameters" in JSON-RPC protocol. This error occurs when the MCP server receives a request with malformed, missing, or invalid parameters that don't match the expected schema for the requested method.

## Root Cause Analysis

Common causes of -32602 errors:

- **Malformed JSON**: Request body contains invalid JSON syntax
- **Missing required parameters**: Required fields are absent from the request
- **Invalid parameter types**: Parameters have wrong data types (string vs number, etc.)
- **Schema mismatch**: Parameters don't conform to the expected JSON schema
- **Extra/unknown parameters**: Request contains fields not defined in the schema

## Fix

### Request/Response Examples

**Proper Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "list_cam_setups",
  "params": {}
}
```

**Invalid Request (missing required param):**
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "method": "create_setup",
  "params": {}
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Missing required parameter: name"
  }
}
```

### Remediation Steps

1. **Validate request schema** before processing
2. **Check required parameters** are present
3. **Verify parameter types** match expected schema
4. **Add parameter validation middleware** to catch issues early
5. **Use `validateRequestParams()` helper** for consistent validation

## Tests

Add these test cases:

- **Unit tests**: Invalid parameter combinations for each method
- **Integration tests**: End-to-end validation with malformed requests
- **Schema validation tests**: Verify all method schemas are correct
- **Error response tests**: Ensure proper -32602 error formatting

## References/Best Practices

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- Use `validateRequestParams(method, params)` helper function
- Implement schema validation at the MCP protocol layer
- Log parameter validation failures for debugging
- Update PR description and changelog when fixing parameter validation issues
