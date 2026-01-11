# CAD Removal Design Document

## Overview

The CAD Removal feature systematically removes all Computer-Aided Design (CAD) functionality from the Fusion 360 MCP Server while preserving all manufacturing (CAM) capabilities. This refactoring streamlines the system to focus exclusively on manufacturing workflows, reducing complexity and maintenance overhead.

The design follows a methodical approach to identify, document, and remove CAD components across both the MCP Server and Fusion Add-In layers while ensuring manufacturing functionality remains completely intact. The removal process is designed to be reversible with comprehensive documentation of all removed components.

## Architecture

### Current System Architecture

The Fusion 360 MCP Server currently follows a two-tier architecture with both CAD and CAM functionality:

1. **MCP Server Layer** (`Server/`)
   - `tools/cad/` - CAD tools (geometry, sketching, modeling, features)
   - `tools/cam/` - CAM tools (toolpaths, setups, tools, parameters)
   - `tools/utility/` - Utility tools (system, export, parameters)
   - `tools/debug/` - Debug tools (controls)

2. **Fusion Add-In Layer** (`FusionMCPBridge/`)
   - `handlers/design/` - Design workspace handlers
   - `handlers/manufacture/` - Manufacturing workspace handlers
   - `handlers/system/` - System handlers

### Target Architecture After Removal

After CAD removal, the system will have a streamlined architecture focused on manufacturing:

1. **MCP Server Layer** (`Server/`)
   - `tools/cam/` - CAM tools (preserved)
   - `tools/utility/` - Utility tools (preserved)
   - `tools/debug/` - Debug tools (preserved)
   - ~~`tools/cad/`~~ - **REMOVED**

2. **Fusion Add-In Layer** (`FusionMCPBridge/`)
   - `handlers/manufacture/` - Manufacturing workspace handlers (preserved)
   - `handlers/system/` - System handlers (preserved)
   - ~~`handlers/design/`~~ - **REMOVED**

### Removal Strategy

The removal follows a systematic approach:

1. **Documentation Phase** - Document all components to be removed
2. **Backup Phase** - Create version control tags for reversibility
3. **Server Removal Phase** - Remove CAD tools from MCP server
4. **Add-In Removal Phase** - Remove design handlers from Fusion Add-In
5. **Configuration Cleanup Phase** - Update configurations and imports
6. **Test Cleanup Phase** - Remove design-related tests
7. **Validation Phase** - Verify manufacturing functionality remains intact

## Components and Interfaces

### CAD Components to Remove

#### MCP Server CAD Tools (`Server/tools/cad/`)

```python
# Files to be removed:
Server/tools/cad/
├── __init__.py
├── geometry.py      # Basic 3D shapes (cylinder, box, sphere)
├── sketching.py     # 2D drawing tools (lines, circles, arcs, splines)
├── modeling.py      # 3D operations (extrude, revolve, loft, sweep)
└── features.py      # Features (fillet, holes, patterns, threading)
```

**Tools to be removed:**
- Geometry tools: `draw_box`, `draw_cylinder`, `draw_sphere`
- Sketching tools: `draw_circle`, `draw_line`, `draw_arc`, `draw_spline`, `draw_ellipse`, `draw_text`
- Modeling tools: `extrude`, `revolve`, `loft`, `sweep`, `boolean_union`, `boolean_subtract`, `boolean_intersect`
- Feature tools: `fillet`, `shell`, `hole`, `thread`, `circular_pattern`, `rectangular_pattern`

#### Fusion Add-In Design Handlers (`FusionMCPBridge/handlers/design/`)

