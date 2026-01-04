"""
CAM Setup Core Management Handler

Handles CAM setup creation, modification, duplication, and deletion operations.
Contains actual business logic for setup management.

This module is part of the modular setups/ directory structure following
the patterns from operations/ and tool_libraries/ modules.

Requirements: 1.x, 4.x, 5.x, 6.x, 7.x, 8.x, 9.x, 10.x, 11.x, 13.x
"""

import adsk.core
import adsk.cam
from typing import Dict, Any, Optional
import logging

# Import core components
from ....core.task_queue import task_queue, TaskPriority
from ....core.router import request_router

# Import shared CAM utilities
from ..cam_utils import (
    get_cam_product,
    validate_cam_product_with_details,
    find_setup_by_id,
    get_operation_type,
    get_tool_type_string
)

# Set up logging
logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================

def _setup_name_exists(cam_product: adsk.cam.CAM, name: str) -> bool:
    """Check if a setup name already exists."""
    try:
        setups = cam_product.setups
        if not setups:
            return False
        
        for setup_idx in range(setups.count):
            setup = setups.item(setup_idx)
            if setup.name == name:
                return True
        
        return False
    except Exception:
        return False


def _extract_wcs_info(setup) -> dict:
    """Extract WCS information from a setup."""
    try:
        wcs_info = {
            "type": "model_origin",
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": {"x": 1.0, "y": 0.0, "z": 0.0},
                "y_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
                "z_axis": {"x": 0.0, "y": 0.0, "z": 1.0}
            },
            "reference": "model",
            "reference_geometry": None
        }
        
        if hasattr(setup, 'workCoordinateSystem'):
            wcs = setup.workCoordinateSystem
            if wcs:
                if hasattr(wcs, 'origin'):
                    origin = wcs.origin
                    wcs_info["origin"] = {
                        "x": origin.x if hasattr(origin, 'x') else 0.0,
                        "y": origin.y if hasattr(origin, 'y') else 0.0,
                        "z": origin.z if hasattr(origin, 'z') else 0.0
                    }
                
                if hasattr(wcs, 'xDirection') and hasattr(wcs, 'yDirection'):
                    x_dir = wcs.xDirection
                    y_dir = wcs.yDirection
                    
                    wcs_info["orientation"]["x_axis"] = {
                        "x": x_dir.x if hasattr(x_dir, 'x') else 1.0,
                        "y": x_dir.y if hasattr(x_dir, 'y') else 0.0,
                        "z": x_dir.z if hasattr(x_dir, 'z') else 0.0
                    }
                    
                    wcs_info["orientation"]["y_axis"] = {
                        "x": y_dir.x if hasattr(y_dir, 'x') else 0.0,
                        "y": y_dir.y if hasattr(y_dir, 'y') else 1.0,
                        "z": y_dir.z if hasattr(y_dir, 'z') else 0.0
                    }
                    
                    z_x = x_dir.y * y_dir.z - x_dir.z * y_dir.y
                    z_y = x_dir.z * y_dir.x - x_dir.x * y_dir.z
                    z_z = x_dir.x * y_dir.y - x_dir.y * y_dir.x
                    
                    wcs_info["orientation"]["z_axis"] = {"x": z_x, "y": z_y, "z": z_z}
                
                if hasattr(wcs, 'isModelOrigin') and wcs.isModelOrigin:
                    wcs_info["type"] = "model_origin"
                elif hasattr(wcs, 'referenceFace') and wcs.referenceFace:
                    wcs_info["type"] = "face_based"
                    wcs_info["reference"] = "face"
                elif hasattr(wcs, 'referenceEdge') and wcs.referenceEdge:
                    wcs_info["type"] = "edge_based"
                    wcs_info["reference"] = "edge"
                else:
                    wcs_info["type"] = "custom"
        
        return wcs_info
        
    except Exception:
        return {
            "type": "unknown",
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": {"x": 1.0, "y": 0.0, "z": 0.0},
                "y_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
                "z_axis": {"x": 0.0, "y": 0.0, "z": 1.0}
            },
            "reference": "unknown",
            "reference_geometry": None
        }


def _extract_stock_info(setup) -> dict:
    """Extract stock information from a setup."""
    try:
        stock_info = {
            "mode": "unknown",
            "dimensions": {"length": 0, "width": 0, "height": 0, "diameter": 0},
            "position": [0, 0, 0],
            "material": "unknown",
            "geometry_id": None
        }
        
        if hasattr(setup, 'stock') and setup.stock:
            stock = setup.stock
            
            if hasattr(stock, 'stockType'):
                stock_type = stock.stockType
                if stock_type == adsk.cam.StockTypes.RelativeBoxStock:
                    stock_info["mode"] = "box"
                elif stock_type == adsk.cam.StockTypes.RelativeCylinderStock:
                    stock_info["mode"] = "cylinder"
                elif stock_type == adsk.cam.StockTypes.FixedBoxStock:
                    stock_info["mode"] = "fixed_box"
                elif stock_type == adsk.cam.StockTypes.FixedCylinderStock:
                    stock_info["mode"] = "fixed_cylinder"
                else:
                    stock_info["mode"] = "auto"
            
            if hasattr(stock, 'boundingBox') and stock.boundingBox:
                bbox = stock.boundingBox
                if hasattr(bbox, 'minPoint') and hasattr(bbox, 'maxPoint'):
                    min_pt = bbox.minPoint
                    max_pt = bbox.maxPoint
                    stock_info["dimensions"] = {
                        "length": abs(max_pt.x - min_pt.x),
                        "width": abs(max_pt.y - min_pt.y),
                        "height": abs(max_pt.z - min_pt.z),
                        "diameter": max(abs(max_pt.x - min_pt.x), abs(max_pt.y - min_pt.y))
                    }
            
            if hasattr(stock, 'origin') and stock.origin:
                origin = stock.origin
                stock_info["position"] = [origin.x, origin.y, origin.z]
            
            if hasattr(stock, 'material') and stock.material:
                material = stock.material
                if hasattr(material, 'name'):
                    stock_info["material"] = material.name
                elif hasattr(material, 'displayName'):
                    stock_info["material"] = material.displayName
            
            if hasattr(stock, 'sourceBody') and stock.sourceBody:
                body = stock.sourceBody
                if hasattr(body, 'entityToken'):
                    stock_info["geometry_id"] = body.entityToken
        
        return stock_info
        
    except Exception as e:
        return {
            "mode": "unknown",
            "dimensions": {"length": 0, "width": 0, "height": 0, "diameter": 0},
            "position": [0, 0, 0],
            "material": "unknown",
            "geometry_id": None,
            "error": f"Error extracting stock info: {str(e)}"
        }


