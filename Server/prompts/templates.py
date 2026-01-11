"""
Prompt template definitions for Fusion 360 MCP Server.

This module contains manufacturing-focused prompt templates for CAM operations,
organized and documented for better maintainability.
"""

from .registry import register_prompt


def cam_setup_prompt():
    """
    CAM Setup prompt - Creates a basic CAM setup for manufacturing.
    
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


def toolpath_analysis_prompt():
    """
    Toolpath Analysis prompt - Analyzes existing toolpaths for manufacturing.
    
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


def tool_library_prompt():
    """
    Tool Library prompt - Manages cutting tools for manufacturing.
    
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


# Register all prompts with the registry
def register_all_prompts():
    """Register all prompt templates with the global registry."""
    
    # Register manufacturing prompts
    register_prompt(
        "cam_setup", 
        cam_setup_prompt,
        "Creates a basic CAM setup for manufacturing operations",
        "manufacturing",
        ["create_cam_setup", "list_cam_setups"]
    )
    
    register_prompt(
        "toolpath_analysis", 
        toolpath_analysis_prompt,
        "Analyzes existing toolpaths for manufacturing optimization",
        "manufacturing",
        ["list_cam_toolpaths", "get_toolpath_details"]
    )
    
    register_prompt(
        "tool_library", 
        tool_library_prompt,
        "Manages cutting tools and tool libraries for manufacturing",
        "manufacturing",
        ["list_tool_libraries", "list_library_tools"]
    )


# Auto-register prompts when module is imported
register_all_prompts()