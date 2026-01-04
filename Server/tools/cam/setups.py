"""
CAM Setup Management Tools

This module contains tools for CAM setup management:
- create_cam_setup: Create new CAM setups with configuration
- list_cam_setups: List all CAM setups with details
- get_setup_details: Get detailed setup information
- modify_setup_configuration: Modify existing setup configuration
- delete_cam_setup: Delete CAM setups with confirmation
- duplicate_cam_setup: Duplicate existing setups
"""

import logging
import requests
from mcp.server.fastmcp import FastMCP
from core.config import get_endpoints, get_timeout
from core.request_handler import send_request, send_get_request

# Get the MCP instance from the main server
# This will be injected by the module loader
mcp = None

def register_tools(mcp_instance: FastMCP):
    """Register setup management tools with the MCP server."""
    global mcp
    mcp = mcp_instance
    
    # Register all tools in this module
    mcp.tool()(create_cam_setup)
    mcp.tool()(list_cam_setups)
    mcp.tool()(get_setup_details)
    mcp.tool()(modify_setup_configuration)
    mcp.tool()(delete_cam_setup)
    mcp.tool()(duplicate_cam_setup)
    
    # Setup-Toolpath Integration Tools (Task 10.6)
    mcp.tool()(get_setup_toolpaths)
    mcp.tool()(find_toolpath_setup)
    mcp.tool()(validate_setup_toolpath_relationship)
    mcp.tool()(get_setup_toolpath_mapping)
    
    # Part Position Tools (Task 14.4)
    mcp.tool()(get_part_position)
    mcp.tool()(set_part_position)

def create_cam_setup(name: str = None, stock_mode: str = "auto", wcs_config: dict = None, model_id: str = None) -> dict:
    """
    Create a new CAM setup with specified configuration.
    
    This tool creates a new CAM setup in Fusion 360 with the specified name, stock configuration,
    and work coordinate system (WCS) settings. The setup serves as a container for machining
    operations and defines the coordinate system and stock material for manufacturing.
    
    Args:
        name: Optional setup name. If not provided, a descriptive name will be generated
              based on the selected geometry or a default pattern
        stock_mode: Stock configuration mode. Options:
                   - "auto": Automatically detect stock from selected bodies (default)
                   - "geometry": Use existing geometry as stock reference
                   - "box": Create primitive box stock with specified dimensions
                   - "cylinder": Create primitive cylinder stock with specified dimensions
        wcs_config: Optional Work Coordinate System configuration. If not provided,
                   defaults to model origin with standard orientation. Structure:
                   {
                       "origin": {"x": 0.0, "y": 0.0, "z": 0.0},  # Origin point
                       "orientation": "model_based",  # or "face_based", "custom"
                       "reference_geometry": "geometry_id"  # For face-based orientation
                   }
        model_id: Optional model ID reference for geometry selection. If not provided,
                 the system will use the active design model
    
    Returns:
        dict: Setup creation result with setup details or error information
              Success response includes:
              - setup_id: Unique identifier for the created setup
              - name: Final setup name (generated or specified)
              - wcs: Work coordinate system configuration
              - stock: Stock configuration details
              - created_date: Setup creation timestamp
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_CREATION_FAILED, INVALID_CONFIG, etc.)
    
    Example usage:
        # Create setup with automatic stock detection
        create_cam_setup(name="Roughing Setup", stock_mode="auto")
        
        # Create setup with custom WCS and box stock
        create_cam_setup(
            name="Finishing Setup",
            stock_mode="box",
            wcs_config={
                "origin": {"x": 10.0, "y": 5.0, "z": 0.0},
                "orientation": "model_based"
            }
        )
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5 (Setup creation with basic configuration)
    """
    try:
        endpoint = get_endpoints("cam")["cam_setups"]
        payload = {
            "name": name,
            "stock_mode": stock_mode,
            "wcs_config": wcs_config,
            "model_id": model_id
        }
        return send_request(endpoint, payload)
    except Exception as e:
        logging.error("Create CAM setup failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to create CAM setup: {str(e)}",
            "code": "SETUP_CREATION_FAILED"
        }

