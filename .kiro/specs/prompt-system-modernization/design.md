# Design Document: Prompt System Modernization

## Overview

This design document describes the migration from a custom prompt registry system to the native fastmcp 2.* decorator-based prompt system. The migration will eliminate approximately 200 lines of custom registry code while maintaining identical functionality for MCP clients.

The key insight is that fastmcp 2.* provides built-in prompt management through the `@mcp.prompt()` decorator, making our custom `PromptRegistry` class unnecessary. By leveraging the framework's native capabilities, we simplify the codebase and follow established patterns.

## Architecture

### Current Architecture (Before Migration)

```
Server/prompts/
├── registry.py          # Custom PromptRegistry class (~200 lines)
│   ├── PromptRegistry   # Custom registry with validation
│   ├── PromptInfo       # Dataclass for prompt metadata
│   └── Global functions # register_prompt(), get_prompt()
├── templates.py         # Prompt template definitions
│   ├── cam_setup_prompt()
│   ├── toolpath_analysis_prompt()
│   ├── tool_library_prompt()
│   └── register_all_prompts()  # Manual registration
└── __init__.py

Server/MCP_Server.py
└── register_prompts_with_mcp()  # Manual MCP registration
```

### New Architecture (After Migration)

```
Server/prompts/
├── templates.py         # Prompt definitions with decorators
│   ├── @mcp.prompt() cam_setup()
│   ├── @mcp.prompt() toolpath_analysis()
│   └── @mcp.prompt() tool_library()
└── __init__.py          # Simple module init

Server/MCP_Server.py
└── import prompts.templates  # Automatic registration
```

**Key Changes:**
- Remove `registry.py` entirely (~200 lines deleted)
- Convert prompt functions to use `@mcp.prompt()` decorator
- Remove manual registration logic
- Rely on fastmcp's automatic discovery

## Components and Interfaces

### Component 1: Prompt Template Definitions

**File:** `Server/prompts/templates.py`

**Before:**
```python
def cam_setup_prompt():
    """Prompt function returning string."""
    return "..."

register_prompt("cam_setup", cam_setup_prompt, "description", "manufacturing")
```

**After:**
```python
@mcp.prompt()
def cam_setup():
    """Creates a basic CAM setup for manufacturing operations."""
    return """
    STEP 1: Create CAM Setup
    ...
    """
```

