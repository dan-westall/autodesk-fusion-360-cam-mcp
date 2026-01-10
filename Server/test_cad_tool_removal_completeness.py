#!/usr/bin/env python3
"""
Property-Based Test for CAD Tool Removal Completeness

This module contains property-based tests to validate that CAD tools have been
completely removed from the MCP server while preserving all other functionality.

Property 1: CAD tool removal completeness
*For any* MCP server instance after CAD removal, the server should only expose 
CAM tools, utility tools, and debug tools, with no design workspace tools 
available to AI assistants

Requirements: 1.1, 1.2, 1.3, 1.5
"""

import pytest
import os
import sys
from typing import Dict, List, Any, Set
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from pathlib import Path

# Add Server directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from core.loader import ModuleLoader, get_categories
from core.config import get_endpoints, get_categories as config_get_categories


class TestCADToolRemovalCompleteness:
    """Property-based tests for CAD tool removal completeness."""
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_cad_modules_discovered(self, _):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any module discovery operation, the system should not discover
        any CAD-related modules in the tools directory structure.
        
        This test verifies that the CAD tools directory has been completely removed
        and no CAD modules can be discovered by the module loader.
        """
        # Create module loader instance
        loader = ModuleLoader()
        
        # Discover all available modules
        discovered_modules = loader.discover_modules()
        
        # Property: No discovered modules should be from the 'cad' category
        cad_modules = [module for module in discovered_modules if '.cad.' in module]
        
        assert len(cad_modules) == 0, (
            f"CAD modules still discovered after removal: {cad_modules}"
        )
        
        # Property: Discovered modules should only be from allowed categories
        allowed_categories = {'cam', 'utility', 'debug'}
        discovered_categories = set()
        
        for module_path in discovered_modules:
            parts = module_path.split('.')
            if len(parts) >= 2:
                category = parts[1]  # tools.category.module
                discovered_categories.add(category)
        
        forbidden_categories = discovered_categories - allowed_categories
        assert len(forbidden_categories) == 0, (
            f"Forbidden categories discovered: {forbidden_categories}. "
            f"Only allowed: {allowed_categories}"
        )
        
        # Property: At least some CAM modules should be discovered (system not broken)
        cam_modules = [module for module in discovered_modules if '.cam.' in module]
        assert len(cam_modules) > 0, (
            "No CAM modules discovered - system may be broken"
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_cad_endpoints_in_configuration(self, _):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any configuration query, the system should not return any
        CAD-related endpoints in the configuration.
        
        This test verifies that all CAD endpoints have been removed from the
        server configuration.
        """
        # Property: 'cad' category should not exist in configuration
        all_categories = config_get_categories()
        assert 'cad' not in all_categories, (
            f"CAD category still exists in configuration: {all_categories}"
        )
        
        # Property: Only allowed categories should exist
        allowed_categories = {'cam', 'utility', 'debug'}
        forbidden_categories = set(all_categories) - allowed_categories
        assert len(forbidden_categories) == 0, (
            f"Forbidden categories in configuration: {forbidden_categories}. "
            f"Only allowed: {allowed_categories}"
        )
        
        # Property: Attempting to get CAD endpoints should return empty dict
        cad_endpoints = get_endpoints('cad')
        assert len(cad_endpoints) == 0, (
            f"CAD endpoints still accessible: {cad_endpoints}"
        )
        
        # Property: All endpoints should not contain CAD-related URLs
        all_endpoints = get_endpoints()  # Get all endpoints
        
        cad_related_urls = []
        cad_keywords = [
            'draw_cylinder', 'draw_box', 'draw_sphere',
            'draw_circle', 'draw_line', 'draw_arc', 'draw_spline',
            'extrude', 'revolve', 'loft', 'sweep',
            'fillet', 'shell', 'hole', 'thread',
            'pattern', 'boolean'
        ]
        
        for endpoint_name, url in all_endpoints.items():
            for keyword in cad_keywords:
                if keyword.lower() in endpoint_name.lower() or keyword.lower() in url.lower():
                    cad_related_urls.append((endpoint_name, url))
                    break
        
        assert len(cad_related_urls) == 0, (
            f"CAD-related endpoints still in configuration: {cad_related_urls}"
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cad_directory_physically_removed(self, _):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any file system check, the CAD tools directory should not
        exist in the tools directory structure.
        
        This test verifies that the CAD directory has been physically removed
        from the file system.
        """
        # Get the Server directory path
        server_dir = Path(__file__).parent
        tools_dir = server_dir / "tools"
        cad_dir = tools_dir / "cad"
        
        # Property: CAD directory should not exist
        assert not cad_dir.exists(), (
            f"CAD directory still exists at: {cad_dir}"
        )
        
        # Property: Tools directory should still exist (system not broken)
        assert tools_dir.exists(), (
            f"Tools directory missing - system may be broken: {tools_dir}"
        )
        
        # Property: Only allowed subdirectories should exist in tools
        allowed_subdirs = {'cam', 'utility', 'debug', '__pycache__'}
        
        if tools_dir.exists():
            actual_subdirs = set()
            for item in tools_dir.iterdir():
                if item.is_dir():
                    actual_subdirs.add(item.name)
            
            forbidden_subdirs = actual_subdirs - allowed_subdirs
            assert len(forbidden_subdirs) == 0, (
                f"Forbidden subdirectories in tools: {forbidden_subdirs}. "
                f"Only allowed: {allowed_subdirs - {'__pycache__'}}"
            )
            
            # Property: At least CAM directory should exist
            assert 'cam' in actual_subdirs, (
                f"CAM directory missing - system may be broken. Found: {actual_subdirs}"
            )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_module_loading_excludes_cad_tools(self, _):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any module loading operation, the system should not attempt
        to load any CAD tools and should only load CAM, utility, and debug tools.
        
        This test verifies that the module loading system correctly excludes
        CAD tools and only loads allowed tool categories.
        """
        # Create module loader and attempt to load all modules
        loader = ModuleLoader()
        
        # Property: Loading all modules should not include any CAD modules
        loaded_modules = loader.load_all_modules()
        
        cad_loaded_modules = []
        for module_path, module_info in loaded_modules.items():
            if '.cad.' in module_path or module_info.category == 'cad':
                cad_loaded_modules.append(module_path)
        
        assert len(cad_loaded_modules) == 0, (
            f"CAD modules were loaded: {cad_loaded_modules}"
        )
        
        # Property: Only allowed categories should be loaded
        allowed_categories = {'cam', 'utility', 'debug'}
        loaded_categories = set()
        
        for module_info in loaded_modules.values():
            if module_info.loaded:  # Only count successfully loaded modules
                loaded_categories.add(module_info.category)
        
        forbidden_categories = loaded_categories - allowed_categories
        assert len(forbidden_categories) == 0, (
            f"Forbidden categories loaded: {forbidden_categories}. "
            f"Only allowed: {allowed_categories}"
        )
        
        # Property: At least some CAM modules should be loaded (system functional)
        cam_modules_loaded = sum(
            1 for module_info in loaded_modules.values() 
            if module_info.loaded and module_info.category == 'cam'
        )
        assert cam_modules_loaded > 0, (
            "No CAM modules loaded - system may be broken"
        )
    
    @given(st.sampled_from(['cad', 'CAD', 'Cad', 'design', 'DESIGN', 'Design']))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cad_category_queries_return_empty(self, cad_category_variant):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any CAD-related category query (regardless of case), the system
        should return empty results, indicating complete removal of CAD functionality.
        
        This test verifies that various forms of CAD category queries return empty
        results after CAD removal.
        """
        # Property: CAD category queries should return empty endpoints
        cad_endpoints = get_endpoints(cad_category_variant)
        assert len(cad_endpoints) == 0, (
            f"CAD endpoints returned for category '{cad_category_variant}': {cad_endpoints}"
        )
        
        # Property: Module discovery for CAD category should return empty list
        loader = ModuleLoader()
        cad_modules = loader.discover_modules(cad_category_variant.lower())
        assert len(cad_modules) == 0, (
            f"CAD modules discovered for category '{cad_category_variant}': {cad_modules}"
        )
        
        # Property: Module loading for CAD category should return empty dict
        loaded_cad_modules = loader.load_category(cad_category_variant.lower())
        assert len(loaded_cad_modules) == 0, (
            f"CAD modules loaded for category '{cad_category_variant}': {loaded_cad_modules}"
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_system_health_after_cad_removal(self, _):
        """
        **Feature: cad-removal, Property 1: CAD tool removal completeness**
        
        Property: For any system health check after CAD removal, the system should
        report healthy status with only CAM, utility, and debug modules loaded.
        
        This test verifies that the system remains healthy and functional after
        CAD removal, with all remaining modules loading successfully.
        """
        # Load all modules and check system health
        loader = ModuleLoader()
        loaded_modules = loader.load_all_modules()
        health_status = loader.get_health_status()
        
        # Property: System health should not be CRITICAL after CAD removal
        assert health_status['health'] != 'CRITICAL', (
            f"System health is CRITICAL after CAD removal: {health_status}"
        )
        
        # Property: Some modules should be successfully loaded
        assert health_status['loaded_modules'] > 0, (
            f"No modules loaded - system broken: {health_status}"
        )
        
        # Property: Categories should only include allowed ones
        allowed_categories = {'cam', 'utility', 'debug'}
        actual_categories = set(health_status['categories'])
        forbidden_categories = actual_categories - allowed_categories
        
        assert len(forbidden_categories) == 0, (
            f"Forbidden categories in health status: {forbidden_categories}. "
            f"Only allowed: {allowed_categories}"
        )
        
        # Property: CAM category should be present (core functionality preserved)
        assert 'cam' in actual_categories, (
            f"CAM category missing from health status: {actual_categories}"
        )
        
        # Property: Failed modules should not include CAD modules (they shouldn't exist)
        failed_modules = loader.get_failed_modules()
        cad_failed_modules = [
            module for module in failed_modules.keys() 
            if '.cad.' in module
        ]
        assert len(cad_failed_modules) == 0, (
            f"CAD modules in failed list (should not exist): {cad_failed_modules}"
        )


if __name__ == "__main__":
    # Run the property tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])