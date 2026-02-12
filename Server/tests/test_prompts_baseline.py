#!/usr/bin/env python3
"""
Baseline tests for the current prompt system (before migration).

This test suite documents and validates the current behavior of the custom
prompt registry system. These tests serve as a baseline to ensure the
migration to fastmcp decorators maintains identical functionality.

Tests cover:
- Prompt registration and retrieval
- Prompt content and metadata
- Registry operations (list, get, validate)
- Integration with MCP server

Requirements validated: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import pytest
import sys
import os

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from prompts.registry import (
    PromptRegistry,
    PromptInfo,
    get_prompt_registry,
    register_prompt,
    get_prompt
)
from prompts import templates


class TestPromptRegistryBasics:
    """Test basic prompt registry functionality."""
    
    def test_registry_instance_creation(self):
        """Test that a PromptRegistry instance can be created."""
        registry = PromptRegistry()
        assert registry is not None
        assert isinstance(registry, PromptRegistry)
    
    def test_global_registry_exists(self):
        """Test that the global registry instance exists."""
        registry = get_prompt_registry()
        assert registry is not None
        assert isinstance(registry, PromptRegistry)
    
    def test_global_registry_is_singleton(self):
        """Test that get_prompt_registry returns the same instance."""
        registry1 = get_prompt_registry()
        registry2 = get_prompt_registry()
        assert registry1 is registry2


class TestPromptRegistration:
    """Test prompt registration functionality."""
    
    def test_register_simple_prompt(self):
        """Test registering a simple prompt."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test prompt content"
        
        result = registry.register_prompt(
            "test_prompt",
            test_prompt,
            "Test description"
        )
        
        assert result is True
        assert "test_prompt" in registry.list_prompts()
    
    def test_register_prompt_with_category(self):
        """Test registering a prompt with a category."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        result = registry.register_prompt(
            "test_prompt",
            test_prompt,
            "Test description",
            category="test_category"
        )
        
        assert result is True
        assert "test_category" in registry.get_categories()
        assert "test_prompt" in registry.list_prompts(category="test_category")
    
    def test_register_prompt_with_dependencies(self):
        """Test registering a prompt with dependencies."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        result = registry.register_prompt(
            "test_prompt",
            test_prompt,
            "Test description",
            dependencies=["tool1", "tool2"]
        )
        
        assert result is True
        prompt_info = registry.get_prompt_info("test_prompt")
        assert prompt_info.dependencies == ["tool1", "tool2"]
    
    def test_register_duplicate_prompt_overwrites(self):
        """Test that registering a duplicate prompt overwrites the original."""
        registry = PromptRegistry()
        
        def prompt_v1():
            return "Version 1"
        
        def prompt_v2():
            return "Version 2"
        
        registry.register_prompt("test_prompt", prompt_v1, "V1")
        registry.register_prompt("test_prompt", prompt_v2, "V2")
        
        content = registry.get_prompt("test_prompt")
        assert content == "Version 2"
    
    def test_register_non_callable_fails(self):
        """Test that registering a non-callable fails."""
        registry = PromptRegistry()
        
        result = registry.register_prompt(
            "test_prompt",
            "not a function",
            "Test description"
        )
        
        assert result is False
        assert "test_prompt" not in registry.list_prompts()
    
    def test_register_non_string_return_fails(self):
        """Test that registering a function that doesn't return string fails."""
        registry = PromptRegistry()
        
        def bad_prompt():
            return 123  # Not a string
        
        result = registry.register_prompt(
            "test_prompt",
            bad_prompt,
            "Test description"
        )
        
        assert result is False
        assert "test_prompt" not in registry.list_prompts()


