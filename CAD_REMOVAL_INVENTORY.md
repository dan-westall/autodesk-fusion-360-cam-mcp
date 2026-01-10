# CAD Removal Component Inventory

**Generated:** January 10, 2026  
**Purpose:** Complete inventory of all CAD components to be removed from the Fusion 360 MCP Server  
**Requirements:** 8.1, 8.2  

## Overview

This document provides a comprehensive inventory of all Computer-Aided Design (CAD) components that will be removed from the Fusion 360 MCP Server system. The removal will streamline the system to focus exclusively on manufacturing (CAM) capabilities while preserving all existing CAM functionality.

## MCP Server CAD Tools (`Server/tools/cad/`)

### Directory Structure
```
Server/tools/cad/
├── __init__.py
├── geometry.py      # Basic 3D shapes
├── sketching.py     # 2D drawing tools
├── modeling.py      # 3D operations
└── features.py      # Features and patterns
```

### CAD Tool Functions

#### Geometry Tools (`Server/tools/cad/geometry.py`)
- `draw_cylinder(radius, height, x, y, z, plane)` - Create cylindrical shapes
- `draw_box(height_value, width_value, depth_value, x_value, y_value, z_value, plane)` - Create box/rectangular shapes
- `draw_sphere(x, y, z, radius)` - Create spherical shapes

#### Sketching Tools (`Server/tools/cad/sketching.py`)
- `draw2Dcircle(radius, x, y, z, plane)` - Create 2D circles
- `draw_lines(points, plane)` - Create line segments from point list
- `draw_one_line(x1, y1, z1, x2, y2, z2, plane)` - Create single line
- `draw_arc(point1, point2, point3, plane)` - Create arc segments
- `spline(points, plane)` - Create spline curves

#### Modeling Tools (`Server/tools/cad/modeling.py`)
- `extrude()` - Extrude sketches into 3D bodies
- `revolve()` - Revolve sketches around axis
- `loft()` - Loft between multiple profiles
- `sweep()` - Sweep profile along path
- `boolean_operation()` - Boolean operations (union, subtract, intersect)

#### Feature Tools (`Server/tools/cad/features.py`)
- `fillet_edges()` - Add fillets to edges
- `shell_body()` - Shell solid bodies
- `holes()` - Create holes in bodies
- `threaded()` - Add threading to holes
- `circular_pattern()` - Create circular patterns
- `rectangular_pattern()` - Create rectangular patterns

## Fusion Add-In Design Handlers (`FusionMCPBridge/handlers/design/`)

### Directory Structure
```
FusionMCPBridge/handlers/design/
├── __init__.py
├── geometry.py          # Basic 3D shape creation handlers
├── geometry_impl.py     # Geometry implementation functions
├── geometry_impl2.py    # Additional geometry implementations
├── sketching.py         # 2D drawing handlers
├── modeling.py          # 3D operation handlers
├── features.py          # Feature creation handlers
└── utilities.py         # Design utility handlers
```

### HTTP Endpoints to Remove

#### Geometry Endpoints
- `/draw_cylinder` - Cylinder creation endpoint
- `/Box` - Box creation endpoint
- `/sphere` - Sphere creation endpoint

#### Sketching Endpoints
- `/create_circle` - 2D circle creation
- `/draw_lines` - Multi-line drawing
- `/draw_one_line` - Single line drawing
- `/arc` - Arc creation
- `/spline` - Spline curve creation
- `/ellipsis` - Ellipse creation
- `/draw_2d_rectangle` - Rectangle drawing
- `/draw_text` - Text creation

#### Modeling Endpoints
- `/extrude_last_sketch` - Extrude operation
- `/extrude_thin` - Thin extrude operation
- `/cut_extrude` - Cut extrude operation
- `/revolve` - Revolve operation
- `/loft` - Loft operation
- `/sweep` - Sweep operation
- `/boolean_operation` - Boolean operations

#### Feature Endpoints
- `/fillet_edges` - Fillet creation
- `/shell_body` - Shell operation
- `/holes` - Hole creation
- `/threaded` - Threading operation
- `/circular_pattern` - Circular pattern
- `/rectangular_pattern` - Rectangular pattern
- `/move_body` - Body movement

#### Export Endpoints (Design-related)
- `/Export_STEP` - STEP file export
- `/Export_STL` - STL file export

## Configuration Files

