# Implementation Plan

## Overview

This implementation plan converts the CAM Setup Management design into a series of actionable coding tasks. The plan follows an incremental approach, starting with API research and basic functionality, then building up to complete setup management capabilities with full integration to existing toolpath functionality.

**New Requirements Added:**
- Requirement 12: Part Position configuration
- Requirement 13: Modular directory structure (`handlers/manufacture/setups/`)

## Task List

- [x] 1. API Research and Foundation
  - Research Fusion 360 WCS API structure and model ID handling
  - Document actual API patterns and data structures
  - Create foundation for setup management functionality
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 1.1 Research WCS API structure and capabilities
  - Investigate `adsk.cam.Setup` WCS properties and methods
  - Document available orientation options (model-based, face-based, etc.)
  - Research origin specification methods (model origin, geometry-based, custom)
  - Document model ID structure and how to reference design geometry
  - Create API documentation for WCS configuration
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 1.2 Research model ID handling and validation
  - Investigate how model IDs are obtained from design workspace
  - Document model ID validation methods
  - Research integration between CAM setup creation and design workspace
  - Test model ID resolution and geometry referencing
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 1.3 Create Fusion 360 business language steering file
  - Document WCS terminology instead of "coordinate_system"
  - Document model structure (root level, not nested under WCS)
  - Document Design vs CAD terminology alignment
  - Create consistency guidelines for future development
  - _Requirements: All requirements (terminology consistency)_

- [ ]* 1.4 Write property test for API research validation
  - **Property 12: Error handling robustness**
  - **Validates: Requirements 2.5, 3.5, 5.4, 6.5, 7.5, 9.5, 12.5**

- [x] 2. Basic Setup Management Infrastructure
  - Create core setup management functions in Fusion Add-In
  - Implement basic setup creation, listing, and retrieval
  - Set up HTTP endpoints for setup operations
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 2.1 Implement core setup functions in setups.py handler
  - Create `create_setup_impl()` function with basic configuration
  - Implement `list_setups_detailed()` function
  - Create `get_setup_by_id_impl()` function
  - Add setup validation and error handling
  - Use proper WCS terminology throughout
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [ ]* 2.2 Write property test for setup creation completeness
  - **Property 1: Setup creation completeness**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

- [x] 2.3 Add HTTP endpoints for basic setup operations
  - Add `POST /cam/setups` endpoint for setup creation
  - Add `GET /cam/setups` endpoint for setup listing
  - Add `GET /cam/setups/{id}` endpoint for setup details
  - Implement proper error handling and status codes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [ ]* 2.4 Write property test for setup information retrieval
  - **Property 4: Setup information retrieval consistency**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 3. WCS Configuration Implementation
  - Implement work coordinate system configuration based on API research
  - Add WCS validation and error handling
  - Support multiple WCS configuration methods
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3.1 Implement WCS configuration functions
  - Create WCS configuration logic in `handlers/manufacture/wcs.py`
  - Implement origin positioning and orientation alignment
  - Add model ID integration for WCS reference
  - Include comprehensive WCS validation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 3.2 Write property test for WCS configuration consistency
  - **Property 2: WCS configuration consistency**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 4. Stock Configuration Implementation
  - Implement stock definition and configuration
  - Add support for multiple stock modes (auto, geometry, primitives)
  - Include stock validation and positioning
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 Implement stock configuration functions
  - Create automatic stock detection in `handlers/manufacture/stock.py`
  - Implement geometry-based stock definition
  - Add primitive stock creation (box, cylinder)
  - Include stock positioning relative to WCS
  - Add material property application
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 4.2 Write property test for stock configuration accuracy
  - **Property 3: Stock configuration accuracy**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 5. MCP Server Tools Implementation
  - Create MCP tools for setup management in Server/tools/cam/setups.py
  - Implement all setup management tools with proper validation
  - Add integration with existing CAM tool patterns
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3_

- [x] 5.1 Create setup management MCP tools
  - Implement `create_cam_setup()` tool
  - Create `list_cam_setups()` tool
  - Add `get_setup_details()` tool
  - Include proper error handling and validation
  - Follow existing CAM tool patterns
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 5.2 Add setup configuration endpoints
  - Extend configuration with setup-specific endpoints
  - Update `Server/core/config.py` with new CAM setup endpoints
  - Ensure consistency with existing endpoint patterns
  - _Requirements: All setup management requirements_