class TestPromptRetrieval:
    """Test prompt retrieval functionality."""
    
    def test_get_existing_prompt(self):
        """Test retrieving an existing prompt."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        registry.register_prompt("test_prompt", test_prompt, "Test")
        content = registry.get_prompt("test_prompt")
        
        assert content == "Test content"
    
    def test_get_nonexistent_prompt_returns_none(self):
        """Test that getting a non-existent prompt returns None."""
        registry = PromptRegistry()
        content = registry.get_prompt("nonexistent")
        
        assert content is None
    
    def test_get_prompt_info(self):
        """Test retrieving prompt information."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        registry.register_prompt(
            "test_prompt",
            test_prompt,
            "Test description",
            category="test_category",
            dependencies=["tool1"]
        )
        
        info = registry.get_prompt_info("test_prompt")
        
        assert info is not None
        assert info.name == "test_prompt"
        assert info.description == "Test description"
        assert info.category == "test_category"
        assert info.dependencies == ["tool1"]
        assert callable(info.function)
    
    def test_get_prompt_info_nonexistent_returns_none(self):
        """Test that getting info for non-existent prompt returns None."""
        registry = PromptRegistry()
        info = registry.get_prompt_info("nonexistent")
        
        assert info is None


class TestPromptListing:
    """Test prompt listing functionality."""
    
    def test_list_all_prompts(self):
        """Test listing all prompts."""
        registry = PromptRegistry()
        
        def prompt1():
            return "Content 1"
        
        def prompt2():
            return "Content 2"
        
        registry.register_prompt("prompt1", prompt1, "Desc 1")
        registry.register_prompt("prompt2", prompt2, "Desc 2")
        
        prompts = registry.list_prompts()
        
        assert len(prompts) == 2
        assert "prompt1" in prompts
        assert "prompt2" in prompts
    
    def test_list_prompts_by_category(self):
        """Test listing prompts filtered by category."""
        registry = PromptRegistry()
        
        def prompt1():
            return "Content 1"
        
        def prompt2():
            return "Content 2"
        
        registry.register_prompt("prompt1", prompt1, "Desc 1", category="cat1")
        registry.register_prompt("prompt2", prompt2, "Desc 2", category="cat2")
        
        cat1_prompts = registry.list_prompts(category="cat1")
        
        assert len(cat1_prompts) == 1
        assert "prompt1" in cat1_prompts
        assert "prompt2" not in cat1_prompts
    
    def test_list_prompts_empty_category(self):
        """Test listing prompts for non-existent category returns empty list."""
        registry = PromptRegistry()
        prompts = registry.list_prompts(category="nonexistent")
        
        assert prompts == []
    
    def test_get_categories(self):
        """Test getting all categories."""
        registry = PromptRegistry()
        
        def prompt1():
            return "Content 1"
        
        def prompt2():
            return "Content 2"
        
        registry.register_prompt("prompt1", prompt1, "Desc 1", category="cat1")
        registry.register_prompt("prompt2", prompt2, "Desc 2", category="cat2")
        
        categories = registry.get_categories()
        
        assert len(categories) == 2
        assert "cat1" in categories
        assert "cat2" in categories


class TestPromptUnregistration:
    """Test prompt unregistration functionality."""
    
    def test_unregister_existing_prompt(self):
        """Test unregistering an existing prompt."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        registry.register_prompt("test_prompt", test_prompt, "Test")
        result = registry.unregister_prompt("test_prompt")
        
        assert result is True
        assert "test_prompt" not in registry.list_prompts()
    
    def test_unregister_nonexistent_prompt(self):
        """Test unregistering a non-existent prompt returns False."""
        registry = PromptRegistry()
        result = registry.unregister_prompt("nonexistent")
        
        assert result is False
    
    def test_unregister_removes_from_category(self):
        """Test that unregistering removes prompt from category index."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        registry.register_prompt("test_prompt", test_prompt, "Test", category="test_cat")
        registry.unregister_prompt("test_prompt")
        
        cat_prompts = registry.list_prompts(category="test_cat")
        assert "test_prompt" not in cat_prompts


