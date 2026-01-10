"""
CAD Sketching Tools

This module contains tools for 2D drawing operations:
- draw2Dcircle: Create 2D circles
- draw_lines: Create line segments
- draw_one_line: Create single line
- draw_arc: Create arc segments
- spline: Create spline curves
"""

import logging
import requests
from mcp.server.fastmcp import FastMCP
from core.config import get_endpoints, get_timeout
from core import interceptor

def register_tools(mcp_instance: FastMCP):
    """Register sketching tools with the MCP server."""
    # Register all tools in this module
    mcp_instance.tool()(draw2Dcircle)
    mcp_instance.tool()(draw_lines)
    mcp_instance.tool()(draw_one_line)
    mcp_instance.tool()(draw_arc)
    mcp_instance.tool()(spline)

def draw2Dcircle(radius: float, x: float, y: float, z: float, plane: str = "XY"):
    """
    Zeichne einen Kreis in Fusion 360
    Du kannst den Radius als Float übergeben
    Du kannst die Koordinaten als Float übergeben
    Du kannst die Ebene als String übergeben
    Beispiel: "XY", "YZ", "XZ"

    KRITISCH - Welche Koordinate für "nach oben":
    - XY-Ebene: z erhöhen = nach oben
    - YZ-Ebene: x erhöhen = nach oben  
    - XZ-Ebene: y erhöhen = nach oben

    Gib immer JSON SO:
    {
        "radius":5,
        "x":0,
        "y":0,
        "z":0,
        "plane":"XY"
    }
    """
    try:
        endpoint = get_endpoints("cad")["draw2Dcircle"]
        data = {
            "radius": radius,
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
        logging.error("Draw 2D circle failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw 2D circle: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_lines(points : list, plane : str):
    """
    Zeichne Linien in Fusion 360
    Du kannst die Punkte als Liste von Listen übergeben
    Beispiel: [[0,0,0],[5,0,0],[5,5,5],[0,5,5],[0,0,0]]
    Es ist essenziell, dass du die Z-Koordinate angibst, auch wenn sie 0 ist
    Wenn nicht explizit danach gefragt ist mache es so, dass die Linien nach oben zeigen
    Du kannst die Ebene als String übergeben
    Beispiel: "XY", "YZ", "XZ"
    """
    try:
        endpoint = get_endpoints("cad")["draw_lines"]
        data = {
            "points": points,
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
        logging.error("Draw lines failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw lines: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_one_line(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, plane: str="XY"):
    """
    Zeichne eine Linie in Fusion 360
    Du kannst die Koordinaten als Float übergeben
    Beispiel: x1 = 0.0, y1 = 0.0, z1 = 0.0, x2 = 10.0, y2 = 10.0, z2 = 10.0
    Du kannst die Ebene als String übergeben
    Beispiel: "XY", "YZ", "XZ"
    """
    try:
        endpoint = get_endpoints("cad")["draw_one_line"]
        data = {
            "x1": x1,
            "y1": y1,
            "z1": z1,
            "x2": x2,
            "y2": y2,
            "z2": z2,
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
        logging.error("Draw one line failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw line: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def draw_arc(point1 : list, point2 : list, point3 : list, plane : str):
    """
    Zeichne einen Bogen in Fusion 360
    Du kannst die Punkte als Liste von Listen übergeben
    Beispiel: point1 = [0,0,0], point2 = [5,5,5], point3 = [10,0,0]
    Du kannst die Ebene als String übergeben
    Es wird eine Linie von point1 zu point3 gezeichnet die durch point2 geht also musst du nicht extra eine Linie zeichnen
    Beispiel: "XY", "YZ", "XZ"
    """
    try:
        endpoint = get_endpoints("cad")["arc"]
        data = {
            "point1": point1,
            "point2": point2,
            "point3": point3,
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
        logging.error("Draw arc failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to draw arc: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }

def spline(points: list, plane: str):
    """
    Zeichne eine Spline Kurve in Fusion 360
    Du kannst die Punkte als Liste von Listen übergeben
    Beispiel: [[0,0,0],[5,0,0],[5,5,5],[0,5,5],[0,0,0]]
    Es ist essenziell, dass du die Z-Koordinate angibst, auch wenn sie 0 ist
    Wenn nicht explizit danach gefragt ist mache es so, dass die Linien nach oben zeigen
    Du kannst die Ebene als String übergeben
    Es ist essenziell, dass die linien die gleiche ebene haben wie das profil was du sweepen willst
    """
    try:
        endpoint = get_endpoints("cad")["spline"]
        data = {
            "points": points,
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
        logging.error("Spline failed: %s", e)
        return {
            "error": True,
            "message": f"Failed to create spline: {str(e)}",
            "code": "UNKNOWN_ERROR"
        }