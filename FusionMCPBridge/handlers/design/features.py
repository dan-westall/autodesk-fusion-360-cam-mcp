# Design Features Handler
# Handles features (fillet, holes, patterns, threading)

import json
from typing import Dict, Any

# Import centralized task queue
from ...core.task_queue import task_queue
from ...core.error_handling import error_handler_decorator, ErrorCategory, ErrorSeverity


@error_handler_decorator("design.features", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_fillet_edges(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle fillet edges operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing fillet radius
        
    Returns:
        Response dictionary
    """
    radius = float(data.get('radius', 0.3))
    
    task_queue.queue_task('fillet_edges', radius, module_context="design.features")
    return {
        "status": 200,
        "data": {"message": "Fillet edges started"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.features", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_holes(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle hole creation operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing hole parameters
        
    Returns:
        Response dictionary
    """
    points = data.get('points', [[0, 0]])
    width = float(data.get('width', 1.0))
    faceindex = int(data.get('faceindex', 0))
    distance = data.get('depth', None)
    if distance is not None:
        distance = float(distance)
    through = bool(data.get('through', False))
    
    task_queue.queue_task('holes', points, width, distance, faceindex, through, module_context="design.features")
    return {
        "status": 200,
        "data": {"message": "Loch wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.features", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_threaded(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle threaded feature creation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing thread parameters
        
    Returns:
        Response dictionary
    """
    inside = bool(data.get('inside', True))
    allsizes = int(data.get('allsizes', 30))
    
    task_queue.queue_task('threaded', inside, allsizes, module_context="design.features")
    return {
        "status": 200,
        "data": {"message": "Threaded Feature wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.features", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_circular_pattern(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle circular pattern creation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing pattern parameters
        
    Returns:
        Response dictionary
    """
    quantity_raw = data.get('quantity')
    if quantity_raw is None:
        return {
            "status": 400,
            "error": True,
            "message": "quantity parameter is required",
            "headers": {"Content-Type": "application/json"}
        }
    quantity = float(quantity_raw)
    axis = str(data.get('axis', "X"))
    plane = str(data.get('plane', 'XY'))  # 'XY', 'XZ', 'YZ'
    
    task_queue.queue_task('circular_pattern', quantity, axis, plane, module_context="design.features")
    return {
        "status": 200,
        "data": {"message": "Circular Pattern wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.features", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_rectangular_pattern(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle rectangular pattern creation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing pattern parameters
        
    Returns:
        Response dictionary
    """
    quantity_one = float(data.get('quantity_one', 2))
    distance_one = float(data.get('distance_one', 5))
    axis_one = str(data.get('axis_one', "X"))
    quantity_two = float(data.get('quantity_two', 2))
    distance_two = float(data.get('distance_two', 5))
    axis_two = str(data.get('axis_two', "Y"))
    plane = str(data.get('plane', 'XY'))  # 'XY', 'XZ', 'YZ'
    
    # Parameter order: axis_one, axis_two, quantity_one, quantity_two, distance_one, distance_two, plane
    task_queue.queue_task('rectangular_pattern', axis_one, axis_two, quantity_one, quantity_two, 
                          distance_one, distance_two, plane, module_context="design.features")
    return {
        "status": 200,
        "data": {"message": "Rectangular Pattern wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }

# Handler registration - these will be automatically registered by the module loader
HANDLERS = [
    {
        "pattern": "/fillet_edges",
        "handler": handle_fillet_edges,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/holes",
        "handler": handle_holes,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/threaded",
        "handler": handle_threaded,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/circular_pattern",
        "handler": handle_circular_pattern,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/rectangular_pattern",
        "handler": handle_rectangular_pattern,
        "methods": ["POST"],
        "category": "design"
    }
]