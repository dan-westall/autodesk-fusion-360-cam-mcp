# Live Integration Tests Design Document

## Overview

The Live Integration Tests feature provides comprehensive HTTP-based testing against the running Fusion 360 add-in. This fills a critical gap in the testing strategy where unit tests cannot catch runtime issues like the task_queue callback pattern bug.

The design leverages pytest's fixture and marker system to create a flexible, maintainable test suite that can be run during active development when Fusion 360 is available.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Runner (pytest)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Smoke Tests │  │ Category    │  │ Empty Response          │  │
│  │             │  │ Tests       │  │ Detection Tests         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         └────────────────┼──────────────────────┘                │
│                          │                                       │
│                    ┌─────▼─────┐                                 │
│                    │  HTTP     │                                 │
│                    │  Client   │                                 │
│                    │  Helper   │                                 │
│                    └─────┬─────┘                                 │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              FusionMCPBridge (port 5001)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Request Router                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Design       │  │ MANUFACTURE  │  │ System               │   │
│  │ Handlers     │  │ Handlers     │  │ Handlers             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Test File Organization

```
FusionMCPBridge/tests/
├── test_live_integration.py      # Current: Basic live tests
├── test_live_design.py           # NEW: Design workspace tests
├── test_live_manufacture.py      # NEW: MANUFACTURE workspace tests
├── test_live_setups.py           # NEW: Setup management tests
├── test_live_toolpaths.py        # NEW: Toolpath tests
├── test_live_tool_libraries.py   # NEW: Tool library tests
├── test_live_errors.py           # NEW: Error response tests
└── conftest.py                   # NEW: Shared fixtures
```

## Components and Interfaces

### HTTP Client Helper (`conftest.py`)

```python
# Shared fixtures and helpers for all live tests

import pytest
import requests
from typing import Dict, Any, Optional

BRIDGE_BASE_URL = "http://localhost:5001"
REQUEST_TIMEOUT = 10

def is_bridge_running() -> bool:
    """Check if the Fusion 360 bridge is accessible."""
    try:
        response = requests.get(f"{BRIDGE_BASE_URL}/test_connection", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def make_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """Make HTTP request and return structured result."""
    # Implementation details...

@pytest.fixture(scope="session")
def bridge_available():
    """Session-scoped fixture to check bridge availability."""
    if not is_bridge_running():
        pytest.skip("Fusion 360 bridge not running")
    return True

@pytest.fixture
def cam_workspace_required(bridge_available):
    """Fixture that verifies MANUFACTURE workspace is accessible."""
    result = make_request("/cam/toolpaths")
    if "NO_CAM_DATA" in str(result):
        pytest.skip("MANUFACTURE workspace not active or no CAM document")
    return True
```

### Test Categories

#### 1. Smoke Tests (`TestSmokeTests`)
Quick validation tests that run in under 10 seconds.

```python
class TestSmokeTests:
    """Quick validation tests for basic functionality."""
    
    def test_bridge_responds(self, bridge_available):
        """Verify bridge is responding."""
        
    def test_cam_setups_not_broken(self, bridge_available):
        """Quick check that CAM setups endpoint works."""
        
    def test_cam_toolpaths_not_broken(self, bridge_available):
        """Quick check that CAM toolpaths endpoint works."""
```

#### 2. Empty Response Detection (`TestEmptyResponseDetection`)
Parameterized tests that catch the task_queue callback bug.

```python
class TestEmptyResponseDetection:
    """Tests to catch the task_queue callback bug."""
    
    ENDPOINTS_TO_CHECK = [
        ("/cam/setups", "GET"),
        ("/cam/toolpaths", "GET"),
        ("/tool-libraries", "GET"),
        # ... more endpoints
    ]
    
    @pytest.mark.parametrize("endpoint,method", ENDPOINTS_TO_CHECK)
    def test_endpoint_not_empty(self, bridge_available, endpoint, method):
        """Verify endpoint does not return empty {}."""
```

#### 3. Design Workspace Tests (`test_live_design.py`)