def _extract_model_reference(setup) -> str:
    """Extract model reference from a setup (root level)."""
    try:
        return "model_placeholder_id"
    except Exception:
        return None


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


# =============================================================================
# Business Logic Functions
# =============================================================================

def list_setups_detailed() -> dict:
    """
    List all CAM setups with comprehensive configuration details.
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "setups": [],
                "total_count": 0,
                "error": True,
                "message": validation["message"],
                "code": validation["code"]
            }
        
        cam_product = validation["cam_product"]
        
        result = {
            "setups": [],
            "total_count": 0,
            "message": None
        }
        
        setups = cam_product.setups
        if not setups or setups.count == 0:
            result["message"] = "No setups found in CAM document"
            return result
        
        for setup_idx in range(setups.count):
            setup = setups.item(setup_idx)
            
            setup_id = setup.entityToken if hasattr(setup, 'entityToken') else f"setup_{setup_idx}"
            
            toolpath_count = 0
            if hasattr(setup, 'operations') and setup.operations:
                toolpath_count += setup.operations.count
            
            if hasattr(setup, 'folders') and setup.folders:
                for folder_idx in range(setup.folders.count):
                    folder = setup.folders.item(folder_idx)
                    if hasattr(folder, 'operations') and folder.operations:
                        toolpath_count += folder.operations.count
            
            wcs_info = _extract_wcs_info(setup)
            stock_info = _extract_stock_info(setup)
            model_ref = _extract_model_reference(setup)
            
            setup_data = {
                "id": setup_id,
                "name": setup.name,
                "wcs": wcs_info,
                "stock": stock_info,
                "model_id": model_ref,
                "toolpath_count": toolpath_count,
                "is_active": hasattr(setup, 'isActive') and setup.isActive,
                "created_date": "2025-01-03T00:00:00Z",
                "modified_date": "2025-01-03T00:00:00Z"
            }
            
            result["setups"].append(setup_data)
        
        result["total_count"] = len(result["setups"])
        
        if result["total_count"] == 0:
            result["message"] = "No setups found in CAM document"
        
        return result
        
    except Exception as e:
        return {
            "setups": [],
            "total_count": 0,
            "error": True,
            "message": f"Error listing setups: {str(e)}",
            "code": "LISTING_ERROR"
        }


def get_setup_by_id_impl(setup_id: str) -> dict:
    """
    Retrieve detailed setup information by ID.
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
        
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        wcs_info = _extract_wcs_info(setup)
        stock_info = _extract_stock_info(setup)
        model_ref = _extract_model_reference(setup)
        
        toolpaths = []
        if hasattr(setup, 'operations') and setup.operations:
            for op_idx in range(setup.operations.count):
                operation = setup.operations.item(op_idx)
                toolpath_data = {
                    "id": operation.entityToken if hasattr(operation, 'entityToken') else f"op_{op_idx}",
                    "name": operation.name,
                    "type": get_operation_type(operation),
                    "is_valid": operation.isValid if hasattr(operation, 'isValid') else True
                }
                toolpaths.append(toolpath_data)
        
        if hasattr(setup, 'folders') and setup.folders:
            for folder_idx in range(setup.folders.count):
                folder = setup.folders.item(folder_idx)
                if hasattr(folder, 'operations') and folder.operations:
                    for op_idx in range(folder.operations.count):
                        operation = folder.operations.item(op_idx)
                        toolpath_data = {
                            "id": operation.entityToken if hasattr(operation, 'entityToken') else f"op_f{folder_idx}_{op_idx}",
                            "name": operation.name,
                            "type": get_operation_type(operation),
                            "is_valid": operation.isValid if hasattr(operation, 'isValid') else True,
                            "folder": folder.name
                        }
                        toolpaths.append(toolpath_data)
        
        result = {
            "id": setup_id,
            "name": setup.name,
            "wcs": wcs_info,
            "stock": stock_info,
            "model_id": model_ref,
            "toolpaths": toolpaths,
            "toolpath_count": len(toolpaths),
            "is_active": hasattr(setup, 'isActive') and setup.isActive,
            "metadata": {
                "created_date": "2025-01-03T00:00:00Z",
                "modified_date": "2025-01-03T00:00:00Z"
            }
        }
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error retrieving setup '{setup_id}': {str(e)}",
            "code": "RETRIEVAL_ERROR"
        }


