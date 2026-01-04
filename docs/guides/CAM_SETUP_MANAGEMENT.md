# CAM Setup Management Guide

## Overview

The CAM Setup Management feature provides comprehensive tools for creating, configuring, and managing CAM setups in Fusion 360 through the MCP Server. This guide covers all available tools, their usage, and common workflows.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Available Tools](#available-tools)
3. [Common Workflows](#common-workflows)
4. [API Reference](#api-reference)
5. [Error Handling](#error-handling)
6. [Troubleshooting](#troubleshooting)

## Core Concepts

### What is a CAM Setup?

A CAM setup in Fusion 360 is a container that defines:
- **Work Coordinate System (WCS)**: The origin and orientation for machining operations
- **Stock Definition**: The raw material being machined (dimensions, position, material)
- **Operations/Toolpaths**: The machining operations contained within the setup

### Terminology

| Term | Description |
|------|-------------|
| WCS | Work Coordinate System - defines machining origin and orientation |
| Stock | Raw material definition including dimensions and position |
| Setup | Container for WCS, stock, and machining operations |
| Toolpath | Generated path for a machining operation |
| Operation | A single machining operation (pocket, contour, drill, etc.) |

## Available Tools

### Setup Management Tools

#### `create_cam_setup`
Creates a new CAM setup with specified configuration.

**Parameters:**
- `name` (optional): Setup name. Auto-generated if not provided
- `stock_mode` (optional): Stock configuration mode - "auto", "geometry", "box", "cylinder"
- `wcs_config` (optional): Work Coordinate System configuration
- `model_id` (optional): Model ID reference for geometry selection

**Example:**
```python
# Create setup with automatic stock detection
create_cam_setup(name="Roughing Setup", stock_mode="auto")

# Create setup with custom WCS
create_cam_setup(
    name="Finishing Setup",
    stock_mode="box",
    wcs_config={
        "origin": {"x": 10.0, "y": 5.0, "z": 0.0},
        "orientation": "model_based"
    }
)
```

#### `list_cam_setups`
Lists all CAM setups with comprehensive configuration details.

**Parameters:**
- `include_toolpaths` (optional): Whether to include toolpath information. Default: True

**Example Response:**
```json
{
    "setups": [
        {
            "id": "setup_001",
            "name": "Roughing Setup",
            "wcs": {
                "type": "model_origin",
                "origin": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "stock": {
                "mode": "auto",
                "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0}
            },
            "toolpath_count": 3
        }
    ],
    "total_count": 1
}
```

#### `get_setup_details`
Gets detailed information about a specific setup.

**Parameters:**
- `setup_id` (required): Unique identifier of the setup

**Example:**
```python
get_setup_details("setup_001")
```

#### `modify_setup_configuration`
Modifies an existing setup configuration.

**Parameters:**
- `setup_id` (required): Setup to modify
- `updates` (required): Dictionary of updates (name, wcs, stock)

**Example:**
```python
modify_setup_configuration("setup_001", {
    "name": "Updated Setup Name",
    "stock": {
        "dimensions": {"length": 120.0, "width": 60.0, "height": 30.0}
    }
})
```

**Note:** Modifying WCS or stock may affect existing operations. The system will provide warnings about potential impacts.

#### `delete_cam_setup`
Deletes a CAM setup with confirmation.

**Parameters:**
- `setup_id` (required): Setup to delete
- `confirm` (optional): Must be True to proceed with deletion. Default: False

**Example:**
```python
# Get impact analysis first
delete_cam_setup("setup_001", confirm=False)

# Then confirm deletion
delete_cam_setup("setup_001", confirm=True)
```

#### `duplicate_cam_setup`
Creates a duplicate of an existing setup.

**Parameters:**
- `setup_id` (required): Setup to duplicate
- `new_name` (optional): Name for the duplicate. Auto-generated if not provided

**Example:**
```python
# Duplicate with auto-generated name
duplicate_cam_setup("setup_001")

# Duplicate with custom name
duplicate_cam_setup("setup_001", new_name="Finishing Setup")
```


### Setup-Toolpath Integration Tools

#### `get_setup_toolpaths`
Gets all toolpaths within a specific setup.

**Parameters:**
- `setup_id` (required): Setup to query
- `include_details` (optional): Include full toolpath details. Default: True

**Example Response:**
```json
{
    "setup_id": "setup_001",
    "setup_name": "Roughing Setup",
    "toolpaths": [
        {
            "id": "op_001",
            "name": "Adaptive Clearing",
            "type": "adaptive",
            "is_valid": true,
            "setup_id": "setup_001",
            "setup_name": "Roughing Setup",
            "tool": {
                "id": "tool_001",
                "name": "6mm Flat Endmill",
                "type": "flat end mill"
            }
        }
    ],
    "total_count": 1
}
```

#### `find_toolpath_setup`
Finds which setup contains a specific toolpath.

**Parameters:**
- `toolpath_id` (required): Toolpath to find

**Example Response:**
```json
{
    "toolpath_id": "op_001",
    "toolpath_name": "Adaptive Clearing",
    "toolpath_type": "adaptive",
    "setup_id": "setup_001",
    "setup_name": "Roughing Setup",
    "folder": null
}
```

#### `validate_setup_toolpath_relationship`
Validates that a toolpath belongs to a specific setup.

**Parameters:**
- `setup_id` (required): Setup ID to validate against
- `toolpath_id` (required): Toolpath ID to check

**Example Response (Valid):**
```json
{
    "valid": true,
    "setup_id": "setup_001",
    "setup_name": "Roughing Setup",
    "toolpath_id": "op_001",
    "toolpath_name": "Adaptive Clearing"
}
```

**Example Response (Mismatch):**
```json
{
    "valid": false,
    "message": "Toolpath 'Contour Finishing' does not belong to setup 'Roughing Setup'",
    "code": "TOOLPATH_SETUP_MISMATCH",
    "actual_setup_id": "setup_002",
    "actual_setup_name": "Finishing Setup"
}
```

#### `get_setup_toolpath_mapping`
Gets comprehensive mapping of all setups to their toolpaths.

**Example Response:**
```json
{
    "setups": [
        {
            "id": "setup_001",
            "name": "Roughing Setup",
            "toolpath_ids": ["op_001", "op_002"],
            "toolpath_count": 2
        }
    ],
    "toolpath_to_setup": {
        "op_001": {"setup_id": "setup_001", "setup_name": "Roughing Setup"},
        "op_002": {"setup_id": "setup_001", "setup_name": "Roughing Setup"}
    },
    "total_setups": 1,
    "total_toolpaths": 2
}
```

## Common Workflows

### Creating a New Manufacturing Setup

1. **Create the setup:**
```python
result = create_cam_setup(name="My Machining Setup", stock_mode="auto")
setup_id = result["id"]
```

2. **Verify the setup was created:**
```python
details = get_setup_details(setup_id)
print(f"Setup created: {details['name']}")
print(f"Stock mode: {details['stock']['mode']}")
```

### Managing Multiple Setups

1. **List all setups:**
```python
setups = list_cam_setups()
for setup in setups["setups"]:
    print(f"{setup['name']}: {setup['toolpath_count']} toolpaths")
```

2. **Duplicate a setup for different operations:**
```python
duplicate_cam_setup("setup_001", new_name="Finishing Setup")
```

### Modifying Setup Configuration

1. **Check current configuration:**
```python
details = get_setup_details("setup_001")
```

2. **Modify with impact analysis:**
```python
result = modify_setup_configuration("setup_001", {
    "name": "Updated Roughing Setup",
    "stock": {"dimensions": {"length": 110.0, "width": 55.0, "height": 28.0}}
})

if result.get("warnings"):
    for warning in result["warnings"]:
        print(f"Warning: {warning}")
```


### Deleting a Setup Safely

1. **Get impact analysis first:**
```python
result = delete_cam_setup("setup_001", confirm=False)
if result.get("requires_confirmation"):
    print(f"Warning: {result['operation_count']} operations will be deleted")
```

2. **Confirm deletion if acceptable:**
```python
result = delete_cam_setup("setup_001", confirm=True)
if result.get("deleted"):
    print("Setup deleted successfully")
```

### Understanding Setup-Toolpath Relationships

1. **Get all toolpaths in a setup:**
```python
toolpaths = get_setup_toolpaths("setup_001")
for tp in toolpaths["toolpaths"]:
    print(f"  {tp['name']} ({tp['type']})")
```

2. **Find which setup contains a toolpath:**
```python
result = find_toolpath_setup("op_001")
print(f"Toolpath is in: {result['setup_name']}")
```

3. **Validate a relationship:**
```python
result = validate_setup_toolpath_relationship("setup_001", "op_001")
if result["valid"]:
    print("Toolpath belongs to this setup")
else:
    print(f"Mismatch: {result['message']}")
```

## API Reference

### HTTP Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cam/setups` | GET | List all setups |
| `/cam/setups` | POST | Create new setup |
| `/cam/setups/{id}` | GET | Get setup details |
| `/cam/setups/{id}` | PUT | Modify setup |
| `/cam/setups/{id}` | DELETE | Delete setup |
| `/cam/setups/{id}/duplicate` | POST | Duplicate setup |
| `/cam/setups/{id}/toolpaths` | GET | Get setup toolpaths |
| `/cam/toolpaths/{id}/setup` | GET | Find toolpath's setup |
| `/cam/setups/{id}/toolpaths/{id}/validate` | GET | Validate relationship |
| `/cam/setup-toolpath-mapping` | GET | Get complete mapping |

### Error Codes

| Code | Description |
|------|-------------|
| `SETUP_NOT_FOUND` | Requested setup does not exist |
| `DUPLICATE_NAME` | Setup name already exists |
| `MISSING_SETUP_ID` | Setup ID parameter is required |
| `INVALID_UPDATES` | Updates dictionary is invalid |
| `TOOLPATH_NOT_FOUND` | Requested toolpath does not exist |
| `TOOLPATH_SETUP_MISMATCH` | Toolpath doesn't belong to specified setup |
| `DELETION_NOT_SUPPORTED` | Setup deletion not supported via API |
| `MOVE_NOT_SUPPORTED` | Moving toolpaths between setups not supported |

## Error Handling

### Common Error Scenarios

**Setup Not Found:**
```json
{
    "error": true,
    "message": "Setup with ID 'setup_999' not found",
    "code": "SETUP_NOT_FOUND"
}
```

**Duplicate Name:**
```json
{
    "error": true,
    "message": "Setup with name 'Roughing Setup' already exists",
    "code": "DUPLICATE_NAME"
}
```

**Missing Required Parameter:**
```json
{
    "error": true,
    "message": "setup_id parameter is required",
    "code": "MISSING_SETUP_ID"
}
```

## Troubleshooting

### Setup Creation Fails

1. **Check CAM workspace is active:**
   - Ensure you're in the MANUFACTURE workspace in Fusion 360
   - Verify a design document is open

2. **Check for duplicate names:**
   - Use `list_cam_setups()` to see existing setup names
   - Choose a unique name for the new setup

### Toolpath Not Found

1. **Verify the toolpath ID:**
   - Use `get_setup_toolpaths()` to list all toolpaths
   - Ensure you're using the correct ID format

2. **Check setup context:**
   - Use `find_toolpath_setup()` to locate the toolpath
   - Verify the toolpath exists in the expected setup

### Modification Warnings

When modifying WCS or stock configuration:
- Review all warnings before proceeding
- Consider regenerating affected toolpaths
- Test toolpaths after modification

### API Limitations

Some operations have limited API support:
- **WCS Modification**: Full WCS changes may require manual adjustment
- **Stock Modification**: Complex stock changes may need manual configuration
- **Toolpath Movement**: Moving toolpaths between setups is not supported

For these operations, the system will provide informative messages with suggestions for manual workarounds.

## Best Practices

1. **Use descriptive setup names** that indicate the purpose (e.g., "Roughing - Top Face", "Finishing - Contours")

2. **Check for impacts** before modifying setups with existing operations

3. **Use confirmation** for destructive operations like deletion

4. **Validate relationships** before performing operations that depend on setup-toolpath associations

5. **Keep setups organized** by operation type or machining phase

## Related Documentation

- [Toolpath Management](./TOOLPATH_MANAGEMENT.md)
- [Tool Library Management](./TOOL_LIBRARY_MANAGEMENT.md)
- [Error Handling Guide](./ERROR_HANDLING.md)
