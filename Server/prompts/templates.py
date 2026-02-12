"""
Prompt template definitions for Fusion 360 MCP Server.

This module contains manufacturing-focused prompt templates for CAM operations,
organized and documented for better maintainability.

Prompts are registered automatically using the @mcp.prompt() decorator from
fastmcp 2.*. When this module is imported, all decorated functions are
automatically discovered and registered with the MCP server.

To add a new prompt:
1. Define a function that returns a string
2. Add the @mcp.prompt() decorator
3. Include a descriptive docstring
4. Import this module in MCP_Server.py

No manual registration is required - the decorator handles everything.
"""

# Import the mcp instance from core.server for decorator usage
from core.server import mcp


@mcp.prompt()
def cam_setup():
    """Create a basic CAM setup for manufacturing operations.
    
    This prompt guides users through creating a CAM setup in Fusion 360's
    MANUFACTURE workspace, including stock material and work coordinate system
    configuration. It provides a step-by-step workflow for initializing a new
    manufacturing setup.
    
    The prompt covers:
    - Creating a new CAM setup with appropriate naming
    - Selecting stock material and work coordinate system
    - Verifying the setup was created successfully
    - Preparing for subsequent toolpath operations
    
    Dependencies: create_cam_setup, list_cam_setups
    Category: manufacturing
    """
    return """
    STEP 1: Create CAM Setup
    - Use Tool: create_cam_setup
    - Setup Name: "Manufacturing Setup"
    - Select your stock material and work coordinate system
    
    STEP 2: Verify Setup
    - Use Tool: list_cam_setups
    - Check that your setup was created successfully
    
    STEP 3: Ready for Operations
    - Your CAM setup is now ready for toolpath operations
    - You can now add milling, drilling, or other machining operations
    """


# Keep old function name for backward compatibility during migration
def cam_setup_prompt():
    """
    CAM Setup prompt - Creates a basic CAM setup for manufacturing.
    
    Dependencies: create_cam_setup, list_cam_setups
    Category: manufacturing
    
    NOTE: This function is deprecated. Use cam_setup() instead.
    Kept for backward compatibility during migration to decorator-based system.
    """
    return cam_setup()


@mcp.prompt()
def toolpath_analysis():
    """Analyze existing toolpaths for manufacturing optimization.
    
    This prompt guides users through analyzing generated toolpaths in Fusion 360's
    MANUFACTURE workspace. It provides a systematic approach to reviewing machining
    parameters, tool information, and identifying optimization opportunities.
    
    The prompt covers:
    - Listing all available toolpaths in the current CAM setup
    - Retrieving detailed information for specific toolpaths
    - Reviewing machining parameters (feeds, speeds, cutting parameters)
    - Identifying optimization opportunities for efficiency and safety
    
    Dependencies: list_cam_toolpaths, get_toolpath_details
    Category: manufacturing
    """
    return """
    STEP 1: List Available Toolpaths
    - Use Tool: list_cam_toolpaths
    - Review all generated toolpaths in your CAM setup
    
    STEP 2: Analyze Specific Toolpath
    - Use Tool: get_toolpath_details
    - Select a toolpath ID from the list
    - Review machining parameters and tool information
    
    STEP 3: Optimization Review
    - Check feed rates, spindle speeds, and cutting parameters
    - Verify toolpath efficiency and safety margins
    """


# Keep old function name for backward compatibility during migration
def toolpath_analysis_prompt():
    """
    Toolpath Analysis prompt - Analyzes existing toolpaths for manufacturing.
    
    Dependencies: list_cam_toolpaths, get_toolpath_details
    Category: manufacturing
    
    NOTE: This function is deprecated. Use toolpath_analysis() instead.
    Kept for backward compatibility during migration to decorator-based system.
    """
    return toolpath_analysis()


@mcp.prompt()
def tool_library():
    """Manage cutting tools and tool libraries for manufacturing.
    
    This prompt guides users through browsing tool libraries and selecting
    appropriate cutting tools for machining operations in Fusion 360's
    MANUFACTURE workspace. It provides a structured workflow for tool
    discovery and selection.
    
    The prompt covers:
    - Listing all available tool libraries in the system
    - Browsing tools within specific libraries
    - Reviewing tool specifications (diameter, length, material, type)
    - Selecting appropriate tools for specific machining operations
    
    Dependencies: list_tool_libraries, list_library_tools
    Category: manufacturing
    """
    return """
    STEP 1: List Tool Libraries
    - Use Tool: list_tool_libraries
    - Review available tool libraries in your system
    
    STEP 2: Browse Tools
    - Use Tool: list_library_tools
    - Select a library to view available cutting tools
    
    STEP 3: Tool Selection
    - Review tool specifications (diameter, length, material)
    - Select appropriate tools for your machining operations
    """



# Keep old function name for backward compatibility during migration
def tool_library_prompt():
    """
    Tool Library prompt - Manages cutting tools for manufacturing.
    
    Dependencies: list_tool_libraries, list_library_tools
    Category: manufacturing
    
    NOTE: This function is deprecated. Use tool_library() instead.
    Kept for backward compatibility during migration to decorator-based system.
    """
    return tool_library()