class TestPromptValidation:
    """Test prompt validation functionality."""
    
    def test_validate_dependencies_no_missing(self):
        """Test validation when all dependencies exist."""
        registry = PromptRegistry()
        
        def prompt1():
            return "Content 1"
        
        def prompt2():
            return "Content 2"
        
        registry.register_prompt("prompt1", prompt1, "Desc 1")
        registry.register_prompt("prompt2", prompt2, "Desc 2", dependencies=["prompt1"])
        
        missing = registry.validate_dependencies()
        
        assert "prompt2" not in missing
    
    def test_validate_dependencies_with_missing(self):
        """Test validation when dependencies are missing."""
        registry = PromptRegistry()
        
        def test_prompt():
            return "Test content"
        
        registry.register_prompt(
            "test_prompt",
            test_prompt,
            "Test",
            dependencies=["missing_tool"]
        )
        
        missing = registry.validate_dependencies()
        
        assert "test_prompt" in missing
        assert "missing_tool" in missing["test_prompt"]


class TestPromptStatistics:
    """Test prompt statistics functionality."""
    
    def test_get_stats_empty_registry(self):
        """Test getting stats from empty registry."""
        registry = PromptRegistry()
        stats = registry.get_stats()
        
        assert stats["total_prompts"] == 0
        assert stats["categories"] == 0
        assert stats["prompts_by_category"] == {}
        assert stats["prompts_with_dependencies"] == 0
    
    def test_get_stats_with_prompts(self):
        """Test getting stats with registered prompts."""
        registry = PromptRegistry()
        
        def prompt1():
            return "Content 1"
        
        def prompt2():
            return "Content 2"
        
        registry.register_prompt("prompt1", prompt1, "Desc 1", category="cat1")
        registry.register_prompt("prompt2", prompt2, "Desc 2", category="cat1", dependencies=["tool1"])
        
        stats = registry.get_stats()
        
        assert stats["total_prompts"] == 2
        assert stats["categories"] == 1
        assert stats["prompts_by_category"]["cat1"] == 2
        assert stats["prompts_with_dependencies"] == 1


class TestGlobalRegistryFunctions:
    """Test global registry convenience functions."""
    
    def test_global_register_prompt(self):
        """Test the global register_prompt function."""
        # Note: This modifies the global registry, so we need to be careful
        # In a real scenario, we'd want to reset the registry after tests
        
        def test_prompt():
            return "Test content"
        
        result = register_prompt("test_global_prompt", test_prompt, "Test")
        
        assert result is True
        
        # Verify it's in the global registry
        registry = get_prompt_registry()
        assert "test_global_prompt" in registry.list_prompts()
        
        # Cleanup
        registry.unregister_prompt("test_global_prompt")
    
    def test_global_get_prompt(self):
        """Test the global get_prompt function."""
        def test_prompt():
            return "Test content"
        
        register_prompt("test_global_get", test_prompt, "Test")
        content = get_prompt("test_global_get")
        
        assert content == "Test content"
        
        # Cleanup
        registry = get_prompt_registry()
        registry.unregister_prompt("test_global_get")


