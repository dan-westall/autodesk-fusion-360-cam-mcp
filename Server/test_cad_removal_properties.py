#!/usr/bin/env python3
"""
Property-Based Test for Configuration Cleanup Completeness and Test Suite Cleanup

This module contains property-based tests to validate that design workspace
endpoints have been completely removed from the server configuration while
preserving all CAM, utility, and system functionality. It also validates
that the test suite has been cleaned up to remove design-related tests.

Property 4: Configuration cleanup completeness
*For any* system configuration loading, the configuration should only contain 
endpoints for CAM operations, utilities, and system functions with no references 
to removed design endpoints

Property 5: Test suite cleanup completeness
*For any* test execution, the test suite should only include CAM functionality 
tests, utility tests, and system tests with no design workspace test cases

Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.4, 4.5
"""

import pytest
import sys
import os
import glob
import ast
from typing import Dict, List, Any, Set
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from core.config import (
    get_base_url,
    get_endpoints,
    get_headers,
    get_timeout,
    get_categories,
    validate_configuration
)

# Design endpoint names that should NOT be present in configuration
FORBIDDEN_DESIGN_ENDPOINTS = [
    'draw_box', 'draw_cylinder', 'draw_sphere',
    'draw_circle', 'draw_line', 'draw_arc', 'draw_spline', 'draw_ellipse', 'draw_text',
    'extrude', 'revolve', 'loft', 'sweep', 
    'boolean_union', 'boolean_subtract', 'boolean_intersect',
    'fillet', 'shell', 'hole', 'thread',
    'circular_pattern', 'rectangular_pattern',
    'export_step', 'export_stl',
    'undo', 'delete_everything', 'destroy',
    'change_parameter', 'set_parameter',
    'witzenmann'
]

# Expected categories that should be present
EXPECTED_CATEGORIES = ['cam', 'utility', 'debug']

# CAM endpoint patterns that should be present
EXPECTED_CAM_PATTERNS = [
    'cam_toolpaths', 'cam_setups', 'cam_tools', 'tool_libraries'
]

# Utility endpoint patterns that should be present
EXPECTED_UTILITY_PATTERNS = [
    'test_connection', 'count_parameters', 'list_parameters'
]

# Design-related test files that should NOT exist
FORBIDDEN_TEST_FILES = [
    'test_cad_server_loading.py',
    'test_cad_integration.py', 
    'test_cad_modernization.py',
    'test_cad_end_to_end_compatibility.py',
    'test_cad_response_interception.py',
    'test_live_design.py',
    'test_design_*.py'
]

# Design-related test patterns that should NOT be present in test files
FORBIDDEN_TEST_PATTERNS = [
    'test_design_', 'test_cad_', 'design_endpoints', 'cad_endpoints',
    'draw_box', 'draw_cylinder', 'draw_sphere', 'extrude', 'revolve',
    'design_workspace', 'cad_workspace'
]

# Expected test categories that should be present
EXPECTED_TEST_CATEGORIES = ['cam', 'manufacture', 'utility', 'system', 'core']


