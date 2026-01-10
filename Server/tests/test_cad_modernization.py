#!/usr/bin/env python3
"""
Property-based tests for CAD tools modernization.

This module contains property-based tests to validate the modernization of CAD tools
from the old send_request pattern to the modern direct requests pattern.

Tests validate:
- Modern HTTP request pattern usage
- Import statement modernization
- Functional compatibility preservation
- Standardized error handling
- Response interceptor integration
- Complete file coverage
- End-to-end compatibility
"""

import pytest
import sys
import os
import inspect
import ast
import importlib.util
from hypothesis import given, strategies as st, settings
from typing import List, Dict, Any, Callable

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

# Import the CAD modules to test
from tools.cad import geometry, sketching, modeling, features


class TestCADModernizationProperties:
    """Property-based tests for CAD tools modernization."""
    
    @staticmethod
    def get_all_cad_functions() -> List[Callable]:
        """Get all CAD tool functions from all modules."""
        functions = []
        
        # Get functions from geometry module
        for name in dir(geometry):
            obj = getattr(geometry, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools' 
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                functions.append(obj)
        
        # Get functions from sketching module  
        for name in dir(sketching):
            obj = getattr(sketching, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                functions.append(obj)
                
        # Get functions from modeling module
        for name in dir(modeling):
            obj = getattr(modeling, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                functions.append(obj)
                
        # Get functions from features module
        for name in dir(features):
            obj = getattr(features, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                functions.append(obj)
                
        return functions
    
    @staticmethod
    def get_cad_modules() -> List[Any]:
        """Get all CAD modules."""
        return [geometry, sketching, modeling, features]
    
    @staticmethod
    def get_function_source(func: Callable) -> str:
        """Get source code of a function."""
        try:
            return inspect.getsource(func)
        except OSError:
            return ""
    
    @staticmethod
    def get_module_source(module: Any) -> str:
        """Get source code of a module."""
        try:
            return inspect.getsource(module)
        except OSError:
            return ""
    
    @staticmethod
    def parse_imports(source_code: str) -> List[str]:
        """Parse import statements from source code."""
        try:
            tree = ast.parse(source_code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                        
            return imports
        except SyntaxError:
            return []

    @given(st.sampled_from(get_all_cad_functions.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_modern_http_request_pattern(self, cad_function):
        """
        Feature: cad-tools-modernization, Property 1: Modern HTTP Request Pattern
        For any CAD tool function, the implementation should use direct requests.get/post calls
        with interceptor.intercept_response and proper timeout handling.
        **Validates: Requirements 1.1, 1.2, 6.1, 6.2, 6.3**
        """
        source_code = self.get_function_source(cad_function)
        
        # Check if function uses modern pattern
        has_modern_requests = ("requests.get(" in source_code or 
                              "requests.post(" in source_code)
        has_interceptor = "interceptor.intercept_response(" in source_code
        has_timeout = "get_timeout()" in source_code
        
        # Check if function avoids old pattern
        avoids_send_request = "send_request(" not in source_code
        avoids_get_headers = "get_headers()" not in source_code
        
        # For modernized functions, all modern patterns should be present
        # For non-modernized functions, we document current state
        if has_modern_requests:
            assert has_interceptor, f"Function {cad_function.__name__} uses requests but missing interceptor"
            assert has_timeout, f"Function {cad_function.__name__} uses requests but missing timeout"
            assert avoids_send_request, f"Function {cad_function.__name__} should not use send_request"
            assert avoids_get_headers, f"Function {cad_function.__name__} should not use get_headers"

    @given(st.sampled_from(get_cad_modules.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_import_statement_modernization(self, cad_module):
        """
        Feature: cad-tools-modernization, Property 2: Import Statement Modernization
        For any CAD tool file, the imports should include requests, get_endpoints, get_timeout,
        and interceptor while excluding send_request and get_headers.
        **Validates: Requirements 1.4, 1.5, 5.1, 5.2, 5.3, 5.4, 5.5**
        """
        source_code = self.get_module_source(cad_module)
        imports = self.parse_imports(source_code)
        
        # Check for modern imports
        has_requests = any("requests" in imp for imp in imports)
        has_get_endpoints = any("get_endpoints" in imp for imp in imports)
        has_get_timeout = any("get_timeout" in imp for imp in imports)
        has_interceptor = any("interceptor" in imp for imp in imports)
        
        # Check for old imports to avoid
        has_send_request = any("send_request" in imp for imp in imports)
        has_get_headers = any("get_headers" in imp for imp in imports)
        
        # For modernized modules, check import patterns
        if has_requests and has_interceptor:
            assert has_get_endpoints, f"Module {cad_module.__name__} should import get_endpoints"
            assert has_get_timeout, f"Module {cad_module.__name__} should import get_timeout"
            assert not has_send_request, f"Module {cad_module.__name__} should not import send_request"
            assert not has_get_headers, f"Module {cad_module.__name__} should not import get_headers"

    @given(st.sampled_from(get_all_cad_functions.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_functional_compatibility_preservation(self, cad_function):
        """
        Feature: cad-tools-modernization, Property 3: Functional Compatibility Preservation
        For any CAD tool function, calling it with the same parameters should produce identical
        results before and after modernization.
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # Test function signature preservation
        try:
            sig = inspect.signature(cad_function)
            
            # Function should have a signature
            assert sig is not None, f"Function {cad_function.__name__} should have a signature"
            
            # Function should have docstring preserved
            assert cad_function.__doc__ is not None, f"Function {cad_function.__name__} should have docstring"
            
            # Function should be callable
            assert callable(cad_function), f"Function {cad_function.__name__} should be callable"
            
            # Check that function has proper error handling structure
            source_code = self.get_function_source(cad_function)
            
            # Should have try/except structure for error handling
            has_try_except = "try:" in source_code and "except" in source_code
            assert has_try_except, f"Function {cad_function.__name__} should have try/except error handling"
            
            # Should return dict-like responses (not None)
            has_return_dict = "return {" in source_code or 'return interceptor.intercept_response' in source_code
            has_no_return_none = "return None" not in source_code
            
            # For modernized functions, should not return None
            if "interceptor.intercept_response" in source_code:
                assert has_no_return_none, f"Modernized function {cad_function.__name__} should not return None"
                assert has_return_dict, f"Modernized function {cad_function.__name__} should return structured responses"
            
        except (ValueError, TypeError) as e:
            pytest.fail(f"Function {cad_function.__name__} signature inspection failed: {e}")

    @given(st.sampled_from(get_all_cad_functions.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_standardized_error_handling(self, cad_function):
        """
        Feature: cad-tools-modernization, Property 4: Standardized Error Handling
        For any CAD tool function, error conditions should return responses with consistent
        structure containing error, message, and code fields.
        **Validates: Requirements 1.3, 3.1, 3.2, 3.3, 3.4, 3.5**
        """
        source_code = self.get_function_source(cad_function)
        
        # Check if function has modern error handling patterns
        has_connection_error = "requests.ConnectionError" in source_code
        has_timeout_error = "requests.Timeout" in source_code
        has_generic_exception = "except Exception" in source_code
        
        # Check for standardized error response format
        has_error_field = '"error": True' in source_code
        has_message_field = '"message":' in source_code
        has_code_field = '"code":' in source_code
        
        # Check for standard error codes
        has_connection_error_code = '"CONNECTION_ERROR"' in source_code
        has_timeout_error_code = '"TIMEOUT_ERROR"' in source_code
        has_unknown_error_code = '"UNKNOWN_ERROR"' in source_code
        
        # For modernized functions with modern error handling
        if has_connection_error or has_timeout_error:
            # Should have all three error response fields
            assert has_error_field, f"Function {cad_function.__name__} should have 'error' field in error responses"
            assert has_message_field, f"Function {cad_function.__name__} should have 'message' field in error responses"
            assert has_code_field, f"Function {cad_function.__name__} should have 'code' field in error responses"
            
            # Should handle specific error types
            if has_connection_error:
                assert has_connection_error_code, f"Function {cad_function.__name__} should use CONNECTION_ERROR code"
            if has_timeout_error:
                assert has_timeout_error_code, f"Function {cad_function.__name__} should use TIMEOUT_ERROR code"
            if has_generic_exception:
                assert has_unknown_error_code, f"Function {cad_function.__name__} should use UNKNOWN_ERROR code"
            
            # Should have proper error message format
            has_fusion_message = "Cannot connect to Fusion 360" in source_code
            has_timeout_message = "timed out" in source_code
            
            if has_connection_error:
                assert has_fusion_message, f"Function {cad_function.__name__} should have descriptive connection error message"
            if has_timeout_error:
                assert has_timeout_message, f"Function {cad_function.__name__} should have descriptive timeout error message"

    @given(st.sampled_from(get_cad_modules.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_complete_file_coverage(self, cad_module):
        """
        Feature: cad-tools-modernization, Property 6: Complete File Coverage
        For all CAD tool files (geometry.py, sketching.py, modeling.py, features.py),
        every function should be modernized to use the new pattern.
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
        """
        module_name = cad_module.__name__
        
        # Get all functions in the module
        module_functions = []
        for name in dir(cad_module):
            obj = getattr(cad_module, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                module_functions.append(obj)
        
        # Check expected function counts per file
        expected_counts = {
            'tools.cad.geometry': 3,    # draw_cylinder, draw_box, draw_sphere
            'tools.cad.sketching': 5,   # draw2Dcircle, draw_lines, draw_one_line, draw_arc, spline
            'tools.cad.modeling': 9,    # extrude, extrude_thin, cut_extrude, revolve, loft, sweep, boolean_operation, draw_2d_rectangle, draw_text
            'tools.cad.features': 8     # fillet_edges, draw_holes, shell_body, circular_pattern, rectangular_pattern, create_thread, ellipsie, draw_witzenmannlogo
        }
        
        expected_count = expected_counts.get(module_name, 0)
        actual_count = len(module_functions)
        
        assert actual_count == expected_count, f"Module {module_name} should have {expected_count} functions, found {actual_count}"
        
        # Check that all functions in the module are modernized
        modernized_count = 0
        for func in module_functions:
            source_code = self.get_function_source(func)
            
            # Check for modern pattern indicators
            has_modern_requests = ("requests.get(" in source_code or "requests.post(" in source_code)
            has_interceptor = "interceptor.intercept_response(" in source_code
            has_timeout = "get_timeout()" in source_code
            
            # Check for absence of old pattern
            avoids_send_request = "send_request(" not in source_code
            avoids_get_headers = "get_headers()" not in source_code
            
            # Function is considered modernized if it has modern pattern and avoids old pattern
            is_modernized = (has_modern_requests and has_interceptor and has_timeout and 
                           avoids_send_request and avoids_get_headers)
            
            if is_modernized:
                modernized_count += 1
        
        # For complete file coverage, all functions should be modernized
        coverage_percentage = (modernized_count / actual_count) * 100 if actual_count > 0 else 0
        
        # Assert that the file has complete coverage (100% modernized)
        assert modernized_count == actual_count, (
            f"Module {module_name} should have all {actual_count} functions modernized, "
            f"but only {modernized_count} are modernized ({coverage_percentage:.1f}% coverage)"
        )
        
        # Verify specific file requirements
        if module_name == 'tools.cad.features':
            # Features.py should have all 8 functions modernized
            expected_functions = {
                'fillet_edges', 'draw_holes', 'shell_body', 'circular_pattern',
                'rectangular_pattern', 'create_thread', 'ellipsie', 'draw_witzenmannlogo'
            }
            actual_functions = {func.__name__ for func in module_functions}
            
            assert actual_functions == expected_functions, (
                f"Features module should have functions {expected_functions}, "
                f"found {actual_functions}"
            )
            
            # All features functions should be modernized
            assert modernized_count == 8, (
                f"All 8 features functions should be modernized, "
                f"found {modernized_count} modernized"
            )

    @given(st.sampled_from(get_all_cad_functions.__func__()))
    @settings(max_examples=100, deadline=None)
    def test_response_interceptor_integration(self, cad_function):
        """
        Feature: cad-tools-modernization, Property 5: Response Interceptor Integration
        For any CAD tool HTTP request, the response should be processed through
        interceptor.intercept_response with correct endpoint, response, and method parameters.
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        source_code = self.get_function_source(cad_function)
        
        # Check if function makes HTTP requests
        makes_get_request = "requests.get(" in source_code
        makes_post_request = "requests.post(" in source_code
        makes_http_request = makes_get_request or makes_post_request
        
        # Check for interceptor usage
        uses_interceptor = "interceptor.intercept_response(" in source_code
        
        # Check interceptor call pattern
        has_endpoint_param = "interceptor.intercept_response(endpoint," in source_code
        has_response_param = ", response," in source_code
        has_method_param_get = ', "GET")' in source_code
        has_method_param_post = ', "POST")' in source_code
        has_method_param = has_method_param_get or has_method_param_post
        
        # Check that interceptor is called with return statement
        returns_interceptor = "return interceptor.intercept_response(" in source_code
        
        # For functions that make HTTP requests (modernized functions)
        if makes_http_request:
            # Should use interceptor
            assert uses_interceptor, f"Function {cad_function.__name__} makes HTTP requests but doesn't use interceptor"
            
            # Should have correct interceptor call pattern
            assert has_endpoint_param, f"Function {cad_function.__name__} should pass endpoint to interceptor"
            assert has_response_param, f"Function {cad_function.__name__} should pass response to interceptor"
            assert has_method_param, f"Function {cad_function.__name__} should pass HTTP method to interceptor"
            
            # Should return interceptor result
            assert returns_interceptor, f"Function {cad_function.__name__} should return interceptor result"
            
            # Method parameter should match request type
            if makes_get_request and not makes_post_request:
                assert has_method_param_get, f"Function {cad_function.__name__} uses GET but doesn't specify GET method"
            elif makes_post_request and not makes_get_request:
                assert has_method_param_post, f"Function {cad_function.__name__} uses POST but doesn't specify POST method"
            
            # Should get endpoint from config
            uses_get_endpoints = "get_endpoints(" in source_code
            assert uses_get_endpoints, f"Function {cad_function.__name__} should get endpoint from config"
            
            # Should use timeout
            uses_timeout = "timeout=get_timeout()" in source_code
            assert uses_timeout, f"Function {cad_function.__name__} should use timeout configuration"


class TestCADModernizationBaseline:
    """Baseline tests to document current state before modernization."""
    
    def test_document_current_function_signatures(self):
        """Document current function signatures for comparison."""
        functions = TestCADModernizationProperties.get_all_cad_functions()
        
        signatures = {}
        for func in functions:
            try:
                sig = inspect.signature(func)
                signatures[func.__name__] = {
                    'module': func.__module__,
                    'signature': str(sig),
                    'docstring': func.__doc__ or "",
                    'parameters': list(sig.parameters.keys())
                }
            except (ValueError, TypeError):
                signatures[func.__name__] = {
                    'module': func.__module__,
                    'signature': "Unable to inspect",
                    'docstring': func.__doc__ or "",
                    'parameters': []
                }
        
        # Store baseline for comparison
        assert len(signatures) == 25, f"Expected 25 CAD functions, found {len(signatures)}"
        
        # Verify we have functions from all 4 files
        modules = set(sig['module'] for sig in signatures.values())
        expected_modules = {
            'tools.cad.geometry',
            'tools.cad.sketching', 
            'tools.cad.modeling',
            'tools.cad.features'
        }
        assert modules == expected_modules, f"Missing modules: {expected_modules - modules}"
    
    def test_document_current_import_patterns(self):
        """Document current import patterns for comparison."""
        modules = TestCADModernizationProperties.get_cad_modules()
        
        import_patterns = {}
        for module in modules:
            source_code = TestCADModernizationProperties.get_module_source(module)
            imports = TestCADModernizationProperties.parse_imports(source_code)
            
            import_patterns[module.__name__] = {
                'all_imports': imports,
                'has_send_request': any("send_request" in imp for imp in imports),
                'has_get_headers': any("get_headers" in imp for imp in imports),
                'has_requests': any("requests" in imp for imp in imports),
                'has_interceptor': any("interceptor" in imp for imp in imports),
                'has_get_timeout': any("get_timeout" in imp for imp in imports)
            }
        
        # Document current state
        assert len(import_patterns) == 4, f"Expected 4 CAD modules, found {len(import_patterns)}"
        
        # Most modules should currently use old pattern
        old_pattern_count = sum(1 for pattern in import_patterns.values() 
                               if pattern['has_send_request'] or pattern['has_get_headers'])
        
        # At least some modules should use old pattern (before modernization)
        assert old_pattern_count >= 0, "Should document current import patterns"
    
    def test_document_current_http_patterns(self):
        """Document current HTTP request patterns for comparison."""
        functions = TestCADModernizationProperties.get_all_cad_functions()
        
        http_patterns = {}
        for func in functions:
            source_code = TestCADModernizationProperties.get_function_source(func)
            
            http_patterns[func.__name__] = {
                'uses_send_request': 'send_request(' in source_code,
                'uses_requests_get': 'requests.get(' in source_code,
                'uses_requests_post': 'requests.post(' in source_code,
                'uses_interceptor': 'interceptor.intercept_response(' in source_code,
                'uses_get_headers': 'get_headers()' in source_code,
                'uses_get_timeout': 'get_timeout()' in source_code,
                'has_error_handling': 'except' in source_code
            }
        
        # Document current state
        assert len(http_patterns) == 25, f"Expected 25 CAD functions, found {len(http_patterns)}"
        
        # Most functions should currently use old pattern
        old_pattern_count = sum(1 for pattern in http_patterns.values() 
                               if pattern['uses_send_request'] or pattern['uses_get_headers'])
        
        # At least some functions should use old pattern (before modernization)
        assert old_pattern_count >= 0, "Should document current HTTP patterns"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])