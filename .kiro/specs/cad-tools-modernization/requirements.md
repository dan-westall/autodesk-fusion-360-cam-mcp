# Requirements Document

## Introduction

This specification defines the requirements for modernizing the CAD tools in the Fusion 360 MCP Server to use the current HTTP request pattern. The CAD tools currently use an outdated pattern that differs from the modern approach used in CAM tools, creating inconsistency in the codebase.

## Glossary

- **CAD Tools**: Tools in `Server/tools/cad/` for creating geometry (geometry, sketching, modeling, features)
- **CAM Tools**: Tools in `Server/tools/cam/` for manufacturing operations (toolpaths, tools, parameters)
- **Old Pattern**: Using `send_request(endpoint, payload, headers)` from `core.request_handler`
- **Modern Pattern**: Using direct `requests.get/post` with `interceptor.intercept_response`
- **HTTP Request Pattern**: The standardized way of making HTTP requests to the Fusion 360 add-in
- **Response Interceptor**: The debugging system that logs HTTP responses when enabled

## Requirements

### Requirement 1: Standardize HTTP Request Pattern

**User Story:** As a developer, I want all CAD tools to use the same HTTP request pattern as CAM tools, so that the codebase is consistent and maintainable.

#### Acceptance Criteria

1. WHEN a CAD tool makes an HTTP request, THE System SHALL use direct `requests.get/post` calls instead of `send_request` wrapper
2. WHEN a CAD tool receives an HTTP response, THE System SHALL process it through `interceptor.intercept_response`
3. WHEN a CAD tool handles errors, THE System SHALL use the same error handling pattern as CAM tools
4. WHEN a CAD tool imports dependencies, THE System SHALL import `requests`, `get_endpoints`, `get_timeout`, and `interceptor` modules
5. THE System SHALL remove dependencies on `core.request_handler.send_request` and `core.config.get_headers`

### Requirement 2: Maintain Functional Compatibility

**User Story:** As a user, I want all CAD tools to continue working exactly as before, so that existing workflows are not disrupted.

#### Acceptance Criteria

1. WHEN a CAD tool is called with the same parameters as before, THE System SHALL produce identical results
2. WHEN a CAD tool encounters an error, THE System SHALL return error responses in the same format as before
3. WHEN a CAD tool succeeds, THE System SHALL return success responses in the same format as before
4. THE System SHALL preserve all existing function signatures and parameter types
5. THE System SHALL maintain all existing docstrings and German language comments

### Requirement 3: Error Handling Consistency

**User Story:** As a developer, I want CAD tools to handle errors consistently with CAM tools, so that debugging and maintenance is easier.

#### Acceptance Criteria

1. WHEN a connection error occurs, THE System SHALL return standardized connection error responses
2. WHEN a timeout occurs, THE System SHALL return standardized timeout error responses  
3. WHEN an unknown error occurs, THE System SHALL return standardized unknown error responses
4. WHEN logging errors, THE System SHALL use consistent error message formats
5. THE System SHALL handle `requests.RequestException` and generic `Exception` types consistently

### Requirement 4: Response Interceptor Integration

**User Story:** As a developer, I want CAD tools to support response interception for debugging, so that I can troubleshoot issues consistently across all tools.

#### Acceptance Criteria

1. WHEN response interception is enabled, THE System SHALL log all CAD tool HTTP responses
2. WHEN making GET requests, THE System SHALL pass responses through `interceptor.intercept_response` with "GET" method
3. WHEN making POST requests, THE System SHALL pass responses through `interceptor.intercept_response` with "POST" method
4. THE System SHALL include endpoint URL, response object, and HTTP method in interceptor calls
5. THE System SHALL maintain interceptor functionality without breaking existing behavior

### Requirement 5: Import and Dependency Updates

**User Story:** As a developer, I want CAD tools to have clean, minimal dependencies, so that the module structure is clear and maintainable.

#### Acceptance Criteria

1. THE System SHALL import `requests` directly for HTTP operations
2. THE System SHALL import `get_endpoints` and `get_timeout` from `core.config`
3. THE System SHALL import `interceptor` from `core` module
4. THE System SHALL remove imports of `send_request` from `core.request_handler`
5. THE System SHALL remove imports of `get_headers` from `core.config`

### Requirement 6: Code Pattern Consistency

**User Story:** As a developer, I want all CAD tools to follow the same code patterns as CAM tools, so that the codebase is uniform and easier to understand.

#### Acceptance Criteria

1. WHEN making GET requests, THE System SHALL use `requests.get(endpoint, timeout=get_timeout())`
2. WHEN making POST requests, THE System SHALL use `requests.post(endpoint, json=data, timeout=get_timeout())`
3. WHEN processing responses, THE System SHALL use `return interceptor.intercept_response(endpoint, response, method)`
4. WHEN handling exceptions, THE System SHALL use try/except blocks with specific exception types
5. THE System SHALL follow the exact pattern established in `Server/tools/cam/toolpaths.py`

### Requirement 7: File Coverage

**User Story:** As a developer, I want all CAD tool files to be modernized, so that there are no inconsistencies in the CAD tools directory.

#### Acceptance Criteria

1. THE System SHALL modernize `Server/tools/cad/geometry.py` with all 3 functions
2. THE System SHALL modernize `Server/tools/cad/sketching.py` with all 5 functions  
3. THE System SHALL modernize `Server/tools/cad/modeling.py` with all 9 functions
4. THE System SHALL modernize `Server/tools/cad/features.py` with all 8 functions
5. THE System SHALL verify all 25 total CAD tool functions use the modern pattern

### Requirement 8: Testing and Validation

**User Story:** As a developer, I want to verify that modernized CAD tools work correctly, so that I can be confident in the changes.

#### Acceptance Criteria

1. WHEN CAD tools are modernized, THE System SHALL allow testing via direct HTTP calls to Fusion 360 add-in
2. WHEN testing CAD tools, THE System SHALL verify that responses match expected formats
3. WHEN running the MCP server, THE System SHALL load all modernized CAD tools without errors
4. WHEN calling CAD tools through MCP, THE System SHALL produce the same results as before modernization
5. THE System SHALL support response interception testing for all modernized CAD tools