def list_cam_setups(include_toolpaths: bool = True) -> dict:
    """
    List all CAM setups with comprehensive configuration details.
    
    This tool returns all CAM setups in the current Fusion 360 document with detailed
    information including WCS configuration, stock definition, toolpath count, and
    setup metadata. Uses proper Fusion 360 WCS terminology throughout.
    
    Args:
        include_toolpaths: Whether to include toolpath information for each setup.
                          Default is True. When False, only setup configuration is returned.
    
    Returns:
        dict: List of all setups with detailed information
              Success response includes:
              - setups: Array of setup objects with:
                - id: Unique setup identifier
                - name: Setup name
                - wcs: Work coordinate system configuration
                - stock: Stock definition and positioning
                - toolpaths: Array of contained toolpaths (if include_toolpaths=True)
                - created_date: Setup creation timestamp
                - modified_date: Last modification timestamp
              - total_count: Total number of setups
              - message: Status message or null
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (CAM_NOT_AVAILABLE, CONNECTION_ERROR, etc.)
    
    Example response:
        {
            "setups": [
                {
                    "id": "setup_001",
                    "name": "Roughing Setup",
                    "wcs": {
                        "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "orientation": "model_based"
                    },
                    "stock": {
                        "mode": "auto",
                        "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0}
                    },
                    "toolpaths": [
                        {
                            "id": "op_001",
                            "name": "Adaptive Clearing",
                            "type": "adaptive",
                            "tool_name": "6mm Flat Endmill",
                            "is_valid": true
                        }
                    ],
                    "created_date": "2025-01-03T10:30:00Z"
                }
            ],
            "total_count": 1,
            "message": null
        }
    
    Typical use cases:
    - Getting overview of all manufacturing setups
    - Finding setup IDs for detailed inspection
    - Understanding setup organization and toolpath distribution
    
    Requirements: 4.1, 4.2 (Setup listing with basic and detailed properties)
    """
    try:
        endpoint = get_endpoints("cam")["cam_setups"]
        params = {"include_toolpaths": include_toolpaths}
        return send_get_request(endpoint, params)
    except Exception as e:
        logging.error("List CAM setups failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to list CAM setups: {str(e)}",
            "code": "SETUP_LIST_FAILED"
        }

