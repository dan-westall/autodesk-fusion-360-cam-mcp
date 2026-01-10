# FusionMCPBridge - Fusion 360 Add-In Entry Point
# Minimal add-in focused on lifecycle management and HTTP server coordination
# All business logic is delegated to modular handler modules

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import threading
import json

# Import existing MANUFACTURE and Tool Library modules
from .handlers import manufacture
from . import tool_library

# Import modular system components
from .core.integration import modular_system
from .core.server import server_manager
from .core.task_queue import task_queue, TaskPriority
from .core.loader import module_loader
from .core.router import request_router
from .core.error_handling import error_handler, ErrorCategory, ErrorSeverity, handle_fusion_api_error

# Set up module-specific logging
module_logger = error_handler.get_module_logger("fusion_bridge")

# Global state
ModelParameterSnapshot = []
app = None
ui = None
design = None
handlers = []
stopFlag = None
myCustomEvent = 'MCPTaskEvent'
customEvent = None


class TaskEventHandler(adsk.core.CustomEventHandler):
    """Custom Event Handler for processing tasks from the queue on the main UI thread"""
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        global ModelParameterSnapshot, design
        try:
            # Process tasks without design-specific parameter snapshots
            task_queue.process_tasks()
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "notify")
            module_logger.error(f"Task event handler error: {error_response.message}")


class TaskThread(threading.Thread):
    """Background thread that fires custom events for task processing"""
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(0.2):
            try:
                app.fireCustomEvent(myCustomEvent, json.dumps({}))
            except:
                break


def register_task_handlers():
    """Register all task handlers with the centralized task queue system"""
    global design, ui
    
    # Research handlers
    task_queue.register_task_handler('work_coordinate_system_api_research', _run_wcs_api_research)
    task_queue.register_task_handler('model_id_research', _run_model_id_research)


def _run_wcs_api_research():
    """Helper function for Work Coordinate System API research"""
    try:
        from .wcs_api_research import run_wcs_api_research
        run_wcs_api_research()
    except Exception as e:
        if ui:
            ui.messageBox(f'Work Coordinate System API research error: {str(e)}')


def _run_model_id_research():
    """Helper function for model ID research"""
    try:
        from .model_id_research import run_model_id_research
        run_model_id_research()
    except Exception as e:
        if ui:
            ui.messageBox(f'Model ID research error: {str(e)}')


def register_http_routes():
    """Register all HTTP routes with the modular router"""
    global ModelParameterSnapshot
    
    # System endpoints
    request_router.register_handler('/test_connection', handle_test_connection, ['GET', 'POST'], 'system', 'main')
    request_router.register_handler('/count_parameters', handle_count_parameters, ['GET'], 'system', 'main')
    request_router.register_handler('/list_parameters', handle_list_parameters, ['GET'], 'system', 'main')
    
    # MANUFACTURE workspace - CAM endpoints
    request_router.register_handler('/cam/setups', handle_cam_setups, ['GET'], 'manufacture', 'main')
    request_router.register_handler('/cam/toolpaths', handle_cam_toolpaths, ['GET'], 'manufacture', 'main')
    request_router.register_handler('/cam/toolpaths/heights', handle_cam_toolpaths_heights, ['GET'], 'manufacture', 'main')
    request_router.register_handler('/cam/tools', handle_cam_tools, ['GET'], 'manufacture', 'main')
    
    # Tool Library endpoints
    request_router.register_handler('/tool-libraries', handle_tool_libraries, ['GET'], 'manufacture', 'main')
    
    # Research endpoints
    request_router.register_handler('/research/work_coordinate_system_api', handle_wcs_research, ['GET'], 'research', 'main')
    request_router.register_handler('/research/model-id', handle_model_id_research, ['GET'], 'research', 'main')


# HTTP Route Handlers - System
def handle_test_connection(path, method, data):
    return {"status": 200, "data": {"message": "Verbindung erfolgreich"}}

def handle_count_parameters(path, method, data):
    return {"status": 200, "data": {"user_parameter_count": len(ModelParameterSnapshot)}}