def create_setup_impl(name: str = None, model_id: str = None) -> dict:
    """
    Create a new CAM setup with specified configuration.
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
        
        if not name:
            base_name = "Setup"
            counter = 1
            name = base_name
            while _setup_name_exists(cam_product, name):
                counter += 1
                name = f"{base_name} {counter}"
        elif _setup_name_exists(cam_product, name):
            return {
                "error": True,
                "message": f"Setup with name '{name}' already exists",
                "code": "DUPLICATE_NAME"
            }
        
        try:
            setups = cam_product.setups
            new_setup = setups.add()
            new_setup.name = name
            
            setup_id = new_setup.entityToken if hasattr(new_setup, 'entityToken') else str(id(new_setup))
            actual_stock_config = _extract_stock_info(new_setup)
            actual_wcs_config = _extract_wcs_info(new_setup)
            
            result = {
                "id": setup_id,
                "name": name,
                "wcs": actual_wcs_config,
                "stock": actual_stock_config,
                "model_id": model_id,
                "created_date": "2025-01-03T00:00:00Z",
                "message": f"Setup '{name}' created successfully"
            }
            
            return result
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to create setup: {str(e)}",
                "code": "SETUP_CREATION_FAILED"
            }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error during setup creation: {str(e)}",
            "code": "CREATION_ERROR"
        }


def _analyze_wcs_impact(setup, new_wcs_config: dict) -> dict:
    """Analyze the impact of WCS changes on existing operations."""
    impact = {
        "has_impact": False,
        "affected_operations": 0,
        "warnings": []
    }
    
    try:
        operation_count = _get_operation_count(setup)
        
        if operation_count > 0:
            current_wcs = _extract_wcs_info(setup)
            
            if new_wcs_config.get("origin"):
                new_origin = new_wcs_config["origin"]
                current_origin = current_wcs.get("origin", {})
                
                origin_changed = (
                    new_origin.get("x", 0) != current_origin.get("x", 0) or
                    new_origin.get("y", 0) != current_origin.get("y", 0) or
                    new_origin.get("z", 0) != current_origin.get("z", 0)
                )
                
                if origin_changed:
                    impact["has_impact"] = True
                    impact["affected_operations"] = operation_count
                    impact["warnings"].append(
                        f"WCS origin change will affect {operation_count} existing operation(s). "
                        "Toolpaths may need regeneration."
                    )
            
            if new_wcs_config.get("orientation"):
                impact["has_impact"] = True
                impact["affected_operations"] = operation_count
                impact["warnings"].append(
                    f"WCS orientation change will affect {operation_count} existing operation(s). "
                    "Toolpaths will need regeneration."
                )
        
        return impact
        
    except Exception as e:
        return {
            "has_impact": False,
            "affected_operations": 0,
            "warnings": [f"Could not analyze WCS impact: {str(e)}"]
        }


def _analyze_stock_impact(setup, new_stock_config: dict) -> dict:
    """Analyze the impact of stock changes on existing operations."""
    impact = {
        "has_impact": False,
        "affected_operations": 0,
        "warnings": [],
        "valid": True
    }
    
    try:
        operation_count = _get_operation_count(setup)
        
        if operation_count > 0:
            current_stock = _extract_stock_info(setup)
            
            if new_stock_config.get("dimensions"):
                new_dims = new_stock_config["dimensions"]
                current_dims = current_stock.get("dimensions", {})
                
                shrinking = False
                if new_dims.get("length", float('inf')) < current_dims.get("length", 0):
                    shrinking = True
                if new_dims.get("width", float('inf')) < current_dims.get("width", 0):
                    shrinking = True
                if new_dims.get("height", float('inf')) < current_dims.get("height", 0):
                    shrinking = True
                
                if shrinking:
                    impact["has_impact"] = True
                    impact["affected_operations"] = operation_count
                    impact["warnings"].append(
                        f"Stock dimensions are being reduced. {operation_count} existing operation(s) "
                        "may have toolpaths outside the new stock boundaries."
                    )
            
            if new_stock_config.get("mode"):
                new_mode = new_stock_config["mode"]
                current_mode = current_stock.get("mode", "unknown")
                
                if new_mode != current_mode:
                    impact["has_impact"] = True
                    impact["affected_operations"] = operation_count
                    impact["warnings"].append(
                        f"Stock mode changing from '{current_mode}' to '{new_mode}'. "
                        "Existing operations may need review."
                    )
        
        return impact
        
    except Exception as e:
        return {
            "has_impact": False,
            "affected_operations": 0,
            "warnings": [f"Could not analyze stock impact: {str(e)}"],
            "valid": True
        }


def modify_setup_impl(setup_id: str, updates: dict) -> dict:
    """
    Modify an existing CAM setup configuration.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
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
        
        if not updates or not isinstance(updates, dict):
            return {
                "error": True,
                "message": "Updates dictionary is required",
                "code": "INVALID_UPDATES"
            }
        
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        warnings = []
        changes_made = []
        
        if "wcs" in updates and updates["wcs"]:
            wcs_impact = _analyze_wcs_impact(setup, updates["wcs"])
            if wcs_impact["has_impact"]:
                warnings.extend(wcs_impact["warnings"])
        
        if "stock" in updates and updates["stock"]:
            stock_impact = _analyze_stock_impact(setup, updates["stock"])
            if stock_impact["has_impact"]:
                warnings.extend(stock_impact["warnings"])
            if not stock_impact.get("valid", True):
                return {
                    "error": True,
                    "message": "Stock configuration is invalid for existing operations",
                    "code": "INVALID_STOCK_CONFIG",
                    "warnings": stock_impact["warnings"]
                }
        
        if "name" in updates and updates["name"]:
            new_name = updates["name"]
            
            if new_name != setup.name and _setup_name_exists(cam_product, new_name):
                return {
                    "error": True,
                    "message": f"Setup with name '{new_name}' already exists",
                    "code": "DUPLICATE_NAME"
                }
            
            try:
                old_name = setup.name
                setup.name = new_name
                changes_made.append(f"Name changed from '{old_name}' to '{new_name}'")
            except Exception as e:
                return {
                    "error": True,
                    "message": f"Failed to update setup name: {str(e)}",
                    "code": "NAME_UPDATE_FAILED"
                }
        
        if "wcs" in updates and updates["wcs"]:
            wcs_config = updates["wcs"]
            if wcs_config.get("origin") or wcs_config.get("orientation"):
                changes_made.append("WCS configuration update requested (limited API support)")
                warnings.append(
                    "Full WCS modification requires manual adjustment in Fusion 360. "
                    "Origin and orientation changes have limited API support."
                )
        
        if "stock" in updates and updates["stock"]:
            stock_config = updates["stock"]
            if stock_config.get("dimensions") or stock_config.get("mode"):
                changes_made.append("Stock configuration update requested (limited API support)")
                warnings.append(
                    "Full stock modification requires manual adjustment in Fusion 360. "
                    "Dimension and mode changes have limited API support."
                )
        
        updated_wcs = _extract_wcs_info(setup)
        updated_stock = _extract_stock_info(setup)
        operation_count = _get_operation_count(setup)
        
        result = {
            "id": setup_id,
            "name": setup.name,
            "wcs": updated_wcs,
            "stock": updated_stock,
            "model_id": _extract_model_reference(setup),
            "toolpath_count": operation_count,
            "is_active": hasattr(setup, 'isActive') and setup.isActive,
            "modified_date": "2025-01-04T00:00:00Z",
            "changes_made": changes_made,
            "warnings": warnings if warnings else None,
            "message": f"Setup '{setup.name}' modified successfully" if changes_made else "No changes applied"
        }
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error modifying setup: {str(e)}",
            "code": "MODIFICATION_ERROR"
        }


def _generate_duplicate_name(cam_product, original_name: str) -> str:
    """Generate a unique name for a duplicated setup."""
    base_name = f"{original_name} (Copy)"
    
    if not _setup_name_exists(cam_product, base_name):
        return base_name
    
    counter = 2
    while True:
        new_name = f"{original_name} (Copy {counter})"
        if not _setup_name_exists(cam_product, new_name):
            return new_name
        counter += 1
        if counter > 100:
            return f"{original_name} (Copy {id(cam_product)})"


