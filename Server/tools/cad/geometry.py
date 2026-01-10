"""
CAD Geometry Tools

This module contains tools for creating basic 3D shapes:
- draw_cylinder: Create cylindrical shapes
- draw_box: Create box/rectangular shapes  
- draw_sphere: Create spherical shapes
"""

import logging
import requests
from mcp.server.fastmcp import FastMCP
from core.config import get_endpoints, get_timeout
from core import interceptor

def register_tools(mcp_instance: FastMCP):
    """Register geometry tools with the MCP server."""
    # Register all tools in this module
    mcp_instance.tool()(draw_cylinder)
    mcp_instance.tool()(draw_box)
    mcp_instance.tool()(draw_sphere)

def draw_cylinder(radius: float , height: float , x: float, y: float, z: float , plane: str="XY"):
    """
    Zeichne einen Zylinder, du kannst du in der XY Ebende arbeiten
    Es gibt Standartwerte
    """
    try:
        endpoint = get_endpoints("cad")["draw_cylinder"]
        data = {
            "radius": radius,
            "height": height,
            "x": x,
            "y": y,
            "z": z,
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
        logging.error("Draw cylinder failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw cylinder: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_box(height_value:str, width_value:str, depth_value:str, x_value:float, y_value:float,z_value:float, plane:str="XY"):
    """
    Du kannst die Höhe, Breite und Tiefe der Box als Strings übergeben.
    Depth ist die Tiefe in z Richtung also wenn gesagt wird die Box soll flach sein,
    dann gibst du einen geringen Wert an!
    Du kannst die Koordinaten x, y,z der Box als Strings übergeben.Gib immer Koordinaten an,
    jene geben den Mittelpunkt der Box an.
    Depth ist die Tiefe in z Richtung
    Ganz wichtg 10 ist 100mm in Fusion 360
    Du kannst die Ebene als String übergeben
    Depth ist die eigentliche höhe in z Richtung
    Ein in der Luft schwebende Box machst du so: 
    {
    `plane`: `XY`,
    `x_value`: 5,
    `y_value`: 5,
    `z_value`: 20,
    `depth_value`: `2`,
    `width_value`: `5`,
    `height_value`: `3`
    }
    Das kannst du beliebig anpassen

    Beispiel: "XY", "YZ", "XZ"
    
    """
    try:
        endpoint = get_endpoints("cad")["draw_box"]
        data = {
            "height":height_value,
            "width": width_value,
            "depth": depth_value,
            "x" : x_value,
            "y" : y_value,
            "z" : z_value,
            "Plane": plane
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
        logging.error("Draw box failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw box: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_sphere(x: float, y: float, z: float, radius: float):
    """
    Zeichne eine Kugel in Fusion 360
    Du kannst die Koordinaten als Float übergeben
    Du kannst den Radius als Float übergeben
    Beispiel: "XY", "YZ", "XZ"
    Gib immer JSON SO:
    {
        "x":0,
        "y":0,
        "z":0,
        "radius":5
    }
    """
    try:
        endpoint = get_endpoints("cad")["draw_sphere"]
        data = {
            "x": x,
            "y": y,
            "z": z,
            "radius": radius
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
        logging.error("Draw sphere failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw sphere: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }