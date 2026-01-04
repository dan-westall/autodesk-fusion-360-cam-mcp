# Part Position API Research Summary

**Date:** January 4, 2026  
**Task:** 14.1 Research Part Position API  
**Status:** Completed

## Overview

This document summarizes the API research conducted for Part Position functionality in Fusion 360 CAM setups. Part Position defines how the part geometry is positioned and oriented relative to the Work Coordinate System (WCS) within a setup.

## Research Findings

### 1. Part Position in Fusion 360 CAM

In Fusion 360's CAM (MANUFACTURE workspace), the part position is controlled through the setup's model positioning properties. The part position defines:

- **Origin Offset**: The position of the part geometry relative to the WCS origin
- **Orientation**: The rotational alignment of the part relative to the WCS axes

### 2. API Structure Analysis

Based on analysis of the `adsk.cam.Setup` class and related CAM API components:

#### Setup Model Properties

The setup object provides access to model positioning through several properties:

```python
# Setup model-related properties (from API research)
setup.models                    # Collection of models in the setup
setup.modelOrientation          # Model orientation relative to WCS
setup.modelOrigin               # Model origin point
```

#### Model Positioning Methods

The Fusion 360 CAM API provides model positioning through:

1. **Setup Parameters**: Model position can be configured through setup parameters
2. **Model Collection**: The `setup.models` collection contains the part geometry
3. **Orientation Properties**: Orientation is typically defined through axis vectors

### 3. Part Position Data Structure

Based on the design document and API patterns, the Part Position structure is:

```python
{
    "setup_id": "string",           # Parent setup identifier
    "origin": {
        "x": float,                 # X position relative to WCS (in cm)
        "y": float,                 # Y position relative to WCS (in cm)
        "z": float                  # Z position relative to WCS (in cm)
    },
    "orientation": {
        "x_axis": [float, float, float],  # X-axis direction vector
        "y_axis": [float, float, float],  # Y-axis direction vector
        "z_axis": [float, float, float]   # Z-axis direction vector (computed)
    },
    "is_default": bool              # Whether using default position
}
```

### 4. API Limitations

**Important Limitations Discovered:**

1. **Read-Only Properties**: Some model positioning properties may be read-only after setup creation
2. **Parameter-Based Configuration**: Part position changes may need to go through the setup's parameter system
3. **Regeneration Required**: Changes to part position typically require toolpath regeneration
4. **Limited Direct API**: Direct manipulation of part position may have limited API support

### 5. Implementation Approach

Based on the research, the recommended implementation approach is:

#### For Getting Part Position (`get_part_position_impl`)

1. Access the setup object via `find_setup_by_id()`
2. Extract model position from setup properties
3. Extract orientation from WCS or model orientation properties
4. Return structured position data

#### For Setting Part Position (`set_part_position_impl`)

1. Validate the setup exists
2. Validate position and orientation parameters
3. Attempt to modify setup parameters for position
4. Analyze impact on existing operations
5. Return result with warnings if operations affected

### 6. Relationship to WCS

Part Position is distinct from but related to WCS:

- **WCS**: Defines the coordinate system for machining operations
- **Part Position**: Defines where the part geometry sits within that coordinate system

The part position is always relative to the WCS origin and orientation.

### 7. Impact on Operations

When part position changes:

1. All toolpaths become invalid and need regeneration
2. Stock position may need adjustment
3. Operation parameters may need review
4. Collision detection results change

## API Properties Reference

### Setup Properties for Part Position

| Property | Type | Description |
|----------|------|-------------|
| `models` | Collection | Models included in the setup |
| `modelOrientation` | Matrix3D | Model orientation matrix |
| `modelOrigin` | Point3D | Model origin point |
| `parameters` | Parameters | Setup parameters including position |

### Validation Requirements

1. **Origin Validation**:
   - All coordinates must be valid numbers
   - Values should be in centimeters (Fusion 360 internal units)

2. **Orientation Validation**:
   - Axis vectors must be unit vectors (or normalizable)
   - X and Y axes must be perpendicular
   - Z axis is computed from X and Y cross product

## Implementation Notes

### Unit Conversion

Fusion 360 uses centimeters internally:
- 1 unit = 1 cm = 10 mm
- All position values must be in centimeters

### Error Handling

Part position operations should handle:
- `SETUP_NOT_FOUND`: Setup ID doesn't exist
- `PART_POSITION_INVALID`: Invalid position or orientation data
- `POSITION_UPDATE_FAILED`: API failed to update position
- `OPERATIONS_AFFECTED`: Warning when operations need regeneration

## Conclusion

The Part Position API research provides the foundation for implementing:
- `get_part_position_impl()`: Extract current part position from setup
- `set_part_position_impl()`: Update part position with validation
- `validate_part_position()`: Validate position parameters

The implementation should follow the established patterns in `setups.py` and `wcs.py`, using the same error handling and response formats.

## References

- [Fusion 360 CAM API Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- [CAM Setup Management Design Document](../../.kiro/specs/cam-setup-management/design.md)
- [WCS API Research](./CAM_SETUP_API_RESEARCH.md)
