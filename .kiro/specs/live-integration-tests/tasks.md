# Live Integration Tests Implementation Plan

## Overview

This implementation plan converts the Live Integration Tests design into actionable coding tasks. The plan follows an incremental approach, starting with shared infrastructure, then building out test coverage by category.

## Task List

- [x] 1. Foundation Infrastructure (Completed)
  - Basic test file created with HTTP client helper
  - Smoke tests implemented
  - Empty response detection tests implemented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 11.1, 11.2, 11.3_

- [x] 2. Shared Test Infrastructure
  - Create conftest.py with shared fixtures
  - Add pytest markers configuration
  - Create endpoint definition helpers
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 12.1, 12.2, 12.3_

- [x] 2.1 Create conftest.py with shared fixtures
  - Move `is_bridge_running()` and `make_request()` to conftest.py
  - Create `bridge_available` session-scoped fixture
  - Create `manufacture_workspace_required` fixture
  - Create `design_document_required` fixture
  - Add request timeout configuration
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.2 Add endpoint definition helpers
  - Create `EndpointDefinition` dataclass
  - Create endpoint registry for all known endpoints
  - Add helper to generate parameterized test cases
  - Add endpoint categorization (design, manufacture, system)
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 2.3 Configure pytest markers
  - Add `live` marker for all live tests
  - Add `smoke` marker for smoke tests
  - Add `slow` marker for tests that take > 5 seconds
  - Add `destructive` marker for tests that modify state
  - Update pyproject.toml with marker definitions
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 3. MANUFACTURE Workspace Tests
  - Comprehensive tests for CAM functionality
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.1 Create test_live_setups.py
  - Test `/cam/setups` list endpoint
  - Test `/cam/setups/{id}` get endpoint
  - Test `/cam/setups` create endpoint
  - Test `/cam/setups/{id}` modify endpoint
  - Test `/cam/setups/{id}` delete endpoint
  - Test `/cam/setups/{id}/duplicate` endpoint
  - Verify response structures match expected format
  - _Requirements: 4.1, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 3.2 Create test_live_toolpaths.py
  - Test `/cam/toolpaths` list endpoint
  - Test `/cam/toolpaths/{id}` get endpoint
  - Test `/cam/toolpaths/{id}/heights` endpoint
  - Test `/cam/toolpaths/{id}/passes` endpoint
  - Test `/cam/toolpaths/{id}/linking` endpoint
  - Test `/cam/toolpaths/{id}/parameters` endpoint
  - Verify toolpath response includes setup context
  - _Requirements: 4.2, 10.1, 10.2_

- [x] 3.3 Create test_live_tool_libraries.py
  - Test `/tool-libraries` list endpoint
  - Test `/tool-libraries/{id}` get endpoint
  - Test `/tool-libraries/tools` list endpoint
  - Test `/tool-libraries/tools/{id}` get endpoint
  - Test `/tool-libraries/search` endpoint
  - Verify tool response structures
  - _Requirements: 4.3, 10.1, 10.2_

- [x] 3.4 Create test_live_operations.py
  - Test `/cam/operations/{id}/tool` endpoint
  - Test `/cam/operations/{id}/heights` endpoint
  - Test `/cam/operations/{id}/heights/{param}` endpoint
  - Test `/cam/operations/{id}/passes` endpoint
  - Test `/cam/operations/{id}/linking` endpoint
  - Verify operation parameter responses
  - _Requirements: 4.4, 10.1, 10.2_

- [x] 4. Setup-Toolpath Integration Tests
  - Tests for bidirectional relationships
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.1 Add setup-toolpath relationship tests
  - Test `/cam/setups/{id}/toolpaths` returns toolpath list
  - Test `/cam/toolpaths/{id}/setup` returns parent setup
  - Test setup-toolpath mapping consistency
  - Test with invalid setup ID returns 404
  - Test with invalid toolpath ID returns 404
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.2 Add validation endpoint tests
  - Test `/cam/setups/{id}/toolpaths/{id}/validate` endpoint
  - Test validation with mismatched setup/toolpath
  - Test validation response structure
  - _Requirements: 5.5_

- [x] 5. Part Position Tests
  - Tests for part position configuration
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5.1 Add part position tests
  - Test `/cam/setups/{id}/part-position` GET endpoint
  - Test `/cam/setups/{id}/part-position` PUT endpoint
  - Test with invalid setup ID returns error
  - Test position validation (invalid coordinates)
  - Test orientation validation (invalid vectors)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6. Stock Configuration Tests
  - Tests for stock definition
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6.1 Add stock configuration tests
  - Test stock configuration returned with setup details
  - Test stock mode values (auto, box, cylinder, geometry)
  - Test stock dimension validation
  - Test stock position validation
  - Test stock change impact warnings
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7. WCS Configuration Tests
  - Tests for Work Coordinate System
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.1 Add WCS configuration tests
  - Test WCS configuration returned with setup details
  - Test WCS origin coordinates validation
  - Test WCS orientation vectors validation
  - Test WCS type values (model_origin, face_based, custom)
  - Test WCS change impact warnings
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8. Design Workspace Tests
  - Tests for geometry and sketching
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 8.1 Create test_live_design.py
  - Test `/test_connection` endpoint
  - Test `/draw-box` endpoint response
  - Test `/draw-cylinder` endpoint response
  - Test `/draw-circle` endpoint response
  - Test `/draw-lines` endpoint response
  - _Requirements: 3.1, 3.2_

