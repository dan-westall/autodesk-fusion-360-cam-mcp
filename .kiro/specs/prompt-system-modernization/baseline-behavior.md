# Baseline Behavior Documentation

**Date:** January 7, 2026  
**Purpose:** Document the current prompt system behavior before migration to fastmcp decorators  
**Test Suite:** `Server/tests/test_prompts_baseline.py`  
**Test Results:** 43/43 tests passing ✅

## Overview

This document captures the exact behavior of the custom prompt registry system before migration to the fastmcp 2.* decorator-based system. These baseline tests ensure that the migration maintains identical functionality.

## Test Coverage Summary

| Test Class | Tests | Purpose |
|------------|-------|---------|
| `TestPromptRegistryBasics` | 3 | Registry instance creation and singleton pattern |
| `TestPromptRegistration` | 6 | Prompt registration with validation |
| `TestPromptRetrieval` | 4 | Prompt content and metadata retrieval |
| `TestPromptListing` | 4 | Listing prompts by category |
| `TestPromptUnregistration` | 3 | Removing prompts from registry |
| `TestPromptValidation` | 2 | Dependency validation |
| `TestPromptStatistics` | 2 | Registry statistics |
| `TestGlobalRegistryFunctions` | 2 | Global convenience functions |
| `TestManufacturingPrompts` | 11 | Actual manufacturing prompt validation |
| `TestPromptContentPreservation` | 3 | Exact content preservation |
| `TestPromptIdentifierStability` | 3 | Identifier stability validation |
| **Total** | **43** | **Complete baseline coverage** |

## Current System Architecture

### Components

1. **PromptRegistry Class** (`Server/prompts/registry.py`)
   - Custom registry with validation
   - Category-based organization
   - Dependency tracking
   - ~200 lines of code

2. **PromptInfo Dataclass** (`Server/prompts/registry.py`)
   - Stores prompt metadata
   - Fields: name, function, description, category, dependencies

3. **Prompt Templates** (`Server/prompts/templates.py`)
   - Three manufacturing prompts defined
   - Manual registration via `register_all_prompts()`
   - Auto-registration on module import

4. **MCP Integration** (`Server/MCP_Server.py`)
   - `register_prompts_with_mcp()` function
   - Dynamic prompt function creation
   - Manual registration with MCP server

### Global Registry Pattern

```python
# Global singleton instance
_global_registry = PromptRegistry()

# Convenience functions
def get_prompt_registry() -> PromptRegistry:
    return _global_registry

def register_prompt(name, func, desc, category, deps):
    return _global_registry.register_prompt(...)

def get_prompt(name):
    return _global_registry.get_prompt(name)
```

## Registered Prompts

### 1. cam_setup

**Identifier:** `cam_setup`  
**Category:** `manufacturing`  
**Dependencies:** `["create_cam_setup", "list_cam_setups"]`  
**Description:** "Creates a basic CAM setup for manufacturing operations"

**Content Structure:**
- STEP 1: Create CAM Setup
- STEP 2: Verify Setup
- STEP 3: Ready for Operations

**Function Name:** `cam_setup_prompt()` (note: different from identifier)

### 2. toolpath_analysis

**Identifier:** `toolpath_analysis`  
**Category:** `manufacturing`  
**Dependencies:** `["list_cam_toolpaths", "get_toolpath_details"]`  
**Description:** "Analyzes existing toolpaths for manufacturing optimization"

**Content Structure:**
- STEP 1: List Available Toolpaths
- STEP 2: Analyze Specific Toolpath
- STEP 3: Optimization Review

**Function Name:** `toolpath_analysis_prompt()` (note: different from identifier)

### 3. tool_library

**Identifier:** `tool_library`  
**Category:** `manufacturing`  
**Dependencies:** `["list_tool_libraries", "list_library_tools"]`  
**Description:** "Manages cutting tools and tool libraries for manufacturing"

**Content Structure:**
- STEP 1: List Tool Libraries
- STEP 2: Browse Tools
- STEP 3: Tool Selection

**Function Name:** `tool_library_prompt()` (note: different from identifier)

## Key Behaviors Documented

### Registration Behavior

1. **Validation on Registration:**
   - Prompt function must be callable
   - Prompt function must return a string
   - Test execution happens during registration
   - Invalid prompts are rejected (return False)

2. **Duplicate Handling:**
   - Registering duplicate name overwrites previous
   - Warning logged but registration succeeds

3. **Category Management:**
   - Categories created automatically on first use
   - Prompts indexed by category
   - Empty categories cleaned up on unregister

### Retrieval Behavior

1. **get_prompt(name):**
   - Returns string content if found
   - Returns None if not found
   - Executes prompt function on each call
   - Logs error if execution fails

2. **get_prompt_info(name):**
   - Returns PromptInfo object if found
   - Returns None if not found
   - Includes all metadata (name, function, description, category, dependencies)

3. **list_prompts(category=None):**
   - Returns list of prompt names
   - Filters by category if specified
   - Returns empty list for non-existent category

### Validation Behavior

