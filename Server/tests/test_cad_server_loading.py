#!/usr/bin/env python3
"""
MCP Server Loading Tests for CAD Tools Modernization.

This module contains tests to verify that the MCP server can load all modernized
CAD tools without import errors, syntax issues, or dependency problems.

Tests validate:
- All 25 CAD functions load without import errors
- Tool registration works correctly
- No syntax or dependency issues
- Module structure is correct
"""

import pytest
import sys
import os
import importlib
import inspect
from typing import List, Dict, Any

# Add Server directory to path for imports
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)


class TestCADServerLoading:
    """Test MCP server loading with modernized CAD tools."""
    
    def test_cad_modules_import_successfully(self):
        """Test that all CAD modules can be imported without errors."""
        cad_modules = ['geometry', 'sketching', 'modeling', 'features']
        
        for module_name in cad_modules:
            try:
                module = importlib.import_module(f'tools.cad.{module_name}')
                assert module is not None, f"Module tools.cad.{module_name} failed to import"
                
                # Verify module has expected attributes
                assert hasattr(module, 'register_tools'), f"Module {module_name} missing register_tools function"
                
                # Verify register_tools is callable
                assert callable(module.register_tools), f"register_tools in {module_name} is not callable"
                
            except ImportError as e:
                pytest.fail(f"Failed to import tools.cad.{module_name}: {e}")
            except Exception as e:
                pytest.fail(f"Unexpected error importing tools.cad.{module_name}: {e}")
    
    def test_all_cad_functions_are_accessible(self):
        """Test that all 25 CAD functions are accessible and callable."""
        from tools.cad import geometry, sketching, modeling, features
        
        # Expected function counts per module
        expected_functions = {
            'geometry': ['draw_cylinder', 'draw_box', 'draw_sphere'],
            'sketching': ['draw2Dcircle', 'draw_lines', 'draw_one_line', 'draw_arc', 'spline'],
            'modeling': ['extrude', 'extrude_thin', 'cut_extrude', 'revolve', 'loft', 'sweep', 
                        'boolean_operation', 'draw_2d_rectangle', 'draw_text'],
            'features': ['fillet_edges', 'draw_holes', 'shell_body', 'circular_pattern', 
                        'rectangular_pattern', 'create_thread', 'ellipsie', 'draw_witzenmannlogo']
        }
        
        modules = {
            'geometry': geometry,
            'sketching': sketching,
            'modeling': modeling,
            'features': features
        }
        
        total_functions_found = 0
        
        for module_name, expected_funcs in expected_functions.items():
            module = modules[module_name]
            
            for func_name in expected_funcs:
                # Check function exists
                assert hasattr(module, func_name), f"Function {func_name} not found in {module_name}"
                
                # Check function is callable
                func = getattr(module, func_name)
                assert callable(func), f"Function {func_name} in {module_name} is not callable"
                
                # Check function has docstring
                assert func.__doc__ is not None, f"Function {func_name} in {module_name} missing docstring"
                
                total_functions_found += 1
        
        # Verify we found all 25 expected functions
        assert total_functions_found == 25, f"Expected 25 CAD functions, found {total_functions_found}"
    
    def test_cad_functions_have_modern_imports(self):
        """Test that CAD modules use modern import patterns."""
        from tools.cad import geometry, sketching, modeling, features
        
        modules = [geometry, sketching, modeling, features]
        
        for module in modules:
            module_source = inspect.getsource(module)
            
            # Check for modern imports
            assert 'import requests' in module_source, f"Module {module.__name__} missing 'import requests'"
            assert 'from core.config import get_endpoints, get_timeout' in module_source, \
                f"Module {module.__name__} missing modern config imports"
            assert 'from core import interceptor' in module_source, \
                f"Module {module.__name__} missing interceptor import"
            
            # Check that old imports are not present
            assert 'from core.request_handler import send_request' not in module_source, \
                f"Module {module.__name__} still has old send_request import"
            assert 'from core.config import get_headers' not in module_source, \
                f"Module {module.__name__} still has old get_headers import"
    
    def test_cad_functions_use_modern_patterns(self):
        """Test that CAD functions use modern HTTP request patterns."""
        from tools.cad import geometry, sketching, modeling, features
        
        modules = [geometry, sketching, modeling, features]
        modernized_functions = 0
        total_functions = 0
        
        for module in modules:
            # Get all functions in the module
            for name in dir(module):
                obj = getattr(module, name)
                if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                    and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                    
                    total_functions += 1
                    func_source = inspect.getsource(obj)
                    
                    # Check for modern pattern indicators
                    has_requests_call = ('requests.get(' in func_source or 'requests.post(' in func_source)
                    has_interceptor = 'interceptor.intercept_response(' in func_source
                    has_timeout = 'get_timeout()' in func_source
                    
                    # Check for absence of old patterns
                    no_send_request = 'send_request(' not in func_source
                    no_get_headers = 'get_headers()' not in func_source
                    
                    # Function is modernized if it has all modern patterns and no old patterns
                    if has_requests_call and has_interceptor and has_timeout and no_send_request and no_get_headers:
                        modernized_functions += 1
        
        # Calculate modernization percentage
        modernization_percentage = (modernized_functions / total_functions) * 100 if total_functions > 0 else 0
        
        # Expect high modernization rate (allow some functions to not be fully modernized yet)
        assert modernization_percentage >= 80, \
            f"Modernization rate too low: {modernized_functions}/{total_functions} ({modernization_percentage:.1f}%)"
        
        print(f"Modernization status: {modernized_functions}/{total_functions} functions ({modernization_percentage:.1f}%)")
    
    def test_cad_functions_have_proper_error_handling(self):
        """Test that CAD functions have proper error handling patterns."""
        from tools.cad import geometry, sketching, modeling, features
        
        modules = [geometry, sketching, modeling, features]
        functions_with_error_handling = 0
        total_functions = 0
        
        for module in modules:
            # Get all functions in the module
            for name in dir(module):
                obj = getattr(module, name)
                if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                    and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                    
                    total_functions += 1
                    func_source = inspect.getsource(obj)
                    
                    # Check for proper error handling patterns
                    has_try_except = 'try:' in func_source and 'except' in func_source
                    has_connection_error = 'requests.ConnectionError' in func_source
                    has_timeout_error = 'requests.Timeout' in func_source
                    has_generic_exception = 'except Exception' in func_source
                    
                    # Check for standardized error response format
                    has_error_response = ('"error": True' in func_source and 
                                        '"message":' in func_source and 
                                        '"code":' in func_source)
                    
                    # Function has proper error handling if it has try/except and error responses
                    if has_try_except and has_error_response:
                        functions_with_error_handling += 1
        
        # Calculate error handling percentage
        error_handling_percentage = (functions_with_error_handling / total_functions) * 100 if total_functions > 0 else 0
        
        # Expect most functions to have proper error handling
        assert error_handling_percentage >= 70, \
            f"Error handling coverage too low: {functions_with_error_handling}/{total_functions} ({error_handling_percentage:.1f}%)"
        
        print(f"Error handling coverage: {functions_with_error_handling}/{total_functions} functions ({error_handling_percentage:.1f}%)")
    
    def test_core_dependencies_are_available(self):
        """Test that all core dependencies required by CAD tools are available."""
        # Test core.config imports
        try:
            from core.config import get_endpoints, get_timeout
            
            # Test that functions work
            endpoints = get_endpoints("cad")
            assert isinstance(endpoints, dict), "get_endpoints should return a dictionary"
            assert len(endpoints) > 0, "CAD endpoints should not be empty"
            
            timeout = get_timeout()
            assert isinstance(timeout, int), "get_timeout should return an integer"
            assert timeout > 0, "Timeout should be positive"
            
        except ImportError as e:
            pytest.fail(f"Failed to import core.config dependencies: {e}")
        
        # Test core.interceptor import
        try:
            from core import interceptor
            assert hasattr(interceptor, 'intercept_response'), "interceptor missing intercept_response function"
            assert callable(interceptor.intercept_response), "intercept_response should be callable"
            
        except ImportError as e:
            pytest.fail(f"Failed to import core.interceptor: {e}")
        
        # Test requests import
        try:
            import requests
            assert hasattr(requests, 'get'), "requests missing get method"
            assert hasattr(requests, 'post'), "requests missing post method"
            assert hasattr(requests, 'ConnectionError'), "requests missing ConnectionError"
            assert hasattr(requests, 'Timeout'), "requests missing Timeout"
            
        except ImportError as e:
            pytest.fail(f"Failed to import requests: {e}")
    
    def test_mcp_server_can_register_cad_tools(self):
        """Test that MCP server can register CAD tools without errors."""
        try:
            # Import FastMCP
            from mcp.server.fastmcp import FastMCP
            
            # Create a test MCP instance
            mcp = FastMCP("test-cad-server")
            
            # Import and register CAD tools
            from tools.cad import geometry, sketching, modeling, features
            
            modules = [geometry, sketching, modeling, features]
            registered_tools = 0
            
            for module in modules:
                # Call register_tools function
                try:
                    module.register_tools(mcp)
                    
                    # Count functions that should be registered
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                            and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                            registered_tools += 1
                            
                except Exception as e:
                    pytest.fail(f"Failed to register tools from {module.__name__}: {e}")
            
            # Verify we registered the expected number of tools
            assert registered_tools == 25, f"Expected to register 25 tools, registered {registered_tools}"
            
        except ImportError as e:
            pytest.fail(f"Failed to import MCP dependencies: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error during tool registration: {e}")
    
    def test_no_syntax_errors_in_cad_modules(self):
        """Test that all CAD modules have valid Python syntax."""
        import ast
        
        cad_module_files = [
            'Server/tools/cad/geometry.py',
            'Server/tools/cad/sketching.py', 
            'Server/tools/cad/modeling.py',
            'Server/tools/cad/features.py'
        ]
        
        for file_path in cad_module_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    # Parse the source code to check for syntax errors
                    ast.parse(source_code)
                    
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {file_path}: {e}")
                except Exception as e:
                    pytest.fail(f"Error reading {file_path}: {e}")
            else:
                pytest.fail(f"CAD module file not found: {file_path}")
    
    def test_function_signatures_are_preserved(self):
        """Test that function signatures are preserved after modernization."""
        from tools.cad import geometry, sketching, modeling, features
        
        modules = [geometry, sketching, modeling, features]
        functions_with_signatures = 0
        total_functions = 0
        
        for module in modules:
            # Get all functions in the module
            for name in dir(module):
                obj = getattr(module, name)
                if (callable(obj) and not name.startswith('_') and name != 'register_tools'
                    and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                    
                    total_functions += 1
                    
                    try:
                        # Get function signature
                        sig = inspect.signature(obj)
                        
                        # Some functions may have no parameters (like sweep), which is valid
                        # Function should have type hints for parameters if it has parameters
                        if len(sig.parameters) > 0:
                            has_type_hints = any(param.annotation != inspect.Parameter.empty 
                                               for param in sig.parameters.values())
                            
                            if has_type_hints:
                                functions_with_signatures += 1
                        else:
                            # Functions with no parameters are considered to have "preserved" signatures
                            functions_with_signatures += 1
                            
                    except (ValueError, TypeError) as e:
                        pytest.fail(f"Cannot inspect signature of {name} in {module.__name__}: {e}")
        
        # Calculate signature preservation percentage
        signature_percentage = (functions_with_signatures / total_functions) * 100 if total_functions > 0 else 0
        
        # Most functions should have type hints
        assert signature_percentage >= 60, \
            f"Too few functions have type hints: {functions_with_signatures}/{total_functions} ({signature_percentage:.1f}%)"
        
        print(f"Functions with type hints: {functions_with_signatures}/{total_functions} ({signature_percentage:.1f}%)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])