class TestManufacturingPrompts:
    """Test the actual manufacturing prompts defined in templates.py."""
    
    def test_cam_setup_prompt_registered(self):
        """Test that cam_setup prompt is registered."""
        registry = get_prompt_registry()
        assert "cam_setup" in registry.list_prompts()
    
    def test_cam_setup_prompt_content(self):
        """Test cam_setup prompt returns expected content."""
        content = get_prompt("cam_setup")
        
        assert content is not None
        assert isinstance(content, str)
        assert "STEP 1: Create CAM Setup" in content
        assert "create_cam_setup" in content
        assert "list_cam_setups" in content
    
    def test_cam_setup_prompt_metadata(self):
        """Test cam_setup prompt has correct metadata."""
        registry = get_prompt_registry()
        info = registry.get_prompt_info("cam_setup")
        
        assert info is not None
        assert info.name == "cam_setup"
        assert info.category == "manufacturing"
        assert "create_cam_setup" in info.dependencies
        assert "list_cam_setups" in info.dependencies
    
    def test_toolpath_analysis_prompt_registered(self):
        """Test that toolpath_analysis prompt is registered."""
        registry = get_prompt_registry()
        assert "toolpath_analysis" in registry.list_prompts()
    
    def test_toolpath_analysis_prompt_content(self):
        """Test toolpath_analysis prompt returns expected content."""
        content = get_prompt("toolpath_analysis")
        
        assert content is not None
        assert isinstance(content, str)
        assert "STEP 1: List Available Toolpaths" in content
        assert "list_cam_toolpaths" in content
        assert "get_toolpath_details" in content
    
    def test_toolpath_analysis_prompt_metadata(self):
        """Test toolpath_analysis prompt has correct metadata."""
        registry = get_prompt_registry()
        info = registry.get_prompt_info("toolpath_analysis")
        
        assert info is not None
        assert info.name == "toolpath_analysis"
        assert info.category == "manufacturing"
        assert "list_cam_toolpaths" in info.dependencies
        assert "get_toolpath_details" in info.dependencies
    
    def test_tool_library_prompt_registered(self):
        """Test that tool_library prompt is registered."""
        registry = get_prompt_registry()
        assert "tool_library" in registry.list_prompts()
    
    def test_tool_library_prompt_content(self):
        """Test tool_library prompt returns expected content."""
        content = get_prompt("tool_library")
        
        assert content is not None
        assert isinstance(content, str)
        assert "STEP 1: List Tool Libraries" in content
        assert "list_tool_libraries" in content
        assert "list_library_tools" in content
    
    def test_tool_library_prompt_metadata(self):
        """Test tool_library prompt has correct metadata."""
        registry = get_prompt_registry()
        info = registry.get_prompt_info("tool_library")
        
        assert info is not None
        assert info.name == "tool_library"
        assert info.category == "manufacturing"
        assert "list_tool_libraries" in info.dependencies
        assert "list_library_tools" in info.dependencies
    
    def test_all_manufacturing_prompts_in_same_category(self):
        """Test that all manufacturing prompts are in the manufacturing category."""
        registry = get_prompt_registry()
        manufacturing_prompts = registry.list_prompts(category="manufacturing")
        
        assert "cam_setup" in manufacturing_prompts
        assert "toolpath_analysis" in manufacturing_prompts
        assert "tool_library" in manufacturing_prompts
    
    def test_manufacturing_prompts_count(self):
        """Test that exactly 3 manufacturing prompts are registered."""
        registry = get_prompt_registry()
        manufacturing_prompts = registry.list_prompts(category="manufacturing")
        
        assert len(manufacturing_prompts) == 3


class TestPromptContentPreservation:
    """Test that prompt content is preserved exactly (for migration validation)."""
    
    def test_cam_setup_exact_content(self):
        """Document exact cam_setup content for migration comparison."""
        content = get_prompt("cam_setup")
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
    
    def test_toolpath_analysis_exact_content(self):
        """Document exact toolpath_analysis content for migration comparison."""
        content = get_prompt("toolpath_analysis")
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
    
    def test_tool_library_exact_content(self):
        """Document exact tool_library content for migration comparison."""
        content = get_prompt("tool_library")
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


class TestPromptIdentifierStability:
    """Test that prompt identifiers are stable (for migration validation)."""
    
    def test_prompt_identifiers_are_strings(self):
        """Test that all prompt identifiers are strings."""
        registry = get_prompt_registry()
        prompts = registry.list_prompts()
        
        for prompt_name in prompts:
            assert isinstance(prompt_name, str)
    
    def test_expected_prompt_identifiers_exist(self):
        """Test that expected prompt identifiers exist."""
        registry = get_prompt_registry()
        prompts = registry.list_prompts()
        
        expected_identifiers = ["cam_setup", "toolpath_analysis", "tool_library"]
        
        for identifier in expected_identifiers:
            assert identifier in prompts, f"Expected identifier '{identifier}' not found"
    
    def test_prompt_identifiers_match_function_names(self):
        """Test that prompt identifiers match their function names."""
        # This documents the current behavior where identifiers are
        # explicitly set during registration, not derived from function names
        registry = get_prompt_registry()
        
        info = registry.get_prompt_info("cam_setup")
        assert info is not None
        # The function name is cam_setup_prompt, but identifier is cam_setup
        assert info.function.__name__ == "cam_setup_prompt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