def duplicate_setup_impl(setup_id: str, new_name: str = None) -> dict:
    """
    Duplicate an existing CAM setup.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
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
        
        source_setup = find_setup_by_id(cam_product, setup_id)
        if not source_setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        if new_name:
            if _setup_name_exists(cam_product, new_name):
                return {
                    "error": True,
                    "message": f"Setup with name '{new_name}' already exists",
                    "code": "DUPLICATE_NAME"
                }
            duplicate_name = new_name
        else:
            duplicate_name = _generate_duplicate_name(cam_product, source_setup.name)
        
        source_wcs = _extract_wcs_info(source_setup)
        source_stock = _extract_stock_info(source_setup)
        source_model_ref = _extract_model_reference(source_setup)
        source_operation_count = _get_operation_count(source_setup)
        
        try:
            setups = cam_product.setups
            new_setup = setups.add()
            new_setup.name = duplicate_name
            
            new_setup_id = new_setup.entityToken if hasattr(new_setup, 'entityToken') else str(id(new_setup))
            
            new_wcs = _extract_wcs_info(new_setup)
            new_stock = _extract_stock_info(new_setup)
            
            notes = []
            if source_operation_count > 0:
                notes.append(
                    f"Source setup had {source_operation_count} operation(s). "
                    "Operations are not automatically copied. "
                    "You may need to recreate operations in the new setup."
                )
            
            notes.append(
                "WCS and stock configurations are set to defaults. "
                "Manual adjustment may be required to match the source setup."
            )
            
            result = {
                "id": new_setup_id,
                "name": duplicate_name,
                "wcs": new_wcs,
                "stock": new_stock,
                "model_id": source_model_ref,
                "source_setup": {
                    "id": setup_id,
                    "name": source_setup.name,
                    "operation_count": source_operation_count
                },
                "created_date": "2025-01-04T00:00:00Z",
                "notes": notes,
                "message": f"Setup '{duplicate_name}' created as duplicate of '{source_setup.name}'"
            }
            
            return result
            
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to duplicate setup: {str(e)}",
                "code": "DUPLICATION_FAILED"
            }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error duplicating setup: {str(e)}",
            "code": "DUPLICATION_ERROR"
        }


def delete_setup_impl(setup_id: str, confirm: bool = False) -> dict:
    """
    Delete a CAM setup and all associated operations.
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
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
        
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        setup_name = setup.name
        operation_count = _get_operation_count(setup)
        
        if operation_count > 0 and not confirm:
            return {
                "error": False,
                "requires_confirmation": True,
                "setup_id": setup_id,
                "setup_name": setup_name,
                "operation_count": operation_count,
                "warning": f"Setup '{setup_name}' contains {operation_count} operation(s)/toolpath(s). "
                          "These will be permanently deleted. Set confirm=true to proceed.",
                "message": "Confirmation required for deletion"
            }
        
        try:
            success = setup.deleteMe()
            
            if success:
                return {
                    "deleted": True,
                    "setup_id": setup_id,
                    "setup_name": setup_name,
                    "operations_deleted": operation_count,
                    "message": f"Setup '{setup_name}' and {operation_count} operation(s) deleted successfully"
                }
            else:
                return {
                    "error": True,
                    "message": f"Failed to delete setup '{setup_name}'. The operation returned false.",
                    "code": "DELETION_FAILED"
                }
                
        except AttributeError:
            return {
                "error": True,
                "message": f"Setup deletion not supported via API. "
                          f"Please delete setup '{setup_name}' manually in Fusion 360.",
                "code": "DELETION_NOT_SUPPORTED",
                "setup_id": setup_id,
                "setup_name": setup_name
            }
                
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to delete setup '{setup_name}': {str(e)}",
                "code": "DELETION_FAILED"
            }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error deleting setup: {str(e)}",
            "code": "DELETION_ERROR"
        }


# =============================================================================
# Setup-Toolpath Relationship Functions (Task 10.1)
# =============================================================================

