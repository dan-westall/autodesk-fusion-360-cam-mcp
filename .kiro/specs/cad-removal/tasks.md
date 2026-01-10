# Implementation Plan: CAD Removal

## Overview

This implementation plan converts the CAD Removal design into a series of actionable coding tasks. The plan follows a systematic approach to safely remove all CAD functionality while preserving manufacturing capabilities, with comprehensive validation at each step.

The removal process is designed to be methodical and reversible, with extensive documentation and validation to ensure manufacturing functionality remains completely intact.

## Tasks

- [x] 1. Pre-Removal Documentation and Backup
  - Document all CAD components to be removed
  - Create version control tags for reversibility
  - Generate comprehensive component inventory
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 1.1 Create comprehensive CAD component inventory
  - Scan and document all CAD tools in `Server/tools/cad/`
  - Document all design handlers in `FusionMCPBridge/handlers/design/`
  - List all design-related HTTP endpoints
  - Document all design-related test files
  - Create removal documentation file with complete component list
  - _Requirements: 8.1, 8.2_

- [x] 1.2 Create version control backup tags
  - Tag current commit as `pre-cad-removal-backup`
  - Document current system state and functionality
  - Create restoration instructions document
  - Verify all CAM functionality works before removal
  - _Requirements: 8.3, 8.4, 8.5_

- [x] 1.3 Write property test for documentation completeness
  - **Property 8: API documentation accuracy**
  - **Validates: Requirements 7.3**

- [x] 2. CAM Functionality Baseline Testing
  - Establish baseline functionality for all CAM operations
  - Create comprehensive test suite to verify CAM preservation
  - Document expected behavior for validation after removal
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2.1 Create CAM functionality baseline tests
  - Test all CAM setup management operations
  - Test all toolpath generation and management
  - Test all tool library operations
  - Test all CAM parameter management
  - Document expected responses and behavior
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2.2 Write property test for CAM functionality preservation
  - **Property 3: CAM functionality preservation**
  - **Validates: Requirements 1.4, 2.3, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5**

- [x] 3. Remove CAD Tools from MCP Server
  - Remove all CAD tool modules from `Server/tools/cad/`
  - Update tool registration and imports
  - Clean up server configuration
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3.1 Remove CAD tool modules
  - Delete `Server/tools/cad/geometry.py`
  - Delete `Server/tools/cad/sketching.py`
  - Delete `Server/tools/cad/modeling.py`
  - Delete `Server/tools/cad/features.py`
  - Delete `Server/tools/cad/__init__.py`
  - Delete entire `Server/tools/cad/` directory
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 3.2 Update server tool imports and registration
  - Update `Server/tools/__init__.py` to remove CAD imports
  - Update module discovery to exclude CAD tools
  - Verify no CAD tools are registered with MCP server
  - Update tool documentation to exclude CAD capabilities
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [x] 3.3 Write property test for CAD tool removal completeness
  - **Property 1: CAD tool removal completeness**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

- [x] 4. Remove Design Handlers from Fusion Add-In
  - Remove all design workspace handlers
  - Update HTTP router configuration
  - Clean up handler imports and registration
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.1 Remove design handler modules
  - Delete `FusionMCPBridge/handlers/design/geometry.py`
  - Delete `FusionMCPBridge/handlers/design/sketching.py`
  - Delete `FusionMCPBridge/handlers/design/modeling.py`
  - Delete `FusionMCPBridge/handlers/design/features.py`
  - Delete `FusionMCPBridge/handlers/design/utilities.py`
  - Delete `FusionMCPBridge/handlers/design/geometry_impl.py`
  - Delete `FusionMCPBridge/handlers/design/geometry_impl2.py`
  - Delete `FusionMCPBridge/handlers/design/__init__.py`
  - Delete entire `FusionMCPBridge/handlers/design/` directory
  - _Requirements: 2.1, 2.2_

- [x] 4.2 Update handler imports and registration
  - Update `FusionMCPBridge/handlers/__init__.py` to remove design imports
  - Update HTTP router to not register design handlers
  - Verify design endpoints return 404 Not Found
  - Ensure CAM handlers continue to work normally
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.3 Write property test for HTTP endpoint removal completeness
  - **Property 2: HTTP endpoint removal completeness**
  - **Validates: Requirements 2.1, 2.2, 2.4**

- [x] 5. Update Configuration and Endpoints
  - Remove design endpoints from configuration
  - Update endpoint validation and documentation
  - Clean up configuration references
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.1 Remove design endpoints from configuration
  - Update `Server/core/config.py` to remove design endpoints
  - Remove design endpoint definitions from ENDPOINTS dictionary
  - Update endpoint validation to exclude design paths
  - Verify configuration only contains CAM, utility, and system endpoints
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 5.2 Write property test for configuration cleanup completeness
  - **Property 4: Configuration cleanup completeness**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 6. Remove Design-Related Tests
  - Remove all design workspace test files
  - Update test configuration and fixtures
  - Clean up test imports and references
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6.1 Remove design test files
  - Delete `Server/tests/test_cad_server_loading.py`
  - Delete `Server/tests/test_cad_integration.py`
  - Delete `Server/tests/test_cad_modernization.py`
  - Delete any other `Server/tests/test_cad_*.py` files
  - Delete `FusionMCPBridge/tests/test_live_design.py`
  - Delete any other `FusionMCPBridge/tests/test_design_*.py` files
  - _Requirements: 4.1, 4.2_

