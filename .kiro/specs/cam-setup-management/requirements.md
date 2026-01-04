# Requirements Document

## Introduction

This specification defines the requirements for CAM setup management functionality in the Fusion 360 MCP Server. CAM setups are fundamental organizational units in Fusion 360's manufacturing workspace that define machining operations, coordinate systems, stock definitions, and toolpath groupings. This feature will enable AI assistants to create, configure, and manage CAM setups through natural language commands, making CAM workflow setup more accessible and efficient.

## Glossary

- **CAM_Setup**: A CAM setup object in Fusion 360 that contains machining operations, WCS definitions, stock configuration, and toolpath organization
- **CAM_System**: The CAM functionality within Fusion 360 that processes setup management requests
- **MCP_Server**: The Model Context Protocol server that bridges AI assistants with Fusion 360
- **Fusion_Add_In**: The HTTP server running inside Fusion 360 that executes CAM API operations
- **WCS**: Work Coordinate System - the coordinate system definition that establishes the origin and orientation for machining operations
- **Stock_Definition**: The material definition including dimensions, position, and material properties for the workpiece
- **Part_Position**: The position and orientation of the part geometry relative to the WCS within a setup
- **Operation_Group**: A collection of related machining operations within a setup
- **Setup_Template**: A predefined configuration that can be applied to new setups for consistency
- **Toolpath**: The generated machining path for an operation within a setup

## Requirements

### Requirement 1

**User Story:** As a CAM programmer, I want to create new CAM setups with basic configuration, so that I can organize my machining operations efficiently.

#### Acceptance Criteria

1. WHEN a user requests to create a CAM setup with a name THEN the CAM_System SHALL create a new setup with the specified name
2. WHEN creating a setup THEN the CAM_System SHALL assign a default work coordinate system at the model origin
3. WHEN creating a setup THEN the CAM_System SHALL detect and configure stock automatically from the selected bodies
4. WHEN a setup is created THEN the CAM_System SHALL return the setup ID and confirmation details
5. WHEN no name is provided THEN the CAM_System SHALL generate a descriptive name based on the selected geometry

### Requirement 2

**User Story:** As a CAM programmer, I want to configure work coordinate systems for setups, so that I can establish proper machining origins and orientations.

#### Acceptance Criteria

1. WHEN a user specifies a WCS origin point THEN the CAM_System SHALL position the WCS at that location
2. WHEN a user specifies orientation vectors THEN the CAM_System SHALL align the WCS axes accordingly
3. WHEN a user selects a face or plane for orientation THEN the CAM_System SHALL automatically calculate appropriate WCS alignment
4. WHEN WCS changes are made THEN the CAM_System SHALL validate that the WCS is properly defined
5. IF invalid WCS data is provided THEN the CAM_System SHALL reject the configuration and provide clear error messages

### Requirement 3

**User Story:** As a CAM programmer, I want to define and modify stock configuration for setups, so that I can accurately represent the raw material being machined.

#### Acceptance Criteria

1. WHEN a user specifies stock dimensions THEN the CAM_System SHALL create stock geometry with those dimensions
2. WHEN a user selects existing geometry as stock THEN the CAM_System SHALL use that geometry for Stock_Definition
3. WHEN stock position is specified THEN the CAM_System SHALL position the stock relative to the WCS
4. WHEN material properties are provided THEN the CAM_System SHALL apply those properties to the Stock_Definition
5. IF stock configuration is invalid THEN the CAM_System SHALL prevent setup creation and provide validation errors

### Requirement 4

**User Story:** As a CAM programmer, I want to list and inspect existing CAM setups, so that I can understand the current manufacturing configuration.

#### Acceptance Criteria

1. WHEN a user requests setup listing THEN the CAM_System SHALL return all CAM_Setup objects with their basic properties
2. WHEN a user requests detailed setup information THEN the CAM_System SHALL return comprehensive CAM_Setup configuration including WCS and stock
3. WHEN a user queries CAM_Setup by ID THEN the CAM_System SHALL return the specific setup details or appropriate error if not found
4. WHEN no CAM_Setup objects exist THEN the CAM_System SHALL return an empty list with appropriate messaging
5. IF CAM_Setup data is corrupted THEN the CAM_System SHALL handle errors gracefully and report the issue

### Requirement 5

**User Story:** As a CAM programmer, I want to modify existing setup configurations, so that I can adapt setups as manufacturing requirements change.

#### Acceptance Criteria

1. WHEN a user modifies CAM_Setup properties THEN the CAM_System SHALL update the setup and preserve existing operations where possible
2. WHEN WCS changes affect existing operations THEN the CAM_System SHALL warn about potential impacts
3. WHEN Stock_Definition changes THEN the CAM_System SHALL validate that existing operations remain valid
4. IF CAM_Setup modifications are invalid THEN the CAM_System SHALL reject changes and maintain the current configuration
5. WHEN modifications are successful THEN the CAM_System SHALL return updated CAM_Setup information

### Requirement 6

**User Story:** As a CAM programmer, I want to delete CAM setups that are no longer needed, so that I can maintain a clean manufacturing workspace.

#### Acceptance Criteria

1. WHEN a user requests CAM_Setup deletion THEN the CAM_System SHALL remove the setup and all associated operations
2. WHEN a CAM_Setup contains active Toolpath objects THEN the CAM_System SHALL warn about data loss before deletion
3. WHEN CAM_Setup deletion is confirmed THEN the CAM_System SHALL permanently remove the setup and return confirmation
4. IF attempting to delete a non-existent CAM_Setup THEN the CAM_System SHALL return appropriate error messaging
5. IF deletion fails due to system constraints THEN the CAM_System SHALL report the specific failure reason