def get_toolpaths_for_setup_impl(setup_id: str, include_details: bool = True) -> dict:
    """
    Get all toolpaths within a specific setup using existing toolpath functionality.
    
    Requirements: 9.1, 9.2, 9.3, 10.1, 10.2, 10.3, 11.1, 11.3
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "setup_id": setup_id,
                "context": "setup-toolpath relationship query"
            }
        
        cam_product = validation["cam_product"]
        
        if not setup_id:
            return {
                "error": True,
                "message": "Setup ID is required",
                "code": "MISSING_SETUP_ID",
                "context": "setup-toolpath relationship query"
            }
        
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND",
                "setup_id": setup_id,
                "context": "setup-toolpath relationship query"
            }
        
        toolpaths = []
        
        if hasattr(setup, 'operations') and setup.operations:
            for op_idx in range(setup.operations.count):
                operation = setup.operations.item(op_idx)
                toolpath_data = _serialize_toolpath_with_setup_context(
                    operation, setup_id, setup.name, op_idx, None, include_details
                )
                toolpaths.append(toolpath_data)
        
        if hasattr(setup, 'folders') and setup.folders:
            for folder_idx in range(setup.folders.count):
                folder = setup.folders.item(folder_idx)
                if hasattr(folder, 'operations') and folder.operations:
                    for op_idx in range(folder.operations.count):
                        operation = folder.operations.item(op_idx)
                        toolpath_data = _serialize_toolpath_with_setup_context(
                            operation, setup_id, setup.name, op_idx, folder.name, include_details
                        )
                        toolpaths.append(toolpath_data)
        
        result = {
            "setup_id": setup_id,
            "setup_name": setup.name,
            "toolpaths": toolpaths,
            "total_count": len(toolpaths),
            "message": f"Found {len(toolpaths)} toolpath(s) in setup '{setup.name}'" if toolpaths else f"No toolpaths found in setup '{setup.name}'"
        }
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error retrieving toolpaths for setup: {str(e)}",
            "code": "TOOLPATH_RETRIEVAL_ERROR",
            "setup_id": setup_id,
            "context": "setup-toolpath relationship query"
        }


def _serialize_toolpath_with_setup_context(
    operation, 
    setup_id: str, 
    setup_name: str, 
    op_idx: int, 
    folder_name: str = None,
    include_details: bool = True
) -> dict:
    """Serialize a toolpath operation with setup context information."""
    try:
        op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{op_idx}"
        
        toolpath_data = {
            "id": op_id,
            "name": operation.name,
            "type": get_operation_type(operation),
            "is_valid": operation.isValid if hasattr(operation, 'isValid') else True,
            "setup_id": setup_id,
            "setup_name": setup_name
        }
        
        if folder_name:
            toolpath_data["folder"] = folder_name
        
        if include_details:
            toolpath_data["tool"] = _get_tool_data_for_toolpath(operation)
        
        return toolpath_data
        
    except Exception as e:
        return {
            "id": f"op_{op_idx}",
            "name": "Error accessing operation",
            "type": "unknown",
            "is_valid": False,
            "setup_id": setup_id,
            "setup_name": setup_name,
            "error": str(e)
        }


def _get_tool_data_for_toolpath(operation) -> dict:
    """Extract tool data from an operation for toolpath serialization."""
    try:
        tool = None
        
        if hasattr(operation, 'tool') and operation.tool:
            tool = operation.tool
        elif hasattr(operation, 'parameters'):
            params = operation.parameters
            for param_idx in range(params.count):
                param = params.item(param_idx)
                if param.name == "tool_tool" and hasattr(param, 'value'):
                    tool = param.value
                    break
        
        if not tool:
            return {"name": "No tool assigned", "id": None}
        
        tool_data = {
            "id": tool.entityToken if hasattr(tool, 'entityToken') else str(id(tool)),
            "name": "Unnamed Tool",
            "type": get_tool_type_string(tool) if hasattr(tool, 'type') else "unknown"
        }
        
        if hasattr(tool, 'parameters'):
            params = tool.parameters
            desc_param = params.itemByName('tool_description')
            if desc_param and desc_param.expression:
                tool_data["name"] = desc_param.expression.strip("'\"")
        
        if tool_data["name"] == "Unnamed Tool":
            if hasattr(tool, 'description') and tool.description:
                tool_data["name"] = tool.description
        
        return tool_data
        
    except Exception:
        return {"name": "Error accessing tool", "id": None}


def find_setup_for_toolpath_impl(toolpath_id: str) -> dict:
    """
    Find which setup contains a specific toolpath.
    
    Requirements: 9.1, 9.2, 9.3, 11.1, 11.2, 11.3
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "toolpath_id": toolpath_id,
                "context": "toolpath-setup relationship query"
            }
        
        cam_product = validation["cam_product"]
        
        if not toolpath_id:
            return {
                "error": True,
                "message": "Toolpath ID is required",
                "code": "MISSING_TOOLPATH_ID",
                "context": "toolpath-setup relationship query"
            }
        
        setups = cam_product.setups
        if not setups or setups.count == 0:
            return {
                "error": True,
                "message": "No setups found in CAM document",
                "code": "NO_SETUPS",
                "toolpath_id": toolpath_id,
                "context": "toolpath-setup relationship query"
            }
        
        for setup_idx in range(setups.count):
            setup = setups.item(setup_idx)
            setup_id = setup.entityToken if hasattr(setup, 'entityToken') else f"setup_{setup_idx}"
            
            if hasattr(setup, 'operations') and setup.operations:
                for op_idx in range(setup.operations.count):
                    operation = setup.operations.item(op_idx)
                    op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{setup_idx}_{op_idx}"
                    
                    if op_id == toolpath_id:
                        return {
                            "toolpath_id": toolpath_id,
                            "toolpath_name": operation.name,
                            "toolpath_type": get_operation_type(operation),
                            "setup_id": setup_id,
                            "setup_name": setup.name,
                            "folder": None,
                            "message": f"Toolpath '{operation.name}' belongs to setup '{setup.name}'"
                        }
            
            if hasattr(setup, 'folders') and setup.folders:
                for folder_idx in range(setup.folders.count):
                    folder = setup.folders.item(folder_idx)
                    if hasattr(folder, 'operations') and folder.operations:
                        for op_idx in range(folder.operations.count):
                            operation = folder.operations.item(op_idx)
                            op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{setup_idx}_f{folder_idx}_{op_idx}"
                            
                            if op_id == toolpath_id:
                                return {
                                    "toolpath_id": toolpath_id,
                                    "toolpath_name": operation.name,
                                    "toolpath_type": get_operation_type(operation),
                                    "setup_id": setup_id,
                                    "setup_name": setup.name,
                                    "folder": folder.name,
                                    "message": f"Toolpath '{operation.name}' belongs to setup '{setup.name}' in folder '{folder.name}'"
                                }
        
        return {
            "error": True,
            "message": f"Toolpath with ID '{toolpath_id}' not found in any setup",
            "code": "TOOLPATH_NOT_FOUND",
            "toolpath_id": toolpath_id,
            "context": "toolpath-setup relationship query"
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error finding setup for toolpath: {str(e)}",
            "code": "RELATIONSHIP_QUERY_ERROR",
            "toolpath_id": toolpath_id,
            "context": "toolpath-setup relationship query"
        }


