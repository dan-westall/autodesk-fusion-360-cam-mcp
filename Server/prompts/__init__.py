"""
Prompt management system for Fusion 360 MCP Server.

This module provides prompt templates for manufacturing operations using
the native fastmcp decorator-based system. Prompts are automatically
discovered and registered by fastmcp when this module is imported.

## Architecture

Prompts are defined in templates.py using the @mcp.prompt() decorator.
The decorator-based approach eliminates the need for manual registration
and custom registry systems, following fastmcp 2.* best practices.

When this module is imported, the decorators automatically register prompts
with fastmcp - no manual registration code is required.

## How It Works

1. Prompt functions are defined in templates.py
2. Each function is decorated with @mcp.prompt()
3. The function name becomes the prompt identifier (e.g., "cam_setup")
4. The docstring becomes the prompt description
5. The return value is the prompt content shown to users
6. Importing this module triggers automatic registration

## Adding New Prompts

To add a new prompt, simply define a decorated function in templates.py:

Example:
    @mcp.prompt()
    def my_new_prompt():
        '''Guide for creating custom manufacturing operations.
        
        This prompt helps users set up specialized CAM operations
        for unique manufacturing scenarios.
        '''
        return '''
        STEP 1: Analyze the part geometry
        - Identify critical features
        - Determine machining requirements
        
        STEP 2: Select appropriate tools
        - Choose tool type based on material
        - Verify tool availability in library
        
        STEP 3: Configure operation parameters
        - Set cutting speeds and feeds
        - Define toolpath strategy
        '''

The prompt will be automatically available to MCP clients as "my_new_prompt"
without any additional registration code.

## Migration Notes

This module was migrated from a custom registry-based system to the native
fastmcp decorator system. The migration eliminated ~200 lines of custom
registry code while maintaining identical functionality for MCP clients.

Key changes:
- Removed PromptRegistry class and manual registration
- Converted prompt functions to use @mcp.prompt() decorator
- Function names now serve as prompt identifiers
- Docstrings now serve as prompt descriptions
- Automatic discovery replaces manual registration

## Available Prompts

- cam_setup: Guide for creating CAM setups
- toolpath_analysis: Guide for analyzing toolpaths
- tool_library: Guide for managing tool libraries
"""

# Import templates module to trigger decorator registration
from . import templates

__all__ = ['templates']