```python
# Files to be removed:
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

**HTTP Endpoints to be removed:**
- Geometry endpoints: `/draw-box`, `/draw-cylinder`, `/draw-sphere`
- Sketching endpoints: `/draw-circle`, `/draw-line`, `/draw-arc`, `/draw-spline`, `/draw-ellipse`, `/draw-text`
- Modeling endpoints: `/extrude`, `/revolve`, `/loft`, `/sweep`, `/boolean-union`, `/boolean-subtract`, `/boolean-intersect`
- Feature endpoints: `/fillet`, `/shell`, `/hole`, `/thread`, `/circular-pattern`, `/rectangular-pattern`
- Export endpoints: `/export-step`, `/export-stl`

### CAM Components to Preserve

#### MCP Server CAM Tools (`Server/tools/cam/`)

```python
# Files to be preserved:
Server/tools/cam/
├── __init__.py
├── setups.py        # CAM setup management
├── toolpaths.py     # Toolpath operations
├── tools.py         # Tool management
├── parameters.py    # Parameter management
├── heights.py       # Height configuration
├── passes.py        # Pass configuration
└── linking.py       # Linking configuration
```

#### Fusion Add-In CAM Handlers (`FusionMCPBridge/handlers/manufacture/`)

```python
# Files to be preserved:
FusionMCPBridge/handlers/manufacture/
├── __init__.py
├── operations/      # Toolpath operations
├── setups/          # Setup management (modular structure)
├── tool_libraries/  # Tool library management
└── cam_utils.py     # CAM utilities
```

### Configuration Updates

#### Server Configuration (`Server/core/config.py`)

```python
# Remove design workspace endpoints from ENDPOINTS dictionary
ENDPOINTS = {
    # CAM endpoints (preserve)
    "cam/setups": "/cam/setups",
    "cam/toolpaths": "/cam/toolpaths",
    "cam/tools": "/cam/tools",
    # ... other CAM endpoints
    
    # Utility endpoints (preserve)
    "system/health": "/system/health",
    "system/parameters": "/system/parameters",
    # ... other utility endpoints
    
    # Design endpoints (REMOVE)
    # "draw-box": "/draw-box",
    # "draw-cylinder": "/draw-cylinder",
    # ... all design endpoints removed
}
```

#### Import Statement Updates

```python
# Server/tools/__init__.py - Remove CAD imports
"""
Tool modules for the Fusion 360 MCP Server.

This package contains all tool modules organized by category:
- cam: CAM-related tools (toolpaths, tools, parameters, heights, passes, linking, setups)
- utility: Utility tools (system, export, parameters)
- debug: Debug tools (controls)
"""
# Remove: - cad: CAD-related tools (geometry, sketching, modeling, features)

# FusionMCPBridge/handlers/__init__.py - Remove design imports
from .system import lifecycle
# Remove: from .design import geometry, sketching, modeling, features, utilities
from . import manufacture

__all__ = [
    'lifecycle',
    # Remove: 'geometry', 'sketching', 'modeling', 'features', 'utilities',
    'manufacture'
]
```

### Test Cleanup

#### Test Files to Remove

```python
# Server test files to remove:
Server/tests/
├── test_cad_server_loading.py      # CAD server loading tests
├── test_cad_integration.py         # CAD integration tests
├── test_cad_modernization.py       # CAD modernization tests
└── test_cad_*.py                   # Any other CAD-specific tests