```python
class TestDesignGeometry:
    """Tests for geometry creation endpoints."""
    
    def test_draw_box_response_structure(self, bridge_available):
        """Test /draw-box returns proper response."""
        
    def test_draw_cylinder_response_structure(self, bridge_available):
        """Test /draw-cylinder returns proper response."""

class TestDesignSketching:
    """Tests for sketching endpoints."""
    
    def test_draw_circle_response_structure(self, bridge_available):
        """Test /draw-circle returns proper response."""

class TestDesignFeatures:
    """Tests for feature endpoints."""
    
    def test_extrude_response_structure(self, bridge_available):
        """Test /extrude returns proper response."""

class TestDesignExport:
    """Tests for export endpoints."""
    
    def test_export_step_response_structure(self, bridge_available):
        """Test /export-step returns proper response."""
```

#### 4. MANUFACTURE Workspace Tests (`test_live_manufacture.py`)

```python
class TestSetupManagement:
    """Tests for CAM setup management."""
    
    def test_list_setups_returns_data(self, cam_workspace_required):
        """Test /cam/setups returns setup list."""
        
    def test_get_setup_with_invalid_id(self, cam_workspace_required):
        """Test /cam/setups/{id} with invalid ID returns 404."""
        
    def test_create_setup_response(self, cam_workspace_required):
        """Test POST /cam/setups creates setup."""

class TestToolpathManagement:
    """Tests for toolpath endpoints."""
    
    def test_list_toolpaths_returns_data(self, cam_workspace_required):
        """Test /cam/toolpaths returns toolpath list."""

class TestToolLibraries:
    """Tests for tool library endpoints."""
    
    def test_list_libraries_returns_data(self, cam_workspace_required):
        """Test /tool-libraries returns library list."""
```

#### 5. Setup-Toolpath Integration Tests (`test_live_setups.py`)

```python
class TestSetupToolpathIntegration:
    """Tests for setup-toolpath relationships."""
    
    def test_get_setup_toolpaths(self, cam_workspace_required):
        """Test /cam/setups/{id}/toolpaths returns toolpaths."""
        
    def test_find_toolpath_setup(self, cam_workspace_required):
        """Test /cam/toolpaths/{id}/setup returns parent setup."""
        
    def test_setup_toolpath_mapping(self, cam_workspace_required):
        """Test bidirectional mapping consistency."""

class TestPartPosition:
    """Tests for part position endpoints."""
    
    def test_get_part_position(self, cam_workspace_required):
        """Test /cam/setups/{id}/part-position returns position."""
        
    def test_set_part_position_validation(self, cam_workspace_required):
        """Test part position validation."""

class TestStockConfiguration:
    """Tests for stock configuration endpoints."""
    
    def test_get_stock_configuration(self, cam_workspace_required):
        """Test stock configuration is returned with setup."""
```

#### 6. Error Response Tests (`test_live_errors.py`)

```python
class TestErrorResponses:
    """Tests for consistent error handling."""
    
    INVALID_ID_ENDPOINTS = [
        ("/cam/setups/invalid_id_12345", "GET", 404),
        ("/cam/toolpaths/invalid_id_12345", "GET", 404),
        ("/tool-libraries/invalid_id_12345", "GET", 404),
    ]
    
    @pytest.mark.parametrize("endpoint,method,expected_status", INVALID_ID_ENDPOINTS)
    def test_invalid_id_returns_404(self, bridge_available, endpoint, method, expected_status):
        """Test invalid IDs return proper 404 responses."""
        
    def test_error_response_structure(self, bridge_available):
        """Test error responses have consistent structure."""
```

## Data Models

### Test Result Model

```python
@dataclass
class TestResult:
    endpoint: str
    method: str
    status_code: Optional[int]
    response: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    duration_ms: Optional[float] = None
```

### Endpoint Definition Model

```python
@dataclass
class EndpointDefinition:
    path: str
    method: str
    category: str  # "design", "manufacture", "system"
    requires_cam: bool = False
    expected_fields: List[str] = field(default_factory=list)
    description: str = ""
```

## Endpoint Coverage Matrix

### Design Workspace Endpoints

| Endpoint | Method | Test Class | Priority |
|----------|--------|------------|----------|
| `/test_connection` | GET | TestSmokeTests | High |
| `/draw-box` | POST | TestDesignGeometry | Medium |
| `/draw-cylinder` | POST | TestDesignGeometry | Medium |
| `/draw-circle` | POST | TestDesignSketching | Medium |
| `/draw-lines` | POST | TestDesignSketching | Medium |
| `/extrude` | POST | TestDesignFeatures | Medium |
| `/revolve` | POST | TestDesignFeatures | Medium |
| `/fillet` | POST | TestDesignFeatures | Medium |
| `/export-step` | POST | TestDesignExport | Low |
| `/export-stl` | POST | TestDesignExport | Low |

### MANUFACTURE Workspace Endpoints

| Endpoint | Method | Test Class | Priority |
|----------|--------|------------|----------|
| `/cam/setups` | GET | TestSetupManagement | High |
| `/cam/setups` | POST | TestSetupManagement | High |
| `/cam/setups/{id}` | GET | TestSetupManagement | High |
| `/cam/setups/{id}` | PUT | TestSetupManagement | Medium |
| `/cam/setups/{id}` | DELETE | TestSetupManagement | Medium |
| `/cam/setups/{id}/duplicate` | POST | TestSetupManagement | Medium |
| `/cam/setups/{id}/toolpaths` | GET | TestSetupToolpathIntegration | High |
| `/cam/setups/{id}/part-position` | GET | TestPartPosition | Medium |
| `/cam/setups/{id}/part-position` | PUT | TestPartPosition | Medium |
| `/cam/toolpaths` | GET | TestToolpathManagement | High |
| `/cam/toolpaths/{id}` | GET | TestToolpathManagement | Medium |
| `/cam/toolpaths/{id}/setup` | GET | TestSetupToolpathIntegration | High |
| `/cam/toolpaths/{id}/heights` | GET | TestToolpathManagement | Medium |
| `/cam/toolpaths/{id}/passes` | GET | TestToolpathManagement | Medium |
| `/cam/toolpaths/{id}/linking` | GET | TestToolpathManagement | Medium |
| `/tool-libraries` | GET | TestToolLibraries | High |
| `/tool-libraries/{id}` | GET | TestToolLibraries | Medium |
| `/cam/tools` | GET | TestToolpathManagement | Medium |

## Error Handling

### Test Failure Messages

All test failures should include:
1. **What failed**: Clear description of the assertion that failed
2. **Why it matters**: Explanation of the bug this catches
3. **How to fix**: Suggested remediation steps

Example:
```python
assert result["response"] != {}, (
    f"CRITICAL: {method} {endpoint} returned empty {{}}. "
    f"This endpoint's handler likely uses the broken task_queue callback pattern. "
    f"Fix: Call the _impl function directly instead of using task_queue for read-only operations."
)
```

### Skip Conditions

Tests should skip gracefully when:
- Bridge is not running
- MANUFACTURE workspace is not active
- No CAM document is open
- Required setup/toolpath doesn't exist

## Testing Strategy

### Test Execution Order

1. **Session Setup**: Check bridge availability
2. **Smoke Tests**: Quick validation (< 10 seconds)
3. **Empty Response Detection**: Catch task_queue bugs
4. **Category Tests**: Design, MANUFACTURE, etc.
5. **Error Response Tests**: Validate error handling

### Parallel Execution

Tests within the same class can run in parallel if they don't modify state. Tests that create/modify/delete entities should be marked for sequential execution.

```python
@pytest.mark.sequential
class TestSetupCRUD:
    """Tests that modify setups - run sequentially."""
```

### Test Data Management

- Tests should not assume specific setups or toolpaths exist
- Tests should handle empty CAM documents gracefully
- Tests that create entities should clean up after themselves (when possible)

## Implementation Plan

### Phase 1: Foundation (Current)
- ✅ Basic test infrastructure
- ✅ Smoke tests
- ✅ Empty response detection
- ✅ Setup management tests

### Phase 2: MANUFACTURE Coverage
- [ ] Comprehensive toolpath tests
- [ ] Tool library tests
- [ ] Operation parameter tests (heights, passes, linking)

### Phase 3: Design Coverage
- [ ] Geometry creation tests
- [ ] Sketching tests
- [ ] Feature tests
- [ ] Export tests

### Phase 4: Advanced Testing
- [ ] Error response validation
- [ ] Response structure validation
- [ ] Performance benchmarks
- [ ] Stress testing

## Success Metrics

- **Coverage**: All HTTP endpoints have at least one live test
- **Detection Rate**: 100% of task_queue bugs caught before deployment
- **Execution Time**: Full suite completes in under 60 seconds
- **Reliability**: Tests pass consistently when bridge is healthy