def handle_list_parameters(path, method, data):
    return {"status": 200, "data": {"ModelParameter": ModelParameterSnapshot}}


# HTTP Route Handlers - MANUFACTURE Workspace (CAM)
def handle_cam_setups(path, method, data):
    try:
        result = manufacture.list_setups_detailed()
        if result.get('error'):
            error_code = result.get('code', 'UNKNOWN_ERROR')
            if error_code in ['NO_APPLICATION', 'NO_DOCUMENT', 'NO_PRODUCTS', 'NO_CAM_DATA', 'NO_CAM_SETUPS', 'CAM_NOT_INITIALIZED']:
                return {"status": 400, **result}
            elif error_code == 'CAM_ACCESS_ERROR':
                return {"status": 403, **result}
            return {"status": 500, **result}
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Unexpected error: {str(e)}", "code": "INTERNAL_ERROR"}

def handle_cam_toolpaths(path, method, data):
    try:
        cam_product = manufacture.get_cam_product()
        result = manufacture.list_all_toolpaths(cam_product)
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "INTERNAL_ERROR"}

def handle_cam_toolpaths_heights(path, method, data):
    try:
        result = manufacture.list_toolpaths_with_heights()
        if result.get('error'):
            error_code = result.get('code', 'UNKNOWN_ERROR')
            if error_code in ['NO_APPLICATION', 'NO_DOCUMENT', 'NO_PRODUCTS', 'NO_CAM_DATA', 'NO_CAM_SETUPS', 'CAM_NOT_INITIALIZED']:
                return {"status": 400, **result}
            elif error_code == 'CAM_ACCESS_ERROR':
                return {"status": 403, **result}
            return {"status": 500, **result}
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "INTERNAL_ERROR"}

def handle_cam_tools(path, method, data):
    try:
        cam_product = manufacture.get_cam_product()
        result = manufacture.list_all_tools(cam_product)
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "INTERNAL_ERROR"}


# HTTP Route Handlers - Tool Library
def handle_tool_libraries(path, method, data):
    try:
        result = tool_library.list_libraries()
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "INTERNAL_ERROR"}


# HTTP Route Handlers - Research
def handle_wcs_research(path, method, data):
    try:
        from .wcs_api_research import run_wcs_api_research
        result = run_wcs_api_research()
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "RESEARCH_ERROR"}

def handle_model_id_research(path, method, data):
    try:
        from .model_id_research import run_model_id_research
        result = run_model_id_research()
        return {"status": 200, "data": result}
    except Exception as e:
        return {"status": 500, "error": True, "message": f"Error: {str(e)}", "code": "RESEARCH_ERROR"}


