"""
CAD Modeling Tools

This module contains tools for 3D modeling operations:
- extrude: Extrude sketches into 3D
- extrude_thin: Create thin-walled extrusions
- cut_extrude: Cut extrude operations
- revolve: Revolve sketches around axis
- loft: Loft between multiple sketches
- sweep: Sweep profile along path
- boolean_operation: Boolean operations between bodies
"""

import logging
import requests
from mcp.server.fastmcp import FastMCP
from core.config import get_endpoints, get_timeout
from core import interceptor

# Get the MCP instance from the main server
# This will be injected by the module loader

def register_tools(mcp_instance: FastMCP):
    """Register modeling tools with the MCP server."""
    # Register all tools in this module
    mcp_instance.tool()(extrude)
    mcp_instance.tool()(extrude_thin)
    mcp_instance.tool()(cut_extrude)
    mcp_instance.tool()(revolve)
    mcp_instance.tool()(loft)
    mcp_instance.tool()(sweep)
    mcp_instance.tool()(boolean_operation)
    mcp_instance.tool()(draw_2d_rectangle)
    mcp_instance.tool()(draw_text)

def extrude(value: float,angle:float):
    """Extrudiert die letzte Skizze um einen angegebenen Wert.
    Du kannst auch einen Winkel angeben
    
    """
    try:
        endpoint = get_endpoints("cad")["extrude"]
        data = {
            "value": value,
            "taperangle": angle
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Extrude failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to extrude: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def extrude_thin(thickness :float, distance : float):
    """
    Du kannst die Dicke der Wand als Float übergeben
    Du kannst schöne Hohlkörper damit erstellen
    :param thickness: Die Dicke der Wand in mm
    """
    try:
        endpoint = get_endpoints("cad")["extrude_thin"]
        data = {
            "thickness": thickness,
            "distance": distance
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Extrude thin failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to extrude thin: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def cut_extrude(depth :float):
    """
    Du kannst die Tiefe des Schnitts als Float übergeben
    :param depth: Die Tiefe des Schnitts in mm
    depth muss negativ sein ganz wichtig!
    """
    try:
        endpoint = get_endpoints("cad")["cut_extrude"]
        data = {
            "depth": depth
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Cut extrude failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to cut extrude: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }
    
def revolve(angle : float):
    """
    Sobald du dieses tool aufrufst wird der nutzer gebeten in Fusion ein profil
    auszuwählen und dann eine Achse.
    Wir übergeben den Winkel als Float
    """
    try:
        endpoint = get_endpoints("cad")["revolve"]
        data = {
            "angle": angle
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Revolve failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to revolve: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def loft(sketchcount: int):
    """
    Du kannst eine Loft Funktion in Fusion 360 erstellen
    Du übergibst die Anzahl der Sketches die du für die Loft benutzt hast als Integer
    Die Sketches müssen in der richtigen Reihenfolge erstellt worden sein
    Also zuerst Sketch 1 dann Sketch 2 dann Sketch 3 usw.
    """
    try:
        endpoint = get_endpoints("cad")["loft"]
        data = {
            "sketchcount": sketchcount
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Loft failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to loft: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def sweep():
    """
    Benutzt den vorhrig erstellten spline und den davor erstellten krei,
    um eine sweep funktion auszuführen
    """
    try:
        endpoint = get_endpoints("cad")["sweep"]
        response = requests.post(endpoint, json={}, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Sweep failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to sweep: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def boolean_operation(operation: str):
    """
    Führe eine boolesche Operation auf dem letzten Körper aus.
    Du kannst die Operation als String übergeben.
    Mögliche Werte sind: "cut", "join", "intersect"
    Wichtig ist, dass du vorher zwei Körper erstellt hast,
    """
    try:
        endpoint = get_endpoints("cad")["boolean_operation"]
        data = {
            "operation": operation
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Boolean operation failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to perform boolean operation: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_2d_rectangle(x_1: float, y_1: float, z_1: float, x_2: float, y_2: float, z_2: float, plane: str):
    """
    Zeichne ein 2D-Rechteck in Fusion 360 für loft /Sweep etc.
    """
    try:
        endpoint = get_endpoints("cad")["draw_2d_rectangle"]
        data = {
            "x_1": x_1,
            "y_1": y_1,
            "z_1": z_1,
            "x_2": x_2,
            "y_2": y_2,
            "z_2": z_2,
            "plane": plane
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Draw 2D rectangle failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw 2D rectangle: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_text(text: str, plane: str, x_1: float, y_1: float, z_1: float, x_2: float, y_2: float, z_2: float, thickness: float,value: float):
    """
    Zeichne einen Text in Fusion 360 der ist ein Sketch also kannst dz  ann extruden
    Mit value kannst du angeben wie weit du den text extrudieren willst
    """
    try:
        endpoint = get_endpoints("cad")["draw_text"]
        data = {
            "text": text,
            "plane": plane,
            "x_1": x_1,
            "y_1": y_1,
            "z_1": z_1,
            "x_2": x_2,
            "y_2": y_2,
            "z_2": z_2,
            "thickness": thickness,
            "extrusion_value": value
        }
        response = requests.post(endpoint, json=data, timeout=get_timeout())
        return interceptor.intercept_response(endpoint, response, "POST")
    except requests.ConnectionError:
        return {
            "error": True,
            "message": "Cannot connect to Fusion 360. Ensure the add-in is running.",
            "code": "CONNECTION_ERROR"
        }
    except requests.Timeout:
        return {
            "error": True,
            "message": "Request to Fusion 360 timed out. The add-in may be busy.",
            "code": "TIMEOUT_ERROR"
        }
    except Exception as e:
        logging.error("Draw text failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw text: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }