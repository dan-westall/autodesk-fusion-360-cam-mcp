# Reference: Fusion 360 Add-in Testing with Pytest
**Strategy:** The Humble Object Pattern (Logic Separation)
**Goal:** Enable standard unit testing without mocks or running Fusion 360.

## 1. The Core Constraint
The Autodesk API (`adsk`) is embedded in Fusion 360. It cannot be installed via pip and does not run in a standard terminal.
* **Result:** Any file containing `import adsk` will crash `pytest`.
* **Solution:** We isolate "Logic" from "API Interactions" completely.

## 2. Integration Testing Limitation (CRITICAL)
**Integration tests are NOT possible with Fusion 360's API outside of the Fusion 360 environment.**

### Why Integration Tests Fail:
- The `adsk` module only exists within Fusion 360's Python environment
- Fusion 360 API requires the full application context to function
- Mock objects cannot replicate the complex API behavior accurately
- Threading constraints require Fusion 360's main UI thread

### Testing Strategy:
- **Unit Tests**: Test pure Python logic in isolation (Green Zone)
- **Manual Testing**: Test API integration within Fusion 360 environment
- **Modular Tests**: Test module loading and routing without API calls
- **Component Tests**: Test individual handlers with mock responses

### What CAN Be Tested:
- ✅ Pure Python logic and algorithms
- ✅ HTTP request routing and validation
- ✅ Module discovery and loading
- ✅ Configuration management
- ✅ Data serialization/deserialization
- ✅ Error handling patterns

### What CANNOT Be Tested:
- ❌ Actual Fusion 360 API calls
- ❌ Geometry creation and manipulation
- ❌ CAM operations and toolpath generation
- ❌ Tool library access and management
- ❌ End-to-end workflow integration
- ❌ Threading behavior with CustomEvents

## 3. The Architecture: "Green Zone" vs. "Red Zone"
We split the codebase into two distinct layers.

![Architecture Diagram](https://mermaid.ink/img/pako:eNp1ksFOwzAMhl_F8gl14bTdeIB24oA4cOIwCW6TNhZNEjvFClT13UlarYGEDi6R49_2b_85oYw1QoE8FttHVEg_zSg0eF9yS-fLhaT8kC5y-Pz8Ch8fH9dGSQZt0Hjwy4y2Cg10oR20g3FwAdoq0C8O_A7WwR0Y4N466IEP8A3s4BEM0M-l1kgrdOQyF-WzUsqC8kVaQkX5VbJ2K-2sLCSXlaRaS9k2yYtS6oKysyTdtU1H-VlS3qR104b9_m-8y1iW5FpW5L3k4mF3X0uR7yXlG2l3d5eWp_xH0j5Kyi-S9kVSfpO0b1e_4wU44A144P94P96PD-PD-DA-jI_jw_g4PoxP4MP4BD6MT-DD-AQ-nI_z43w4P86P8-P8OD_OT_KT_CQ_yU_yk_wkP8lP8rP8LD_Lz_Kz_Cw_y8_yC_kFf8k)

| Zone | Layer Name | Dependencies | Testable? | Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| 🟢 | **Green Zone** (Logic) | Standard Python only (`math`, `json`, etc.) | **YES** (Pytest) | Math, Algorithms, Data Parsing, State Logic. |
| 🔴 | **Red Zone** (Interface) | `adsk.core`, `adsk.fusion` | **NO** (Manual) | Reading Fusion inputs, Calling Green Zone, Creating Fusion geometry. |

## 4. Implementation

### Directory Structure
```text
my_addin/
├── logic.py         # 🟢 PURE PYTHON (No adsk imports)
├── commands.py      # 🔴 FUSION API (Imports adsk & logic)
└── tests/
    └── test_logic.py # 🟢 STANDARD PYTEST
```

### Code Example A: The Green Zone (`logic.py`)
*This file contains the "brains." It is safe for Pytest because it knows nothing about Fusion.*

```python
# logic.py
# STRICT RULE: Do not import adsk here.

def calculate_grid_coordinates(width: float, height: float, count: int) -> list:
    \"\"\"
    Pure math logic.
    Returns standard Python tuples: [(0,0), (10,0), (20,0)...]
    \"\"\"
    step_x = width / (count - 1)
    points = []
    for i in range(count):
        points.append((i * step_x, 0.0))
    return points
```

### Code Example B: The Red Zone (`commands.py`)
*This file is the "Humble Object." It is a thin wrapper that bridges Fusion to the logic.*

```python
# commands.py
import adsk.core, adsk.fusion
from .logic import calculate_grid_coordinates  # Import logic

def run_grid_command(width, height, count):
    # 1. DELEGATE: Get raw data from the Green Zone
    raw_points = calculate_grid_coordinates(width, height, count)
    
    # 2. EXECUTE: Use Fusion API to draw the result
    app = adsk.core.Application.get()
    sketch = app.activeProduct.rootComponent.sketches.add(
        app.activeProduct.rootComponent.xYConstructionPlane
    )
    
    for x, y in raw_points:
        # Convert standard tuple to Fusion Point3D here
        pt = adsk.core.Point3D.create(x, y, 0)
        sketch.sketchPoints.add(pt)
```

### Code Example C: The Test (`test_logic.py`)
*Runs instantly in CI/CD or local terminal.*

```python
# test_logic.py
import pytest
from my_addin.logic import calculate_grid_coordinates

def test_grid_math():
    # Tests the algorithm without launching Fusion 360
    points = calculate_grid_coordinates(width=100.0, height=50.0, count=3)
    
    assert len(points) == 3
    assert points[0] == (0.0, 0.0)
    assert points[1] == (50.0, 0.0)
    assert points[2] == (100.0, 0.0)
```

## 5. The Golden Rule of Dependencies
To ensure `pytest` never crashes:
1.  **Red** may import **Green**.
2.  **Green** must **NEVER** import **Red**.
3.  Tests only import **Green**.

## 6. Testing Best Practices for Fusion 360 Add-ins

### Recommended Testing Approach:
1. **Isolate Logic**: Extract all business logic into pure Python functions
2. **Test Logic Only**: Write comprehensive unit tests for the Green Zone
3. **Manual API Testing**: Test Fusion 360 integration manually within the application
4. **Modular Testing**: Test system components that don't require Fusion 360 API
5. **Error Handling**: Test error conditions and edge cases in pure Python

### Testing Tools:
- **pytest**: For Green Zone unit testing
- **Fusion 360 Text Commands**: For manual API testing and debugging
- **HTTP clients**: For testing HTTP endpoints (curl, Postman)
- **Module loaders**: For testing modular architecture components

### Validation Strategy:
- Validate all mathematical calculations and algorithms with unit tests
- Validate HTTP routing and request handling with integration tests
- Validate Fusion 360 API integration through manual testing
- Validate error handling and edge cases with comprehensive test coverage

## 7. Test Organization Structure (CRITICAL)

### Separate Test Directories
This project has TWO separate `core/` module structures with DIFFERENT interfaces:
- `Server/core/` - MCP Server components (module-level functions)
- `FusionMCPBridge/core/` - Fusion 360 Add-in components (class-based)

**Tests MUST be organized in separate directories to avoid Python module caching conflicts:**

```text
Server/
├── core/
│   ├── config.py          # Module-level functions: get_base_url(), get_endpoints()
│   ├── registry.py        # ToolRegistry class and global functions
│   ├── request_handler.py # HTTP request handling with retry logic
│   └── loader.py          # Module discovery and loading
└── tests/
    ├── __init__.py
    ├── test_core_config.py
    ├── test_core_registry.py
    └── test_core_request_handler.py

FusionMCPBridge/
├── core/
│   ├── config.py          # ConfigurationManager class
│   ├── router.py          # RequestRouter class
│   ├── validation.py      # RequestValidator class
│   └── loader.py          # ModuleLoader class (different interface)
└── tests/
    ├── __init__.py
    ├── test_core_config.py
    ├── test_core_router.py
    ├── test_core_validation.py
    └── test_core_loader.py
```

### Running Tests (MANDATORY)
**Tests MUST be run separately** due to Python module caching:

```bash
# Run Server tests
uv run pytest Server/tests/ -v

# Run FusionMCPBridge tests  
uv run pytest FusionMCPBridge/tests/ -v

# DO NOT run both together - causes import conflicts!
# ❌ uv run pytest Server/tests/ FusionMCPBridge/tests/
```

### Why Separate Test Runs?
- Both directories have `core/` modules with the same names but different interfaces
- Python caches the first imported module
- Running tests together causes the wrong `core.config` to be imported
- This results in `AttributeError` or `ImportError` failures

### Test File Naming Convention
- Test files should be named `test_<module_name>.py`
- Place tests in the same package as the code they test
- Use relative imports within test files:

```python
# Server/tests/test_core_config.py
import sys
import os
server_path = os.path.join(os.path.dirname(__file__), "..")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

from core.config import get_base_url, get_endpoints
```

### Test Coverage Summary
- **Server/tests/**: Tests for MCP Server components (~85 tests)
- **FusionMCPBridge/tests/**: Tests for Fusion 360 Add-in components (~84 tests)
- Total: ~169 passing tests

### Adding New Tests
1. Determine which component you're testing (Server or FusionMCPBridge)
2. Create test file in the appropriate `tests/` directory
3. Use correct import path for that component's `core/` module
4. Run tests for that directory only to verify

## 8. Live Integration Tests (CRITICAL for Active Development)

### The Testing Gap
Unit tests using the Humble Object Pattern cannot catch certain runtime issues:
- **Task queue callback bugs**: Handlers using the broken `task_queue` callback pattern return empty `{}`
- **HTTP endpoint routing issues**: Actual request/response behavior
- **Real API behavior**: Differences between mocked and actual Fusion 360 responses

### Integration Test Suite
Location: `FusionMCPBridge/tests/test_live_*.py`

These tests make **real HTTP requests** to the running Fusion 360 add-in and catch issues that unit tests miss.

### Prerequisites
1. Fusion 360 running
2. FusionMCPBridge add-in active
3. A document with setups open (for MANUFACTURE workspace tests)

### Running Integration Tests
Integration tests are **skipped by default**. Use the `--integration` flag to run them:

```bash
# Run all integration tests (requires Fusion 360 running)
uv run pytest FusionMCPBridge/tests/ -v --integration

# Run only smoke tests (quick validation)
uv run pytest FusionMCPBridge/tests/ -v --integration -m "smoke"

# Run only MANUFACTURE workspace tests
uv run pytest FusionMCPBridge/tests/ -v --integration -m "manufacture"

# Run only Design workspace tests
uv run pytest FusionMCPBridge/tests/ -v --integration -m "design"

# Skip destructive tests (that modify Fusion 360 state)
uv run pytest FusionMCPBridge/tests/ -v --integration -m "not destructive"

# Run unit tests only (integration tests skipped)
uv run pytest FusionMCPBridge/tests/ -v
```

### What Integration Tests Catch
- ✅ Empty `{}` responses from broken task_queue callback patterns
- ✅ HTTP endpoint routing issues
- ✅ Response structure validation
- ✅ Real API behavior vs mocked behavior
- ✅ Handler registration problems

### The Task Queue Callback Bug
This is the specific bug that integration tests catch:

**BROKEN Pattern** (returns empty `{}`):
```python
def handle_list_setups(path, method, data):
    result = {}
    def callback():
        nonlocal result
        result = list_setups_detailed()  # Never executes!
    task_queue.queue_task(..., callback=callback)
    return {"data": result}  # Returns empty {}
```

**CORRECT Pattern** (for read-only operations):
```python
def handle_list_setups(path, method, data):
    # Call impl directly - no task_queue for read-only operations
    result = list_setups_detailed()
    return {"data": result}
```

### Development Workflow with Integration Tests
1. Make code changes to handlers
2. Restart add-in: `curl http://localhost:5002/addon/restart`
3. Run smoke tests: `uv run pytest FusionMCPBridge/tests/ -v --integration -m "smoke"`
4. If smoke tests pass, run full integration test suite
5. Fix any failures before committing

### Test Categories

| Test Class | Purpose |
|------------|---------|
| `TestSmokeTests` | Quick validation that basic endpoints work |
| `TestEmptyResponseDetection` | Catches task_queue callback bugs |
| `TestSetupManagementLive` | CAM setup endpoint validation |
| `TestToolpathLive` | Toolpath endpoint validation |
| `TestToolLibraryLive` | Tool library endpoint validation |
| `TestPartPositionLive` | Part position endpoint validation |

### When to Run Live Tests
- **Always**: Before committing handler changes
- **Always**: After fixing task_queue related bugs
- **Always**: When adding new HTTP endpoints
- **Recommended**: As part of development workflow after add-in restart