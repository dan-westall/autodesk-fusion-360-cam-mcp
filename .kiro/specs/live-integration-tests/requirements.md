# Live Integration Tests Requirements

## Introduction

This specification defines requirements for comprehensive live integration tests that run against the active Fusion 360 add-in. These tests fill a critical gap in the testing strategy by catching runtime issues that unit tests cannot detect, such as the task_queue callback pattern bug that causes handlers to return empty `{}` responses.

## Glossary

- **Live_Test**: A test that makes real HTTP requests to the running Fusion 360 add-in
- **Bridge**: The FusionMCPBridge HTTP server running inside Fusion 360 on port 5001
- **Smoke_Test**: Quick validation tests that verify basic functionality
- **Empty_Response_Bug**: The bug where handlers using task_queue callbacks return `{}`
- **Handler**: HTTP request handler function in the add-in
- **Endpoint**: HTTP URL path that maps to a handler
- **MANUFACTURE_Workspace**: Fusion 360's CAM workspace (official terminology)
- **Design_Workspace**: Fusion 360's design/modeling workspace

## Requirements

### Requirement 1: Test Infrastructure

**User Story:** As a developer, I want a test infrastructure that can make HTTP requests to the live add-in, so that I can validate real endpoint behavior.

#### Acceptance Criteria

1. WHEN running live tests THEN the test framework SHALL check if the bridge is running before executing tests
2. WHEN the bridge is not running THEN the test framework SHALL skip all live tests with a clear message
3. WHEN making HTTP requests THEN the test framework SHALL support GET, POST, PUT, and DELETE methods
4. WHEN requests timeout THEN the test framework SHALL handle timeouts gracefully and report them
5. WHEN responses are received THEN the test framework SHALL parse JSON and provide structured results

### Requirement 2: Empty Response Detection

**User Story:** As a developer, I want tests that detect empty `{}` responses, so that I can catch the task_queue callback bug before deployment.

#### Acceptance Criteria

1. WHEN testing any endpoint THEN the test SHALL fail if the response is an empty `{}`
2. WHEN an empty response is detected THEN the test SHALL provide a clear error message explaining the likely cause
3. WHEN testing read-only endpoints THEN the test SHALL verify they return meaningful data
4. WHEN testing write endpoints THEN the test SHALL verify they return confirmation or error details
5. WHEN parameterizing tests THEN the test framework SHALL test multiple endpoints for empty responses

### Requirement 3: Design Workspace Tests

**User Story:** As a developer, I want tests for Design workspace endpoints, so that I can validate geometry creation and manipulation functionality.

#### Acceptance Criteria

1. WHEN testing geometry endpoints THEN the tests SHALL verify `/draw-box`, `/draw-cylinder`, and similar endpoints
2. WHEN testing sketch endpoints THEN the tests SHALL verify `/draw-circle`, `/draw-lines`, and similar endpoints
3. WHEN testing feature endpoints THEN the tests SHALL verify `/extrude`, `/revolve`, `/fillet`, and similar endpoints
4. WHEN testing export endpoints THEN the tests SHALL verify `/export-step` and `/export-stl` endpoints
5. WHEN geometry operations fail THEN the tests SHALL verify appropriate error responses

### Requirement 4: MANUFACTURE Workspace Tests

**User Story:** As a developer, I want tests for MANUFACTURE workspace endpoints, so that I can validate CAM functionality.

#### Acceptance Criteria

1. WHEN testing setup endpoints THEN the tests SHALL verify `/cam/setups` list, get, create, modify, delete, and duplicate
2. WHEN testing toolpath endpoints THEN the tests SHALL verify `/cam/toolpaths` and related endpoints
3. WHEN testing tool library endpoints THEN the tests SHALL verify `/tool-libraries` and related endpoints
4. WHEN testing operation endpoints THEN the tests SHALL verify heights, passes, and linking endpoints
5. WHEN CAM operations require MANUFACTURE workspace THEN the tests SHALL handle workspace errors gracefully

### Requirement 5: Setup-Toolpath Integration Tests

**User Story:** As a developer, I want tests for setup-toolpath relationships, so that I can validate bidirectional navigation between setups and toolpaths.

#### Acceptance Criteria

1. WHEN testing setup toolpaths THEN the tests SHALL verify `/cam/setups/{id}/toolpaths` returns toolpath list
2. WHEN testing toolpath setup THEN the tests SHALL verify `/cam/toolpaths/{id}/setup` returns parent setup
3. WHEN testing setup-toolpath mapping THEN the tests SHALL verify bidirectional consistency
4. WHEN testing with invalid IDs THEN the tests SHALL verify appropriate 404 responses
5. WHEN testing validation endpoints THEN the tests SHALL verify relationship validation works

### Requirement 6: Part Position Tests

**User Story:** As a developer, I want tests for part position endpoints, so that I can validate part positioning relative to WCS.

#### Acceptance Criteria

1. WHEN testing get part position THEN the tests SHALL verify `/cam/setups/{id}/part-position` returns position data
2. WHEN testing set part position THEN the tests SHALL verify position updates are accepted
3. WHEN testing with invalid setup ID THEN the tests SHALL verify appropriate error responses
4. WHEN testing position validation THEN the tests SHALL verify invalid positions are rejected
5. WHEN position affects operations THEN the tests SHALL verify impact warnings are returned

### Requirement 7: Stock Configuration Tests

**User Story:** As a developer, I want tests for stock configuration endpoints, so that I can validate stock definition functionality.

#### Acceptance Criteria

1. WHEN testing get stock THEN the tests SHALL verify `/cam/setups/{id}/stock` returns stock configuration
2. WHEN testing set stock THEN the tests SHALL verify stock updates are accepted
3. WHEN testing stock modes THEN the tests SHALL verify auto, box, cylinder, and geometry modes
4. WHEN testing stock dimensions THEN the tests SHALL verify dimension validation
5. WHEN stock changes affect operations THEN the tests SHALL verify impact warnings

### Requirement 8: WCS Configuration Tests

**User Story:** As a developer, I want tests for WCS configuration endpoints, so that I can validate Work Coordinate System functionality.

#### Acceptance Criteria

1. WHEN testing get WCS THEN the tests SHALL verify WCS configuration is returned with setup details
2. WHEN testing WCS origin THEN the tests SHALL verify origin coordinates are valid
3. WHEN testing WCS orientation THEN the tests SHALL verify axis vectors are valid
4. WHEN testing WCS types THEN the tests SHALL verify model_origin, face_based, and custom types
5. WHEN WCS changes affect operations THEN the tests SHALL verify impact warnings

### Requirement 9: Error Response Validation

**User Story:** As a developer, I want tests that validate error responses, so that I can ensure consistent error handling across all endpoints.

#### Acceptance Criteria

1. WHEN testing with invalid IDs THEN the tests SHALL verify 404 responses with SETUP_NOT_FOUND or similar codes
2. WHEN testing with missing parameters THEN the tests SHALL verify 400 responses with clear messages
3. WHEN testing with invalid data THEN the tests SHALL verify validation error responses
4. WHEN testing server errors THEN the tests SHALL verify 500 responses include error details
5. WHEN testing all error codes THEN the tests SHALL verify consistent error response structure

### Requirement 10: Response Structure Validation

**User Story:** As a developer, I want tests that validate response structures, so that I can ensure API consistency.

#### Acceptance Criteria

1. WHEN testing list endpoints THEN the tests SHALL verify responses include count and items array
2. WHEN testing get endpoints THEN the tests SHALL verify responses include all required fields
3. WHEN testing create endpoints THEN the tests SHALL verify responses include created entity ID
4. WHEN testing modify endpoints THEN the tests SHALL verify responses include updated entity
5. WHEN testing delete endpoints THEN the tests SHALL verify responses include confirmation

### Requirement 11: Smoke Test Suite

**User Story:** As a developer, I want a quick smoke test suite, so that I can rapidly validate basic functionality after changes.

#### Acceptance Criteria

1. WHEN running smoke tests THEN the tests SHALL complete in under 10 seconds
2. WHEN smoke tests run THEN they SHALL test bridge connectivity first
3. WHEN smoke tests run THEN they SHALL test at least one endpoint from each major category
4. WHEN smoke tests fail THEN they SHALL provide clear indication of which category failed
5. WHEN smoke tests pass THEN the developer SHALL have confidence to run full test suite

### Requirement 12: Test Markers and Organization

**User Story:** As a developer, I want tests organized with markers, so that I can run specific test categories.

#### Acceptance Criteria

1. WHEN tests are marked THEN all live tests SHALL have the `@pytest.mark.live` marker
2. WHEN running tests THEN developers SHALL be able to skip live tests with `-m "not live"`
3. WHEN organizing tests THEN tests SHALL be grouped by functionality (setup, toolpath, etc.)
4. WHEN naming tests THEN test names SHALL clearly indicate what they validate
5. WHEN documenting tests THEN each test class SHALL have a docstring explaining its purpose

### Requirement 13: Parameterized Endpoint Testing

**User Story:** As a developer, I want parameterized tests for multiple endpoints, so that I can efficiently test many endpoints with the same validation logic.

#### Acceptance Criteria

1. WHEN testing empty responses THEN the tests SHALL parameterize across all critical endpoints
2. WHEN testing response structures THEN the tests SHALL parameterize validation rules
3. WHEN testing error responses THEN the tests SHALL parameterize error scenarios
4. WHEN adding new endpoints THEN developers SHALL be able to add them to parameterized lists
5. WHEN parameterized tests fail THEN the failure message SHALL indicate which endpoint failed

### Requirement 14: Test Documentation and Reporting

**User Story:** As a developer, I want clear test documentation and reporting, so that I can understand test results and fix issues.

#### Acceptance Criteria

1. WHEN tests fail THEN the failure message SHALL explain the likely cause
2. WHEN tests fail THEN the failure message SHALL suggest remediation steps
3. WHEN running tests THEN the output SHALL show which endpoints were tested
4. WHEN tests complete THEN a summary SHALL show pass/fail counts by category
5. WHEN documenting tests THEN the test file SHALL include usage instructions

### Requirement 15: Development Workflow Integration

**User Story:** As a developer, I want live tests integrated into my development workflow, so that I can catch issues before committing.

#### Acceptance Criteria

1. WHEN making handler changes THEN the workflow SHALL include running smoke tests
2. WHEN adding new endpoints THEN the workflow SHALL include adding live tests
3. WHEN fixing bugs THEN the workflow SHALL include running relevant live tests
4. WHEN tests are available THEN the README SHALL document how to run them
5. WHEN tests require Fusion 360 THEN the documentation SHALL explain prerequisites