def get_setup_details(setup_id: str) -> dict:
    """
    Get detailed information about a specific CAM setup.
    
    This tool retrieves comprehensive configuration details for a specific setup,
    including WCS configuration, stock definition, contained toolpaths, and metadata.
    Use this after list_cam_setups() to inspect the full configuration of a specific setup.
    
    Args:
        setup_id: Unique identifier of the setup to retrieve. Must match exactly
                 what was returned by list_cam_setups()
    
    Returns:
        dict: Detailed setup information or error
              Success response includes:
              - id: Setup identifier
              - name: Setup name
              - model_id: Model reference (root level)
              - wcs: Complete Work Coordinate System configuration
              - stock: Complete stock definition and positioning
              - toolpaths: Array of all contained toolpaths with details
              - created_date: Setup creation timestamp
              - modified_date: Last modification timestamp
              - operation_count: Number of machining operations
              - is_valid: Whether setup configuration is valid
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, CAM_NOT_AVAILABLE, etc.)
    
    Example usage:
        get_setup_details("setup_001")
    
    Example response:
        {
            "id": "setup_001",
            "name": "Roughing Setup",
            "model_id": "model_123",
            "wcs": {
                "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
                "orientation": "model_based",
                "x_axis": {"x": 1.0, "y": 0.0, "z": 0.0},
                "y_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
                "z_axis": {"x": 0.0, "y": 0.0, "z": 1.0}
            },
            "stock": {
                "mode": "auto",
                "geometry_id": "body_456",
                "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0},
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "material": "Aluminum 6061"
            },
            "toolpaths": [...],
            "created_date": "2025-01-03T10:30:00Z",
            "modified_date": "2025-01-03T11:15:00Z",
            "operation_count": 3,
            "is_valid": true
        }
    
    Requirements: 4.3 (Query setup by ID with specific details or error)
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup']}/{setup_id}"
        return send_get_request(endpoint)
    except Exception as e:
        logging.error("Get setup details failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to get setup details: {str(e)}",
            "code": "SETUP_DETAILS_FAILED"
        }

def modify_setup_configuration(setup_id: str, updates: dict) -> dict:
    """
    Modify existing CAM setup configuration.
    
    This tool updates the configuration of an existing setup while preserving
    existing operations where possible. It validates changes and provides warnings
    when modifications might affect existing toolpaths.
    
    Args:
        setup_id: Unique identifier of the setup to modify
        updates: Dictionary containing the configuration updates. Supported fields:
                - name: New setup name
                - wcs: Work coordinate system updates
                - stock: Stock configuration updates
                - model_id: Model reference updates
                
                Example updates structure:
                {
                    "name": "Updated Setup Name",
                    "wcs": {
                        "origin": {"x": 10.0, "y": 5.0, "z": 0.0}
                    },
                    "stock": {
                        "mode": "box",
                        "dimensions": {"length": 120.0, "width": 60.0, "height": 30.0}
                    }
                }
    
    Returns:
        dict: Modification result with updated setup information or error
              Success response includes:
              - setup_id: Setup identifier
              - updated_fields: List of fields that were modified
              - warnings: Array of warnings about potential impacts on operations
              - setup: Updated setup configuration
              - modified_date: Timestamp of modification
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, INVALID_UPDATES, etc.)
    
    Example usage:
        modify_setup_configuration("setup_001", {
            "name": "Revised Roughing Setup",
            "stock": {
                "mode": "box",
                "dimensions": {"length": 110.0, "width": 55.0, "height": 28.0}
            }
        })
    
    Requirements: 5.1, 5.2, 5.3, 5.5 (Modify setup properties with validation and warnings)
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup']}/{setup_id}"
        payload = {"updates": updates}
        return send_request(endpoint, payload, method="PUT")
    except Exception as e:
        logging.error("Modify setup configuration failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to modify setup configuration: {str(e)}",
            "code": "SETUP_MODIFICATION_FAILED"
        }