- [x] 8.2 Add feature endpoint tests
  - Test `/extrude` endpoint response
  - Test `/revolve` endpoint response
  - Test `/fillet` endpoint response
  - Test `/shell` endpoint response
  - _Requirements: 3.3_

- [x] 8.3 Add export endpoint tests
  - Test `/export-step` endpoint response
  - Test `/export-stl` endpoint response
  - Test export with invalid parameters
  - _Requirements: 3.4_

- [x] 8.4 Add geometry error tests
  - Test geometry operations with invalid parameters
  - Test operations when no design is open
  - Verify error response structure
  - _Requirements: 3.5_

- [x] 9. Error Response Tests
  - Comprehensive error handling validation
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 9.1 Create test_live_errors.py
  - Test 404 responses for invalid IDs
  - Test 400 responses for missing parameters
  - Test 400 responses for invalid data
  - Test 500 responses include error details
  - Verify consistent error response structure
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 9.2 Add parameterized error tests
  - Create list of all endpoints with expected error scenarios
  - Parameterize tests for invalid ID responses
  - Parameterize tests for missing parameter responses
  - Verify error codes are consistent
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 13.3_

- [x] 10. Response Structure Validation
  - Validate API response consistency
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10.1 Add response structure tests
  - Test list endpoints include count and items array
  - Test get endpoints include all required fields
  - Test create endpoints include created entity ID
  - Test modify endpoints include updated entity
  - Test delete endpoints include confirmation
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10.2 Create response schema validators
  - Define JSON schemas for common response types
  - Create schema validation helper functions
  - Add schema validation to parameterized tests
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 11. Parameterized Endpoint Testing
  - Efficient multi-endpoint testing
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 11.1 Expand empty response detection
  - Add all Design workspace endpoints to check list
  - Add all MANUFACTURE workspace endpoints to check list
  - Add all system endpoints to check list
  - Verify parameterized test failure messages are clear
  - _Requirements: 2.4, 2.5, 13.1, 13.4, 13.5_

- [x] 11.2 Add response structure parameterized tests
  - Create endpoint-to-expected-fields mapping
  - Parameterize field presence tests
  - Parameterize field type tests
  - _Requirements: 13.2, 13.4_

- [x] 12. Documentation and Reporting
  - Clear test documentation
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 12.1 Add comprehensive docstrings
  - Add module-level docstrings to all test files
  - Add class-level docstrings explaining test categories
  - Add function-level docstrings for complex tests
  - Include usage instructions in main test file
  - _Requirements: 14.5_

- [x] 12.2 Improve failure messages
  - Add likely cause to all assertion messages
  - Add remediation steps to critical test failures
  - Include endpoint and method in all failure messages
  - _Requirements: 14.1, 14.2_

- [ ] 12.3 Add test summary reporting
  - Create custom pytest plugin for category summaries
  - Show pass/fail counts by test category
  - Show which endpoints were tested
  - _Requirements: 14.3, 14.4_

- [x] 13. Development Workflow Integration
  - Integrate tests into development process
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 13.1 Update documentation
  - Update README with live test instructions
  - Update python-testing.md steering file
  - Add troubleshooting guide for common issues
  - Document prerequisites clearly
  - _Requirements: 15.4, 15.5_

- [x] 13.2 Create development workflow guide
  - Document when to run smoke tests
  - Document when to run full test suite
  - Document how to add tests for new endpoints
  - Create checklist for handler changes
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 14. Final Validation
  - Ensure all tests pass and coverage is complete
  - _Requirements: All_

- [ ] 14.1 Run full test suite validation
  - Run all live tests with Fusion 360 active
  - Verify all tests pass or skip appropriately
  - Document any flaky tests
  - Measure total execution time
  - _Requirements: All_

- [ ] 14.2 Coverage analysis
  - List all HTTP endpoints in the add-in
  - Verify each endpoint has at least one test
  - Identify gaps in test coverage
  - Create issues for missing tests
  - _Requirements: All_

## Notes

- Tasks are ordered by priority and dependency
- Phase 1 (Foundation) is complete with basic infrastructure
- Phase 2 (MANUFACTURE workspace) is complete
- Phase 3 (Design workspace) is complete
- Phase 4 (Error and structure validation) is complete
- Task 12.3 (test summary reporting) deferred - requires custom pytest plugin
- Task 14 (Final Validation) requires running with Fusion 360 active
- All tests should be runnable independently
- Tests should skip gracefully when prerequisites aren't met

## Test Files Created

| File | Description | Test Count (approx) |
|------|-------------|---------------------|
| `conftest.py` | Shared fixtures and endpoint registry | N/A |
| `helpers.py` | Shared helper functions (make_request, etc.) | N/A |
| `test_live_integration.py` | Original smoke tests | ~15 |
| `test_live_setups.py` | Setup management | ~20 |
| `test_live_toolpaths.py` | Toolpath management | ~15 |
| `test_live_tool_libraries.py` | Tool library management | ~20 |
| `test_live_operations.py` | Operation management | ~15 |
| `test_live_setup_toolpath.py` | Setup-toolpath relationships | ~15 |
| `test_live_part_position.py` | Part position configuration | ~10 |
| `test_live_stock.py` | Stock configuration | ~15 |
| `test_live_wcs.py` | WCS configuration | ~15 |
| `test_live_design.py` | Design workspace | ~20 |
| `test_live_errors.py` | Error handling | ~20 |

**Total: 172 live integration tests** (verified via pytest collection)