def run(context):
    """Add-in entry point - Initialize and start the modular system"""
    global app, ui, design, handlers, stopFlag, customEvent, ModelParameterSnapshot
    
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if design is None:
            ui.messageBox("No active design open! Please open a design document.")
            return

        module_logger.info("Starting Fusion MCP Bridge")

        # Initialize modular system
        try:
            if modular_system.initialize_system():
                module_logger.info("Modular system initialized")
            else:
                module_logger.warning("Modular system initialization returned false")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Modular system error: {error_response.message}")

        # Load handler modules
        try:
            loaded_count = module_loader.load_all_modules()
            module_logger.info(f"Loaded {loaded_count} handler modules")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Module loading error: {error_response.message}")

        # Register task handlers
        try:
            register_task_handlers()
            module_logger.info("Task handlers registered")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Task handler registration error: {error_response.message}")

        # Register HTTP routes
        try:
            register_http_routes()
            module_logger.info("HTTP routes registered")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"HTTP route registration error: {error_response.message}")

        # Initial parameter snapshot - design functionality removed
        try:
            # Design parameter functionality has been removed as part of CAD removal
            ModelParameterSnapshot = []
            module_logger.info("Parameter snapshot initialized (design functionality removed)")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Parameter snapshot error: {error_response.message}")
            ModelParameterSnapshot = []

        # Register custom event for task processing
        try:
            customEvent = app.registerCustomEvent(myCustomEvent)
            onTaskEvent = TaskEventHandler()
            customEvent.add(onTaskEvent)
            handlers.append(onTaskEvent)
            module_logger.info("Custom event handler registered")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Custom event registration error: {error_response.message}")

        # Start task thread
        try:
            stopFlag = threading.Event()
            taskThread = TaskThread(stopFlag)
            taskThread.daemon = True
            taskThread.start()
            module_logger.info("Task thread started")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.error(f"Task thread start error: {error_response.message}")

        # Start HTTP server
        try:
            if server_manager.start_server():
                server_info = server_manager.get_server_info()
                module_logger.info(f"HTTP server started on port {server_info['port']}")
                ui.messageBox(f"Fusion MCP Bridge started!\n"
                             f"Port: {server_info['port']}\n"
                             f"Parameters: {len(ModelParameterSnapshot)}\n"
                             f"Routes: {server_info['routes_registered']}")
            else:
                module_logger.critical("Failed to start HTTP server")
                ui.messageBox("Failed to start HTTP server!")
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.critical(f"Server startup error: {error_response.message}")
            ui.messageBox(f"Server startup error: {error_response.message}")

    except Exception as e:
        try:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "run")
            module_logger.critical(f"Critical startup error: {error_response.message}")
            ui.messageBox(f'Add-in error:\n{error_response.message}\n\n{traceback.format_exc()}')
        except:
            pass


def stop(context):
    """Add-in shutdown - Clean up all resources"""
    global stopFlag, handlers, app, customEvent
    
    module_logger.info("Stopping Fusion MCP Bridge")
    
    # Stop modular system
    try:
        modular_system.stop_system()
        module_logger.info("Modular system stopped")
    except Exception as e:
        error_response = handle_fusion_api_error(e, "fusion_bridge", "stop")
        module_logger.error(f"Modular system stop error: {error_response.message}")
    
    # Stop HTTP server
    try:
        if server_manager.stop_server():
            module_logger.info("HTTP server stopped")
        else:
            module_logger.warning("HTTP server stop returned false")
    except Exception as e:
        error_response = handle_fusion_api_error(e, "fusion_bridge", "stop")
        module_logger.error(f"HTTP server stop error: {error_response.message}")
    
    # Stop task thread
    try:
        if stopFlag:
            stopFlag.set()
            module_logger.info("Task thread stop signal sent")
    except Exception as e:
        error_response = handle_fusion_api_error(e, "fusion_bridge", "stop")
        module_logger.error(f"Task thread stop error: {error_response.message}")

    # Clean up event handlers
    cleaned_handlers = 0
    for handler in handlers:
        try:
            if customEvent:
                customEvent.remove(handler)
                cleaned_handlers += 1
        except Exception as e:
            error_response = handle_fusion_api_error(e, "fusion_bridge", "stop")
            module_logger.warning(f"Handler cleanup error: {error_response.message}")
    
    handlers.clear()
    module_logger.info(f"Cleaned up {cleaned_handlers} event handlers")

    # Clear task queue
    try:
        cleared_tasks = task_queue.clear_queue()
        module_logger.info(f"Cleared {cleared_tasks} tasks from queue")
    except Exception as e:
        error_response = handle_fusion_api_error(e, "fusion_bridge", "stop")
        module_logger.error(f"Task queue clear error: {error_response.message}")
    
    # Log final statistics
    try:
        error_stats = error_handler.get_error_statistics()
        module_logger.info(f"Final stats: {error_stats.get('total_errors', 0)} total errors")
    except Exception as e:
        module_logger.error(f"Failed to get final error statistics: {str(e)}")
    
    module_logger.info("Fusion MCP Bridge stopped")

    try:
        app = adsk.core.Application.get()
        if app:
            ui = app.userInterface
            if ui:
                ui.messageBox("Fusion MCP Bridge stopped")
    except:
        pass