def delete_cam_setup(setup_id: str, confirm: bool = False) -> dict:
    """
    Delete a CAM setup with confirmation and impact warnings.
    
    This tool removes a CAM setup and all associated operations. It provides warnings
    about data loss when the setup contains active toolpaths and requires explicit
    confirmation for deletion.
    
    Args:
        setup_id: Unique identifier of the setup to delete
        confirm: Explicit confirmation flag. Must be True to proceed with deletion.
                If False, returns impact analysis without deleting.
    
    Returns:
        dict: Deletion result or impact analysis
              When confirm=False (impact analysis):
              - setup_id: Setup identifier
              - setup_name: Setup name
              - toolpath_count: Number of toolpaths that will be deleted
              - operation_count: Number of operations that will be deleted
              - warnings: Array of warnings about data loss
              - requires_confirmation: True
              
              When confirm=True (actual deletion):
              - deleted: True
              - setup_id: Deleted setup identifier
              - setup_name: Name of deleted setup
              - deleted_operations: Count of deleted operations
              - deleted_toolpaths: Count of deleted toolpaths
              - deletion_date: Timestamp of deletion
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, DELETION_FAILED, etc.)
    
    Example usage:
        # First, get impact analysis
        delete_cam_setup("setup_001", confirm=False)
        
        # Then, confirm deletion
        delete_cam_setup("setup_001", confirm=True)
    
    Requirements: 6.1, 6.2, 6.3 (Delete setup with warnings and confirmation)
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup']}/{setup_id}"
        payload = {"confirm": confirm}
        return send_request(endpoint, payload, method="DELETE")
    except Exception as e:
        logging.error("Delete CAM setup failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to delete CAM setup: {str(e)}",
            "code": "SETUP_DELETION_FAILED"
        }

def duplicate_cam_setup(setup_id: str, new_name: str = None) -> dict:
    """
    Create a duplicate of an existing CAM setup.
    
    This tool creates a complete copy of an existing setup including WCS configuration,
    stock definition, and operation templates. The duplicate setup will have identical
    configuration but a unique name and identifier.
    
    Args:
        setup_id: Unique identifier of the setup to duplicate
        new_name: Optional name for the duplicated setup. If not provided,
                 a unique name will be generated based on the original setup name
                 (e.g., "Original Setup Copy", "Original Setup Copy 2", etc.)
    
    Returns:
        dict: Duplication result with new setup information or error
              Success response includes:
              - original_setup_id: ID of the source setup
              - new_setup_id: ID of the created duplicate
              - new_setup_name: Name of the duplicated setup
              - copied_elements: List of configuration elements that were copied
              - duplication_date: Timestamp of duplication
              - setup: Complete configuration of the new setup
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, DUPLICATION_FAILED, etc.)
    
    Example usage:
        # Duplicate with automatic name generation
        duplicate_cam_setup("setup_001")
        
        # Duplicate with custom name
        duplicate_cam_setup("setup_001", new_name="Finishing Setup")
    
    Example response:
        {
            "original_setup_id": "setup_001",
            "new_setup_id": "setup_002",
            "new_setup_name": "Roughing Setup Copy",
            "copied_elements": ["wcs", "stock", "operations"],
            "duplication_date": "2025-01-03T12:00:00Z",
            "setup": {
                "id": "setup_002",
                "name": "Roughing Setup Copy",
                "wcs": {...},
                "stock": {...}
            }
        }
    
    Requirements: 7.1, 7.2, 7.3, 7.4 (Duplicate setup with identical configuration and naming)
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup_duplicate']}/{setup_id}/duplicate"
        payload = {"new_name": new_name}
        return send_request(endpoint, payload)
    except Exception as e:
        logging.error("Duplicate CAM setup failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to duplicate CAM setup: {str(e)}",
            "code": "SETUP_DUPLICATION_FAILED"
        }


# =============================================================================
# Setup-Toolpath Integration Tools (Task 10.6)
# =============================================================================

