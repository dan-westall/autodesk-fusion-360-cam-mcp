# Requirements Document: Prompt System Modernization

## Introduction

This specification defines the requirements for modernizing the Fusion 360 MCP Server's prompt system from a custom registry-based implementation to the native fastmcp 2.* prompt system using the `@mcp.prompt()` decorator pattern.

## Glossary

- **FastMCP**: The MCP server framework used by the Fusion 360 MCP Server
- **Prompt**: A reusable message template that helps LLMs generate structured, purposeful responses
- **Prompt Registry**: The current custom system for managing prompts (to be replaced)
- **MCP Decorator**: The `@mcp.prompt()` decorator provided by fastmcp 2.* for defining prompts
- **Prompt Template**: A function that returns formatted text to guide LLM responses
- **Manufacturing Prompt**: A prompt specifically designed for CAM/manufacturing workflows

## Requirements

### Requirement 1: Remove Custom Prompt Registry

**User Story:** As a developer, I want to use the native fastmcp prompt system, so that the codebase is simpler and follows framework conventions.

#### Acceptance Criteria

1. THE System SHALL remove the custom `PromptRegistry` class from `Server/prompts/registry.py`
2. THE System SHALL remove the `PromptInfo` dataclass from `Server/prompts/registry.py`
3. THE System SHALL remove all registry-related helper functions (`register_prompt`, `get_prompt`, etc.)
4. THE System SHALL remove the `_global_registry` instance and related global functions
5. THE System SHALL delete the `Server/prompts/registry.py` file after migration is complete

### Requirement 2: Convert Prompt Templates to FastMCP Decorators

**User Story:** As a developer, I want prompts defined using `@mcp.prompt()` decorators, so that they integrate natively with the fastmcp framework.

#### Acceptance Criteria

1. WHEN defining a prompt, THE System SHALL use the `@mcp.prompt()` decorator pattern
2. WHEN defining a prompt, THE System SHALL use the function name as the prompt identifier
3. WHEN defining a prompt, THE System SHALL include a docstring that serves as the prompt description
4. WHEN defining a prompt, THE System SHALL return a string containing the prompt content
5. THE System SHALL convert all existing prompts (`cam_setup`, `toolpath_analysis`, `tool_library`) to use the decorator pattern

### Requirement 3: Simplify Prompt Module Structure

**User Story:** As a developer, I want a simple prompt module structure, so that prompts are easy to find and maintain.

#### Acceptance Criteria

1. THE System SHALL define all prompts in `Server/prompts/templates.py`
2. THE System SHALL remove the `register_all_prompts()` function
3. THE System SHALL remove auto-registration logic from module imports
4. THE System SHALL ensure prompts are automatically discovered by fastmcp when the module is imported
5. THE System SHALL maintain the `Server/prompts/__init__.py` file for module initialization

### Requirement 4: Update Server Initialization

**User Story:** As a developer, I want the server to automatically discover prompts, so that no manual registration is required.

#### Acceptance Criteria

1. WHEN the server starts, THE System SHALL import the prompts module to trigger decorator registration
2. WHEN the server starts, THE System SHALL NOT call any manual prompt registration functions
3. THE System SHALL remove the `register_prompts_with_mcp()` function from `Server/MCP_Server.py`
4. THE System SHALL remove prompt registry imports from `Server/MCP_Server.py`
5. THE System SHALL ensure prompts are available to MCP clients after server initialization

### Requirement 5: Preserve Prompt Functionality

**User Story:** As a user, I want all existing prompts to work identically, so that my workflows are not disrupted.

#### Acceptance Criteria

1. THE System SHALL preserve the exact content of the `cam_setup` prompt
2. THE System SHALL preserve the exact content of the `toolpath_analysis` prompt
3. THE System SHALL preserve the exact content of the `tool_library` prompt
4. WHEN a client requests a prompt, THE System SHALL return the same formatted text as before
5. THE System SHALL maintain the same prompt names (`cam_setup`, `toolpath_analysis`, `tool_library`)

### Requirement 6: Maintain Backward Compatibility

**User Story:** As a developer, I want the migration to be non-breaking, so that existing MCP clients continue to work.

#### Acceptance Criteria

1. THE System SHALL maintain the same prompt identifiers for MCP clients
2. THE System SHALL return prompts in the same format expected by MCP clients
3. THE System SHALL ensure no changes to the MCP protocol interface
4. WHEN a client lists prompts, THE System SHALL return all available prompts
5. WHEN a client requests a prompt, THE System SHALL return the prompt content successfully

### Requirement 7: Improve Code Maintainability

**User Story:** As a developer, I want cleaner, more maintainable prompt code, so that adding new prompts is straightforward.

#### Acceptance Criteria

1. THE System SHALL reduce the total lines of code in the prompts module by at least 50%
2. THE System SHALL eliminate the need for manual prompt registration
3. THE System SHALL use standard Python patterns (decorators) instead of custom registry systems
4. WHEN adding a new prompt, THE Developer SHALL only need to define a decorated function
5. THE System SHALL follow fastmcp 2.* best practices for prompt definition

### Requirement 8: Update Documentation

**User Story:** As a developer, I want updated documentation, so that I understand how to work with the new prompt system.

#### Acceptance Criteria

1. THE System SHALL update code comments to reflect the new decorator-based approach
2. THE System SHALL include docstrings that explain each prompt's purpose
3. THE System SHALL remove references to the old registry system from comments
4. THE System SHALL update any inline documentation about prompt registration
5. THE System SHALL ensure docstrings follow fastmcp conventions

### Requirement 9: Clean Up Unused Code

**User Story:** As a developer, I want unused code removed, so that the codebase stays clean and maintainable.

#### Acceptance Criteria

1. THE System SHALL remove the `Server/prompts/registry.py` file
2. THE System SHALL remove registry imports from `Server/MCP_Server.py`
3. THE System SHALL remove the `register_prompts_with_mcp()` function
4. THE System SHALL remove any unused helper functions related to the old registry
5. THE System SHALL ensure no dead code remains after migration

### Requirement 10: Validate Migration Success

**User Story:** As a developer, I want to verify the migration worked, so that I can be confident the system functions correctly.

#### Acceptance Criteria

1. WHEN the server starts, THE System SHALL log successful prompt loading
2. WHEN listing prompts via MCP, THE System SHALL return all three prompts
3. WHEN requesting a prompt via MCP, THE System SHALL return the correct content
4. THE System SHALL start without errors related to prompt registration
5. THE System SHALL maintain the same prompt behavior as before migration
