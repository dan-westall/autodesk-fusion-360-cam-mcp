#!/usr/bin/env python3
"""
CAM Functionality Baseline Tests

This module establishes baseline functionality for all CAM operations before CAD removal.
It documents expected behavior and responses to validate that CAM functionality remains
intact after CAD components are removed.

Test Categories:
- CAM Setup Management: Create, list, modify, delete, duplicate setups
- Toolpath Operations: List, get details, analyze sequences
- Tool Management: List tools, get info, manage libraries
- Parameter Management: Modify toolpath parameters
- Height Management: Get/set height parameters
- Pass Management: Configure multi-pass operations
- Linking Management: Configure linking parameters

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import pytest
import json
import logging
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import os

# Import CAM tools to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.cam.setups import (
    create_cam_setup, list_cam_setups, get_setup_details,
    modify_setup_configuration, delete_cam_setup, duplicate_cam_setup,
    get_setup_toolpaths, find_toolpath_setup, validate_setup_toolpath_relationship,
    get_setup_toolpath_mapping, get_part_position, set_part_position
)
from tools.cam.toolpaths import (
    list_cam_toolpaths, get_toolpath_details, list_toolpaths_with_heights,
    analyze_toolpath_sequence
)
from tools.cam.tools import (
    list_cam_tools, get_tool_info, list_tool_libraries,
    list_library_tools, get_tool_details
)
from tools.cam.parameters import modify_toolpath_parameter
from tools.cam.heights import get_toolpath_heights
from tools.cam.passes import get_toolpath_passes, modify_toolpath_passes
from tools.cam.linking import get_toolpath_linking, modify_toolpath_linking


class CAMBaselineUtils:
    """Utilities for CAM baseline testing and documentation."""
    
    @staticmethod
    def extract_function_signature(func: Callable) -> Dict[str, Any]:
        """Extract function signature information."""
        import inspect
        
        sig = inspect.signature(func)
        return {
            'name': func.__name__,
            'module': func.__module__,
            'parameters': [
                {
                    'name': param.name,
                    'annotation': str(param.annotation) if param.annotation != inspect.Parameter.empty else None,
                    'default': str(param.default) if param.default != inspect.Parameter.empty else None,
                    'kind': str(param.kind)
                }
                for param in sig.parameters.values()
            ],
            'return_annotation': str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else None,
            'signature_str': str(sig),
            'docstring': func.__doc__
        }
    
    @staticmethod
    def test_function_response_structure(func: Callable, test_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a function and analyze its response structure."""
        try:
            if test_args:
                response = func(**test_args)
            else:
                # Try calling with no args for functions that don't require them
                response = func()
            
            return {
                'success': True,
                'response_type': type(response).__name__,
                'response_keys': list(response.keys()) if isinstance(response, dict) else None,
                'has_error': response.get('error', False) if isinstance(response, dict) else False,
                'error_code': response.get('code') if isinstance(response, dict) and response.get('error') else None,
                'response_sample': response if len(str(response)) < 500 else str(response)[:500] + "..."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @staticmethod
    def create_cam_baseline_report() -> Dict[str, Any]:
        """Create comprehensive CAM functionality baseline report."""
        
        # All CAM functions to test
        cam_functions = {
            'setup_management': [
                create_cam_setup, list_cam_setups, get_setup_details,
                modify_setup_configuration, delete_cam_setup, duplicate_cam_setup,
                get_setup_toolpaths, find_toolpath_setup, validate_setup_toolpath_relationship,
                get_setup_toolpath_mapping, get_part_position, set_part_position
            ],
            'toolpath_operations': [
                list_cam_toolpaths, get_toolpath_details, list_toolpaths_with_heights,
                analyze_toolpath_sequence
            ],
            'tool_management': [
                list_cam_tools, get_tool_info, list_tool_libraries,
                list_library_tools, get_tool_details
            ],
            'parameter_management': [
                modify_toolpath_parameter
            ],
            'height_management': [
                get_toolpath_heights
            ],
            'pass_management': [
                get_toolpath_passes, modify_toolpath_passes
            ],
            'linking_management': [
                get_toolpath_linking, modify_toolpath_linking
            ]
        }
        
        # Extract signatures for all functions
        function_signatures = {}
        response_structures = {}
        
        for category, functions in cam_functions.items():
            function_signatures[category] = {}
            response_structures[category] = {}
            
            for func in functions:
                # Extract signature
                sig = CAMBaselineUtils.extract_function_signature(func)
                function_signatures[category][func.__name__] = sig
                
                # Test response structure for functions that don't require parameters
                if func.__name__ in ['list_cam_setups', 'list_cam_toolpaths', 'list_cam_tools', 'list_tool_libraries']:
                    response_test = CAMBaselineUtils.test_function_response_structure(func)
                    response_structures[category][func.__name__] = response_test
        
        # Count totals
        total_functions = sum(len(functions) for functions in cam_functions.values())
        
        return {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'purpose': 'CAM functionality baseline before CAD removal',
                'requirements': ['9.1', '9.2', '9.3', '9.4', '9.5']
            },
            'summary': {
                'total_functions': total_functions,
                'categories': list(cam_functions.keys()),
                'functions_by_category': {cat: len(funcs) for cat, funcs in cam_functions.items()}
            },
            'function_signatures': function_signatures,
            'response_structures': response_structures
        }
    
    @staticmethod
    def save_baseline_report(report: Dict[str, Any], filepath: str) -> None:
        """Save baseline report to JSON file."""
        dirpath = os.path.dirname(filepath)
        if dirpath:  # Only create directories if there's a directory path
            os.makedirs(dirpath, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    @staticmethod
    def load_baseline_report(filepath: str) -> Dict[str, Any]:
        """Load baseline report from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)


class TestCAMFunctionalityBaseline:
    """Baseline tests to document CAM functionality before CAD removal."""
    
    def test_document_cam_setup_functions(self):
        """Document all CAM setup management function signatures."""
        setup_functions = [
            create_cam_setup, list_cam_setups, get_setup_details,
            modify_setup_configuration, delete_cam_setup, duplicate_cam_setup,
            get_setup_toolpaths, find_toolpath_setup, validate_setup_toolpath_relationship,
            get_setup_toolpath_mapping, get_part_position, set_part_position
        ]
        
        signatures = {}
        for func in setup_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        # Validate expected functions exist
        expected_functions = [
            'create_cam_setup', 'list_cam_setups', 'get_setup_details',
            'modify_setup_configuration', 'delete_cam_setup', 'duplicate_cam_setup',
            'get_setup_toolpaths', 'find_toolpath_setup', 'validate_setup_toolpath_relationship',
            'get_setup_toolpath_mapping', 'get_part_position', 'set_part_position'
        ]
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected setup function: {expected}"
        
        assert len(signatures) == 12, f"Expected 12 setup functions, found {len(signatures)}"
    
    def test_document_cam_toolpath_functions(self):
        """Document all CAM toolpath operation function signatures."""
        toolpath_functions = [
            list_cam_toolpaths, get_toolpath_details, list_toolpaths_with_heights,
            analyze_toolpath_sequence
        ]
        
        signatures = {}
        for func in toolpath_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        expected_functions = [
            'list_cam_toolpaths', 'get_toolpath_details', 'list_toolpaths_with_heights',
            'analyze_toolpath_sequence'
        ]
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected toolpath function: {expected}"
        
        assert len(signatures) == 4, f"Expected 4 toolpath functions, found {len(signatures)}"
    
    def test_document_cam_tool_functions(self):
        """Document all CAM tool management function signatures."""
        tool_functions = [
            list_cam_tools, get_tool_info, list_tool_libraries,
            list_library_tools, get_tool_details
        ]
        
        signatures = {}
        for func in tool_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        expected_functions = [
            'list_cam_tools', 'get_tool_info', 'list_tool_libraries',
            'list_library_tools', 'get_tool_details'
        ]
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected tool function: {expected}"
        
        assert len(signatures) == 5, f"Expected 5 tool functions, found {len(signatures)}"
    
    def test_document_cam_parameter_functions(self):
        """Document all CAM parameter management function signatures."""
        parameter_functions = [modify_toolpath_parameter]
        
        signatures = {}
        for func in parameter_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        assert 'modify_toolpath_parameter' in signatures
        assert len(signatures) == 1, f"Expected 1 parameter function, found {len(signatures)}"
    
    def test_document_cam_height_functions(self):
        """Document all CAM height management function signatures."""
        height_functions = [get_toolpath_heights]
        
        signatures = {}
        for func in height_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        expected_functions = ['get_toolpath_heights']
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected height function: {expected}"
        
        assert len(signatures) == 1, f"Expected 1 height function, found {len(signatures)}"
    
    def test_document_cam_pass_functions(self):
        """Document all CAM pass management function signatures."""
        pass_functions = [get_toolpath_passes, modify_toolpath_passes]
        
        signatures = {}
        for func in pass_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        expected_functions = ['get_toolpath_passes', 'modify_toolpath_passes']
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected pass function: {expected}"
        
        assert len(signatures) == 2, f"Expected 2 pass functions, found {len(signatures)}"
    
    def test_document_cam_linking_functions(self):
        """Document all CAM linking management function signatures."""
        linking_functions = [get_toolpath_linking, modify_toolpath_linking]
        
        signatures = {}
        for func in linking_functions:
            sig = CAMBaselineUtils.extract_function_signature(func)
            signatures[func.__name__] = sig
        
        expected_functions = ['get_toolpath_linking', 'modify_toolpath_linking']
        
        for expected in expected_functions:
            assert expected in signatures, f"Missing expected linking function: {expected}"
        
        assert len(signatures) == 2, f"Expected 2 linking functions, found {len(signatures)}"
    
    @pytest.mark.integration
    def test_cam_function_response_structures(self):
        """Test response structures of key CAM functions."""
        # Test functions that don't require parameters
        test_functions = [
            ('list_cam_setups', list_cam_setups, {}),
            ('list_cam_toolpaths', list_cam_toolpaths, {}),
            ('list_cam_tools', list_cam_tools, {}),
            ('list_tool_libraries', list_tool_libraries, {})
        ]
        
        response_tests = {}
        for name, func, args in test_functions:
            response_test = CAMBaselineUtils.test_function_response_structure(func, args)
            response_tests[name] = response_test
            
            # All functions should return dict responses
            if response_test['success']:
                assert response_test['response_type'] == 'dict', (
                    f"{name} should return dict, got {response_test['response_type']}"
                )
        
        # At least one function should succeed (if Fusion 360 is available)
        successful_tests = [test for test in response_tests.values() if test['success']]
        if not successful_tests:
            pytest.skip("No CAM functions succeeded - Fusion 360 may not be available")
    
    def test_generate_comprehensive_baseline_report(self, tmp_path):
        """Generate and save comprehensive CAM baseline report."""
        report = CAMBaselineUtils.create_cam_baseline_report()
        
        # Validate report structure
        assert 'metadata' in report
        assert 'summary' in report
        assert 'function_signatures' in report
        assert 'response_structures' in report
        
        # Validate metadata
        assert 'created_at' in report['metadata']
        assert 'purpose' in report['metadata']
        assert 'requirements' in report['metadata']
        
        # Validate summary
        assert report['summary']['total_functions'] > 0
        assert len(report['summary']['categories']) > 0
        
        # Save report to temp path
        baseline_path = tmp_path / "cam_baseline_report.json"
        CAMBaselineUtils.save_baseline_report(report, str(baseline_path))
        
        # Verify file was created
        assert baseline_path.exists(), "Baseline report file should be created"
        
        # Verify file can be loaded
        loaded_report = CAMBaselineUtils.load_baseline_report(str(baseline_path))
        assert loaded_report['summary']['total_functions'] == report['summary']['total_functions']


if __name__ == "__main__":
    # Generate baseline report when run directly
    print("Generating CAM Functionality Baseline Report...")
    print("=" * 50)
    
    utils = CAMBaselineUtils()
    report = utils.create_cam_baseline_report()
    
    print(f"Total Functions: {report['summary']['total_functions']}")
    print(f"Categories: {', '.join(report['summary']['categories'])}")
    print("\nFunctions by Category:")
    for category, count in report['summary']['functions_by_category'].items():
        print(f"  {category}: {count} functions")
    
    # Save report
    baseline_path = "Server/tests/cam_baseline_report.json"
    utils.save_baseline_report(report, baseline_path)
    print(f"\nBaseline report saved to: {baseline_path}")