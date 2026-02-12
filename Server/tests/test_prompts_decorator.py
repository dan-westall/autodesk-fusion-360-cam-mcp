#!/usr/bin/env python3
"""
Tests for the decorator-based prompt system (after migration).

This test suite validates that the new fastmcp decorator-based prompt system
works correctly and maintains the same functionality as the old registry system.

Tests cover:
- Decorator usage and registration
- Prompt content preservation
- MCP identifier stability
- Prompt functionality

Requirements validated: 2.1, 2.2, 2.3, 2.4, 5.4, 6.1, 10.3, 10.5
"""

import pytest
import sys
import os
import inspect

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from prompts import templates


class TestDecoratorBasedPrompts:
    """Test the new decorator-based prompt system."""
    
    def test_prompts_module_imports(self):
        """Test that prompts module imports successfully."""
        assert templates is not None
        assert hasattr(templates, 'cam_setup')
        assert hasattr(templates, 'toolpath_analysis')
        assert hasattr(templates, 'tool_library')
    
    def test_prompt_functions_are_callable(self):
        """Test that all prompt functions are callable."""
        assert callable(templates.cam_setup)
        assert callable(templates.toolpath_analysis)
        assert callable(templates.tool_library)
    
    def test_prompt_functions_have_docstrings(self):
        """Test that all prompt functions have docstrings (Requirement 2.3, 8.2)."""
        assert templates.cam_setup.__doc__ is not None
        assert len(templates.cam_setup.__doc__.strip()) > 0
        
        assert templates.toolpath_analysis.__doc__ is not None
        assert len(templates.toolpath_analysis.__doc__.strip()) > 0
        
        assert templates.tool_library.__doc__ is not None
        assert len(templates.tool_library.__doc__.strip()) > 0
    
    def test_prompt_functions_return_strings(self):
        """Test that all prompt functions return strings (Requirement 2.4)."""
        cam_setup_result = templates.cam_setup()
        assert isinstance(cam_setup_result, str)
        assert len(cam_setup_result) > 0
        
        toolpath_result = templates.toolpath_analysis()
        assert isinstance(toolpath_result, str)
        assert len(toolpath_result) > 0
        
        tool_lib_result = templates.tool_library()
        assert isinstance(tool_lib_result, str)
        assert len(tool_lib_result) > 0
    
    def test_prompt_function_names_match_expected(self):
        """Test that function names match expected identifiers (Requirement 2.2)."""
        assert templates.cam_setup.__name__ == "cam_setup"
        assert templates.toolpath_analysis.__name__ == "toolpath_analysis"
        assert templates.tool_library.__name__ == "tool_library"