### Server Configuration (`Server/core/config.py`)
CAD endpoints in the "cad" category:
```python
"cad": {
    # Geometry tools
    "draw_cylinder": "http://localhost:5001/draw_cylinder",
    "draw_box": "http://localhost:5001/Box",
    "draw_sphere": "http://localhost:5001/sphere",
    
    # Sketching tools
    "draw2Dcircle": "http://localhost:5001/create_circle",
    "draw_lines": "http://localhost:5001/draw_lines",
    "draw_one_line": "http://localhost:5001/draw_one_line",
    "draw_arc": "http://localhost:5001/arc",
    "spline": "http://localhost:5001/spline",
    "ellipsie": "http://localhost:5001/ellipsis",
    "draw_2d_rectangle": "http://localhost:5001/draw_2d_rectangle",
    "draw_text": "http://localhost:5001/draw_text",
    
    # Modeling tools
    "extrude": "http://localhost:5001/extrude_last_sketch",
    "extrude_thin": "http://localhost:5001/extrude_thin",
    "cut_extrude": "http://localhost:5001/cut_extrude",
    "revolve": "http://localhost:5001/revolve",
    "loft": "http://localhost:5001/loft",
    "sweep": "http://localhost:5001/sweep",
    "boolean_operation": "http://localhost:5001/boolean_operation",
    
    # Feature tools
    "fillet_edges": "http://localhost:5001/fillet_edges",
    "shell_body": "http://localhost:5001/shell_body",
    "holes": "http://localhost:5001/holes",
    "threaded": "http://localhost:5001/threaded",
    "circular_pattern": "http://localhost:5001/circular_pattern",
    "rectangular_pattern": "http://localhost:5001/rectangular_pattern",
    "move_body": "http://localhost:5001/move_body",
}
```

### Legacy Configuration (`Server/config.py`)
- Imports from core configuration
- Exposes flattened ENDPOINTS dictionary including CAD endpoints

## Test Files to Remove

### Server Test Files
- `Server/tests/test_cad_server_loading.py` - CAD server loading tests
- `Server/tests/test_cad_integration.py` - CAD integration tests
- `Server/tests/test_cad_modernization.py` - CAD modernization tests
- `Server/tests/test_cad_response_interception.py` - CAD response interception tests
- `Server/tests/test_cad_end_to_end_compatibility.py` - CAD end-to-end compatibility tests

### FusionMCPBridge Test Files
- `FusionMCPBridge/tests/test_live_design.py` - Live design workspace tests

### Test Configuration Updates Required
- `FusionMCPBridge/tests/conftest.py` - Remove design workspace endpoints and fixtures
- Remove design-related test markers and fixtures

## Import Dependencies to Update

### Server Imports
- `Server/tools/__init__.py` - Remove CAD tool imports
- Any modules importing from `tools.cad.*`

### FusionMCPBridge Imports
- `FusionMCPBridge/handlers/__init__.py` - Remove design handler imports
- Any modules importing from `handlers.design.*`

## Preserved Components (CAM/Manufacturing)

### CAM Tools (Preserved)
- `Server/tools/cam/` - All CAM tools preserved
- `FusionMCPBridge/handlers/manufacture/` - All manufacturing handlers preserved

### Utility Tools (Preserved)
- `Server/tools/utility/` - System and export tools preserved
- `Server/tools/debug/` - Debug tools preserved

### System Components (Preserved)
- `FusionMCPBridge/handlers/system/` - System handlers preserved
- `FusionMCPBridge/handlers/research/` - Research handlers preserved

## Removal Impact Analysis

### Files to Delete (25 files)
- 4 CAD tool modules (`Server/tools/cad/*.py`)
- 7 design handler modules (`FusionMCPBridge/handlers/design/*.py`)
- 5 CAD-specific test files (`Server/tests/test_cad_*.py`)
- 1 design test file (`FusionMCPBridge/tests/test_live_design.py`)
- 2 directories (`Server/tools/cad/`, `FusionMCPBridge/handlers/design/`)
- Associated `__pycache__` directories

### Configuration Changes
- Remove entire "cad" category from `Server/core/config.py`
- Update import statements in multiple files
- Remove design-related test fixtures

### Endpoints Removed (25+ endpoints)
- All geometry, sketching, modeling, and feature endpoints
- Design-related export endpoints
- Design workspace utility endpoints

### Functions Removed (25+ functions)
- All CAD tool functions from MCP server
- All design handler functions from Fusion Add-In
- All design-related test functions

## Validation Checklist

### Pre-Removal Validation
- [ ] All CAD components documented
- [ ] All design handlers identified
- [ ] All test files catalogued
- [ ] All configuration references noted
- [ ] All import dependencies mapped

### Post-Removal Validation
- [ ] No CAD tools accessible via MCP server
- [ ] No design endpoints responding (404 expected)
- [ ] All CAM functionality preserved
- [ ] System starts without import errors
- [ ] Test suite runs with only CAM tests

## Restoration Information

### Version Control
- Tag: `pre-cad-removal-backup`
- Branch: Current working branch before removal
- Commit: Full commit hash of last working state

### Restoration Process
1. Checkout the `pre-cad-removal-backup` tag
2. Create new branch from backup tag
3. Merge or cherry-pick desired changes
4. Restore removed files from backup

### Critical Files for Restoration
- All files listed in "Files to Delete" section
- Configuration changes in `Server/core/config.py`
- Import statement changes in `__init__.py` files
- Test configuration changes in `conftest.py`

## Summary

**Total Components to Remove:**
- 4 CAD tool modules (25+ functions)
- 7 design handler modules
- 6 test files
- 25+ HTTP endpoints
- 1 configuration category
- Multiple import statements

**Total Components Preserved:**
- All CAM tools and handlers
- All utility and system tools
- All manufacturing-related tests
- All non-design functionality

This inventory ensures complete and reversible removal of all CAD functionality while preserving the manufacturing-focused capabilities of the system.