def get_setup_toolpaths(setup_id: str, include_details: bool = True) -> dict:
    """
    Get all toolpaths within a specific CAM setup.
    
    This tool retrieves all toolpath operations contained within a setup,
    providing bidirectional setup-toolpath relationship queries. Each toolpath
    includes setup context information as required for proper CAM workflow management.
    
    Args:
        setup_id: Unique identifier of the setup to query
        include_details: Whether to include full toolpath details including tool
                        information. Default is True.
    
    Returns:
        dict: Toolpaths within the setup with setup context
              Success response includes:
              - setup_id: Setup identifier
              - setup_name: Setup name
              - toolpaths: Array of toolpath objects with:
                - id: Toolpath identifier
                - name: Toolpath name
                - type: Operation type (adaptive, pocket, contour, etc.)
                - is_valid: Validity status
                - setup_id: Parent setup ID (always included)
                - setup_name: Parent setup name
                - tool: Tool information (if include_details=True)
                - folder: Folder name if toolpath is in a folder
              - total_count: Number of toolpaths in the setup
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, etc.)
    
    Example usage:
        # Get all toolpaths with full details
        get_setup_toolpaths("setup_001")
        
        # Get toolpaths without tool details (faster)
        get_setup_toolpaths("setup_001", include_details=False)
    
    Example response:
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
            "total_count": 1,
            "message": "Found 1 toolpath(s) in setup 'Roughing Setup'"
        }
    
    Typical use cases:
    - Getting all operations within a specific setup
    - Understanding setup organization
    - Validating setup-toolpath relationships
    
    Requirements: 9.1, 9.2, 10.1, 10.2, 10.3, 11.1, 11.3
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup_toolpaths']}/{setup_id}/toolpaths"
        params = {"include_details": include_details}
        return send_get_request(endpoint, params)
    except Exception as e:
        logging.error("Get setup toolpaths failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to get setup toolpaths: {str(e)}",
            "code": "SETUP_TOOLPATHS_FAILED"
        }


def find_toolpath_setup(toolpath_id: str) -> dict:
    """
    Find which setup contains a specific toolpath.
    
    This tool provides bidirectional setup-toolpath relationship queries,
    resolving the parent setup from a toolpath ID. Use this when you have
    a toolpath ID and need to know which setup it belongs to.
    
    Args:
        toolpath_id: Unique identifier of the toolpath to find
    
    Returns:
        dict: Setup information for the toolpath
              Success response includes:
              - toolpath_id: The queried toolpath ID
              - toolpath_name: Name of the toolpath
              - toolpath_type: Operation type
              - setup_id: Parent setup ID
              - setup_name: Parent setup name
              - folder: Folder name if toolpath is in a folder (null otherwise)
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (TOOLPATH_NOT_FOUND, etc.)
    
    Example usage:
        find_toolpath_setup("op_001")
    
    Example response:
        {
            "toolpath_id": "op_001",
            "toolpath_name": "Adaptive Clearing",
            "toolpath_type": "adaptive",
            "setup_id": "setup_001",
            "setup_name": "Roughing Setup",
            "folder": null,
            "message": "Toolpath 'Adaptive Clearing' belongs to setup 'Roughing Setup'"
        }
    
    Typical use cases:
    - Finding the parent setup for a toolpath
    - Validating toolpath context before operations
    - Understanding CAM document structure
    
    Requirements: 9.1, 9.2, 9.3, 11.1, 11.2, 11.3
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_toolpath_setup']}/{toolpath_id}/setup"
        return send_get_request(endpoint)
    except Exception as e:
        logging.error("Find toolpath setup failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to find toolpath setup: {str(e)}",
            "code": "TOOLPATH_SETUP_FAILED"
        }


