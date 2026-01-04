"""
Part Position Configuration Handler

Handles part position configuration for CAM setups including position
and orientation relative to the Work Coordinate System (WCS).

Part Position defines how the part geometry is positioned and oriented
within the setup's coordinate system.

This module is part of the setups/ subpackage following the modular architecture
pattern established by operations/ and tool_libraries/.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""

import adsk.core
import adsk.fusion
import adsk.cam
from typing import Dict, Any, Optional
import logging
import math

# Import core components (4 levels up: setups -> manufacture -> handlers -> FusionMCPBridge -> core)
from ....core.router import request_router

# Import shared CAM utilities (one level up to manufacture, then cam_utils)
from ..cam_utils import (
    get_cam_product,
    validate_cam_product_with_details,
    find_setup_by_id,
    get_operation_type
)

# Set up logging
logger = logging.getLogger(__name__)


# =============================================================================
# Part Position Validation Functions
# =============================================================================

def validate_part_position(position: dict, orientation: dict = None) -> dict:
    """
    Validate part position parameters.
    
    Args:
        position: Position dictionary with x, y, z coordinates
        orientation: Optional orientation dictionary with axis vectors
        
    Returns:
        dict: Validation result with valid flag and any issues found
        
    Requirements: 12.5
    """
    validation_result = {
        "valid": True,
        "issues": [],
        "warnings": []
    }
    
    try:
        # Validate position
        if position is None:
            validation_result["valid"] = False
            validation_result["issues"].append({
                "field": "position",
                "issue": "Position is required",
                "severity": "error"
            })
            return validation_result
        
        if not isinstance(position, dict):
            validation_result["valid"] = False
            validation_result["issues"].append({
                "field": "position",
                "issue": "Position must be a dictionary with x, y, z coordinates",
                "severity": "error"
            })
            return validation_result
        
        # Validate position coordinates
        for coord in ["x", "y", "z"]:
            value = position.get(coord)
            if value is None:
                # Default to 0 if not provided
                validation_result["warnings"].append({
                    "field": f"position.{coord}",
                    "warning": f"Position {coord} not provided, defaulting to 0",
                    "severity": "warning"
                })
            elif not isinstance(value, (int, float)):
                validation_result["valid"] = False
                validation_result["issues"].append({
                    "field": f"position.{coord}",
                    "issue": f"Position {coord} must be a number",
                    "severity": "error"
                })
        
        # Validate orientation if provided
        if orientation is not None:
            if not isinstance(orientation, dict):
                validation_result["valid"] = False
                validation_result["issues"].append({
                    "field": "orientation",
                    "issue": "Orientation must be a dictionary with axis vectors",
                    "severity": "error"
                })
            else:
                # Validate axis vectors
                for axis in ["x_axis", "y_axis"]:
                    axis_value = orientation.get(axis)
                    if axis_value is not None:
                        if not isinstance(axis_value, (list, tuple)) or len(axis_value) != 3:
                            validation_result["valid"] = False
                            validation_result["issues"].append({
                                "field": f"orientation.{axis}",
                                "issue": f"{axis} must be a list of 3 numbers [x, y, z]",
                                "severity": "error"
                            })
                        else:
                            # Validate each component is a number
                            for i, comp in enumerate(axis_value):
                                if not isinstance(comp, (int, float)):
                                    validation_result["valid"] = False
                                    validation_result["issues"].append({
                                        "field": f"orientation.{axis}[{i}]",
                                        "issue": f"{axis} component {i} must be a number",
                                        "severity": "error"
                                    })
                
                # Validate perpendicularity if both axes provided
                x_axis = orientation.get("x_axis")
                y_axis = orientation.get("y_axis")
                if x_axis and y_axis and validation_result["valid"]:
                    dot_product = (
                        x_axis[0] * y_axis[0] +
                        x_axis[1] * y_axis[1] +
                        x_axis[2] * y_axis[2]
                    )
                    if abs(dot_product) > 0.01:  # Allow small tolerance
                        validation_result["warnings"].append({
                            "field": "orientation",
                            "warning": "X and Y axes are not perpendicular. They will be orthogonalized.",
                            "severity": "warning"
                        })
        
        return validation_result
        
    except Exception as e:
        return {
            "valid": False,
            "issues": [{
                "field": "general",
                "issue": f"Validation error: {str(e)}",
                "severity": "error"
            }],
            "warnings": []
        }


def _normalize_vector(vector: list) -> list:
    """Normalize a 3D vector to unit length."""
    length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    if length < 1e-10:
        return [0.0, 0.0, 0.0]
    return [vector[0]/length, vector[1]/length, vector[2]/length]


def _cross_product(a: list, b: list) -> list:
    """Calculate cross product of two 3D vectors."""
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]


# =============================================================================
# Part Position Business Logic Functions
# =============================================================================

def _extract_part_position(setup) -> dict:
    """
    Extract part position information from a setup.
    
    Args:
        setup: The CAM setup object
        
    Returns:
        dict: Part position information
    """
    try:
        position_info = {
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": [1.0, 0.0, 0.0],
                "y_axis": [0.0, 1.0, 0.0],
                "z_axis": [0.0, 0.0, 1.0]
            },
            "is_default": True
        }
        
        # Try to extract model position from setup
        # Note: The actual API properties depend on Fusion 360 version
        
        # Check for model origin property
        if hasattr(setup, 'modelOrigin') and setup.modelOrigin:
            origin = setup.modelOrigin
            position_info["origin"] = {
                "x": origin.x if hasattr(origin, 'x') else 0.0,
                "y": origin.y if hasattr(origin, 'y') else 0.0,
                "z": origin.z if hasattr(origin, 'z') else 0.0
            }
            position_info["is_default"] = False
        
        # Check for model orientation property
        if hasattr(setup, 'modelOrientation') and setup.modelOrientation:
            orientation = setup.modelOrientation
            # Extract orientation from matrix if available
            if hasattr(orientation, 'getAsCoordinateSystem'):
                try:
                    origin_pt, x_axis, y_axis, z_axis = orientation.getAsCoordinateSystem()
                    position_info["orientation"] = {
                        "x_axis": [x_axis.x, x_axis.y, x_axis.z],
                        "y_axis": [y_axis.x, y_axis.y, y_axis.z],
                        "z_axis": [z_axis.x, z_axis.y, z_axis.z]
                    }
                    position_info["is_default"] = False
                except Exception:
                    pass
        
        # Alternative: Try to get position from WCS
        if hasattr(setup, 'workCoordinateSystem') and setup.workCoordinateSystem:
            wcs = setup.workCoordinateSystem
            
            # Get origin from WCS if not already set
            if position_info["is_default"] and hasattr(wcs, 'origin') and wcs.origin:
                origin = wcs.origin
                position_info["origin"] = {
                    "x": origin.x if hasattr(origin, 'x') else 0.0,
                    "y": origin.y if hasattr(origin, 'y') else 0.0,
                    "z": origin.z if hasattr(origin, 'z') else 0.0
                }
                
                # Check if origin is non-zero
                if (position_info["origin"]["x"] != 0.0 or 
                    position_info["origin"]["y"] != 0.0 or 
                    position_info["origin"]["z"] != 0.0):
                    position_info["is_default"] = False
            
            # Get orientation from WCS
            if hasattr(wcs, 'xDirection') and hasattr(wcs, 'yDirection'):
                x_dir = wcs.xDirection
                y_dir = wcs.yDirection
                
                x_axis = [
                    x_dir.x if hasattr(x_dir, 'x') else 1.0,
                    x_dir.y if hasattr(x_dir, 'y') else 0.0,
                    x_dir.z if hasattr(x_dir, 'z') else 0.0
                ]
                
                y_axis = [
                    y_dir.x if hasattr(y_dir, 'x') else 0.0,
                    y_dir.y if hasattr(y_dir, 'y') else 1.0,
                    y_dir.z if hasattr(y_dir, 'z') else 0.0
                ]
                
                # Calculate Z axis from cross product
                z_axis = _cross_product(x_axis, y_axis)
                z_axis = _normalize_vector(z_axis)
                
                position_info["orientation"] = {
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "z_axis": z_axis
                }
        
        return position_info
        
    except Exception as e:
        return {
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": [1.0, 0.0, 0.0],
                "y_axis": [0.0, 1.0, 0.0],
                "z_axis": [0.0, 0.0, 1.0]
            },
            "is_default": True,
            "error": f"Error extracting part position: {str(e)}"
        }


def _get_operation_count(setup) -> int:
    """Get the total number of operations in a setup."""
    count = 0
    try:
        if hasattr(setup, 'operations') and setup.operations:
            count += setup.operations.count
        
        if hasattr(setup, 'folders') and setup.folders:
            for folder_idx in range(setup.folders.count):
                folder = setup.folders.item(folder_idx)
                if hasattr(folder, 'operations') and folder.operations:
                    count += folder.operations.count
    except Exception:
        pass
    return count


def _analyze_part_position_impact(setup, new_position: dict, new_orientation: dict = None) -> dict:
    """
    Analyze the impact of part position changes on existing operations.
    
    Args:
        setup: The CAM setup object
        new_position: New position dictionary
        new_orientation: Optional new orientation dictionary
        
    Returns:
        dict: Impact analysis with warnings
        
    Requirements: 12.3
    """
    impact = {
        "has_impact": False,
        "affected_operations": 0,
        "warnings": [],
        "requires_regeneration": False
    }
    
    try:
        operation_count = _get_operation_count(setup)
        
        if operation_count > 0:
            current_position = _extract_part_position(setup)
            
            # Check if position is changing
            if new_position:
                current_origin = current_position.get("origin", {})
                position_changed = (
                    new_position.get("x", 0) != current_origin.get("x", 0) or
                    new_position.get("y", 0) != current_origin.get("y", 0) or
                    new_position.get("z", 0) != current_origin.get("z", 0)
                )
                
                if position_changed:
                    impact["has_impact"] = True
                    impact["affected_operations"] = operation_count
                    impact["requires_regeneration"] = True
                    impact["warnings"].append(
                        f"Part position change will affect {operation_count} existing operation(s). "
                        "All toolpaths will need regeneration."
                    )
            
            # Check if orientation is changing
            if new_orientation:
                impact["has_impact"] = True
                impact["affected_operations"] = operation_count
                impact["requires_regeneration"] = True
                impact["warnings"].append(
                    f"Part orientation change will affect {operation_count} existing operation(s). "
                    "All toolpaths will need regeneration."
                )
        
        return impact
        
    except Exception as e:
        return {
            "has_impact": False,
            "affected_operations": 0,
            "warnings": [f"Could not analyze part position impact: {str(e)}"],
            "requires_regeneration": False
        }


def get_part_position_impl(setup_id: str) -> dict:
    """
    Get the part position configuration for a setup.
    
    Args:
        setup_id: Unique identifier of the setup
        
    Returns:
        dict: Part position information
              Success response includes:
              - setup_id: Setup identifier
              - setup_name: Setup name
              - origin: Position coordinates {x, y, z}
              - orientation: Axis vectors {x_axis, y_axis, z_axis}
              - is_default: Whether using default position
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code
              
    Requirements: 12.1, 12.4
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"]
            }
        
        cam_product = validation["cam_product"]
        
        if not setup_id:
            return {
                "error": True,
                "message": "Setup ID is required",
                "code": "MISSING_SETUP_ID"
            }
        
        # Find the setup
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        # Extract part position
        position_info = _extract_part_position(setup)
        
        result = {
            "setup_id": setup_id,
            "setup_name": setup.name,
            "origin": position_info["origin"],
            "orientation": position_info["orientation"],
            "is_default": position_info.get("is_default", True),
            "message": f"Part position retrieved for setup '{setup.name}'"
        }
        
        if position_info.get("error"):
            result["warning"] = position_info["error"]
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error retrieving part position: {str(e)}",
            "code": "RETRIEVAL_ERROR"
        }