1. **validate_dependencies():**
   - Checks if dependencies exist as prompts
   - Returns dict of missing dependencies
   - Empty dict if all dependencies satisfied

2. **get_stats():**
   - Returns total prompt count
   - Returns category count
   - Returns prompts per category
   - Returns count of prompts with dependencies

## Exact Content Preservation

The following content must be preserved exactly during migration:

### cam_setup Content
```
    STEP 1: Create CAM Setup
    - Use Tool: create_cam_setup
    - Setup Name: "Manufacturing Setup"
    - Select your stock material and work coordinate system
    
    STEP 2: Verify Setup
    - Use Tool: list_cam_setups
    - Check that your setup was created successfully
    
    STEP 3: Ready for Operations
    - Your CAM setup is now ready for toolpath operations
    - You can now add milling, drilling, or other machining operations
    
```

### toolpath_analysis Content
```
    STEP 1: List Available Toolpaths
    - Use Tool: list_cam_toolpaths
    - Review all generated toolpaths in your CAM setup
    
    STEP 2: Analyze Specific Toolpath
    - Use Tool: get_toolpath_details
    - Select a toolpath ID from the list
    - Review machining parameters and tool information
    
    STEP 3: Optimization Review
    - Check feed rates, spindle speeds, and cutting parameters
    - Verify toolpath efficiency and safety margins
    
```

### tool_library Content
```
    STEP 1: List Tool Libraries
    - Use Tool: list_tool_libraries
    - Review available tool libraries in your system
    
    STEP 2: Browse Tools
    - Use Tool: list_library_tools
    - Select a library to view available cutting tools
    
    STEP 3: Tool Selection
    - Review tool specifications (diameter, length, material)
    - Select appropriate tools for your machining operations
    
```

## Identifier Stability

**Critical for Migration:**

The following identifiers MUST remain stable:
- `cam_setup`
- `toolpath_analysis`
- `tool_library`

**Note:** Current system has mismatch between:
- **Identifier:** `cam_setup` (used by MCP clients)
- **Function Name:** `cam_setup_prompt()` (internal implementation)

After migration, the function name will become the identifier, so functions must be renamed to match current identifiers.

## MCP Integration Pattern

### Current Registration Flow

1. Server imports `prompts.templates` module
2. Module import triggers `register_all_prompts()`
3. Prompts registered in global registry
4. Server calls `register_prompts_with_mcp(mcp)`
5. Function iterates registry and creates dynamic prompt functions
6. Each prompt registered with MCP via `mcp.prompt()(func)`

### Dynamic Prompt Function Creation

```python
def create_prompt_function(name, info):
    def prompt_function():
        return registry.get_prompt(name)
    prompt_function.__name__ = name
    prompt_function.__doc__ = info.description
    return prompt_function
```

This pattern ensures:
- Function name matches prompt identifier
- Docstring contains description
- Function returns prompt content from registry

## Migration Requirements

Based on baseline behavior, the migration MUST:

1. ✅ Preserve exact prompt content (character-for-character)
2. ✅ Maintain prompt identifiers (`cam_setup`, `toolpath_analysis`, `tool_library`)
3. ✅ Keep prompts in `manufacturing` category (via naming or documentation)
4. ✅ Preserve dependency information (via docstrings or comments)
5. ✅ Return same string content when prompts are requested
6. ✅ Make prompts available via MCP protocol
7. ✅ Maintain backward compatibility with MCP clients

## Test Execution

### Running Baseline Tests

```bash
# Run all baseline tests
uv run python -m pytest Server/tests/test_prompts_baseline.py -v

# Run specific test class
uv run python -m pytest Server/tests/test_prompts_baseline.py::TestManufacturingPrompts -v

# Run with coverage
uv run python -m pytest Server/tests/test_prompts_baseline.py --cov=prompts
```

### Expected Results

All 43 tests should pass:
- ✅ 3 registry basics tests
- ✅ 6 registration tests
- ✅ 4 retrieval tests
- ✅ 4 listing tests
- ✅ 3 unregistration tests
- ✅ 2 validation tests
- ✅ 2 statistics tests
- ✅ 2 global function tests
- ✅ 11 manufacturing prompt tests
- ✅ 3 content preservation tests
- ✅ 3 identifier stability tests

## Validation Checklist

After migration, verify:

- [ ] All 43 baseline tests still pass (or equivalent new tests)
- [ ] Prompt identifiers unchanged
- [ ] Prompt content byte-for-byte identical
- [ ] MCP clients can list prompts
- [ ] MCP clients can request prompts
- [ ] Server starts without errors
- [ ] No registry.py file exists
- [ ] No manual registration code remains
- [ ] Code is simpler and more maintainable

## References

- **Test Suite:** `Server/tests/test_prompts_baseline.py`
- **Requirements:** `.kiro/specs/prompt-system-modernization/requirements.md`
- **Design:** `.kiro/specs/prompt-system-modernization/design.md`
- **Tasks:** `.kiro/specs/prompt-system-modernization/tasks.md`

## Change Log

- **January 7, 2026:** Initial baseline documentation created with 43 passing tests