**Interface Changes:**
- Function names become prompt identifiers (no separate name parameter)
- Docstrings serve as descriptions (no separate description parameter)
- Decorator handles registration automatically (no manual registration)
- Categories are not needed (fastmcp doesn't use them)

### Component 2: Server Initialization

**File:** `Server/MCP_Server.py`

**Before:**
```python
from prompts.registry import get_prompt_registry
from prompts import templates  # Triggers auto-registration

def register_prompts_with_mcp(mcp):
    registry = get_prompt_registry()
    for prompt_name in registry.list_prompts():
        # Manual registration logic
        ...
```

**After:**
```python
from prompts import templates  # Decorator registration happens automatically
# No manual registration needed
```

**Interface Changes:**
- Remove `register_prompts_with_mcp()` function
- Remove registry imports
- Prompts are automatically available after import

### Component 3: Module Structure

**File:** `Server/prompts/__init__.py`

**Before:**
```python
from .registry import register_prompt, get_prompt, get_prompt_registry
from . import templates
```

**After:**
```python
# Simple module initialization
# Prompts are registered via decorators in templates.py
```

## Data Models

### Prompt Definition Model

**Before (Custom Registry):**
```python
@dataclass
class PromptInfo:
    name: str
    function: Callable
    description: str
    category: str = "general"
    dependencies: List[str] = None
```

**After (FastMCP Native):**
```python
# No explicit data model needed
# FastMCP manages prompt metadata internally
# Decorator extracts:
#   - name: from function name
#   - description: from docstring
#   - function: the decorated function itself
```

### Prompt Content Model

Both before and after, prompts return plain strings:

```python
def prompt_function() -> str:
    return """
    STEP 1: ...
    STEP 2: ...
    """
```

**No changes to prompt content format or structure.**

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Decorator Usage Consistency
*For any* prompt function in `Server/prompts/templates.py`, it should be decorated with `@mcp.prompt()`.
**Validates: Requirements 2.1**

### Property 2: Function Name as Identifier
*For any* prompt function, the prompt identifier available to MCP clients should match the function's `__name__` attribute.
**Validates: Requirements 2.2**

### Property 3: Docstring Presence
*For any* prompt function, it should have a non-empty docstring that serves as the prompt description.
**Validates: Requirements 2.3, 8.2**

### Property 4: String Return Type
*For any* prompt function, calling it should return a value of type `str`.
**Validates: Requirements 2.4**

### Property 5: Prompt Content Preservation
*For any* existing prompt (cam_setup, toolpath_analysis, tool_library), the content returned after migration should be identical to the content before migration.
**Validates: Requirements 5.4**

### Property 6: MCP Identifier Stability
*For any* prompt, the identifier exposed to MCP clients after migration should be identical to the identifier before migration.
**Validates: Requirements 6.1**

### Property 7: MCP Format Consistency
*For any* prompt, the format of the response returned to MCP clients should conform to the MCP protocol specification both before and after migration.
**Validates: Requirements 6.2**

### Property 8: Successful Prompt Requests
*For any* valid prompt identifier, requesting that prompt via MCP should return the prompt content without errors.
**Validates: Requirements 6.5, 10.3**

### Property 9: Prompt Behavior Equivalence
*For any* prompt operation (list, get), the behavior after migration should be functionally equivalent to the behavior before migration.
**Validates: Requirements 10.5**

## Error Handling

### Migration Errors

**Error:** Decorator not applied to prompt function
- **Detection:** Import-time error when fastmcp tries to discover prompts
- **Handling:** Python will raise `AttributeError` or similar
- **Prevention:** Code review checklist ensures all prompts use decorator

**Error:** Missing docstring
- **Detection:** Prompt appears in MCP with empty description
- **Handling:** Fastmcp uses empty string as description
- **Prevention:** Linting rule to require docstrings on decorated functions

**Error:** Non-string return value
- **Detection:** Runtime error when MCP client requests prompt
- **Handling:** Fastmcp may raise `TypeError`
- **Prevention:** Type hints and unit tests verify return types

### Runtime Errors

**Error:** Prompt not found
- **Detection:** MCP client requests non-existent prompt
- **Handling:** Fastmcp returns "Unknown prompt" error (standard MCP error)
- **Recovery:** Client should list available prompts first

**Error:** Import failure
- **Detection:** Server fails to start due to import error in prompts module
- **Handling:** Server logs error and exits
- **Recovery:** Fix syntax/import errors in prompts module

## Testing Strategy

### Unit Tests

**Test File:** `Server/tests/test_prompts_migration.py`

**Example Tests:**
1. Test that all prompt functions have `@mcp.prompt()` decorator
2. Test that all prompt functions have docstrings
3. Test that all prompt functions return strings
4. Test that specific prompts (cam_setup, etc.) return expected content
5. Test that registry.py file doesn't exist after migration
6. Test that no registry imports exist in MCP_Server.py

### Property-Based Tests

**Test File:** `Server/tests/test_prompts_properties.py`

**Property Tests:**
1. **Property 1: Decorator Usage** - Verify all prompts use decorator
2. **Property 2: Name Matching** - Verify function names match MCP identifiers
3. **Property 3: Docstring Presence** - Verify all prompts have docstrings
4. **Property 4: String Returns** - Verify all prompts return strings
5. **Property 5: Content Preservation** - Compare old vs new prompt content
6. **Property 8: Successful Requests** - Verify all prompts can be requested

### Integration Tests

**Test File:** `Server/tests/test_prompts_integration.py`

**Integration Tests:**
1. Start server and verify prompts are registered
2. List prompts via MCP protocol and verify all three appear
3. Request each prompt via MCP and verify content is returned
4. Verify no errors in server logs related to prompts
5. Verify backward compatibility with MCP clients

### Manual Testing Checklist

- [ ] Server starts without errors
- [ ] `Server/prompts/registry.py` file doesn't exist
- [ ] No registry imports in `Server/MCP_Server.py`
- [ ] All three prompts appear when listing via MCP
- [ ] Each prompt returns correct content when requested
- [ ] No manual registration code remains
- [ ] Code is simpler and easier to understand

## Implementation Notes

### Decorator Pattern

The `@mcp.prompt()` decorator is the core of the new system:

```python
@mcp.prompt()
def cam_setup():
    """Creates a basic CAM setup for manufacturing operations."""
    return """
    STEP 1: Create CAM Setup
    - Use Tool: create_cam_setup
    ...
    """
```

**What the decorator does:**
1. Registers the function with fastmcp's internal prompt registry
2. Extracts the function name as the prompt identifier
3. Extracts the docstring as the prompt description
4. Makes the prompt available to MCP clients automatically

### Import Order

The prompts module must be imported during server initialization:

```python
# Server/MCP_Server.py
from prompts import templates  # This triggers decorator registration
```

**Why this works:**
- Python executes decorators when the module is imported
- The `@mcp.prompt()` decorator registers prompts with fastmcp
- No explicit registration call is needed

### Backward Compatibility

The migration maintains backward compatibility because:

1. **Prompt identifiers unchanged:** Function names match old prompt names
2. **Prompt content unchanged:** Return values are identical
3. **MCP protocol unchanged:** Fastmcp uses standard MCP protocol
4. **Client interface unchanged:** Clients use same list/get operations

### Code Reduction

**Lines of code removed:**
- `Server/prompts/registry.py`: ~200 lines
- `register_all_prompts()` function: ~30 lines
- `register_prompts_with_mcp()` function: ~25 lines
- Registry imports and calls: ~10 lines
- **Total: ~265 lines removed**

**Lines of code added:**
- Decorator imports: ~1 line
- Decorators on functions: ~3 lines
- **Total: ~4 lines added**

**Net reduction: ~261 lines (>50% reduction in prompts module)**

## Migration Steps

### Phase 1: Preparation
1. Review current prompt system and document behavior
2. Create test suite to verify current behavior
3. Document all prompt names and content

### Phase 2: Conversion
1. Add `@mcp.prompt()` decorators to prompt functions in `templates.py`
2. Rename functions to match desired prompt identifiers
3. Ensure docstrings are present and descriptive
4. Remove `register_all_prompts()` function

### Phase 3: Server Updates
1. Remove `register_prompts_with_mcp()` from `MCP_Server.py`
2. Remove registry imports from `MCP_Server.py`
3. Ensure `prompts.templates` is imported during initialization

### Phase 4: Cleanup
1. Delete `Server/prompts/registry.py`
2. Update `Server/prompts/__init__.py`
3. Remove any remaining registry references

### Phase 5: Validation
1. Run unit tests to verify prompt behavior
2. Run property tests to verify correctness properties
3. Start server and test via MCP protocol
4. Verify all prompts work identically to before

## Future Considerations

### Adding New Prompts

**Before (Complex):**
```python
def new_prompt():
    return "..."

register_prompt("new_prompt", new_prompt, "description", "category")
```

**After (Simple):**
```python
@mcp.prompt()
def new_prompt():
    """Description of the prompt."""
    return "..."
```

### Prompt Parameters

Fastmcp 2.* supports parameterized prompts:

```python
@mcp.prompt()
def setup_with_params(setup_name: str, material: str = "aluminum"):
    """Create a CAM setup with specific parameters."""
    return f"""
    STEP 1: Create CAM Setup
    - Setup Name: {setup_name}
    - Material: {material}
    ...
    """
```

This could be added in the future without changing the architecture.

### Async Prompts

Fastmcp supports async prompts for I/O operations:

```python
@mcp.prompt()
async def dynamic_prompt():
    """Prompt that fetches data asynchronously."""
    data = await fetch_external_data()
    return f"Use this data: {data}"
```

This could be useful for prompts that need to query Fusion 360 state.

### Prompt Categories

While fastmcp doesn't have built-in categories, we could add them via naming conventions:

```python
@mcp.prompt()
def manufacturing_cam_setup():
    """CAM setup prompt (manufacturing category)."""
    ...

@mcp.prompt()
def design_sketch_workflow():
    """Sketch workflow prompt (design category)."""
    ...
```

## References

- [FastMCP Prompts Documentation](https://gofastmcp.com/servers/prompts)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [Fusion MCP Modular Architecture](../../.kiro/steering/fusion-mcp-modular-architecture.md)