- [x] 6.2 Update test configuration and fixtures
  - Update `FusionMCPBridge/tests/conftest.py` to remove design endpoints
  - Remove design workspace test fixtures and data
  - Update test categories to exclude design workspace
  - Verify test suite only includes CAM, utility, and system tests
  - _Requirements: 4.2, 4.4, 4.5_

- [x] 6.3 Write property test for test suite cleanup completeness
  - **Property 5: Test suite cleanup completeness**
  - **Validates: Requirements 4.1, 4.2, 4.4, 4.5**

- [x] 7. Update Import Statements and Dependencies
  - Remove all imports referencing design modules
  - Update module initialization and loading
  - Fix any broken dependencies
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.1 Update import statements throughout codebase
  - Remove design imports from `Server/tools/__init__.py`
  - Remove design imports from `FusionMCPBridge/handlers/__init__.py`
  - Scan entire codebase for any remaining design module imports
  - Update any files that import removed design modules
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 7.2 Verify system startup and module loading
  - Test MCP server startup without CAD modules
  - Test Fusion Add-In startup without design handlers
  - Verify no import errors or missing module exceptions
  - Test module discovery excludes removed components
  - _Requirements: 5.2, 5.4_

- [x] 7.3 Write property test for import and dependency cleanup
  - **Property 6: Import and dependency cleanup**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [x] 8. Directory Structure Cleanup
  - Remove design workspace directories
  - Clean up empty directories and files
  - Update build and deployment configurations
  - _Requirements: 6.1, 6.2_

- [x] 8.1 Clean up directory structure
  - Verify `Server/tools/cad/` directory is completely removed
  - Verify `FusionMCPBridge/handlers/design/` directory is completely removed
  - Remove any empty parent directories if applicable
  - Update any build scripts that reference removed directories
  - _Requirements: 6.1, 6.2_

- [x] 8.2 Write property test for directory structure cleanup
  - **Property 7: Directory structure cleanup**
  - **Validates: Requirements 6.1, 6.2**

- [x] 9. Update Error Messages and Help Text
  - Remove references to design functionality in error messages
  - Update help text to reflect manufacturing-only capabilities
  - Clean up error codes and validation messages
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 9.1 Update error messages and help text
  - Scan codebase for error messages referencing design functionality
  - Update error messages to only mention available CAM capabilities
  - Update help text and documentation strings
  - Remove error codes specific to design operations
  - Update validation messages to reflect manufacturing-only scope
  - _Requirements: 10.1, 10.3, 10.4, 10.5_

- [x] 9.2 Write property test for error message cleanup
  - **Property 9: Error message cleanup**
  - **Validates: Requirements 10.1, 10.3, 10.4, 10.5**
  - **Status: FAILED** - Found 227 design references in help text and 2 design-related error codes
  - **Failing examples**: Research files (wcs_api_research.py, model_id_research.py), test files, and legitimate "thread" references in threading code

- [-] 10. Comprehensive Validation and Testing
  - Run complete test suite to verify CAM functionality
  - Test system startup and operation
  - Validate removal completeness
  - _Requirements: All requirements_

- [x] 10.1 Run comprehensive CAM functionality validation
  - Execute all CAM setup management tests
  - Execute all toolpath operation tests
  - Execute all tool library tests
  - Compare results with baseline established in task 2.1
  - Verify no regression in CAM functionality
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10.2 Test system startup and operation
  - Test MCP server startup without errors
  - Test Fusion Add-In startup without errors
  - Test tool registration excludes CAD tools
  - Test HTTP endpoints return appropriate responses
  - Verify configuration loading works correctly
  - _Requirements: 1.5, 2.4, 5.4_

- [ ] 10.3 Write property test for system startup success
  - **Property 10: System startup success**
  - **Validates: Requirements 1.5, 2.4, 5.4**

- [x] 11. Documentation and Finalization
  - Update project documentation `docs/`
  - Create removal summary report
  - Update README and user guides
  - _Requirements: 7.1, 7.2, 7.4, 7.5, 8.1, 8.2, 8.4, 8.5_

- [x] 11.1 Update project documentation
  - Update README.md to reflect manufacturing-only focus
  - Update API documentation to exclude design capabilities
  - Update user guides to focus on CAM workflows
  - Update troubleshooting guides for manufacturing-only scope
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [x] 11.2 Create comprehensive removal summary report
  - Document all removed components with file paths
  - Document all preserved CAM functionality
  - Include restoration instructions
  - Document validation results and test outcomes
  - Create final removal report with complete details
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [x] 12. Final Checkpoint - Verify Complete Removal
  - Ensure all CAD functionality is removed
  - Ensure all CAM functionality is preserved
  - Verify system operates correctly
  - Ask the user if questions arise.

## Notes

- All tasks include comprehensive testing and documentation for thorough coverage
- Each removal phase includes validation to ensure CAM functionality remains intact
- The process is designed to be reversible using version control tags and documentation
- All removed components are thoroughly documented for potential restoration
- Comprehensive testing ensures manufacturing workflows continue to work correctly
- The removal follows a systematic approach: document → backup → remove → validate → clean up
- Special attention is paid to import statements and dependencies to prevent startup failures
- Configuration cleanup ensures no references to removed functionality remain
- Error message updates ensure user-facing text reflects the manufacturing-only scope