- [x] 6. Setup Modification and Deletion MCP Tools
  - Add MCP tools for modify, delete, and duplicate operations
  - Include proper validation and error handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6.1 Add modification and deletion MCP tools
  - Implement `modify_setup_configuration()` tool in Server/tools/cam/setups.py
  - Create `delete_cam_setup()` tool with confirmation
  - Implement `duplicate_cam_setup()` tool
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6.2 Wire HTTP handlers for modify/delete/duplicate
  - Wire `PUT /cam/setups/{id}` handler to modify_setup_impl
  - Wire `DELETE /cam/setups/{id}` handler to delete_setup_impl
  - Wire `POST /cam/setups/{id}/duplicate` handler to duplicate_setup_impl
  - _Requirements: 5.1, 6.1, 7.1_

- [ ]* 6.3 Write property test for setup modification preservation
  - **Property 5: Setup modification preservation**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**

- [ ]* 6.4 Write property test for setup deletion completeness
  - **Property 6: Setup deletion completeness**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [ ]* 6.5 Write property test for setup duplication fidelity
  - **Property 7: Setup duplication fidelity**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [x] 7. Wire Handler Integration for Modify/Duplicate/Delete
  - Connect HTTP handlers to business logic functions
  - All handlers now call actual implementation functions
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7.1 Implement modify_setup business logic function
  - Create `modify_setup_impl()` function in setups.py handler
  - Add impact analysis for WCS and stock changes
  - Include operation preservation logic
  - Implement proper error handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.2 Wire handle_modify_setup to modify_setup_impl function
  - Update FusionMCPBridge/handlers/manufacture/setups.py handle_modify_setup
  - Call modify_setup_impl() with proper task queue integration
  - Handle response formatting and error codes
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.3 Implement duplicate_setup business logic function
  - Create `duplicate_setup_impl()` function in setups.py handler
  - Copy WCS, stock, and operation configurations
  - Implement automatic name generation for duplicates
  - Add validation and error handling
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7.4 Wire handle_duplicate_setup to duplicate_setup_impl function
  - Update FusionMCPBridge/handlers/manufacture/setups.py handle_duplicate_setup
  - Call duplicate_setup_impl() with proper task queue integration
  - Handle response formatting and error codes
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7.5 Implement delete_setup business logic function
  - Create `delete_setup_impl()` function in setups.py handler
  - Add toolpath impact warnings
  - Implement complete setup and operation removal
  - Include proper error handling for edge cases
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7.6 Wire handle_delete_setup to delete_setup_impl function
  - Update FusionMCPBridge/handlers/manufacture/setups.py handle_delete_setup
  - Call delete_setup_impl() with proper task queue integration
  - Handle response formatting and error codes
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Multi-Setup Document Management
  - Multi-setup support implemented via list_setups_detailed()
  - Unique identification via entityToken in place
  - Name collision checking in create_setup_impl()
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 9.1 Write property test for multi-setup document consistency
  - **Property 8: Multi-setup document consistency**
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 10. Setup-Toolpath Integration
  - Implement bidirectional setup-toolpath relationships
  - Add toolpath context and setup association
  - Create helper functions for relationship management
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 10.1 Implement setup-toolpath relationship functions
  - Create `get_toolpaths_for_setup()` function using existing toolpath functionality
  - Implement `find_setup_for_toolpath()` helper function
  - Add `validate_setup_toolpath_relationship()` function
  - Include setup context in toolpath responses
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.5_

- [ ]* 10.2 Write property test for toolpath-setup association integrity
  - **Property 9: Toolpath-setup association integrity**
  - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**

- [x] 10.3 Implement bidirectional relationship helper functions
  - Create comprehensive setup-toolpath mapping functions
  - Add toolpath movement between setups (if supported by API)
  - Implement consistent ID mapping maintenance
  - Include detailed error context for relationship operations
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 10.4 Write property test for existing functionality integration
  - **Property 10: Existing functionality integration**
  - **Validates: Requirements 10.1, 10.2, 10.3, 10.5**

- [ ]* 10.5 Write property test for bidirectional relationship consistency
  - **Property 11: Bidirectional relationship consistency**
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**

- [x] 10.6 Add setup-toolpath integration MCP tools and HTTP endpoints
  - Implement `get_setup_toolpaths()` MCP tool in Server/tools/cam/setups.py
  - Create `find_toolpath_setup()` MCP tool
  - Add HTTP handlers in FusionMCPBridge/handlers/manufacture/setups.py
  - Update Server/core/config.py with new endpoints if needed
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.5, 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Integration Testing and Documentation
  - Create comprehensive integration tests
  - Update documentation and examples
  - Validate end-to-end functionality
  - _Requirements: All requirements_

