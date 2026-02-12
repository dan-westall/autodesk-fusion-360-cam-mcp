# Implementation Plan: Prompt System Modernization

## Overview

This implementation plan converts the custom prompt registry system to the native fastmcp 2.* decorator-based system. The migration will be done in phases to ensure safety and maintain backward compatibility throughout the process.

## Tasks

- [x] 1. Create test suite for current prompt behavior
  - Create baseline tests that verify current prompt system works correctly
  - Test prompt listing, retrieval, and content
  - Document expected behavior for comparison after migration
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ]* 1.1 Write property test for prompt content preservation
  - **Property 5: Prompt Content Preservation**
  - **Validates: Requirements 5.4**
  - Test that prompt content remains identical after migration
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 1.2 Write property test for MCP identifier stability
  - **Property 6: MCP Identifier Stability**
  - **Validates: Requirements 6.1**
  - Test that prompt identifiers don't change
  - _Requirements: 6.1, 5.5_

- [ ] 2. Convert prompt functions to use decorators
  - [x] 2.1 Add `@mcp.prompt()` decorator to `cam_setup_prompt()` function
    - Rename function from `cam_setup_prompt()` to `cam_setup()`
    - Add `@mcp.prompt()` decorator above function definition
    - Ensure docstring is present and descriptive
    - Verify function returns string
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.2 Add `@mcp.prompt()` decorator to `toolpath_analysis_prompt()` function
    - Rename function from `toolpath_analysis_prompt()` to `toolpath_analysis()`
    - Add `@mcp.prompt()` decorator above function definition
    - Ensure docstring is present and descriptive
    - Verify function returns string
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.3 Add `@mcp.prompt()` decorator to `tool_library_prompt()` function
    - Rename function from `tool_library_prompt()` to `tool_library()`
    - Add `@mcp.prompt()` decorator above function definition
    - Ensure docstring is present and descriptive
    - Verify function returns string
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 2.4 Write property test for decorator usage
  - **Property 1: Decorator Usage Consistency**
  - **Validates: Requirements 2.1**
  - Test that all prompt functions use `@mcp.prompt()` decorator
  - _Requirements: 2.1_

- [ ]* 2.5 Write property test for function name as identifier
  - **Property 2: Function Name as Identifier**
  - **Validates: Requirements 2.2**
  - Test that function names match MCP identifiers
  - _Requirements: 2.2_

- [ ]* 2.6 Write property test for docstring presence
  - **Property 3: Docstring Presence**
  - **Validates: Requirements 2.3, 8.2**
  - Test that all prompts have non-empty docstrings
  - _Requirements: 2.3, 8.2_

- [ ]* 2.7 Write property test for string return type
  - **Property 4: String Return Type**
  - **Validates: Requirements 2.4**
  - Test that all prompts return strings
  - _Requirements: 2.4_

- [x] 3. Remove manual registration logic from templates.py
  - Remove `register_all_prompts()` function
  - Remove all `register_prompt()` calls
  - Remove auto-registration logic at module bottom
  - Update module docstring to reflect decorator-based approach
  - _Requirements: 3.2, 3.3, 8.1, 8.3_

- [ ] 4. Update server initialization in MCP_Server.py
  - [x] 4.1 Remove `register_prompts_with_mcp()` function
    - Delete the entire function definition
    - Remove any calls to this function
    - _Requirements: 4.2, 4.3, 9.3_

  - [x] 4.2 Remove prompt registry imports
    - Remove `from prompts.registry import get_prompt_registry`
    - Remove any other registry-related imports
    - _Requirements: 4.4, 9.2_

  - [x] 4.3 Ensure prompts module is imported
    - Verify `from prompts import templates` exists
    - Add comment explaining that import triggers decorator registration
    - _Requirements: 4.1_

  - [x] 4.4 Update server initialization docstring
    - Remove references to manual prompt registration
    - Add note about automatic decorator-based registration
    - _Requirements: 8.1, 8.4_

- [x] 5. Checkpoint - Test decorator-based system
  - Start server and verify it initializes without errors
  - Verify prompts are available via MCP protocol
  - Run unit tests to verify prompt behavior
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 10.1, 10.4, 10.5_