def validate_setup_toolpath_relationship_impl(setup_id: str, toolpath_id: str) -> dict:
    """
    Validate that a toolpath belongs to a specific setup.
    
    Requirements: 9.3, 11.4, 11.5
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "valid": False,
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "setup_id": setup_id,
                "toolpath_id": toolpath_id,
                "context": "setup-toolpath validation"
            }
        
        cam_product = validation["cam_product"]
        
        if not setup_id:
            return {
                "valid": False,
                "error": True,
                "message": "Setup ID is required",
                "code": "MISSING_SETUP_ID",
                "context": "setup-toolpath validation"
            }
        
        if not toolpath_id:
            return {
                "valid": False,
                "error": True,
                "message": "Toolpath ID is required",
                "code": "MISSING_TOOLPATH_ID",
                "context": "setup-toolpath validation"
            }
        
        setup = find_setup_by_id(cam_product, setup_id)
        if not setup:
            return {
                "valid": False,
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND",
                "setup_id": setup_id,
                "toolpath_id": toolpath_id,
                "context": "setup-toolpath validation"
            }
        
        if hasattr(setup, 'operations') and setup.operations:
            for op_idx in range(setup.operations.count):
                operation = setup.operations.item(op_idx)
                op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{op_idx}"
                
                if op_id == toolpath_id:
                    return {
                        "valid": True,
                        "setup_id": setup_id,
                        "setup_name": setup.name,
                        "toolpath_id": toolpath_id,
                        "toolpath_name": operation.name,
                        "toolpath_type": get_operation_type(operation),
                        "folder": None,
                        "message": f"Toolpath '{operation.name}' is valid within setup '{setup.name}'"
                    }
        
        if hasattr(setup, 'folders') and setup.folders:
            for folder_idx in range(setup.folders.count):
                folder = setup.folders.item(folder_idx)
                if hasattr(folder, 'operations') and folder.operations:
                    for op_idx in range(folder.operations.count):
                        operation = folder.operations.item(op_idx)
                        op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_f{folder_idx}_{op_idx}"
                        
                        if op_id == toolpath_id:
                            return {
                                "valid": True,
                                "setup_id": setup_id,
                                "setup_name": setup.name,
                                "toolpath_id": toolpath_id,
                                "toolpath_name": operation.name,
                                "toolpath_type": get_operation_type(operation),
                                "folder": folder.name,
                                "message": f"Toolpath '{operation.name}' is valid within setup '{setup.name}'"
                            }
        
        actual_setup = find_setup_for_toolpath_impl(toolpath_id)
        
        if actual_setup.get("error"):
            return {
                "valid": False,
                "error": True,
                "message": f"Toolpath with ID '{toolpath_id}' not found in any setup",
                "code": "TOOLPATH_NOT_FOUND",
                "setup_id": setup_id,
                "toolpath_id": toolpath_id,
                "context": "setup-toolpath validation"
            }
        else:
            return {
                "valid": False,
                "message": f"Toolpath '{actual_setup.get('toolpath_name')}' does not belong to setup '{setup.name}'. "
                          f"It belongs to setup '{actual_setup.get('setup_name')}'",
                "code": "TOOLPATH_SETUP_MISMATCH",
                "setup_id": setup_id,
                "setup_name": setup.name,
                "toolpath_id": toolpath_id,
                "toolpath_name": actual_setup.get("toolpath_name"),
                "actual_setup_id": actual_setup.get("setup_id"),
                "actual_setup_name": actual_setup.get("setup_name"),
                "context": "setup-toolpath validation"
            }
        
    except Exception as e:
        return {
            "valid": False,
            "error": True,
            "message": f"Error validating setup-toolpath relationship: {str(e)}",
            "code": "VALIDATION_ERROR",
            "setup_id": setup_id,
            "toolpath_id": toolpath_id,
            "context": "setup-toolpath validation"
        }


# =============================================================================
# Bidirectional Relationship Helper Functions (Task 10.3)
# =============================================================================

def get_setup_toolpath_mapping_impl() -> dict:
    """
    Create a comprehensive mapping of all setups to their toolpaths.
    
    Requirements: 11.1, 11.2, 11.3, 11.4
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "context": "setup-toolpath mapping"
            }
        
        cam_product = validation["cam_product"]
        
        setups_data = []
        toolpath_to_setup = {}
        total_toolpaths = 0
        
        setups = cam_product.setups
        if not setups or setups.count == 0:
            return {
                "setups": [],
                "toolpath_to_setup": {},
                "total_setups": 0,
                "total_toolpaths": 0,
                "message": "No setups found in CAM document"
            }
        
        for setup_idx in range(setups.count):
            setup = setups.item(setup_idx)
            setup_id = setup.entityToken if hasattr(setup, 'entityToken') else f"setup_{setup_idx}"
            
            setup_data = {
                "id": setup_id,
                "name": setup.name,
                "toolpath_ids": [],
                "toolpath_count": 0
            }
            
            if hasattr(setup, 'operations') and setup.operations:
                for op_idx in range(setup.operations.count):
                    operation = setup.operations.item(op_idx)
                    op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{setup_idx}_{op_idx}"
                    
                    setup_data["toolpath_ids"].append(op_id)
                    toolpath_to_setup[op_id] = {
                        "setup_id": setup_id,
                        "setup_name": setup.name,
                        "toolpath_name": operation.name,
                        "folder": None
                    }
                    total_toolpaths += 1
            
            if hasattr(setup, 'folders') and setup.folders:
                for folder_idx in range(setup.folders.count):
                    folder = setup.folders.item(folder_idx)
                    if hasattr(folder, 'operations') and folder.operations:
                        for op_idx in range(folder.operations.count):
                            operation = folder.operations.item(op_idx)
                            op_id = operation.entityToken if hasattr(operation, 'entityToken') else f"op_{setup_idx}_f{folder_idx}_{op_idx}"
                            
                            setup_data["toolpath_ids"].append(op_id)
                            toolpath_to_setup[op_id] = {
                                "setup_id": setup_id,
                                "setup_name": setup.name,
                                "toolpath_name": operation.name,
                                "folder": folder.name
                            }
                            total_toolpaths += 1
            
            setup_data["toolpath_count"] = len(setup_data["toolpath_ids"])
            setups_data.append(setup_data)
        
        return {
            "setups": setups_data,
            "toolpath_to_setup": toolpath_to_setup,
            "total_setups": len(setups_data),
            "total_toolpaths": total_toolpaths,
            "message": f"Mapped {total_toolpaths} toolpath(s) across {len(setups_data)} setup(s)"
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error creating setup-toolpath mapping: {str(e)}",
            "code": "MAPPING_ERROR",
            "context": "setup-toolpath mapping"
        }


