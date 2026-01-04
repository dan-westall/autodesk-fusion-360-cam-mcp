# Design Modeling Handler
# Handles 3D operations (extrude, revolve, loft, sweep, boolean operations)

import json
from typing import Dict, Any

# Import centralized task queue
from ...core.task_queue import task_queue
from ...core.error_handling import error_handler_decorator, ErrorCategory, ErrorSeverity


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_extrude_last_sketch(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle extrusion of the last sketch
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing extrusion parameters
        
    Returns:
        Response dictionary
    """
    value = float(data.get('value', 1.0))
    taperangle = float(data.get('taperangle', 0.0))
    
    task_queue.queue_task('extrude_last_sketch', value, taperangle, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Letzter Sketch wird extrudiert"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_cut_extrude(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle cut extrusion operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing cut depth
        
    Returns:
        Response dictionary
    """
    depth = float(data.get('depth', 1.0))
    
    task_queue.queue_task('cut_extrude', depth, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Cut Extrude wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_extrude_thin(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle thin extrusion operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing thickness and distance
        
    Returns:
        Response dictionary
    """
    thickness = float(data.get('thickness', 0.5))
    distance = float(data.get('distance', 1.0))
    
    task_queue.queue_task('extrude_thin', thickness, distance, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Thin Extrude wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_revolve(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle revolve operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing revolve angle
        
    Returns:
        Response dictionary
    """
    angle = float(data.get('angle', 360))
    
    task_queue.queue_task('revolve_profile', angle, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Profil wird revolviert"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_loft(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle loft operation between sketches
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing sketch count
        
    Returns:
        Response dictionary
    """
    sketchcount = int(data.get('sketchcount', 2))
    
    task_queue.queue_task('loft', sketchcount, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Loft wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_sweep(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle sweep operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data (sweep uses last two sketches)
        
    Returns:
        Response dictionary
    """
    task_queue.queue_task('sweep', module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Sweep wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_boolean_operation(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle boolean operations (join, cut, intersect)
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing operation type
        
    Returns:
        Response dictionary
    """
    operation = data.get('operation', 'join')  # 'join', 'cut', 'intersect'
    
    task_queue.queue_task('boolean_operation', operation, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Boolean Operation wird ausgeführt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_shell_body(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle shell body operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing thickness and face index
        
    Returns:
        Response dictionary
    """
    thickness = float(data.get('thickness', 0.5))
    faceindex = int(data.get('faceindex', 0))
    
    task_queue.queue_task('shell_body', thickness, faceindex, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Shell body wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_move_body(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle body movement operation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing movement vector
        
    Returns:
        Response dictionary
    """
    x = float(data.get('x', 0))
    y = float(data.get('y', 0))
    z = float(data.get('z', 0))
    
    task_queue.queue_task('move_body', x, y, z, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Body wird verschoben"},
        "headers": {"Content-Type": "application/json"}
    }


@error_handler_decorator("design.modeling", ErrorCategory.REQUEST_HANDLING, ErrorSeverity.MEDIUM)
def handle_offsetplane(path: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle offset plane creation
    
    Args:
        path: Request path
        method: HTTP method
        data: Request data containing offset and plane
        
    Returns:
        Response dictionary
    """
    offset = float(data.get('offset', 0.0))
    plane = data.get('plane', 'XY')  # 'XY', 'XZ', 'YZ'
    
    task_queue.queue_task('offsetplane', offset, plane, module_context="design.modeling")
    return {
        "status": 200,
        "data": {"message": "Offset Plane wird erstellt"},
        "headers": {"Content-Type": "application/json"}
    }

# Handler registration - these will be automatically registered by the module loader
HANDLERS = [
    {
        "pattern": "/extrude_last_sketch",
        "handler": handle_extrude_last_sketch,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/cut_extrude",
        "handler": handle_cut_extrude,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/extrude_thin",
        "handler": handle_extrude_thin,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/revolve",
        "handler": handle_revolve,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/loft",
        "handler": handle_loft,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/sweep",
        "handler": handle_sweep,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/boolean_operation",
        "handler": handle_boolean_operation,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/shell_body",
        "handler": handle_shell_body,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/move_body",
        "handler": handle_move_body,
        "methods": ["POST"],
        "category": "design"
    },
    {
        "pattern": "/offsetplane",
        "handler": handle_offsetplane,
        "methods": ["POST"],
        "category": "design"
    }
]