### Requirement 7

**User Story:** As a CAM programmer, I want to duplicate existing setups, so that I can create similar configurations efficiently.

#### Acceptance Criteria

1. WHEN a user requests CAM_Setup duplication THEN the CAM_System SHALL create a new setup with identical configuration
2. WHEN duplicating a CAM_Setup THEN the CAM_System SHALL copy WCS, Stock_Definition, and operation templates
3. WHEN a new name is provided for duplication THEN the CAM_System SHALL use that name for the duplicated CAM_Setup
4. WHEN no name is provided THEN the CAM_System SHALL generate a unique name based on the original CAM_Setup
5. IF duplication fails THEN the CAM_System SHALL report the error and maintain the original CAM_Setup unchanged

### Requirement 8

**User Story:** As a CAM programmer, I want to manage multiple setups within a single CAM document, so that I can organize complex manufacturing workflows with different orientations and configurations.

#### Acceptance Criteria

1. WHEN multiple CAM_Setup objects exist in a document THEN the CAM_System SHALL list all setups with their unique identifiers
2. WHEN creating additional CAM_Setup objects THEN the CAM_System SHALL ensure unique naming and prevent conflicts
3. WHEN switching between CAM_Setup objects THEN the CAM_System SHALL maintain context and provide clear setup identification
4. WHEN CAM_Setup objects share common resources THEN the CAM_System SHALL manage resource allocation appropriately
5. WHEN CAM_Setup operations affect document state THEN the CAM_System SHALL maintain consistency across all setups

### Requirement 9

**User Story:** As a CAM programmer, I want toolpaths to always know which setup they belong to, so that I can maintain proper context and organization.

#### Acceptance Criteria

1. WHEN querying Toolpath information THEN the CAM_System SHALL include the parent CAM_Setup ID in the response
2. WHEN Toolpath objects are created within a CAM_Setup THEN the CAM_System SHALL automatically associate them with that setup
3. WHEN Toolpath operations are performed THEN the CAM_System SHALL validate CAM_Setup context and permissions
4. WHEN Toolpath objects are moved between CAM_Setup objects THEN the CAM_System SHALL update setup associations accordingly
5. IF CAM_Setup context is invalid THEN the CAM_System SHALL prevent Toolpath operations and provide clear error messages

### Requirement 10

**User Story:** As a CAM programmer, I want setups to list their contained toolpaths using existing toolpath functionality, so that I can leverage current capabilities while maintaining setup organization.

#### Acceptance Criteria

1. WHEN requesting Toolpath objects for a specific CAM_Setup THEN the CAM_System SHALL use existing toolpath listing functions filtered by setup ID
2. WHEN CAM_Setup Toolpath queries are made THEN the CAM_System SHALL return Toolpath objects with full details using current toolpath serialization
3. WHEN Toolpath operations are performed within CAM_Setup context THEN the CAM_System SHALL use existing toolpath modification functions
4. WHEN CAM_Setup-filtered Toolpath lists are empty THEN the CAM_System SHALL return appropriate messaging indicating no toolpaths in the setup
5. WHEN existing Toolpath functions are called THEN the CAM_System SHALL provide CAM_Setup context as additional metadata

### Requirement 11

**User Story:** As a CAM programmer, I want helper functions that bridge setup and toolpath functionality, so that I can work seamlessly between setup management and toolpath operations.

#### Acceptance Criteria

1. WHEN helper functions are called THEN the CAM_System SHALL provide bidirectional CAM_Setup-Toolpath relationship queries
2. WHEN Toolpath context is needed THEN the CAM_System SHALL provide functions to resolve CAM_Setup from Toolpath ID
3. WHEN CAM_Setup context is needed THEN the CAM_System SHALL provide functions to list Toolpath objects within a setup
4. WHEN cross-referencing is required THEN the CAM_System SHALL maintain consistent ID mapping between CAM_Setup and Toolpath objects
5. IF helper functions encounter errors THEN the CAM_System SHALL provide detailed error information including both CAM_Setup and Toolpath context

### Requirement 12

**User Story:** As a CAM programmer, I want to configure part position within setups, so that I can control how the part geometry is positioned and oriented relative to the WCS.

#### Acceptance Criteria

1. WHEN a user specifies Part_Position parameters THEN the CAM_System SHALL position the part geometry accordingly within the CAM_Setup
2. WHEN Part_Position includes orientation data THEN the CAM_System SHALL orient the part relative to the WCS
3. WHEN Part_Position is modified THEN the CAM_System SHALL update all dependent operations and Toolpath objects
4. WHEN querying CAM_Setup details THEN the CAM_System SHALL include Part_Position information in the response
5. IF Part_Position configuration is invalid THEN the CAM_System SHALL reject the configuration and provide clear error messages

### Requirement 13

**User Story:** As a developer, I want the setup management functionality organized in a modular directory structure, so that the codebase remains maintainable and consistent with existing manufacturing modules.

#### Acceptance Criteria

1. WHEN implementing setup management THEN the Fusion_Add_In SHALL organize code in a `handlers/manufacture/setups/` directory structure
2. WHEN organizing setup modules THEN the Fusion_Add_In SHALL create separate modules for setup core (`setup.py`), stock (`stock.py`), and part position (`part_position.py`)
3. WHEN creating the setups module THEN the Fusion_Add_In SHALL follow the same patterns as existing `operations/` and `tool_libraries/` modules
4. WHEN exposing setup functionality THEN the Fusion_Add_In SHALL use an `__init__.py` that exports all public functions from submodules
5. WHEN adding new setup-related functionality THEN the Fusion_Add_In SHALL place it in the appropriate submodule within the `setups/` directory