# FusionMCPBridge test files to remove:
FusionMCPBridge/tests/
├── test_live_design.py             # Live design workspace tests
└── test_design_*.py                # Any other design-specific tests
```

#### Test Configuration Updates

```python
# FusionMCPBridge/tests/conftest.py - Remove design endpoints
ENDPOINTS = {
    # Remove all design workspace endpoints:
    # "draw_box": EndpointDefinition(...),
    # "draw_cylinder": EndpointDefinition(...),
    # ... all design endpoints removed
    
    # Preserve CAM endpoints:
    "cam_setups": EndpointDefinition(...),
    "cam_toolpaths": EndpointDefinition(...),
    # ... all CAM endpoints preserved
}
```

## Data Models

### Removal Documentation Model

```python
{
    "removal_summary": {
        "timestamp": "2026-01-10T12:00:00Z",
        "version_tag": "pre-cad-removal-v1.0",
        "removed_components": {
            "server_tools": [
                "Server/tools/cad/geometry.py",
                "Server/tools/cad/sketching.py",
                "Server/tools/cad/modeling.py",
                "Server/tools/cad/features.py",
                "Server/tools/cad/__init__.py"
            ],
            "fusion_handlers": [
                "FusionMCPBridge/handlers/design/geometry.py",
                "FusionMCPBridge/handlers/design/sketching.py",
                "FusionMCPBridge/handlers/design/modeling.py",
                "FusionMCPBridge/handlers/design/features.py",
                "FusionMCPBridge/handlers/design/utilities.py",
                "FusionMCPBridge/handlers/design/geometry_impl.py",
                "FusionMCPBridge/handlers/design/geometry_impl2.py",
                "FusionMCPBridge/handlers/design/__init__.py"
            ],
            "test_files": [
                "Server/tests/test_cad_server_loading.py",
                "Server/tests/test_cad_integration.py",
                "Server/tests/test_cad_modernization.py",
                "FusionMCPBridge/tests/test_live_design.py"
            ],
            "endpoints_removed": [
                "/draw-box", "/draw-cylinder", "/draw-sphere",
                "/draw-circle", "/draw-line", "/draw-arc", "/draw-spline",
                "/extrude", "/revolve", "/loft", "/sweep",
                "/fillet", "/shell", "/hole", "/thread",
                "/export-step", "/export-stl"
            ],
            "tools_removed": [
                "draw_box", "draw_cylinder", "draw_sphere",
                "draw_circle", "draw_line", "draw_arc", "draw_spline",
                "extrude", "revolve", "loft", "sweep",
                "fillet", "shell", "hole", "thread",
                "export_step", "export_stl"
            ]
        },
        "preserved_components": {
            "cam_tools": [
                "create_cam_setup", "list_cam_setups", "get_setup_details",
                "list_toolpaths", "get_toolpath_details", "list_tools"
            ],
            "cam_endpoints": [
                "/cam/setups", "/cam/toolpaths", "/cam/tools",
                "/cam/setups/{id}/toolpaths", "/tool-libraries"
            ],
            "utility_tools": [
                "get_system_health", "list_parameters", "export_data"
            ]
        }
    }
}
```

### Validation Model

```python
{
    "validation_results": {
        "cam_functionality_intact": boolean,
        "design_endpoints_removed": boolean,
        "design_tools_removed": boolean,
        "import_errors": [],
        "missing_dependencies": [],
        "test_results": {
            "cam_tests_passing": boolean,
            "design_tests_removed": boolean,
            "total_tests_after_removal": number
        },
        "performance_impact": {
            "startup_time_improvement": float,
            "memory_usage_reduction": float,
            "tool_count_reduction": number
        }
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Properties 1.1, 1.2, 1.3 can be combined into a comprehensive tool removal verification property
- Properties 2.1, 2.2, 2.4 can be combined into HTTP endpoint removal property
- Properties 3.1, 3.2, 3.3, 3.4 can be combined into configuration cleanup property
- Properties 4.1, 4.2, 4.4, 4.5 can be combined into test suite cleanup property
- Properties 5.1, 5.2, 5.3, 5.4, 5.5 can be combined into import and dependency cleanup property
- Properties 9.1, 9.2, 9.3, 9.4, 9.5 can be combined into CAM functionality preservation property

### Core Properties

**Property 1: CAD tool removal completeness**
*For any* MCP server instance after CAD removal, the server should only expose CAM tools, utility tools, and debug tools, with no design workspace tools available to AI assistants
**Validates: Requirements 1.1, 1.2, 1.3, 1.5**

**Property 2: HTTP endpoint removal completeness**
*For any* HTTP request to removed design endpoints, the Fusion Add-In should return 404 Not Found responses while continuing to process all CAM requests normally
**Validates: Requirements 2.1, 2.2, 2.4**

**Property 3: CAM functionality preservation**
*For any* CAM operation (setup creation, toolpath generation, tool management), the system should maintain identical functionality and behavior as before CAD removal
**Validates: Requirements 1.4, 2.3, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5**

**Property 4: Configuration cleanup completeness**
*For any* system configuration loading, the configuration should only contain endpoints for CAM operations, utilities, and system functions with no references to removed design endpoints
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

**Property 5: Test suite cleanup completeness**
*For any* test execution, the test suite should only include CAM functionality tests, utility tests, and system tests with no design workspace test cases
**Validates: Requirements 4.1, 4.2, 4.4, 4.5**

**Property 6: Import and dependency cleanup**
*For any* module loading or system startup, the system should not import any removed design modules and should only reference existing manufacturing modules without import errors
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

**Property 7: Directory structure cleanup**
*For any* file system examination, the system should not contain any design workspace directories and should only contain CAM-related handler directories
**Validates: Requirements 6.1, 6.2**

**Property 8: API documentation accuracy**
*For any* generated API documentation, the documentation should only include CAM tools and endpoints with no references to removed design capabilities
**Validates: Requirements 7.3**

**Property 9: Error message cleanup**
*For any* error condition, the system should not reference removed design functionality in error messages and should only mention available manufacturing capabilities in help text
**Validates: Requirements 10.1, 10.3, 10.4, 10.5**

**Property 10: System startup success**
*For any* system startup after CAD removal, the system should start successfully without attempting to load CAD tools or register design handlers
**Validates: Requirements 1.5, 2.4, 5.4**

## Error Handling

### Error Categories

1. **Removal Validation Errors**
   - CAD components not completely removed
   - CAM functionality accidentally affected
   - Import statements still referencing removed modules
   - Configuration still containing removed endpoints

2. **Functionality Preservation Errors**
   - CAM tools not working after removal
   - Manufacturing endpoints returning errors
   - Setup management functionality broken
   - Toolpath operations failing

3. **System Integration Errors**
   - Module loading failures due to broken imports
   - HTTP router registration failures
   - Configuration loading errors
   - Test suite execution failures

4. **Reversibility Errors**
   - Insufficient documentation for restoration
   - Missing version control tags
   - Incomplete component inventory
   - Lost configuration settings

### Error Response Format

All validation errors follow this format:

```python
{
    "error": True,
    "message": "Human-readable error description",
    "code": "ERROR_CODE_CONSTANT",
    "context": {
        "component_type": "string",     # "tool", "endpoint", "handler", "test"
        "component_name": "string",     # Name of affected component
        "removal_phase": "string",      # Phase where error occurred
        "impact_level": "string"        # "low", "medium", "high", "critical"
    }
}
```

### Error Codes

- `CAD_TOOL_NOT_REMOVED` - CAD tool still present after removal
- `CAM_FUNCTIONALITY_BROKEN` - CAM functionality affected by removal
- `IMPORT_ERROR_AFTER_REMOVAL` - Import statement references removed module
- `ENDPOINT_STILL_ACCESSIBLE` - Design endpoint still responding
- `CONFIGURATION_CONTAINS_REMOVED` - Configuration references removed components
- `TEST_REFERENCES_REMOVED` - Test still references removed functionality
- `DIRECTORY_NOT_CLEANED` - Design directory still exists
- `DOCUMENTATION_INCOMPLETE` - Removal documentation missing components
- `STARTUP_FAILURE_AFTER_REMOVAL` - System fails to start after removal

## Testing Strategy

### Unit Testing Approach

Unit tests will focus on:
- Verification that CAD tools are completely removed
- Validation that CAM functionality remains intact
- Testing configuration cleanup completeness
- Verifying import statement updates
- Testing error message updates

### Property-Based Testing Approach

The implementation will use **Hypothesis** for Python property-based testing. Each correctness property will be implemented as a property-based test with a minimum of 100 iterations.

Property-based tests will:
- Generate various system states and verify CAD removal completeness
- Test CAM functionality preservation across different scenarios
- Verify configuration cleanup across different configuration variations
- Test system startup success under various conditions
- Validate error handling for different failure scenarios

### Test Tagging

Each property-based test will be tagged with:
```python
# **Feature: cad-removal, Property 1: CAD tool removal completeness**
```

### Integration Testing

Integration tests will verify:
- End-to-end CAM workflows still function correctly
- HTTP endpoints respond appropriately (404 for design, 200 for CAM)
- MCP server tool registration excludes CAD tools
- System startup completes without errors
- Configuration loading works with cleaned configurations

### Validation Testing

Validation tests will ensure:
- All CAD components are documented before removal
- Version control tags are created for reversibility
- CAM functionality benchmarks match pre-removal performance
- No broken imports or dependencies remain
- Test suite runs successfully with only CAM tests

### Test Data Management

Tests will use:
- Snapshots of system state before and after removal
- CAM functionality test cases to verify preservation
- Configuration templates to test cleanup completeness
- Mock HTTP requests to verify endpoint removal
- System startup logs to verify successful initialization