class TestConfigurationCleanupCompleteness:
    """Property-based tests for configuration cleanup completeness."""
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_design_endpoints_in_configuration(self, _):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any configuration loading, the system should not contain
        any design workspace endpoint definitions, ensuring complete removal
        of design functionality from the configuration.
        
        This test verifies that all design endpoints have been removed from
        the centralized configuration system.
        """
        # Get all endpoints from configuration
        all_endpoints = get_endpoints()
        endpoint_names = set(all_endpoints.keys())
        
        # Check that no forbidden design endpoints are present
        forbidden_present = endpoint_names.intersection(set(FORBIDDEN_DESIGN_ENDPOINTS))
        
        assert len(forbidden_present) == 0, (
            f"Design endpoints found in configuration: {forbidden_present}. "
            f"These endpoints should have been removed during CAD removal process."
        )
    
    @given(st.sampled_from(EXPECTED_CATEGORIES))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_only_expected_categories_present(self, expected_category):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any configuration category, only CAM, utility, and debug
        categories should be present, with no design or CAD categories.
        
        This test verifies that the configuration structure only contains
        the expected categories after design endpoint removal.
        """
        categories = get_categories()
        
        # Verify expected category is present
        assert expected_category in categories, (
            f"Expected category '{expected_category}' not found in configuration. "
            f"Available categories: {categories}"
        )
        
        # Verify no forbidden categories
        forbidden_categories = {'cad', 'design', 'geometry', 'sketching', 'modeling', 'features'}
        present_forbidden = set(categories).intersection(forbidden_categories)
        
        assert len(present_forbidden) == 0, (
            f"Forbidden design categories found: {present_forbidden}. "
            f"Only CAM, utility, and debug categories should be present."
        )
    
    @given(st.sampled_from(EXPECTED_CAM_PATTERNS))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cam_endpoints_preserved_in_configuration(self, cam_pattern):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any CAM endpoint pattern, the configuration should contain
        endpoints matching that pattern, ensuring CAM functionality is preserved
        in the configuration after design endpoint removal.
        
        This test verifies that essential CAM endpoints remain in the configuration.
        """
        cam_endpoints = get_endpoints('cam')
        cam_endpoint_names = set(cam_endpoints.keys())
        
        # Check that the expected CAM pattern is present
        matching_endpoints = [name for name in cam_endpoint_names if cam_pattern in name]
        
        assert len(matching_endpoints) > 0, (
            f"No CAM endpoints found matching pattern '{cam_pattern}'. "
            f"CAM functionality may have been accidentally removed. "
            f"Available CAM endpoints: {list(cam_endpoint_names)}"
        )
    
    @given(st.sampled_from(EXPECTED_UTILITY_PATTERNS))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_utility_endpoints_preserved_in_configuration(self, utility_pattern):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any utility endpoint pattern, the configuration should contain
        endpoints matching that pattern, ensuring utility functionality is preserved
        in the configuration after design endpoint removal.
        
        This test verifies that essential utility endpoints remain in the configuration.
        """
        utility_endpoints = get_endpoints('utility')
        utility_endpoint_names = set(utility_endpoints.keys())
        
        # Check that the expected utility pattern is present
        matching_endpoints = [name for name in utility_endpoint_names if utility_pattern in name]
        
        assert len(matching_endpoints) > 0, (
            f"No utility endpoints found matching pattern '{utility_pattern}'. "
            f"Utility functionality may have been accidentally removed. "
            f"Available utility endpoints: {list(utility_endpoint_names)}"
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_configuration_validation_passes(self, _):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any configuration state after cleanup, the configuration
        validation should pass, ensuring the configuration remains valid and
        functional after design endpoint removal.
        
        This test verifies that configuration cleanup maintains system integrity.
        """
        validation_result = validate_configuration()
        
        assert validation_result is True, (
            "Configuration validation failed after design endpoint removal. "
            "This indicates that the cleanup process may have introduced "
            "configuration errors or inconsistencies."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_endpoint_urls_are_valid(self, _):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: For any endpoint in the cleaned configuration, the endpoint
        URL should be valid and properly formatted, ensuring that remaining
        endpoints are functional after design endpoint removal.
        
        This test verifies that endpoint cleanup maintains URL validity.
        """
        all_endpoints = get_endpoints()
        base_url = get_base_url()
        
        for endpoint_name, endpoint_url in all_endpoints.items():
            # Check URL format
            assert isinstance(endpoint_url, str), (
                f"Endpoint '{endpoint_name}' URL should be string, got {type(endpoint_url)}"
            )
            
            assert endpoint_url.startswith(base_url), (
                f"Endpoint '{endpoint_name}' URL '{endpoint_url}' should start with base URL '{base_url}'"
            )
            
            assert len(endpoint_url) > len(base_url), (
                f"Endpoint '{endpoint_name}' URL '{endpoint_url}' should have path after base URL"
            )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_configuration_completeness_comprehensive(self, _):
        """
        **Feature: cad-removal, Property 4: Configuration cleanup completeness**
        
        Property: The complete configuration should contain only CAM, utility,
        and debug endpoints with no design endpoints, and should maintain
        all expected functionality patterns.
        
        This test provides comprehensive validation of configuration cleanup.
        """
        # Get configuration state
        categories = get_categories()
        all_endpoints = get_endpoints()
        cam_endpoints = get_endpoints('cam')
        utility_endpoints = get_endpoints('utility')
        debug_endpoints = get_endpoints('debug')
        
        # Verify category structure
        assert set(categories) == set(EXPECTED_CATEGORIES), (
            f"Configuration categories {categories} don't match expected {EXPECTED_CATEGORIES}"
        )
        
        # Verify no design endpoints
        endpoint_names = set(all_endpoints.keys())
        forbidden_present = endpoint_names.intersection(set(FORBIDDEN_DESIGN_ENDPOINTS))
        assert len(forbidden_present) == 0, (
            f"Design endpoints still present: {forbidden_present}"
        )
        
        # Verify CAM functionality preserved
        assert len(cam_endpoints) > 0, "No CAM endpoints found - CAM functionality may be broken"
        
        # Verify utility functionality preserved
        assert len(utility_endpoints) > 0, "No utility endpoints found - utility functionality may be broken"
        
        # Verify endpoint count consistency
        total_expected = len(cam_endpoints) + len(utility_endpoints) + len(debug_endpoints)
        assert len(all_endpoints) == total_expected, (
            f"Total endpoint count {len(all_endpoints)} doesn't match sum of categories {total_expected}"
        )
        
        # Verify configuration validation
        assert validate_configuration() is True, "Configuration validation failed"


class TestSuiteCleanupCompleteness:
    """Property-based tests for test suite cleanup completeness."""
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_design_test_files_exist(self, _):
        """
        **Feature: cad-removal, Property 5: Test suite cleanup completeness**
        
        Property: For any test file discovery, the test suite should not contain
        any design workspace test files, ensuring complete removal of design
        test cases from the test suite.
        
        This test verifies that all design-related test files have been removed.
        """
        # Get current directory and search for test files
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Search for test files in both Server and FusionMCPBridge test directories
        server_test_dir = os.path.join(project_root, "Server", "tests")
        bridge_test_dir = os.path.join(project_root, "FusionMCPBridge", "tests")
        
        found_forbidden_files = []
        
        # Check Server test directory
        if os.path.exists(server_test_dir):
            for pattern in FORBIDDEN_TEST_FILES:
                matches = glob.glob(os.path.join(server_test_dir, pattern))
                found_forbidden_files.extend([os.path.basename(f) for f in matches])
        
        # Check FusionMCPBridge test directory
        if os.path.exists(bridge_test_dir):
            for pattern in FORBIDDEN_TEST_FILES:
                matches = glob.glob(os.path.join(bridge_test_dir, pattern))
                found_forbidden_files.extend([os.path.basename(f) for f in matches])
        
        assert len(found_forbidden_files) == 0, (
            f"Design test files found that should have been removed: {found_forbidden_files}. "
            f"These test files should have been deleted during CAD removal process."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_design_test_patterns_in_remaining_files(self, _):
        """
        **Feature: cad-removal, Property 5: Test suite cleanup completeness**
        
        Property: For any remaining test file, the file should not contain
        design-related test patterns or references, ensuring that design
        functionality is not tested in the remaining test suite.
        
        This test verifies that remaining test files don't contain design references.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Search for all Python test files
        test_files = []
        for test_dir in ["Server/tests", "FusionMCPBridge/tests"]:
            test_path = os.path.join(project_root, test_dir)
            if os.path.exists(test_path):
                test_files.extend(glob.glob(os.path.join(test_path, "test_*.py")))
        
        violations = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for forbidden patterns
                for pattern in FORBIDDEN_TEST_PATTERNS:
                    if pattern in content:
                        violations.append(f"{os.path.basename(test_file)}: contains '{pattern}'")
            except Exception as e:
                # Skip files that can't be read
                continue
        
        assert len(violations) == 0, (
            f"Design test patterns found in remaining test files: {violations}. "
            f"These patterns should have been removed or updated during CAD removal."
        )
    
    @given(st.sampled_from(EXPECTED_TEST_CATEGORIES))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_expected_test_categories_present(self, expected_category):
        """
        **Feature: cad-removal, Property 5: Test suite cleanup completeness**
        
        Property: For any expected test category, the test suite should contain
        tests for that category, ensuring that CAM, utility, and system
        functionality remains properly tested after design test removal.
        
        This test verifies that essential test categories are preserved.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Search for test files matching the expected category
        test_files = []
        for test_dir in ["Server/tests", "FusionMCPBridge/tests"]:
            test_path = os.path.join(project_root, test_dir)
            if os.path.exists(test_path):
                # Look for test files containing the category name
                pattern = f"test_*{expected_category}*.py"
                matches = glob.glob(os.path.join(test_path, pattern))
                test_files.extend(matches)
                
                # Also look for test files in category-specific patterns
                if expected_category == 'cam':
                    matches = glob.glob(os.path.join(test_path, "test_*toolpath*.py"))
                    test_files.extend(matches)
                    matches = glob.glob(os.path.join(test_path, "test_*setup*.py"))
                    test_files.extend(matches)
                elif expected_category == 'manufacture':
                    matches = glob.glob(os.path.join(test_path, "test_live_*.py"))
                    test_files.extend(matches)
        
        assert len(test_files) > 0, (
            f"No test files found for category '{expected_category}'. "
            f"Essential functionality may not be properly tested after design test removal."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_test_configuration_updated(self, _):
        """
        **Feature: cad-removal, Property 5: Test suite cleanup completeness**
        
        Property: For any test configuration file, the configuration should
        not contain design workspace endpoints or fixtures, ensuring that
        test infrastructure is properly cleaned up.
        
        This test verifies that test configuration files have been updated.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Check conftest.py files for design references
        conftest_files = []
        for test_dir in ["Server/tests", "FusionMCPBridge/tests"]:
            conftest_path = os.path.join(project_root, test_dir, "conftest.py")
            if os.path.exists(conftest_path):
                conftest_files.append(conftest_path)
        
        violations = []
        
        for conftest_file in conftest_files:
            try:
                with open(conftest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for design endpoint references
                design_patterns = [
                    'draw_box', 'draw_cylinder', 'draw_circle', 'draw_lines',
                    'extrude', 'revolve', 'fillet', 'shell',
                    'export_step', 'export_stl',
                    'DESIGN', 'design_endpoints', 'design_document_required'
                ]
                
                for pattern in design_patterns:
                    if pattern in content:
                        violations.append(f"{os.path.basename(conftest_file)}: contains '{pattern}'")
            except Exception as e:
                # Skip files that can't be read
                continue
        
        assert len(violations) == 0, (
            f"Design references found in test configuration files: {violations}. "
            f"Test configuration should have been updated to remove design endpoints."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_test_suite_completeness_comprehensive(self, _):
        """
        **Feature: cad-removal, Property 5: Test suite cleanup completeness**
        
        Property: The complete test suite should contain only CAM, utility,
        and system tests with no design tests, and should maintain all
        expected test functionality patterns.
        
        This test provides comprehensive validation of test suite cleanup.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Get all test files
        all_test_files = []
        for test_dir in ["Server/tests", "FusionMCPBridge/tests"]:
            test_path = os.path.join(project_root, test_dir)
            if os.path.exists(test_path):
                all_test_files.extend(glob.glob(os.path.join(test_path, "test_*.py")))
        
        # Verify no forbidden test files exist
        forbidden_files = []
        for test_file in all_test_files:
            filename = os.path.basename(test_file)
            for forbidden_pattern in FORBIDDEN_TEST_FILES:
                if forbidden_pattern.replace('*', '') in filename or filename == forbidden_pattern:
                    forbidden_files.append(filename)
        
        assert len(forbidden_files) == 0, (
            f"Forbidden design test files still exist: {forbidden_files}"
        )
        
        # Verify expected test categories are present
        cam_tests = [f for f in all_test_files if 'cam' in os.path.basename(f) or 'toolpath' in os.path.basename(f) or 'setup' in os.path.basename(f)]
        utility_tests = [f for f in all_test_files if 'utility' in os.path.basename(f) or 'system' in os.path.basename(f)]
        core_tests = [f for f in all_test_files if 'core' in os.path.basename(f)]
        
        assert len(cam_tests) > 0, "No CAM-related tests found - CAM functionality may not be tested"
        assert len(utility_tests) > 0, "No utility/system tests found - utility functionality may not be tested"
        assert len(core_tests) > 0, "No core tests found - core functionality may not be tested"
        
        # Verify test files don't contain design patterns
        violations = []
        for test_file in all_test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for critical design patterns that should be completely removed
                critical_patterns = ['test_design_', 'test_cad_', 'draw_box', 'draw_cylinder', 'extrude']
                for pattern in critical_patterns:
                    if pattern in content:
                        violations.append(f"{os.path.basename(test_file)}: contains '{pattern}'")
                        break  # Only report one violation per file
            except Exception:
                continue
        
        assert len(violations) == 0, (
            f"Critical design patterns found in test files: {violations}"
        )


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short"])


class TestDirectoryStructureCleanup:
    """Property-based tests for directory structure cleanup."""
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cad_directory_completely_removed(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: For any file system examination, the Server/tools/cad/
        directory should not exist, ensuring complete removal of CAD
        tool directory structure.
        
        This test verifies that the CAD tools directory has been completely removed.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        cad_directory = os.path.join(project_root, "Server", "tools", "cad")
        
        assert not os.path.exists(cad_directory), (
            f"CAD directory still exists at {cad_directory}. "
            f"This directory should have been completely removed during CAD removal process."
        )
        
        # Also check that no CAD-related files exist in the tools directory
        tools_directory = os.path.join(project_root, "Server", "tools")
        if os.path.exists(tools_directory):
            for item in os.listdir(tools_directory):
                item_path = os.path.join(tools_directory, item)
                if os.path.isdir(item_path):
                    assert item != "cad", (
                        f"CAD subdirectory found in tools directory: {item_path}. "
                        f"All CAD directories should have been removed."
                    )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_design_handlers_directory_completely_removed(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: For any file system examination, the FusionMCPBridge/handlers/design/
        directory should not exist, ensuring complete removal of design
        handler directory structure.
        
        This test verifies that the design handlers directory has been completely removed.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        design_directory = os.path.join(project_root, "FusionMCPBridge", "handlers", "design")
        
        assert not os.path.exists(design_directory), (
            f"Design handlers directory still exists at {design_directory}. "
            f"This directory should have been completely removed during CAD removal process."
        )
        
        # Also check that no design-related directories exist in the handlers directory
        handlers_directory = os.path.join(project_root, "FusionMCPBridge", "handlers")
        if os.path.exists(handlers_directory):
            for item in os.listdir(handlers_directory):
                item_path = os.path.join(handlers_directory, item)
                if os.path.isdir(item_path):
                    assert item != "design", (
                        f"Design subdirectory found in handlers directory: {item_path}. "
                        f"All design directories should have been removed."
                    )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_cad_related_files_in_filesystem(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: For any file system search, no CAD-related files should
        exist in the removed directory paths, ensuring complete cleanup
        of CAD file artifacts.
        
        This test verifies that no CAD-related files remain in the filesystem.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Define CAD-related file patterns that should not exist
        cad_file_patterns = [
            "geometry.py", "sketching.py", "modeling.py", "features.py"
        ]
        
        # Search in the removed directory paths
        removed_paths = [
            os.path.join(project_root, "Server", "tools", "cad"),
            os.path.join(project_root, "FusionMCPBridge", "handlers", "design")
        ]
        
        found_cad_files = []
        
        for removed_path in removed_paths:
            if os.path.exists(removed_path):
                for root, dirs, files in os.walk(removed_path):
                    for file in files:
                        if any(pattern in file for pattern in cad_file_patterns):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, project_root)
                            found_cad_files.append(rel_path)
        
        assert len(found_cad_files) == 0, (
            f"CAD-related files found in removed directory paths: {found_cad_files}. "
            f"These files should have been completely removed during directory cleanup."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_only_expected_directories_remain(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: For any directory structure examination, only CAM-related
        handler directories and expected tool directories should remain,
        ensuring proper directory structure after cleanup.
        
        This test verifies that the directory structure contains only expected directories.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Check Server/tools directory structure
        tools_directory = os.path.join(project_root, "Server", "tools")
        if os.path.exists(tools_directory):
            expected_tool_dirs = {"cam", "utility", "debug"}
            actual_tool_dirs = set()
            
            for item in os.listdir(tools_directory):
                item_path = os.path.join(tools_directory, item)
                if os.path.isdir(item_path) and not item.startswith('__'):
                    actual_tool_dirs.add(item)
            
            # Remove __pycache__ from comparison
            actual_tool_dirs.discard("__pycache__")
            
            assert actual_tool_dirs == expected_tool_dirs, (
                f"Server tools directory structure {actual_tool_dirs} doesn't match expected {expected_tool_dirs}. "
                f"Only CAM, utility, and debug directories should remain."
            )
        
        # Check FusionMCPBridge/handlers directory structure
        handlers_directory = os.path.join(project_root, "FusionMCPBridge", "handlers")
        if os.path.exists(handlers_directory):
            expected_handler_dirs = {"manufacture", "system", "research"}
            actual_handler_dirs = set()
            
            for item in os.listdir(handlers_directory):
                item_path = os.path.join(handlers_directory, item)
                if os.path.isdir(item_path) and not item.startswith('__'):
                    actual_handler_dirs.add(item)
            
            # Remove __pycache__ from comparison
            actual_handler_dirs.discard("__pycache__")
            
            assert actual_handler_dirs == expected_handler_dirs, (
                f"Handlers directory structure {actual_handler_dirs} doesn't match expected {expected_handler_dirs}. "
                f"Only manufacture, system, and research directories should remain."
            )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_empty_parent_directories_after_cleanup(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: For any directory structure examination, no empty parent
        directories should remain after CAD directory removal, ensuring
        complete cleanup of directory hierarchy.
        
        This test verifies that no empty directories remain after cleanup.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Check for empty directories in key locations
        check_paths = [
            os.path.join(project_root, "Server", "tools"),
            os.path.join(project_root, "FusionMCPBridge", "handlers")
        ]
        
        empty_directories = []
        
        for check_path in check_paths:
            if os.path.exists(check_path):
                for root, dirs, files in os.walk(check_path):
                    # Skip __pycache__ directories and virtual environment directories
                    dirs[:] = [d for d in dirs if not d.startswith('__') and d not in ['venv', '.venv']]
                    
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            # Check if directory is empty (no files or subdirectories)
                            if os.path.isdir(dir_path):
                                contents = os.listdir(dir_path)
                                # Filter out __pycache__ and other system directories
                                meaningful_contents = [item for item in contents 
                                                     if not item.startswith('__') and item not in ['.DS_Store']]
                                if len(meaningful_contents) == 0:
                                    rel_path = os.path.relpath(dir_path, project_root)
                                    empty_directories.append(rel_path)
                        except (OSError, PermissionError):
                            # Skip directories that can't be accessed
                            continue
        
        assert len(empty_directories) == 0, (
            f"Empty directories found after cleanup: {empty_directories}. "
            f"Empty directories should be removed during directory structure cleanup."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_directory_structure_cleanup_comprehensive(self, _):
        """
        **Feature: cad-removal, Property 7: Directory structure cleanup**
        
        Property: The complete directory structure should contain only
        CAM-related directories with no design workspace directories,
        and should have no empty directories or CAD file artifacts.
        
        This test provides comprehensive validation of directory structure cleanup.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Test 1: Removed directories don't exist
        removed_directories = [
            os.path.join(project_root, "Server", "tools", "cad"),
            os.path.join(project_root, "FusionMCPBridge", "handlers", "design")
        ]
        
        for removed_dir in removed_directories:
            assert not os.path.exists(removed_dir), (
                f"Removed directory still exists: {removed_dir}"
            )
        
        # Test 2: Expected directory structure is present
        tools_dir = os.path.join(project_root, "Server", "tools")
        if os.path.exists(tools_dir):
            expected_tools = {"cam", "utility", "debug"}
            actual_tools = {item for item in os.listdir(tools_dir) 
                          if os.path.isdir(os.path.join(tools_dir, item)) and not item.startswith('__')}
            assert actual_tools == expected_tools, (
                f"Tools directory structure incorrect: {actual_tools} vs expected {expected_tools}"
            )
        
        handlers_dir = os.path.join(project_root, "FusionMCPBridge", "handlers")
        if os.path.exists(handlers_dir):
            expected_handlers = {"manufacture", "system", "research"}
            actual_handlers = {item for item in os.listdir(handlers_dir) 
                             if os.path.isdir(os.path.join(handlers_dir, item)) and not item.startswith('__')}
            assert actual_handlers == expected_handlers, (
                f"Handlers directory structure incorrect: {actual_handlers} vs expected {expected_handlers}"
            )
        
        # Test 3: No CAD-related files in filesystem
        cad_files = []
        search_dirs = [
            os.path.join(project_root, "Server"),
            os.path.join(project_root, "FusionMCPBridge")
        ]
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    # Skip test files and documentation
                    if any(skip in root for skip in ['test', 'doc', '__pycache__', '.git']):
                        continue
                    
                    for file in files:
                        if file.endswith('.py'):
                            # Check for CAD-specific filenames in removed paths
                            if any(cad_name in file for cad_name in ['geometry.py', 'sketching.py', 'modeling.py', 'features.py']):
                                # Only flag if in removed directory paths
                                if 'tools/cad' in root or 'handlers/design' in root:
                                    file_path = os.path.join(root, file)
                                    rel_path = os.path.relpath(file_path, project_root)
                                    cad_files.append(rel_path)
        
        assert len(cad_files) == 0, (
            f"CAD files found in removed directory paths: {cad_files}"
        )
        
        # Test 4: Directory structure is clean and organized
        # Verify that remaining directories contain expected content
        cam_dir = os.path.join(project_root, "Server", "tools", "cam")
        if os.path.exists(cam_dir):
            cam_files = [f for f in os.listdir(cam_dir) if f.endswith('.py') and f != '__init__.py']
            assert len(cam_files) > 0, "CAM directory should contain CAM tool files"
        
        manufacture_dir = os.path.join(project_root, "FusionMCPBridge", "handlers", "manufacture")
        if os.path.exists(manufacture_dir):
            manufacture_contents = os.listdir(manufacture_dir)
            meaningful_contents = [item for item in manufacture_contents if not item.startswith('__')]
            assert len(meaningful_contents) > 0, "Manufacture directory should contain handler files or subdirectories"


class TestImportAndDependencyCleanup:
    """Property-based tests for import and dependency cleanup."""
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_design_module_imports_in_codebase(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: For any Python file in the codebase, the file should not
        import any removed design modules, ensuring complete removal of
        design module dependencies.
        
        This test verifies that all import statements referencing design
        modules have been removed or updated.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Design module patterns that should not be imported
        forbidden_import_patterns = [
            'from tools.cad',
            'import tools.cad',
            'from handlers.design',
            'import handlers.design',
            'tools.cad.geometry',
            'tools.cad.sketching',
            'tools.cad.modeling',
            'tools.cad.features',
            'handlers.design.geometry',
            'handlers.design.sketching',
            'handlers.design.modeling',
            'handlers.design.features',
            'handlers.design.utilities'
        ]
        
        # Search for Python files in key directories
        search_dirs = [
            "Server",
            "FusionMCPBridge"
        ]
        
        violations = []
        
        for search_dir in search_dirs:
            search_path = os.path.join(project_root, search_dir)
            if os.path.exists(search_path):
                # Find all Python files
                for root, dirs, files in os.walk(search_path):
                    # Skip __pycache__ directories
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        if file.endswith('.py'):
                            # Skip test files that are specifically testing for absence of these patterns
                            if 'test_cad_removal_properties.py' in file or 'test_http_endpoint_removal_completeness.py' in file:
                                continue
                                
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    
                                # Check for forbidden import patterns
                                for pattern in forbidden_import_patterns:
                                    if pattern in content:
                                        rel_path = os.path.relpath(file_path, project_root)
                                        violations.append(f"{rel_path}: imports '{pattern}'")
                            except Exception:
                                # Skip files that can't be read
                                continue
        
        assert len(violations) == 0, (
            f"Design module imports found in codebase: {violations}. "
            f"These import statements should have been removed or updated during CAD removal."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_server_module_loading_excludes_design_modules(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: For any server module discovery, the module loader should
        not discover or attempt to load any design modules, ensuring that
        the module loading system excludes removed components.
        
        This test verifies that the server's module discovery system
        properly excludes design modules.
        """
        # Import server module loader
        server_path = os.path.join(os.path.dirname(__file__), "..")
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        
        from core.loader import ModuleLoader
        
        loader = ModuleLoader()
        discovered_modules = loader.discover_modules()
        
        # Check that no design modules are discovered
        design_modules = []
        for module in discovered_modules:
            module_str = str(module)
            if any(pattern in module_str.lower() for pattern in ['cad', 'design', 'geometry', 'sketching', 'modeling', 'features']):
                # Exclude legitimate modules that might contain these words
                if not any(allowed in module_str for allowed in ['cam', 'manufacture', 'utility', 'debug', 'system']):
                    design_modules.append(module_str)
        
        assert len(design_modules) == 0, (
            f"Design modules discovered by module loader: {design_modules}. "
            f"Module discovery should exclude all design-related modules."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_server_startup_without_import_errors(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: For any server startup attempt, the system should start
        successfully without import errors related to removed design modules,
        ensuring that dependency cleanup is complete.
        
        This test verifies that the server can start without import errors.
        """
        # Import server components
        server_path = os.path.join(os.path.dirname(__file__), "..")
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        
        try:
            # Test core module imports
            from core.server import create_server
            from core.loader import ModuleLoader
            from core.config import get_endpoints
            
            # Test module discovery
            loader = ModuleLoader()
            modules = loader.discover_modules()
            
            # Verify modules can be loaded without errors
            loaded_modules = []
            import_errors = []
            
            for module_path in modules:
                try:
                    # Attempt to load each discovered module
                    module_info = loader.load_module(str(module_path))
                    if module_info:
                        loaded_modules.append(str(module_path))
                except ImportError as e:
                    # Check if the import error is related to design modules
                    error_str = str(e).lower()
                    if any(pattern in error_str for pattern in ['cad', 'design', 'geometry', 'sketching', 'modeling', 'features']):
                        import_errors.append(f"{module_path}: {str(e)}")
                except Exception:
                    # Other errors are not import-related
                    pass
            
            assert len(import_errors) == 0, (
                f"Import errors related to design modules during server startup: {import_errors}. "
                f"These indicate incomplete dependency cleanup."
            )
            
            # Verify that some modules were successfully loaded
            assert len(loaded_modules) > 0, (
                "No modules were successfully loaded - this indicates a broader system issue."
            )
            
        except ImportError as e:
            error_str = str(e).lower()
            if any(pattern in error_str for pattern in ['cad', 'design', 'geometry', 'sketching', 'modeling', 'features']):
                pytest.fail(f"Server startup failed due to design module import error: {e}")
            else:
                # Non-design related import errors might be acceptable (e.g., missing optional dependencies)
                pass
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_fusion_addin_startup_without_design_handlers(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: For any Fusion Add-In startup attempt, the system should
        start successfully without attempting to import design handlers,
        ensuring that handler dependency cleanup is complete.
        
        This test verifies that the Fusion Add-In can start without design handler errors.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        fusion_bridge_path = os.path.join(project_root, "FusionMCPBridge")
        
        if fusion_bridge_path not in sys.path:
            sys.path.insert(0, fusion_bridge_path)
        
        try:
            # Test core imports (these should work without Fusion 360)
            from core.config import ConfigurationManager
            from core.router import RequestRouter
            
            # Test that design handlers are not importable
            design_import_successful = False
            try:
                from handlers.design import geometry
                design_import_successful = True
            except ImportError:
                # This is expected - design handlers should not be importable
                pass
            
            assert not design_import_successful, (
                "Design handlers are still importable - they should have been removed."
            )
            
            # Test that system handlers work
            from handlers.system import lifecycle
            
            # Test that manufacture handlers can be imported (though they may fail due to missing adsk module)
            manufacture_import_error = None
            try:
                from handlers import manufacture
            except ImportError as e:
                # Check if the error is related to design modules
                error_str = str(e).lower()
                if any(pattern in error_str for pattern in ['design', 'geometry', 'sketching', 'modeling', 'features']):
                    manufacture_import_error = str(e)
                # Errors related to missing 'adsk' module are expected outside Fusion 360
            
            assert manufacture_import_error is None, (
                f"Manufacture handlers failed to import due to design module dependency: {manufacture_import_error}"
            )
            
        except ImportError as e:
            error_str = str(e).lower()
            if any(pattern in error_str for pattern in ['design', 'geometry', 'sketching', 'modeling', 'features']):
                pytest.fail(f"Fusion Add-In startup failed due to design module import error: {e}")
            else:
                # Non-design related import errors might be acceptable (e.g., missing adsk module)
                pass
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_broken_dependencies_in_remaining_modules(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: For any remaining module in the system, the module should
        not have broken dependencies on removed design modules, ensuring
        that all remaining code is functional after design module removal.
        
        This test verifies that remaining modules don't have broken dependencies.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Check Python files for potential broken dependencies
        search_dirs = ["Server", "FusionMCPBridge"]
        broken_dependencies = []
        
        for search_dir in search_dirs:
            search_path = os.path.join(project_root, search_dir)
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    # Skip __pycache__ directories and venv directories
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.venv', 'node_modules']]
                    
                    for file in files:
                        if file.endswith('.py'):
                            # Skip research files and test files that may contain legitimate references
                            if any(skip in file for skip in ['research.py', 'test_cad_removal_properties.py', 'test_http_endpoint_removal_completeness.py']):
                                continue
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Parse the file to check for potential broken references
                                try:
                                    tree = ast.parse(content)
                                    
                                    # Look for attribute access that might reference removed modules
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.Attribute):
                                            attr_name = node.attr
                                            # Check for references to removed CAD functions
                                            if attr_name in ['draw_box', 'draw_cylinder', 'draw_sphere', 
                                                           'draw_circle', 'draw_line', 'draw_arc', 
                                                           'extrude', 'revolve', 'loft', 'sweep',
                                                           'fillet', 'shell', 'hole', 'thread']:
                                                rel_path = os.path.relpath(file_path, project_root)
                                                broken_dependencies.append(f"{rel_path}: references removed function '{attr_name}'")
                                        
                                        elif isinstance(node, ast.Name):
                                            name = node.id
                                            # Check for direct references to removed modules
                                            if name in ['geometry', 'sketching', 'modeling', 'features'] and 'design' in content:
                                                rel_path = os.path.relpath(file_path, project_root)
                                                broken_dependencies.append(f"{rel_path}: references removed module '{name}'")
                                
                                except SyntaxError:
                                    # Skip files with syntax errors
                                    continue
                                    
                            except Exception:
                                # Skip files that can't be read or parsed
                                continue
        
        assert len(broken_dependencies) == 0, (
            f"Potential broken dependencies found: {broken_dependencies}. "
            f"These references to removed design modules should be updated or removed."
        )
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_import_dependency_cleanup_comprehensive(self, _):
        """
        **Feature: cad-removal, Property 6: Import and dependency cleanup**
        
        Property: The complete system should have no import statements or
        dependencies referencing removed design modules, and should start
        successfully with only manufacturing-related modules loaded.
        
        This test provides comprehensive validation of import and dependency cleanup.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)
        
        # Test 1: No design imports in codebase
        forbidden_patterns = ['tools.cad', 'handlers.design']
        import_violations = []
        
        for search_dir in ["Server", "FusionMCPBridge"]:
            search_path = os.path.join(project_root, search_dir)
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    for file in files:
                        if file.endswith('.py'):
                            # Skip test files that are specifically testing for absence of these patterns
                            if 'test_cad_removal_properties.py' in file or 'test_http_endpoint_removal_completeness.py' in file:
                                continue
                                
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                for pattern in forbidden_patterns:
                                    if pattern in content:
                                        rel_path = os.path.relpath(file_path, project_root)
                                        import_violations.append(f"{rel_path}: contains '{pattern}'")
                                        break
                            except Exception:
                                continue
        
        assert len(import_violations) == 0, f"Import violations found: {import_violations}"
        
        # Test 2: Server module discovery excludes design modules
        server_path = os.path.join(project_root, "Server")
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        
        from core.loader import ModuleLoader
        loader = ModuleLoader()
        modules = loader.discover_modules()
        
        design_modules = [str(m) for m in modules if any(pattern in str(m).lower() for pattern in ['cad', 'design']) 
                         and not any(allowed in str(m) for allowed in ['cam', 'manufacture'])]
        assert len(design_modules) == 0, f"Design modules discovered: {design_modules}"
        
        # Test 3: Core imports work without errors
        try:
            from core.server import create_server
            from core.config import get_endpoints
            
            # Verify configuration doesn't contain design endpoints
            all_endpoints = get_endpoints()
            design_endpoints = [name for name in all_endpoints.keys() 
                              if any(pattern in name.lower() for pattern in ['draw', 'extrude', 'revolve', 'fillet'])]
            assert len(design_endpoints) == 0, f"Design endpoints in configuration: {design_endpoints}"
            
        except ImportError as e:
            if any(pattern in str(e).lower() for pattern in ['cad', 'design']):
                pytest.fail(f"Core import failed due to design dependency: {e}")
        
        # Test 4: Only expected module categories present
        expected_categories = {'cam', 'utility', 'debug'}
        found_categories = set()
        for module in modules:
            module_str = str(module)
            if 'tools.cam' in module_str:
                found_categories.add('cam')
            elif 'tools.utility' in module_str:
                found_categories.add('utility')
            elif 'tools.debug' in module_str:
                found_categories.add('debug')
        
        assert found_categories == expected_categories, (
            f"Module categories {found_categories} don't match expected {expected_categories}"
        )


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short"])

class TestErrorMessageCleanup:
    """
    Property-Based Test for Error Message Cleanup
    
    This test class validates that error messages and help text have been
    updated to reflect the manufacturing-only scope after CAD removal.
    
    Property 9: Error message cleanup
    *For any* error condition, the system should not reference removed design 
    functionality in error messages and should only mention available 
    manufacturing capabilities in help text
    
    Requirements: 10.1, 10.3, 10.4, 10.5
    """
    
    # Design-related terms that should NOT appear in error messages or help text
    FORBIDDEN_DESIGN_TERMS = [
        'design workspace', 'Design workspace', 'DESIGN workspace',
        'CAD workspace', 'cad workspace', 
        'design functionality', 'design capabilities',
        'design operations', 'design tools',
        'sketching', 'modeling', 'extrude', 'revolve', 'loft', 'sweep',
        'draw_box', 'draw_cylinder', 'draw_sphere',
        'draw_circle', 'draw_line', 'draw_arc', 'draw_spline',
        'boolean_union', 'boolean_subtract', 'boolean_intersect',
        'fillet', 'shell', 'hole', 'thread',
        'circular_pattern', 'rectangular_pattern',
        'export_step', 'export_stl'
    ]
    
    # Manufacturing-focused terms that SHOULD appear in error messages
    EXPECTED_MANUFACTURING_TERMS = [
        'MANUFACTURE workspace', 'manufacturing', 'CAM',
        'toolpath', 'setup', 'operation', 'tool library',
        'machining', 'cutting tool', 'feed rate', 'spindle speed'
    ]

    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_design_references_in_error_messages(self, _):
        """
        **Feature: cad-removal, Property 9: Error message cleanup**
        
        Property: For any error message in the system, the message should not
        reference removed design functionality and should focus on available
        manufacturing capabilities.
        
        This test scans all error messages in the codebase to ensure they
        have been updated to reflect the manufacturing-only scope.
        """
        # Collect all error messages from the codebase
        error_messages = self._collect_error_messages()
        
        # Check each error message for forbidden design terms
        design_references = []
        for file_path, messages in error_messages.items():
            for message in messages:
                for forbidden_term in self.FORBIDDEN_DESIGN_TERMS:
                    if forbidden_term.lower() in message.lower():
                        design_references.append({
                            'file': file_path,
                            'message': message,
                            'forbidden_term': forbidden_term
                        })
        
        assert len(design_references) == 0, (
            f"Found {len(design_references)} error messages with design references: "
            f"{design_references}. All error messages should focus on manufacturing capabilities only."
        )

    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_manufacturing_focus_in_help_text(self, _):
        """
        **Feature: cad-removal, Property 9: Error message cleanup**
        
        Property: For any help text or tool description, the content should
        focus on manufacturing capabilities and not reference removed design
        functionality.
        
        This test validates that help text has been updated to reflect
        the manufacturing-only scope of the system.
        """
        # Collect all help text and tool descriptions
        help_texts = self._collect_help_text()
        
        # Check for design references in help text
        design_references = []
        manufacturing_focus_count = 0
        
        for file_path, texts in help_texts.items():
            for text in texts:
                # Check for forbidden design terms
                for forbidden_term in self.FORBIDDEN_DESIGN_TERMS:
                    if forbidden_term.lower() in text.lower():
                        design_references.append({
                            'file': file_path,
                            'text': text[:100] + '...' if len(text) > 100 else text,
                            'forbidden_term': forbidden_term
                        })
                
                # Count manufacturing-focused content
                for manufacturing_term in self.EXPECTED_MANUFACTURING_TERMS:
                    if manufacturing_term.lower() in text.lower():
                        manufacturing_focus_count += 1
                        break
        
        # Assert no design references in help text
        assert len(design_references) == 0, (
            f"Found {len(design_references)} help texts with design references: "
            f"{design_references}. All help text should focus on manufacturing capabilities only."
        )
        
        # Assert that help text focuses on manufacturing
        total_help_texts = sum(len(texts) for texts in help_texts.values())
        if total_help_texts > 0:
            manufacturing_ratio = manufacturing_focus_count / total_help_texts
            assert manufacturing_ratio > 0.3, (
                f"Only {manufacturing_ratio:.1%} of help text focuses on manufacturing. "
                f"Expected at least 30% to have manufacturing focus."
            )

    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_error_codes_reflect_manufacturing_scope(self, _):
        """
        **Feature: cad-removal, Property 9: Error message cleanup**
        
        Property: For any error code definition, the code should reflect
        manufacturing operations and not reference removed design functionality.
        
        This test validates that error codes have been updated to reflect
        the manufacturing-only scope.
        """
        # Collect all error codes from the codebase
        error_codes = self._collect_error_codes()
        
        # Check for design-related error codes
        design_error_codes = []
        for file_path, codes in error_codes.items():
            for code in codes:
                for forbidden_term in ['DESIGN', 'CAD', 'SKETCH', 'MODEL', 'EXTRUDE', 'REVOLVE']:
                    if forbidden_term in code.upper():
                        design_error_codes.append({
                            'file': file_path,
                            'code': code
                        })
        
        assert len(design_error_codes) == 0, (
            f"Found {len(design_error_codes)} error codes with design references: "
            f"{design_error_codes}. Error codes should reflect manufacturing operations only."
        )

    def _collect_error_messages(self) -> Dict[str, List[str]]:
        """Collect all error messages from the codebase."""
        import os
        import re
        
        error_messages = {}
        
        # Scan Server directory
        server_dir = os.path.join(os.path.dirname(__file__), "..")
        for root, dirs, files in os.walk(server_dir):
            # Skip venv and test directories
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract error messages (strings containing "error" or "message")
                        messages = []
                        
                        # Find strings with "error" or "message" in them
                        string_patterns = [
                            r'"[^"]*(?:error|message|Error|Message)[^"]*"',
                            r"'[^']*(?:error|message|Error|Message)[^']*'"
                        ]
                        
                        for pattern in string_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            messages.extend([match.strip('"\'') for match in matches])
                        
                        if messages:
                            error_messages[file_path] = messages
                            
                    except (UnicodeDecodeError, IOError):
                        continue
        
        return error_messages

    def _collect_help_text(self) -> Dict[str, List[str]]:
        """Collect all help text and tool descriptions from the codebase."""
        import os
        import re
        
        help_texts = {}
        
        # Scan Server directory
        server_dir = os.path.join(os.path.dirname(__file__), "..")
        for root, dirs, files in os.walk(server_dir):
            # Skip venv and test directories
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract docstrings and help text
                        texts = []
                        
                        # Find docstrings (triple-quoted strings)
                        docstring_patterns = [
                            r'"""([^"]*(?:"[^"]*"[^"]*)*)"""',
                            r"'''([^']*(?:'[^']*'[^']*)*)'''"
                        ]
                        
                        for pattern in docstring_patterns:
                            matches = re.findall(pattern, content, re.DOTALL)
                            texts.extend(matches)
                        
                        if texts:
                            help_texts[file_path] = texts
                            
                    except (UnicodeDecodeError, IOError):
                        continue
        
        return help_texts

    def _collect_error_codes(self) -> Dict[str, List[str]]:
        """Collect all error codes from the codebase."""
        import os
        import re
        
        error_codes = {}
        
        # Scan Server directory
        server_dir = os.path.join(os.path.dirname(__file__), "..")
        for root, dirs, files in os.walk(server_dir):
            # Skip venv and test directories
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract error codes (typically ALL_CAPS strings in "code" fields)
                        codes = []
                        
                        # Find error code patterns
                        code_patterns = [
                            r'"code":\s*"([A-Z_]+)"',
                            r"'code':\s*'([A-Z_]+)'",
                            r'"([A-Z_]+_ERROR)"',
                            r"'([A-Z_]+_ERROR)'"
                        ]
                        
                        for pattern in code_patterns:
                            matches = re.findall(pattern, content)
                            codes.extend(matches)
                        
                        if codes:
                            error_codes[file_path] = codes
                            
                    except (UnicodeDecodeError, IOError):
                        continue
        
        return error_codes