- [x] 12.1 Create integration tests
  - Test complete setup management workflows
  - Validate integration with existing toolpath functionality
  - Test error scenarios and edge cases
  - Include multi-setup document testing
  - _Requirements: All requirements_

- [x] 12.2 Write comprehensive unit tests
  - Create unit tests for all setup management functions
  - Test WCS configuration and validation
  - Test stock configuration and positioning
  - Test part position configuration and validation
  - Test setup modification and deletion
  - Test setup-toolpath relationship functions
  - _Requirements: All requirements_

- [x] 12.3 Update documentation and examples
  - Document new setup management tools and endpoints
  - Create usage examples for common workflows
  - Update API documentation with setup functionality
  - Include troubleshooting guide for setup operations
  - _Requirements: All requirements_

- [x] 13. Final Checkpoint - Make sure all tests are passing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Part Position Implementation (Requirement 12)
  - Implement part position configuration functionality
  - Add support for position and orientation relative to WCS
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 14.1 Research Part Position API
  - Investigate `adsk.cam.Setup` part position properties and methods
  - Document available positioning options (origin, orientation)
  - Research how part position relates to WCS
  - Document API structure for part position configuration
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 14.2 Implement part position functions in part_position.py
  - Create `get_part_position_impl()` function
  - Implement `set_part_position_impl()` function with origin and orientation
  - Add `validate_part_position()` function
  - Include impact analysis for dependent operations and toolpaths
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 14.3 Add Part Position HTTP endpoints
  - Add `GET /cam/setups/{id}/part-position` endpoint
  - Add `PUT /cam/setups/{id}/part-position` endpoint
  - Wire handlers to part_position.py functions
  - Implement proper error handling and status codes
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 14.4 Add Part Position MCP tools
  - Implement `get_part_position()` MCP tool in Server/tools/cam/setups.py
  - Create `set_part_position()` MCP tool
  - Include proper error handling and validation
  - Follow existing CAM tool patterns
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 14.5 Write property test for part position configuration accuracy
  - **Property 13: Part position configuration accuracy**
  - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**

- [x] 15. Modular Directory Structure Refactoring (Requirement 13)
  - Refactor existing setups.py to modular directory structure
  - Align with existing `operations/` and `tool_libraries/` patterns
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15.1 Create modular setups directory structure
  - Create `FusionMCPBridge/handlers/manufacture/setups/` directory
  - Create `__init__.py` with public function exports
  - Create `setup.py` for core setup management functions
  - Create `stock.py` for stock configuration functions
  - Create `part_position.py` for part position functions
  - Create `wcs.py` for WCS configuration functions
  - Follow patterns from `operations/` and `tool_libraries/` modules
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15.2 Migrate existing setups.py code to modular structure
  - Move setup core functions to `setups/setup.py`
  - Move stock functions to `setups/stock.py`
  - Move WCS functions to `setups/wcs.py`
  - Update `__init__.py` to export all public functions
  - Update imports in dependent modules (manufacture/__init__.py updated)
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15.3 Verify modular structure and update tests
  - Verify all HTTP handlers still work after refactoring
  - All 298 tests pass with new modular structure
  - Backward compatibility maintained via re-exports in __init__.py
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ]* 15.4 Write property test for modular architecture compliance
  - **Property 14: Modular architecture compliance**
  - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

- [x] 16. Final Checkpoint - Verify all new functionality
  - Ensure all tests pass for Part Position and modular structure
  - Verify HTTP endpoints work correctly
  - Verify MCP tools work correctly
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests
- All core setup management functionality (create, list, get, modify, duplicate, delete) is implemented
- HTTP handlers are fully wired to business logic functions
- Multi-setup management is complete through existing list/create functions
- Setup-toolpath integration builds on existing toolpath functionality in operations/toolpaths.py
- **NEW: Tasks 14.x** - Part Position implementation (Requirement 12)
- **NEW: Tasks 15.x** - Modular directory structure refactoring (Requirement 13)
- Modular structure follows patterns from `operations/` and `tool_libraries/` modules:
  ```
  handlers/manufacture/setups/
  ├── __init__.py
  ├── setup.py
  ├── stock.py
  ├── part_position.py
  └── wcs.py
  ```