def validate_setup_toolpath_relationship(setup_id: str, toolpath_id: str) -> dict:
    """
    Validate that a toolpath belongs to a specific setup.
    
    This tool validates setup context and permissions for toolpath operations.
    Use this before performing operations that require a toolpath to be in
    a specific setup, or to verify the relationship between setups and toolpaths.
    
    Args:
        setup_id: Setup ID to validate against
        toolpath_id: Toolpath ID to check
    
    Returns:
        dict: Validation result
              Valid relationship response:
              - valid: True
              - setup_id: The setup ID
              - setup_name: Setup name
              - toolpath_id: The toolpath ID
              - toolpath_name: Toolpath name
              - toolpath_type: Operation type
              - folder: Folder name if applicable
              - message: Confirmation message
              
              Invalid relationship response:
              - valid: False
              - message: Description of the mismatch
              - code: TOOLPATH_SETUP_MISMATCH
              - setup_id: The queried setup ID
              - toolpath_id: The queried toolpath ID
              - actual_setup_id: The setup where toolpath actually exists
              - actual_setup_name: Name of the actual setup
              
              Error response includes:
              - valid: False
              - error: True
              - message: Human-readable error description
              - code: Error code
    
    Example usage:
        validate_setup_toolpath_relationship("setup_001", "op_001")
    
    Example response (valid):
        {
            "valid": true,
            "setup_id": "setup_001",
            "setup_name": "Roughing Setup",
            "toolpath_id": "op_001",
            "toolpath_name": "Adaptive Clearing",
            "toolpath_type": "adaptive",
            "folder": null,
            "message": "Toolpath 'Adaptive Clearing' is valid within setup 'Roughing Setup'"
        }
    
    Example response (mismatch):
        {
            "valid": false,
            "message": "Toolpath 'Contour Finishing' does not belong to setup 'Roughing Setup'. It belongs to setup 'Finishing Setup'",
            "code": "TOOLPATH_SETUP_MISMATCH",
            "setup_id": "setup_001",
            "toolpath_id": "op_002",
            "actual_setup_id": "setup_002",
            "actual_setup_name": "Finishing Setup"
        }
    
    Requirements: 9.3, 11.4, 11.5
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup_toolpath_validate']}/{setup_id}/toolpaths/{toolpath_id}/validate"
        return send_get_request(endpoint)
    except Exception as e:
        logging.error("Validate setup-toolpath relationship failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to validate setup-toolpath relationship: {str(e)}",
            "code": "VALIDATION_FAILED"
        }


def get_setup_toolpath_mapping() -> dict:
    """
    Get comprehensive mapping of all setups to their toolpaths.
    
    This tool provides a complete bidirectional view of the setup-toolpath
    relationships in the CAM document. Use this to understand the overall
    structure of the CAM document and for validation purposes.
    
    Returns:
        dict: Complete mapping with:
              - setups: Array of setups with their toolpath IDs
                - id: Setup identifier
                - name: Setup name
                - toolpath_ids: Array of toolpath IDs in this setup
                - toolpath_count: Number of toolpaths
              - toolpath_to_setup: Dictionary mapping toolpath IDs to setup info
                - [toolpath_id]: {setup_id, setup_name, toolpath_name, folder}
              - total_setups: Number of setups
              - total_toolpaths: Total number of toolpaths
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code
    
    Example usage:
        get_setup_toolpath_mapping()
    
    Example response:
        {
            "setups": [
                {
                    "id": "setup_001",
                    "name": "Roughing Setup",
                    "toolpath_ids": ["op_001", "op_002"],
                    "toolpath_count": 2
                },
                {
                    "id": "setup_002",
                    "name": "Finishing Setup",
                    "toolpath_ids": ["op_003"],
                    "toolpath_count": 1
                }
            ],
            "toolpath_to_setup": {
                "op_001": {"setup_id": "setup_001", "setup_name": "Roughing Setup", "toolpath_name": "Adaptive Clearing", "folder": null},
                "op_002": {"setup_id": "setup_001", "setup_name": "Roughing Setup", "toolpath_name": "Pocket", "folder": null},
                "op_003": {"setup_id": "setup_002", "setup_name": "Finishing Setup", "toolpath_name": "Contour", "folder": null}
            },
            "total_setups": 2,
            "total_toolpaths": 3,
            "message": "Mapped 3 toolpath(s) across 2 setup(s)"
        }
    
    Typical use cases:
    - Understanding CAM document structure
    - Validating setup-toolpath relationships
    - Building UI representations of CAM hierarchy
    
    Requirements: 11.1, 11.2, 11.3, 11.4
    """
    try:
        endpoint = get_endpoints("cam")["cam_setup_toolpath_mapping"]
        return send_get_request(endpoint)
    except Exception as e:
        logging.error("Get setup-toolpath mapping failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to get setup-toolpath mapping: {str(e)}",
            "code": "MAPPING_FAILED"
        }


# =============================================================================
# Part Position Tools (Task 14.4)
# =============================================================================

def get_part_position(setup_id: str) -> dict:
    """
    Get the part position configuration for a CAM setup.
    
    This tool retrieves the part position and orientation relative to the Work
    Coordinate System (WCS) for a specific setup. Part position defines how the
    part geometry is positioned within the setup's coordinate system.
    
    Args:
        setup_id: Unique identifier of the setup to query. Must match exactly
                 what was returned by list_cam_setups()
    
    Returns:
        dict: Part position information
              Success response includes:
              - setup_id: Setup identifier
              - setup_name: Setup name
              - origin: Position coordinates {x, y, z} in centimeters
              - orientation: Axis vectors {x_axis, y_axis, z_axis}
              - is_default: Whether using default position (True if not modified)
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, CAM_NOT_AVAILABLE, etc.)
    
    Example usage:
        get_part_position("setup_001")
    
    Example response:
        {
            "setup_id": "setup_001",
            "setup_name": "Roughing Setup",
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": [1.0, 0.0, 0.0],
                "y_axis": [0.0, 1.0, 0.0],
                "z_axis": [0.0, 0.0, 1.0]
            },
            "is_default": true,
            "message": "Part position retrieved for setup 'Roughing Setup'"
        }
    
    Typical use cases:
    - Inspecting current part position before modification
    - Verifying part alignment relative to WCS
    - Understanding setup configuration for toolpath planning
    
    Requirements: 12.1, 12.4
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup_part_position']}/{setup_id}/part-position"
        return send_get_request(endpoint)
    except Exception as e:
        logging.error("Get part position failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to get part position: {str(e)}",
            "code": "PART_POSITION_RETRIEVAL_FAILED"
        }