class TestPromptContentPreservation:
    """Test that prompt content is preserved exactly (Requirement 5.4)."""
    
    def test_cam_setup_content_preserved(self):
        """Test cam_setup prompt content is preserved."""
        content = templates.cam_setup()
        expected = """
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
        
        assert content == expected
    
    def test_toolpath_analysis_content_preserved(self):
        """Test toolpath_analysis prompt content is preserved."""
        content = templates.toolpath_analysis()
        expected = """
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
        
        assert content == expected
    
    def test_tool_library_content_preserved(self):
        """Test tool_library prompt content is preserved."""
        content = templates.tool_library()
        expected = """
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
        
        assert content == expected


class TestPromptDocstrings:
    """Test that prompt docstrings are descriptive and follow conventions."""
    
    def test_cam_setup_docstring_quality(self):
        """Test cam_setup has a quality docstring."""
        docstring = templates.cam_setup.__doc__
        
        # Should mention CAM setup
        assert "CAM setup" in docstring or "CAM Setup" in docstring
        
        # Should mention manufacturing
        assert "manufacturing" in docstring.lower()
        
        # Should be substantial (more than just a one-liner)
        assert len(docstring.strip()) > 50
    
    def test_toolpath_analysis_docstring_quality(self):
        """Test toolpath_analysis has a quality docstring."""
        docstring = templates.toolpath_analysis.__doc__
        
        # Should mention toolpath
        assert "toolpath" in docstring.lower()
        
        # Should mention analysis or optimization
        assert "analyz" in docstring.lower() or "optimiz" in docstring.lower()
        
        # Should be substantial
        assert len(docstring.strip()) > 50
    
    def test_tool_library_docstring_quality(self):
        """Test tool_library has a quality docstring."""
        docstring = templates.tool_library.__doc__
        
        # Should mention tools or library
        assert "tool" in docstring.lower() or "librar" in docstring.lower()
        
        # Should mention manufacturing or cutting
        assert "manufacturing" in docstring.lower() or "cutting" in docstring.lower()
        
        # Should be substantial
        assert len(docstring.strip()) > 50


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_old_function_names_exist(self):
        """Test that old function names still exist for backward compatibility."""
        assert hasattr(templates, 'cam_setup_prompt')
        assert hasattr(templates, 'toolpath_analysis_prompt')
        assert hasattr(templates, 'tool_library_prompt')
    
    def test_old_functions_are_callable(self):
        """Test that old function names are still callable."""
        assert callable(templates.cam_setup_prompt)
        assert callable(templates.toolpath_analysis_prompt)
        assert callable(templates.tool_library_prompt)
    
    def test_old_functions_return_same_content(self):
        """Test that old function names return the same content."""
        # cam_setup
        assert templates.cam_setup_prompt() == templates.cam_setup()
        
        # toolpath_analysis
        assert templates.toolpath_analysis_prompt() == templates.toolpath_analysis()
        
        # tool_library
        assert templates.tool_library_prompt() == templates.tool_library()


class TestPromptStructure:
    """Test the structure and format of prompts."""
    
    def test_prompts_have_step_structure(self):
        """Test that all prompts follow a STEP-based structure."""
        cam_content = templates.cam_setup()
        assert "STEP 1:" in cam_content
        assert "STEP 2:" in cam_content
        assert "STEP 3:" in cam_content
        
        toolpath_content = templates.toolpath_analysis()
        assert "STEP 1:" in toolpath_content
        assert "STEP 2:" in toolpath_content
        assert "STEP 3:" in toolpath_content
        
        tool_lib_content = templates.tool_library()
        assert "STEP 1:" in tool_lib_content
        assert "STEP 2:" in tool_lib_content
        assert "STEP 3:" in tool_lib_content
    
    def test_prompts_reference_tools(self):
        """Test that prompts reference specific MCP tools."""
        cam_content = templates.cam_setup()
        assert "create_cam_setup" in cam_content
        assert "list_cam_setups" in cam_content
        
        toolpath_content = templates.toolpath_analysis()
        assert "list_cam_toolpaths" in toolpath_content
        assert "get_toolpath_details" in toolpath_content
        
        tool_lib_content = templates.tool_library()
        assert "list_tool_libraries" in tool_lib_content
        assert "list_library_tools" in tool_lib_content


class TestNoRegistryReferences:
    """Test that no registry references remain in the code."""
    
    def test_no_registry_imports_in_templates(self):
        """Test that templates.py doesn't import registry."""
        with open(os.path.join(server_path, "prompts", "templates.py"), "r") as f:
            content = f.read()
        
        # Should not import from registry
        assert "from prompts.registry import" not in content
        assert "from .registry import" not in content
        assert "import prompts.registry" not in content
    
    def test_no_register_prompt_calls(self):
        """Test that templates.py doesn't call register_prompt."""
        with open(os.path.join(server_path, "prompts", "templates.py"), "r") as f:
            content = f.read()
        
        # Should not call register_prompt
        assert "register_prompt(" not in content
    
    def test_registry_file_does_not_exist(self):
        """Test that registry.py file has been deleted."""
        registry_path = os.path.join(server_path, "prompts", "registry.py")
        assert not os.path.exists(registry_path), "registry.py should be deleted"


class TestMCPDecoratorUsage:
    """Test that prompts use the @mcp.prompt() decorator."""
    
    def test_templates_imports_mcp(self):
        """Test that templates.py imports mcp from core.server."""
        with open(os.path.join(server_path, "prompts", "templates.py"), "r") as f:
            content = f.read()
        
        # Should import mcp
        assert "from core.server import mcp" in content
    
    def test_prompts_use_decorator_syntax(self):
        """Test that prompt functions use @mcp.prompt() decorator."""
        with open(os.path.join(server_path, "prompts", "templates.py"), "r") as f:
            content = f.read()
        
        # Should have @mcp.prompt() decorators
        assert "@mcp.prompt()" in content
        
        # Should have at least 3 decorators (one for each prompt)
        decorator_count = content.count("@mcp.prompt()")
        assert decorator_count >= 3, f"Expected at least 3 @mcp.prompt() decorators, found {decorator_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