- [ ] 6. Clean up registry module
  - [x] 6.1 Delete Server/prompts/registry.py file
    - Remove the entire file
    - Verify no other files import from it
    - _Requirements: 1.5, 9.1_

  - [x] 6.2 Update Server/prompts/__init__.py
    - Remove registry imports
    - Simplify to minimal module initialization
    - Add comment about decorator-based system
    - _Requirements: 3.5, 8.1_

  - [x] 6.3 Verify no registry references remain
    - Search codebase for "PromptRegistry"
    - Search codebase for "register_prompt"
    - Search codebase for "get_prompt_registry"
    - Remove any remaining references
    - _Requirements: 9.4, 9.5_

- [ ]* 6.4 Write unit tests for code cleanup
  - Test that registry.py file doesn't exist
  - Test that no registry imports exist in MCP_Server.py
  - Test that register_prompts_with_mcp() doesn't exist
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.2, 9.3, 9.4_

- [ ] 7. Update documentation and comments
  - [x] 7.1 Update prompts module docstring
    - Explain decorator-based approach
    - Remove references to registry system
    - Add examples of adding new prompts
    - _Requirements: 8.1, 8.3, 8.4_

  - [x] 7.2 Update individual prompt docstrings
    - Ensure each prompt has clear description
    - Explain prompt purpose and usage
    - Follow fastmcp documentation conventions
    - _Requirements: 8.2, 8.5_

  - [x] 7.3 Update MCP_Server.py comments
    - Remove registry-related comments
    - Add comments about automatic prompt discovery
    - Explain decorator registration mechanism
    - _Requirements: 8.1, 8.3, 8.4_

- [x] 8. Checkpoint - Verify code quality
  - Run linter to check code style
  - Verify all docstrings are present
  - Check that no dead code remains
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 9.5_

- [ ]* 9. Write integration tests
  - [ ]* 9.1 Write test for server startup
    - Test that server starts without errors
    - Test that prompts are registered during startup
    - _Requirements: 10.1, 10.4_

  - [ ]* 9.2 Write test for listing prompts via MCP
    - Test that all three prompts appear in list
    - Test that prompt metadata is correct
    - _Requirements: 6.4, 10.2_

  - [ ]* 9.3 Write test for requesting prompts via MCP
    - Test that each prompt can be requested successfully
    - Test that correct content is returned
    - _Requirements: 6.5, 10.3_

  - [ ]* 9.4 Write property test for MCP format consistency
    - **Property 7: MCP Format Consistency**
    - **Validates: Requirements 6.2**
    - Test that MCP responses conform to protocol
    - _Requirements: 6.2, 6.3_

  - [ ]* 9.5 Write property test for successful prompt requests
    - **Property 8: Successful Prompt Requests**
    - **Validates: Requirements 6.5, 10.3**
    - Test that all valid prompts can be requested
    - _Requirements: 6.5, 10.3_

  - [ ]* 9.6 Write property test for prompt behavior equivalence
    - **Property 9: Prompt Behavior Equivalence**
    - **Validates: Requirements 10.5**
    - Test that all operations work identically to before
    - _Requirements: 10.5_

- [ ] 10. Final validation and testing
  - [x] 10.1 Run complete test suite
    - Run all unit tests
    - Run all property tests
    - Run all integration tests
    - Verify 100% pass rate
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 10.2 Verify code metrics
    - Count lines of code removed (should be ~261)
    - Verify >50% reduction in prompts module
    - Check that no dead code remains
    - _Requirements: 7.1, 9.5_

  - [x] 10.3 Manual testing checklist
    - Start server and verify no errors
    - List prompts via MCP client
    - Request each prompt and verify content
    - Test with actual AI assistant (Claude/Copilot)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 10.4 Verify backward compatibility
    - Test with existing MCP clients
    - Verify prompt identifiers unchanged
    - Verify prompt content unchanged
    - Verify MCP protocol unchanged
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 11. Final checkpoint - Complete migration
  - All tests passing
  - Code is cleaner and simpler
  - Backward compatibility maintained
  - Documentation updated
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end MCP protocol behavior

## Migration Safety

This migration is designed to be safe and reversible:

1. **Phase 1** creates tests to verify current behavior
2. **Phase 2-4** make the core changes while keeping old code
3. **Phase 5** validates the new system works before cleanup
4. **Phase 6** removes old code only after validation
5. **Phase 7-11** polish and final validation

If issues arise at any checkpoint, we can pause and investigate before proceeding.