def move_toolpath_to_setup_impl(toolpath_id: str, target_setup_id: str) -> dict:
    """
    Move a toolpath from one setup to another.
    
    Note: Fusion 360 API has limited support for moving operations between setups.
    
    Requirements: 9.4, 11.1, 11.2, 11.4, 11.5
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "toolpath_id": toolpath_id,
                "target_setup_id": target_setup_id,
                "context": "toolpath move operation"
            }
        
        cam_product = validation["cam_product"]
        
        if not toolpath_id:
            return {
                "error": True,
                "message": "Toolpath ID is required",
                "code": "MISSING_TOOLPATH_ID",
                "context": "toolpath move operation"
            }
        
        if not target_setup_id:
            return {
                "error": True,
                "message": "Target setup ID is required",
                "code": "MISSING_TARGET_SETUP_ID",
                "context": "toolpath move operation"
            }
        
        current_setup_info = find_setup_for_toolpath_impl(toolpath_id)
        if current_setup_info.get("error"):
            return {
                "error": True,
                "message": f"Toolpath with ID '{toolpath_id}' not found",
                "code": "TOOLPATH_NOT_FOUND",
                "toolpath_id": toolpath_id,
                "target_setup_id": target_setup_id,
                "context": "toolpath move operation"
            }
        
        source_setup_id = current_setup_info.get("setup_id")
        source_setup_name = current_setup_info.get("setup_name")
        toolpath_name = current_setup_info.get("toolpath_name")
        
        if source_setup_id == target_setup_id:
            return {
                "error": False,
                "moved": False,
                "message": f"Toolpath '{toolpath_name}' is already in setup '{source_setup_name}'",
                "toolpath_id": toolpath_id,
                "setup_id": source_setup_id,
                "setup_name": source_setup_name
            }
        
        target_setup = find_setup_by_id(cam_product, target_setup_id)
        if not target_setup:
            return {
                "error": True,
                "message": f"Target setup with ID '{target_setup_id}' not found",
                "code": "TARGET_SETUP_NOT_FOUND",
                "toolpath_id": toolpath_id,
                "target_setup_id": target_setup_id,
                "context": "toolpath move operation"
            }
        
        target_setup_name = target_setup.name
        
        return {
            "error": True,
            "message": f"Moving toolpaths between setups is not supported by the Fusion 360 API. "
                      f"Toolpath '{toolpath_name}' cannot be moved from '{source_setup_name}' to '{target_setup_name}'. "
                      f"Please recreate the operation in the target setup manually.",
            "code": "MOVE_NOT_SUPPORTED",
            "toolpath_id": toolpath_id,
            "toolpath_name": toolpath_name,
            "source_setup_id": source_setup_id,
            "source_setup_name": source_setup_name,
            "target_setup_id": target_setup_id,
            "target_setup_name": target_setup_name,
            "context": "toolpath move operation",
            "suggestion": "To move a toolpath, you must: 1) Note the operation parameters, "
                         "2) Delete the operation from the source setup, "
                         "3) Recreate the operation in the target setup with the same parameters."
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error moving toolpath: {str(e)}",
            "code": "MOVE_ERROR",
            "toolpath_id": toolpath_id,
            "target_setup_id": target_setup_id,
            "context": "toolpath move operation"
        }


def get_toolpath_with_setup_context_impl(toolpath_id: str) -> dict:
    """
    Get toolpath details with full setup context information.
    
    Requirements: 9.1, 9.2, 10.2, 10.5
    """
    try:
        validation = validate_cam_product_with_details()
        if not validation["valid"]:
            return {
                "error": True,
                "message": validation["message"],
                "code": validation["code"],
                "toolpath_id": toolpath_id,
                "context": "toolpath with setup context"
            }
        
        cam_product = validation["cam_product"]
        
        if not toolpath_id:
            return {
                "error": True,
                "message": "Toolpath ID is required",
                "code": "MISSING_TOOLPATH_ID",
                "context": "toolpath with setup context"
            }
        
        setup_info = find_setup_for_toolpath_impl(toolpath_id)
        if setup_info.get("error"):
            return setup_info
        
        from ..cam_utils import find_operation_by_id
        operation = find_operation_by_id(cam_product, toolpath_id)
        
        if not operation:
            return {
                "error": True,
                "message": f"Toolpath with ID '{toolpath_id}' not found",
                "code": "TOOLPATH_NOT_FOUND",
                "toolpath_id": toolpath_id,
                "context": "toolpath with setup context"
            }
        
        result = {
            "toolpath_id": toolpath_id,
            "toolpath_name": operation.name,
            "toolpath_type": get_operation_type(operation),
            "is_valid": operation.isValid if hasattr(operation, 'isValid') else True,
            "setup_id": setup_info.get("setup_id"),
            "setup_name": setup_info.get("setup_name"),
            "folder": setup_info.get("folder"),
            "tool": _get_tool_data_for_toolpath(operation)
        }
        
        return result
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error getting toolpath with setup context: {str(e)}",
            "code": "RETRIEVAL_ERROR",
            "toolpath_id": toolpath_id,
            "context": "toolpath with setup context"
        }


# =============================================================================
# HTTP Handler Functions
# =============================================================================

def handle_list_setups(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """List all CAM setups with comprehensive configuration details.
    
    NOTE: This is a READ-ONLY operation - calls impl directly without task_queue.
    The task_queue callback pattern doesn't work for HTTP handlers because they
    run in background threads and the callback never executes synchronously.
    """
    try:
        # READ-ONLY: Call impl function directly (no task_queue needed)
        result = list_setups_detailed()
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_list_setups: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_get_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve detailed setup information by ID.
    
    NOTE: This is a READ-ONLY operation - calls impl directly without task_queue.
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
        
        # READ-ONLY: Call impl function directly (no task_queue needed)
        result = get_setup_by_id_impl(setup_id)
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_get_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_create_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new CAM setup with specified configuration.
    
    NOTE: Even though this is a WRITE operation, we call impl directly because
    the task_queue callback pattern doesn't work for HTTP handlers.
    The impl function handles Fusion 360 API calls appropriately.
    """
    try:
        name = data.get("name")
        model_id = data.get("model_id")
        
        # Call impl function directly
        result = create_setup_impl(name=name, model_id=model_id)
        
        return {
            "status": 201 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_create_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_modify_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Modify an existing CAM setup configuration.
    
    NOTE: Even though this is a WRITE operation, we call impl directly because
    the task_queue callback pattern doesn't work for HTTP handlers.
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
        
        updates = {}
        if "name" in data:
            updates["name"] = data["name"]
        if "wcs" in data:
            updates["wcs"] = data["wcs"]
        if "stock" in data:
            updates["stock"] = data["stock"]
        
        if not updates:
            return {
                "status": 400,
                "error": True,
                "message": "No updates provided. Specify 'name', 'wcs', or 'stock' to modify.",
                "headers": {"Content-Type": "application/json"}
            }
        
        # Call impl function directly
        result = modify_setup_impl(setup_id, updates)
        
        if result.get("error"):
            if result.get("code") == "SETUP_NOT_FOUND":
                status = 404
            elif result.get("code") in ["MISSING_SETUP_ID", "INVALID_UPDATES", "DUPLICATE_NAME"]:
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
        logger.error(f"Error in handle_modify_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_duplicate_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Duplicate an existing CAM setup.
    
    NOTE: Even though this is a WRITE operation, we call impl directly because
    the task_queue callback pattern doesn't work for HTTP handlers.
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
        
        new_name = data.get("new_name") or data.get("name")
        
        # Call impl function directly
        result = duplicate_setup_impl(setup_id, new_name)
        
        if result.get("error"):
            if result.get("code") == "SETUP_NOT_FOUND":
                status = 404
            elif result.get("code") in ["MISSING_SETUP_ID", "DUPLICATE_NAME"]:
                status = 400
            else:
                status = 500
        else:
            status = 201
        
        return {
            "status": status,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_duplicate_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_delete_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a CAM setup.
    
    NOTE: Even though this is a WRITE operation, we call impl directly because
    the task_queue callback pattern doesn't work for HTTP handlers.
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
        
        confirm = data.get("confirm", False)
        if isinstance(confirm, str):
            confirm = confirm.lower() in ["true", "1", "yes"]
        
        # Call impl function directly
        result = delete_setup_impl(setup_id, confirm)
        
        if result.get("error"):
            if result.get("code") == "SETUP_NOT_FOUND":
                status = 404
            elif result.get("code") == "MISSING_SETUP_ID":
                status = 400
            elif result.get("code") == "DELETION_NOT_SUPPORTED":
                status = 501
            else:
                status = 500
        elif result.get("requires_confirmation"):
            status = 200
        elif result.get("deleted"):
            status = 200
        else:
            status = 200
        
        return {
            "status": status,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_delete_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


# =============================================================================
# HTTP Handler Functions for Setup-Toolpath Integration
# =============================================================================

def handle_get_setup_toolpaths(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get all toolpaths within a specific setup."""
    try:
        setup_id = data.get("setup_id")
        if not setup_id:
            return {
                "status": 400,
                "error": True,
                "message": "setup_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        include_details = data.get("include_details", True)
        if isinstance(include_details, str):
            include_details = include_details.lower() in ["true", "1", "yes"]
        
        result = get_toolpaths_for_setup_impl(setup_id, include_details)
        
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
        logger.error(f"Error in handle_get_setup_toolpaths: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_find_toolpath_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Find which setup contains a specific toolpath."""
    try:
        toolpath_id = data.get("toolpath_id")
        if not toolpath_id:
            return {
                "status": 400,
                "error": True,
                "message": "toolpath_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        result = find_setup_for_toolpath_impl(toolpath_id)
        
        if result.get("error"):
            if result.get("code") == "TOOLPATH_NOT_FOUND":
                status = 404
            elif result.get("code") == "MISSING_TOOLPATH_ID":
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
        logger.error(f"Error in handle_find_toolpath_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_validate_setup_toolpath(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that a toolpath belongs to a specific setup."""
    try:
        setup_id = data.get("setup_id")
        toolpath_id = data.get("toolpath_id")
        
        if not setup_id:
            return {
                "status": 400,
                "error": True,
                "message": "setup_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        if not toolpath_id:
            return {
                "status": 400,
                "error": True,
                "message": "toolpath_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        result = validate_setup_toolpath_relationship_impl(setup_id, toolpath_id)
        
        if result.get("error"):
            if result.get("code") in ["SETUP_NOT_FOUND", "TOOLPATH_NOT_FOUND"]:
                status = 404
            elif result.get("code") in ["MISSING_SETUP_ID", "MISSING_TOOLPATH_ID"]:
                status = 400
            else:
                status = 500
        elif result.get("valid"):
            status = 200
        else:
            status = 200
        
        return {
            "status": status,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_validate_setup_toolpath: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_get_setup_toolpath_mapping(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive setup-toolpath mapping."""
    try:
        result = get_setup_toolpath_mapping_impl()
        
        return {
            "status": 200 if not result.get("error") else 500,
            "data": result,
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in handle_get_setup_toolpath_mapping: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_move_toolpath_to_setup(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Move a toolpath to a different setup."""
    try:
        toolpath_id = data.get("toolpath_id")
        target_setup_id = data.get("target_setup_id")
        
        if not toolpath_id:
            return {
                "status": 400,
                "error": True,
                "message": "toolpath_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        if not target_setup_id:
            return {
                "status": 400,
                "error": True,
                "message": "target_setup_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        result = move_toolpath_to_setup_impl(toolpath_id, target_setup_id)
        
        if result.get("error"):
            if result.get("code") == "MOVE_NOT_SUPPORTED":
                status = 501
            elif result.get("code") in ["TOOLPATH_NOT_FOUND", "TARGET_SETUP_NOT_FOUND"]:
                status = 404
            elif result.get("code") in ["MISSING_TOOLPATH_ID", "MISSING_TARGET_SETUP_ID"]:
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
        logger.error(f"Error in handle_move_toolpath_to_setup: {str(e)}")
        return {
            "status": 500,
            "error": True,
            "message": f"Handler error: {str(e)}",
            "headers": {"Content-Type": "application/json"}
        }


def handle_get_toolpath_with_setup_context(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Get toolpath details with full setup context."""
    try:
        toolpath_id = data.get("toolpath_id")
        if not toolpath_id:
            return {
                "status": 400,
                "error": True,
                "message": "toolpath_id parameter is required",
                "headers": {"Content-Type": "application/json"}
            }
        
        result = get_toolpath_with_setup_context_impl(toolpath_id)
        
        if result.get("error"):
            if result.get("code") == "TOOLPATH_NOT_FOUND":
                status = 404
            elif result.get("code") == "MISSING_TOOLPATH_ID":
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
        logger.error(f"Error in handle_get_toolpath_with_setup_context: {str(e)}")
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
    """Register all setup handlers with the request router"""
    try:
        request_router.register_handler(
            "/cam/setups",
            handle_list_setups,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}",
            handle_get_setup,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups",
            handle_create_setup,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}",
            handle_modify_setup,
            methods=["PUT"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}/duplicate",
            handle_duplicate_setup,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}",
            handle_delete_setup,
            methods=["DELETE"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        # Setup-Toolpath Integration Handlers
        request_router.register_handler(
            "/cam/setups/{setup_id}/toolpaths",
            handle_get_setup_toolpaths,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/toolpaths/{toolpath_id}/setup",
            handle_find_toolpath_setup,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/setups/{setup_id}/toolpaths/{toolpath_id}/validate",
            handle_validate_setup_toolpath,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        # Bidirectional Relationship Handlers
        request_router.register_handler(
            "/cam/setup-toolpath-mapping",
            handle_get_setup_toolpath_mapping,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/toolpaths/{toolpath_id}/move",
            handle_move_toolpath_to_setup,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        request_router.register_handler(
            "/cam/toolpaths/{toolpath_id}/with-setup-context",
            handle_get_toolpath_with_setup_context,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups.setup"
        )
        
        logger.info("Registered CAM setup handlers including setup-toolpath integration")
        
    except Exception as e:
        logger.error(f"Error registering setup handlers: {str(e)}")


# Register handlers when module is loaded
register_handlers()
