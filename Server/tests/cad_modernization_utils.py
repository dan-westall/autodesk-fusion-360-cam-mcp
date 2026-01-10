#!/usr/bin/env python3
"""
Test utilities for CAD tools modernization.

This module provides utilities for comparing old vs new behavior during modernization,
documenting function signatures, and validating response formats.
"""

import inspect
import ast
import json
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class FunctionSignature:
    """Represents a function signature for comparison."""
    name: str
    module: str
    parameters: List[str]
    signature_str: str
    docstring: str
    return_annotation: Optional[str] = None


@dataclass
class ImportPattern:
    """Represents import patterns in a module."""
    module_name: str
    all_imports: List[str]
    has_send_request: bool
    has_get_headers: bool
    has_requests: bool
    has_interceptor: bool
    has_get_timeout: bool
    has_get_endpoints: bool


@dataclass
class HTTPPattern:
    """Represents HTTP request patterns in a function."""
    function_name: str
    uses_send_request: bool
    uses_requests_get: bool
    uses_requests_post: bool
    uses_interceptor: bool
    uses_get_headers: bool
    uses_get_timeout: bool
    has_error_handling: bool
    has_connection_error_handling: bool
    has_timeout_error_handling: bool


class CADModernizationUtils:
    """Utilities for CAD tools modernization testing."""
    
    @staticmethod
    def extract_function_signature(func: Callable) -> FunctionSignature:
        """Extract function signature information."""
        try:
            sig = inspect.signature(func)
            return FunctionSignature(
                name=func.__name__,
                module=func.__module__,
                parameters=list(sig.parameters.keys()),
                signature_str=str(sig),
                docstring=func.__doc__ or "",
                return_annotation=str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else None
            )
        except (ValueError, TypeError):
            return FunctionSignature(
                name=func.__name__,
                module=func.__module__,
                parameters=[],
                signature_str="Unable to inspect",
                docstring=func.__doc__ or ""
            )
    
    @staticmethod
    def parse_module_imports(source_code: str) -> List[str]:
        """Parse import statements from module source code."""
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
    
    @staticmethod
    def analyze_import_pattern(module: Any) -> ImportPattern:
        """Analyze import patterns in a module."""
        try:
            source_code = inspect.getsource(module)
        except OSError:
            source_code = ""
            
        imports = CADModernizationUtils.parse_module_imports(source_code)
        
        return ImportPattern(
            module_name=module.__name__,
            all_imports=imports,
            has_send_request=any("send_request" in imp for imp in imports),
            has_get_headers=any("get_headers" in imp for imp in imports),
            has_requests=any("requests" in imp for imp in imports),
            has_interceptor=any("interceptor" in imp for imp in imports),
            has_get_timeout=any("get_timeout" in imp for imp in imports),
            has_get_endpoints=any("get_endpoints" in imp for imp in imports)
        )
    
    @staticmethod
    def analyze_http_pattern(func: Callable) -> HTTPPattern:
        """Analyze HTTP request patterns in a function."""
        try:
            source_code = inspect.getsource(func)
        except OSError:
            source_code = ""
        
        return HTTPPattern(
            function_name=func.__name__,
            uses_send_request='send_request(' in source_code,
            uses_requests_get='requests.get(' in source_code,
            uses_requests_post='requests.post(' in source_code,
            uses_interceptor='interceptor.intercept_response(' in source_code,
            uses_get_headers='get_headers()' in source_code,
            uses_get_timeout='get_timeout()' in source_code,
            has_error_handling='except' in source_code,
            has_connection_error_handling='ConnectionError' in source_code,
            has_timeout_error_handling='Timeout' in source_code
        )
    
    @staticmethod
    def is_modern_pattern(http_pattern: HTTPPattern) -> bool:
        """Check if a function uses the modern HTTP pattern."""
        has_modern_requests = http_pattern.uses_requests_get or http_pattern.uses_requests_post
        has_modern_components = (
            has_modern_requests and 
            http_pattern.uses_interceptor and 
            http_pattern.uses_get_timeout
        )
        avoids_old_pattern = not http_pattern.uses_send_request and not http_pattern.uses_get_headers
        
        return has_modern_components and avoids_old_pattern
    
    @staticmethod
    def is_modern_imports(import_pattern: ImportPattern) -> bool:
        """Check if a module uses modern import patterns."""
        has_modern_imports = (
            import_pattern.has_requests and
            import_pattern.has_get_endpoints and
            import_pattern.has_get_timeout and
            import_pattern.has_interceptor
        )
        avoids_old_imports = not import_pattern.has_send_request and not import_pattern.has_get_headers
        
        return has_modern_imports and avoids_old_imports
    
    @staticmethod
    def compare_signatures(before: FunctionSignature, after: FunctionSignature) -> Dict[str, Any]:
        """Compare function signatures before and after modernization."""
        return {
            'name_changed': before.name != after.name,
            'parameters_changed': before.parameters != after.parameters,
            'signature_changed': before.signature_str != after.signature_str,
            'docstring_changed': before.docstring != after.docstring,
            'return_annotation_changed': before.return_annotation != after.return_annotation,
            'differences': {
                'name': {'before': before.name, 'after': after.name},
                'parameters': {'before': before.parameters, 'after': after.parameters},
                'signature': {'before': before.signature_str, 'after': after.signature_str},
                'docstring_length': {'before': len(before.docstring), 'after': len(after.docstring)}
            }
        }
    
    @staticmethod
    def validate_error_response_format(response: Dict[str, Any]) -> bool:
        """Validate that an error response follows the standard format."""
        if not isinstance(response, dict):
            return False
            
        required_fields = ['error', 'message', 'code']
        has_required_fields = all(field in response for field in required_fields)
        
        if not has_required_fields:
            return False
            
        # Validate field types
        if not isinstance(response['error'], bool) or not response['error']:
            return False
            
        if not isinstance(response['message'], str) or not response['message']:
            return False
            
        if not isinstance(response['code'], str) or not response['code']:
            return False
            
        # Validate standard error codes
        valid_codes = ['CONNECTION_ERROR', 'TIMEOUT_ERROR', 'UNKNOWN_ERROR']
        if response['code'] not in valid_codes:
            return False
            
        return True
    
    @staticmethod
    def create_baseline_report(functions: List[Callable], modules: List[Any]) -> Dict[str, Any]:
        """Create a comprehensive baseline report."""
        function_signatures = {}
        for func in functions:
            sig = CADModernizationUtils.extract_function_signature(func)
            function_signatures[func.__name__] = sig
        
        import_patterns = {}
        for module in modules:
            pattern = CADModernizationUtils.analyze_import_pattern(module)
            import_patterns[module.__name__] = pattern
        
        http_patterns = {}
        for func in functions:
            pattern = CADModernizationUtils.analyze_http_pattern(func)
            http_patterns[func.__name__] = pattern
        
        # Count patterns
        modern_functions = sum(1 for pattern in http_patterns.values() 
                              if CADModernizationUtils.is_modern_pattern(pattern))
        modern_modules = sum(1 for pattern in import_patterns.values() 
                            if CADModernizationUtils.is_modern_imports(pattern))
        
        return {
            'summary': {
                'total_functions': len(functions),
                'total_modules': len(modules),
                'modern_functions': modern_functions,
                'modern_modules': modern_modules,
                'modernization_progress': {
                    'functions': f"{modern_functions}/{len(functions)} ({modern_functions/len(functions)*100:.1f}%)",
                    'modules': f"{modern_modules}/{len(modules)} ({modern_modules/len(modules)*100:.1f}%)"
                }
            },
            'function_signatures': function_signatures,
            'import_patterns': import_patterns,
            'http_patterns': http_patterns
        }
    
    @staticmethod
    def save_baseline_report(report: Dict[str, Any], filepath: str) -> None:
        """Save baseline report to JSON file."""
        # Convert dataclasses to dicts for JSON serialization
        serializable_report = {}
        
        for key, value in report.items():
            if key == 'function_signatures':
                serializable_report[key] = {
                    name: {
                        'name': sig.name,
                        'module': sig.module,
                        'parameters': sig.parameters,
                        'signature_str': sig.signature_str,
                        'docstring': sig.docstring,
                        'return_annotation': sig.return_annotation
                    } for name, sig in value.items()
                }
            elif key == 'import_patterns':
                serializable_report[key] = {
                    name: {
                        'module_name': pattern.module_name,
                        'all_imports': pattern.all_imports,
                        'has_send_request': pattern.has_send_request,
                        'has_get_headers': pattern.has_get_headers,
                        'has_requests': pattern.has_requests,
                        'has_interceptor': pattern.has_interceptor,
                        'has_get_timeout': pattern.has_get_timeout,
                        'has_get_endpoints': pattern.has_get_endpoints
                    } for name, pattern in value.items()
                }
            elif key == 'http_patterns':
                serializable_report[key] = {
                    name: {
                        'function_name': pattern.function_name,
                        'uses_send_request': pattern.uses_send_request,
                        'uses_requests_get': pattern.uses_requests_get,
                        'uses_requests_post': pattern.uses_requests_post,
                        'uses_interceptor': pattern.uses_interceptor,
                        'uses_get_headers': pattern.uses_get_headers,
                        'uses_get_timeout': pattern.uses_get_timeout,
                        'has_error_handling': pattern.has_error_handling,
                        'has_connection_error_handling': pattern.has_connection_error_handling,
                        'has_timeout_error_handling': pattern.has_timeout_error_handling
                    } for name, pattern in value.items()
                }
            else:
                serializable_report[key] = value
        
        with open(filepath, 'w') as f:
            json.dump(serializable_report, f, indent=2)
    
    @staticmethod
    def load_baseline_report(filepath: str) -> Dict[str, Any]:
        """Load baseline report from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)


# Convenience functions for common operations
def get_cad_functions():
    """Get all CAD tool functions."""
    import sys
    import os
    
    # Add Server directory to path for imports
    server_path = os.path.join(os.path.dirname(__file__), "..")
    if server_path not in sys.path:
        sys.path.insert(0, server_path)
    
    from tools.cad import geometry, sketching, modeling, features
    
    functions = []
    for module in [geometry, sketching, modeling, features]:
        for name in dir(module):
            obj = getattr(module, name)
            if (callable(obj) and not name.startswith('_') and name != 'register_tools' 
                and hasattr(obj, '__module__') and obj.__module__.startswith('tools.cad')):
                functions.append(obj)
    
    return functions


def get_cad_modules():
    """Get all CAD modules."""
    import sys
    import os
    
    # Add Server directory to path for imports
    server_path = os.path.join(os.path.dirname(__file__), "..")
    if server_path not in sys.path:
        sys.path.insert(0, server_path)
    
    from tools.cad import geometry, sketching, modeling, features
    return [geometry, sketching, modeling, features]


if __name__ == "__main__":
    # Generate baseline report
    functions = get_cad_functions()
    modules = get_cad_modules()
    
    utils = CADModernizationUtils()
    report = utils.create_baseline_report(functions, modules)
    
    print("CAD Tools Modernization Baseline Report")
    print("=" * 50)
    print(f"Total Functions: {report['summary']['total_functions']}")
    print(f"Total Modules: {report['summary']['total_modules']}")
    print(f"Modern Functions: {report['summary']['modernization_progress']['functions']}")
    print(f"Modern Modules: {report['summary']['modernization_progress']['modules']}")
    
    # Save report
    utils.save_baseline_report(report, "Server/tests/cad_modernization_baseline.json")
    print("\nBaseline report saved to: Server/tests/cad_modernization_baseline.json")