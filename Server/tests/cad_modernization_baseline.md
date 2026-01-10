# CAD Tools Modernization Baseline Documentation

## Overview

This document captures the current state of CAD tools before modernization to enable comparison and validation of changes.

## Current Function Inventory

### Geometry Module (Server/tools/cad/geometry.py)
- `draw_cylinder(radius, height, x, y, z, plane="XY")` - Creates cylindrical shapes
- `draw_box(height_value, width_value, depth_value, x_value, y_value, z_value, plane="XY")` - Creates box/rectangular shapes
- `draw_sphere(x, y, z, radius)` - Creates spherical shapes

**Total Functions: 3**

### Sketching Module (Server/tools/cad/sketching.py)
- `draw2Dcircle(radius, x, y, z, plane="XY")` - Creates 2D circles
- `draw_lines(points, plane)` - Creates line segments
- `draw_one_line(x1, y1, z1, x2, y2, z2, plane="XY")` - Creates single line
- `draw_arc(point1, point2, point3, plane)` - Creates arc segments
- `spline(points, plane)` - Creates spline curves

**Total Functions: 5**

### Modeling Module (Server/tools/cad/modeling.py)
- `extrude(value, angle)` - Extrudes sketches into 3D
- `extrude_thin(thickness, distance)` - Creates thin-walled extrusions
- `cut_extrude(depth)` - Cut extrude operations
- `revolve(angle)` - Revolves sketches around axis
- `loft(sketchcount)` - Lofts between multiple sketches
- `sweep()` - Sweeps profile along path
- `boolean_operation(operation)` - Boolean operations between bodies
- `draw_2d_rectangle(x_1, y_1, z_1, x_2, y_2, z_2, plane)` - Creates 2D rectangles
- `draw_text(text, plane, x_1, y_1, z_1, x_2, y_2, z_2, thickness, value)` - Creates text

**Total Functions: 9**

### Features Module (Server/tools/cad/features.py)
- `fillet_edges(radius)` - Creates edge fillets
- `draw_holes(points, depth, width, faceindex=0)` - Creates holes in bodies
- `shell_body(thickness, faceindex)` - Creates shell features
- `circular_pattern(plane, quantity, axis)` - Creates circular patterns
- `rectangular_pattern(plane, quantity_one, quantity_two, distance_one, distance_two, axis_one, axis_two)` - Creates rectangular patterns
- `create_thread(inside, allsizes)` - Creates threaded features
- `ellipsie(x_center, y_center, z_center, x_major, y_major, z_major, x_through, y_through, z_through, plane)` - Creates ellipses
- `draw_witzenmannlogo(scale=1.0, z=1.0)` - Creates Witzenmann logo

**Total Functions: 8**

**Grand Total: 25 functions across 4 files**

## Current Import Patterns

### Old Pattern (Currently Used)
```python
from core.request_handler import send_request
from core.config import get_endpoints, get_headers
```

### Modern Pattern (Target)
```python
import requests
from core.config import get_endpoints, get_timeout
from core import interceptor
```

## Current HTTP Request Patterns

### Old Pattern (Currently Used)
```python
def old_function(param1, param2):
    try:
        endpoint = get_endpoints("cad")["endpoint_name"]
        data = {"param1": param1, "param2": param2}
        headers = get_headers()
        return send_request(endpoint, data, headers)
    except requests.RequestException as e:
        logging.error("Function failed: %s", e)
        return None  # or raise
```

### Modern Pattern (Target)
```python
def modern_function(param1, param2):
    try:
        endpoint = get_endpoints("cad")["endpoint_name"]
        data = {"param1": param1, "param2": param2}
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Function failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to execute function: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }
```

## Current Error Handling Patterns

### Inconsistent Error Handling
- Some functions return `None` on error
- Some functions raise exceptions
- Some functions have minimal error handling
- Error messages are not standardized

### Target Error Handling
- Standardized error response format with `error`, `message`, and `code` fields
- Consistent exception handling for `ConnectionError`, `Timeout`, and generic `Exception`
- Proper error logging with context

## Current Response Formats

### Mixed Response Formats
- Some functions return raw HTTP responses
- Some functions return parsed JSON
- Some functions return `None` on error
- No consistent response interception

### Target Response Format
- All responses processed through `interceptor.intercept_response`
- Consistent error response structure
- Proper response logging for debugging

## Modernization Checklist

For each function, the following changes are required:

### Import Changes
- [ ] Remove `from core.request_handler import send_request`
- [ ] Remove `from core.config import get_headers` (if present)
- [ ] Add `import requests`
- [ ] Add `from core.config import get_timeout`
- [ ] Add `from core import interceptor`

### HTTP Request Changes
- [ ] Replace `send_request(endpoint, data, headers)` with `requests.post(endpoint, json=data, timeout=get_timeout())`
- [ ] Add `return interceptor.intercept_response(endpoint, response, "POST")`
- [ ] Remove `headers = get_headers()` calls

### Error Handling Changes
- [ ] Add standardized `ConnectionError` handling
- [ ] Add standardized `Timeout` handling
- [ ] Add standardized generic `Exception` handling
- [ ] Use consistent error response format
- [ ] Improve error logging with context

### Function Signature Preservation
- [ ] Maintain exact function signatures
- [ ] Preserve docstrings and German comments
- [ ] Maintain parameter types and defaults

## Testing Strategy

### Property-Based Tests
1. **Modern HTTP Request Pattern** - Verify all functions use direct `requests` calls
2. **Import Statement Modernization** - Verify all modules have correct imports
3. **Functional Compatibility Preservation** - Verify function signatures unchanged
4. **Standardized Error Handling** - Verify consistent error response format
5. **Response Interceptor Integration** - Verify all responses go through interceptor
6. **Complete File Coverage** - Verify all 25 functions modernized
7. **End-to-End Compatibility** - Verify MCP server loads and functions work

### Baseline Comparison
- Document current function signatures
- Document current import patterns
- Document current HTTP request patterns
- Compare before/after modernization

## Success Criteria

### Functional Requirements
- All 25 CAD tool functions modernized
- All function signatures preserved
- All docstrings and comments maintained
- MCP server loads without errors
- All tools callable through MCP

### Technical Requirements
- No `send_request` usage remaining
- No `get_headers` usage remaining
- All functions use `requests.get/post` directly
- All responses go through `interceptor.intercept_response`
- Consistent error handling across all functions

### Quality Requirements
- Property-based tests pass for all functions
- Baseline comparison shows no functional regressions
- Response interception works for debugging
- Error messages are user-friendly and consistent

This baseline documentation will be used to validate the modernization process and ensure no functionality is lost during the transformation.