def set_part_position(setup_id: str, position: dict, orientation: dict = None) -> dict:
    """
    Set the part position and orientation relative to WCS for a CAM setup.
    
    This tool configures the part position within a setup's coordinate system.
    Part position changes affect all toolpaths in the setup and may require
    toolpath regeneration.
    
    Args:
        setup_id: Unique identifier of the setup to modify
        position: Position dictionary with x, y, z coordinates in centimeters.
                 Example: {"x": 10.0, "y": 5.0, "z": 0.0}
        orientation: Optional orientation dictionary with axis vectors.
                    If not provided, current orientation is preserved.
                    Example: {
                        "x_axis": [1.0, 0.0, 0.0],
                        "y_axis": [0.0, 1.0, 0.0]
                    }
                    Note: z_axis is calculated from cross product of x and y axes.
    
    Returns:
        dict: Result of the position update
              Success response includes:
              - setup_id: Setup identifier
              - setup_name: Setup name
              - origin: Updated position coordinates {x, y, z}
              - orientation: Updated axis vectors {x_axis, y_axis, z_axis}
              - position_updated: Whether position was actually modified
              - warnings: Array of warnings about impacts on operations
              - requires_regeneration: Whether toolpaths need regeneration
              - affected_operations: Number of operations affected
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code (SETUP_NOT_FOUND, PART_POSITION_INVALID, etc.)
              - validation_issues: Array of validation issues (if applicable)
    
    Example usage:
        # Set position only
        set_part_position("setup_001", {"x": 10.0, "y": 5.0, "z": 0.0})
        
        # Set position and orientation
        set_part_position(
            "setup_001",
            {"x": 10.0, "y": 5.0, "z": 0.0},
            {
                "x_axis": [1.0, 0.0, 0.0],
                "y_axis": [0.0, 1.0, 0.0]
            }
        )
    
    Example response:
        {
            "setup_id": "setup_001",
            "setup_name": "Roughing Setup",
            "origin": {"x": 10.0, "y": 5.0, "z": 0.0},
            "orientation": {
                "x_axis": [1.0, 0.0, 0.0],
                "y_axis": [0.0, 1.0, 0.0],
                "z_axis": [0.0, 0.0, 1.0]
            },
            "position_updated": true,
            "warnings": ["Part position change will affect 3 existing operation(s). All toolpaths will need regeneration."],
            "requires_regeneration": true,
            "affected_operations": 3,
            "message": "Part position updated for setup 'Roughing Setup'"
        }
    
    Important notes:
    - All position values are in centimeters (Fusion 360 internal units)
    - Position changes affect all toolpaths in the setup
    - Toolpaths may need regeneration after position changes
    - Orientation axes should be perpendicular (will be orthogonalized if not)
    
    Requirements: 12.1, 12.2, 12.3, 12.5
    """
    try:
        endpoint = f"{get_endpoints('cam')['cam_setup_part_position']}/{setup_id}/part-position"
        payload = {
            "setup_id": setup_id,
            "position": position,
            "orientation": orientation
        }
        return send_request(endpoint, payload, method="PUT")
    except Exception as e:
        logging.error("Set part position failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to set part position: {str(e)}",
            "code": "PART_POSITION_UPDATE_FAILED"
        }