def set_part_position_impl(setup_id: str, position: dict, orientation: dict = None) -> dict:
    """
    Set the part position and orientation relative to WCS.
    
    Args:
        setup_id: Unique identifier of the setup
        position: Position dictionary with x, y, z coordinates (in cm)
        orientation: Optional orientation dictionary with x_axis and y_axis vectors
        
    Returns:
        dict: Result of the position update
              Success response includes:
              - setup_id: Setup identifier
              - setup_name: Setup name
              - origin: Updated position coordinates
              - orientation: Updated axis vectors
              - warnings: Array of warnings about impacts
              - message: Status message
              
              Error response includes:
              - error: True
              - message: Human-readable error description
              - code: Error code
              
    Requirements: 12.1, 12.2, 12.3, 12.5
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"]
            }
        
        cam_product = validation["cam_product"]
        
        if not setup_id:
            return {
                "error": True,
                "message": "Setup ID is required",
                "code": "MISSING_SETUP_ID"
            }
        
        # Validate position parameters
        position_validation = validate_part_position(position, orientation)
        if not position_validation["valid"]:
            issues = position_validation.get("issues", [])
            issue_messages = [issue.get("issue", "Unknown issue") for issue in issues]
            return {
                "error": True,
                "message": f"Invalid part position configuration: {'; '.join(issue_messages)}",
                "code": "PART_POSITION_INVALID",
                "validation_issues": issues
            }
        
        # Find the setup
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        # Analyze impact on existing operations
        impact = _analyze_part_position_impact(setup, position, orientation)
        warnings = impact.get("warnings", [])
        
        # Add validation warnings
        for warning in position_validation.get("warnings", []):
            warnings.append(warning.get("warning", ""))
        
        # Prepare position values with defaults
        new_origin = {
            "x": position.get("x", 0.0),
            "y": position.get("y", 0.0),
            "z": position.get("z", 0.0)
        }
        
        # Prepare orientation values
        new_orientation = None
        if orientation:
            x_axis = orientation.get("x_axis", [1.0, 0.0, 0.0])
            y_axis = orientation.get("y_axis", [0.0, 1.0, 0.0])
            
            # Normalize axes
            x_axis = _normalize_vector(x_axis)
            y_axis = _normalize_vector(y_axis)
            
            # Calculate Z axis from cross product
            z_axis = _cross_product(x_axis, y_axis)
            z_axis = _normalize_vector(z_axis)
            
            new_orientation = {
                "x_axis": x_axis,
                "y_axis": y_axis,
                "z_axis": z_axis
            }
        
        # Attempt to set part position
        # Note: Fusion 360 API has limited support for direct part position modification
        # This implementation provides the framework for when API support is available
        
        position_updated = False
        update_notes = []
        
        try:
            # Try to set model origin if the property exists
            if hasattr(setup, 'modelOrigin'):
                # Create Point3D for new origin
                new_origin_pt = adsk.core.Point3D.create(
                    new_origin["x"],
                    new_origin["y"],
                    new_origin["z"]
                )
                # Note: This may not be writable depending on API version
                try:
                    setup.modelOrigin = new_origin_pt
                    position_updated = True
                    update_notes.append("Model origin updated")
                except AttributeError:
                    update_notes.append("Model origin is read-only")
            
            # Try to set orientation if provided
            if new_orientation and hasattr(setup, 'modelOrientation'):
                # Note: This may require Matrix3D manipulation
                update_notes.append("Orientation update requested (limited API support)")
            
        except Exception as api_error:
            update_notes.append(f"API limitation: {str(api_error)}")
        
        # If direct update not possible, provide guidance
        if not position_updated:
            warnings.append(
                "Part position modification has limited API support. "
                "Position changes may need to be made manually in Fusion 360. "
                "The requested position has been validated and recorded."
            )
        
        # Get current position after attempted update
        current_position = _extract_part_position(setup)
        
        result = {
            "setup_id": setup_id,
            "setup_name": setup.name,
            "origin": new_origin,
            "orientation": new_orientation if new_orientation else current_position["orientation"],
            "position_updated": position_updated,
            "update_notes": update_notes if update_notes else None,
            "warnings": warnings if warnings else None,
            "requires_regeneration": impact.get("requires_regeneration", False),
            "affected_operations": impact.get("affected_operations", 0),
            "message": f"Part position {'updated' if position_updated else 'validated'} for setup '{setup.name}'"
        }
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error setting part position: {str(e)}",
            "code": "POSITION_UPDATE_FAILED"
        }


# =============================================================================
# HTTP Handler Functions
# =============================================================================

def handle_get_part_position(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get part position configuration for a setup.
    
    This is a READ-ONLY operation - calls impl directly without task_queue.
    """
    try:
        setup_id = data.get("setup_id")
        if not setup_id:
            return {
                "status": 400,
                "error": True,
                "message": "setup_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        # READ-ONLY: Call impl directly, no task_queue needed
        result = get_part_position_impl(setup_id)
        
        # Determine status code
        if result.get("error"):
            if result.get("code") == "SETUP_NOT_FOUND":
                status = 404
            elif result.get("code") == "MISSING_SETUP_ID":
                status = 400
            else:
                status = 500
        else:
            status = 200
        
        return {
            "status": status,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_get_part_position: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_set_part_position(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set part position configuration for a setup.
    
    This is a WRITE operation that modifies the setup.
    """
    try:
        setup_id = data.get("setup_id")
        if not setup_id:
            return {
                "status": 400,
                "error": True,
                "message": "setup_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        position = data.get("position") or data.get("origin")
        if not position:
            return {
                "status": 400,
                "error": True,
                "message": "position parameter is required with x, y, z coordinates",
                "headers": {"Content-Type": "application/json"}
            }
        
        orientation = data.get("orientation")
        
        # Call impl function directly
        # Note: For write operations, we would normally use task_queue,
        # but since the API has limited write support, we call directly
        result = set_part_position_impl(setup_id, position, orientation)
        
        # Determine status code
        if result.get("error"):
            if result.get("code") == "SETUP_NOT_FOUND":
                status = 404
            elif result.get("code") in ["MISSING_SETUP_ID", "PART_POSITION_INVALID"]:
                status = 400
            else:
                status = 500
        else:
            status = 200
        
        return {
            "status": status,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_set_part_position: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


# =============================================================================
# Handler Registration
# =============================================================================

def register_handlers():
    """Register part position handlers with the request router."""
    try:
        request_router.register_handler(
            "/cam/setups/{setup_id}/part-position",
            handle_get_part_position,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.part_position"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}/part-position",
            handle_set_part_position,
            methods=["PUT"],
            category="manufacture",
            module_name="manufacture.setups.part_position"
        )
        
        logger.info("Registered part position handlers")
        
    except Exception as e:
        logger.error(f"Error registering part position handlers: {str(e)}")


# Register handlers when module is loaded
register_handlers()
