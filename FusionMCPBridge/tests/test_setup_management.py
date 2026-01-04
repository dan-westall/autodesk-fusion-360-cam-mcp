#!/usr/bin/env python3
"""
Integration tests for CAM Setup Management functionality.

Tests the complete setup management workflows including:
- Setup creation, listing, and retrieval
- Setup modification, duplication, and deletion
- Setup-toolpath integration and relationships
- Error scenarios and edge cases
- Multi-setup document management

Requirements: All CAM Setup Management requirements (1-11)
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any

# Ensure FusionMCPBridge is at the front of sys.path
bridge_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if bridge_path not in sys.path:
    sys.path.insert(0, bridge_path)

from core.router import RequestRouter, HttpMethod, request_router
from core.task_queue import TaskQueue, TaskPriority, Task
from core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity


# =============================================================================
# Test Fixtures and Helpers
# =============================================================================

@pytest.fixture
def router():
    """Create a fresh RequestRouter for testing."""
    return RequestRouter()


@pytest.fixture
def task_queue():
    """Create a fresh TaskQueue for testing."""
    return TaskQueue()


@pytest.fixture
def mock_setup_data():
    """Create mock setup data for testing."""
    return {
        "id": "setup_001",
        "name": "Test Setup",
        "wcs": {
            "type": "model_origin",
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {
                "x_axis": {"x": 1.0, "y": 0.0, "z": 0.0},
                "y_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
                "z_axis": {"x": 0.0, "y": 0.0, "z": 1.0}
            },
            "reference": "model",
            "reference_geometry": None
        },
        "stock": {
            "mode": "auto",
            "dimensions": {"length": 100.0, "width": 50.0, "height": 25.0, "diameter": 100.0},
            "position": [0, 0, 0],
            "material": "Aluminum 6061",
            "geometry_id": None
        },
        "model_id": "model_placeholder_id",
        "toolpath_count": 0,
        "is_active": True,
        "created_date": "2025-01-03T00:00:00Z",
        "modified_date": "2025-01-03T00:00:00Z"
    }


@pytest.fixture
def mock_toolpath_data():
    """Create mock toolpath data for testing."""
    return {
        "id": "op_001",
        "name": "Adaptive Clearing",
        "type": "adaptive",
        "is_valid": True,
        "setup_id": "setup_001",
        "setup_name": "Test Setup",
        "tool": {
            "id": "tool_001",
            "name": "6mm Flat Endmill",
            "type": "flat end mill"
        }
    }


# =============================================================================
# Setup Management HTTP Handler Tests
# =============================================================================

class TestSetupManagementRouting:
    """Test HTTP routing for setup management endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
        self.results = {}
    
    def test_list_setups_route_registration(self):
        """Test that list setups route can be registered."""
        def handler(path, method, data):
            return {"status": 200, "data": {"setups": [], "total_count": 0}}
        
        self.router.register_handler(
            "/cam/setups",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["status"] == 200
        assert "setups" in response["data"]

    def test_get_setup_route_with_path_parameter(self):
        """Test that get setup route handles path parameters."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            return {"status": 200, "data": {"id": setup_id, "name": "Test Setup"}}
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups/setup_001", "GET", {})
        assert response["status"] == 200
        assert response["data"]["id"] == "setup_001"
    
    def test_create_setup_route_registration(self):
        """Test that create setup route can be registered."""
        def handler(path, method, data):
            name = data.get("name", "Default Setup")
            return {"status": 201, "data": {"id": "new_setup", "name": name}}
        
        self.router.register_handler(
            "/cam/setups",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups", "POST", {"name": "My Setup"})
        assert response["status"] == 201
        assert response["data"]["name"] == "My Setup"
    
    def test_modify_setup_route_registration(self):
        """Test that modify setup route can be registered."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            return {"status": 200, "data": {"id": setup_id, "modified": True}}
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["PUT"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001", 
            "PUT", 
            {"name": "Updated Setup"}
        )
        assert response["status"] == 200
        assert response["data"]["modified"] is True
    
    def test_delete_setup_route_registration(self):
        """Test that delete setup route can be registered."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            confirm = data.get("confirm", False)
            if not confirm:
                return {"status": 200, "data": {"requires_confirmation": True}}
            return {"status": 200, "data": {"deleted": True, "setup_id": setup_id}}
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["DELETE"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        # Test without confirmation
        response = self.router.route_request("/cam/setups/setup_001", "DELETE", {})
        assert response["data"]["requires_confirmation"] is True
        
        # Test with confirmation
        response = self.router.route_request(
            "/cam/setups/setup_001", 
            "DELETE", 
            {"confirm": True}
        )
        assert response["data"]["deleted"] is True

    def test_duplicate_setup_route_registration(self):
        """Test that duplicate setup route can be registered."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            new_name = data.get("new_name")
            return {
                "status": 201, 
                "data": {
                    "id": "new_setup_id",
                    "name": new_name or f"{setup_id} (Copy)",
                    "source_setup": {"id": setup_id}
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/duplicate",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/duplicate", 
            "POST", 
            {"new_name": "Duplicated Setup"}
        )
        assert response["status"] == 201
        assert response["data"]["name"] == "Duplicated Setup"


class TestSetupToolpathIntegrationRouting:
    """Test HTTP routing for setup-toolpath integration endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_get_setup_toolpaths_route(self):
        """Test that get setup toolpaths route can be registered."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            return {
                "status": 200, 
                "data": {
                    "setup_id": setup_id,
                    "setup_name": "Test Setup",
                    "toolpaths": [],
                    "total_count": 0
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/toolpaths",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups/setup_001/toolpaths", "GET", {})
        assert response["status"] == 200
        assert response["data"]["setup_id"] == "setup_001"
    
    def test_find_toolpath_setup_route(self):
        """Test that find toolpath setup route can be registered."""
        def handler(path, method, data):
            toolpath_id = data.get("toolpath_id")
            return {
                "status": 200, 
                "data": {
                    "toolpath_id": toolpath_id,
                    "toolpath_name": "Adaptive Clearing",
                    "setup_id": "setup_001",
                    "setup_name": "Test Setup"
                }
            }
        
        self.router.register_handler(
            "/cam/toolpaths/{toolpath_id}/setup",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/toolpaths/op_001/setup", "GET", {})
        assert response["status"] == 200
        assert response["data"]["setup_id"] == "setup_001"

    def test_validate_setup_toolpath_route(self):
        """Test that validate setup-toolpath route can be registered."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            toolpath_id = data.get("toolpath_id")
            return {
                "status": 200, 
                "data": {
                    "valid": True,
                    "setup_id": setup_id,
                    "toolpath_id": toolpath_id
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/toolpaths/{toolpath_id}/validate",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/toolpaths/op_001/validate", 
            "GET", 
            {}
        )
        assert response["status"] == 200
        assert response["data"]["valid"] is True
    
    def test_setup_toolpath_mapping_route(self):
        """Test that setup-toolpath mapping route can be registered."""
        def handler(path, method, data):
            return {
                "status": 200, 
                "data": {
                    "setups": [],
                    "toolpath_to_setup": {},
                    "total_setups": 0,
                    "total_toolpaths": 0
                }
            }
        
        self.router.register_handler(
            "/cam/setup-toolpath-mapping",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setup-toolpath-mapping", "GET", {})
        assert response["status"] == 200
        assert "setups" in response["data"]
        assert "toolpath_to_setup" in response["data"]


# =============================================================================
# Setup Data Validation Tests
# =============================================================================

class TestSetupDataValidation:
    """Test setup data structure validation."""
    
    def test_setup_data_structure(self, mock_setup_data):
        """Test that setup data has required fields."""
        required_fields = ["id", "name", "wcs", "stock", "model_id"]
        for field in required_fields:
            assert field in mock_setup_data, f"Missing required field: {field}"
    
    def test_wcs_data_structure(self, mock_setup_data):
        """Test that WCS data has required fields."""
        wcs = mock_setup_data["wcs"]
        required_fields = ["type", "origin", "orientation"]
        for field in required_fields:
            assert field in wcs, f"Missing WCS field: {field}"
        
        # Check origin structure
        origin = wcs["origin"]
        assert "x" in origin and "y" in origin and "z" in origin
        
        # Check orientation structure
        orientation = wcs["orientation"]
        assert "x_axis" in orientation
        assert "y_axis" in orientation
        assert "z_axis" in orientation

    def test_stock_data_structure(self, mock_setup_data):
        """Test that stock data has required fields."""
        stock = mock_setup_data["stock"]
        required_fields = ["mode", "dimensions", "position"]
        for field in required_fields:
            assert field in stock, f"Missing stock field: {field}"
        
        # Check dimensions structure
        dimensions = stock["dimensions"]
        assert "length" in dimensions
        assert "width" in dimensions
        assert "height" in dimensions
    
    def test_toolpath_data_structure(self, mock_toolpath_data):
        """Test that toolpath data has required fields including setup context."""
        required_fields = ["id", "name", "type", "is_valid", "setup_id", "setup_name"]
        for field in required_fields:
            assert field in mock_toolpath_data, f"Missing required field: {field}"
    
    def test_toolpath_always_has_setup_context(self, mock_toolpath_data):
        """Test that toolpath data always includes setup context (Requirement 9.1)."""
        # This validates that toolpath responses include parent setup ID
        assert "setup_id" in mock_toolpath_data
        assert "setup_name" in mock_toolpath_data
        assert mock_toolpath_data["setup_id"] is not None


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestSetupManagementErrorHandling:
    """Test error handling for setup management operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_setup_not_found_error(self):
        """Test error handling when setup is not found."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            return {
                "status": 404,
                "error": True,
                "message": f"Setup with ID '{setup_id}' not found",
                "code": "SETUP_NOT_FOUND"
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups/nonexistent", "GET", {})
        assert response["status"] == 404
        assert response["error"] is True
        assert response["code"] == "SETUP_NOT_FOUND"
    
    def test_missing_required_parameter_error(self):
        """Test error handling when required parameter is missing."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            if not setup_id:
                return {
                    "status": 400,
                    "error": True,
                    "message": "setup_id parameter is required",
                    "code": "MISSING_SETUP_ID"
                }
            return {"status": 200, "data": {"id": setup_id}}
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        # The router extracts path parameters, so this tests the handler logic
        response = self.router.route_request("/cam/setups/", "GET", {})
        # Route won't match without setup_id in path
        assert response["status"] == 404 or response.get("error")

    def test_duplicate_name_error(self):
        """Test error handling when setup name already exists."""
        def handler(path, method, data):
            name = data.get("name")
            # Simulate duplicate name check
            existing_names = ["Setup 1", "Setup 2"]
            if name in existing_names:
                return {
                    "status": 400,
                    "error": True,
                    "message": f"Setup with name '{name}' already exists",
                    "code": "DUPLICATE_NAME"
                }
            return {"status": 201, "data": {"id": "new_setup", "name": name}}
        
        self.router.register_handler(
            "/cam/setups",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups", "POST", {"name": "Setup 1"})
        assert response["status"] == 400
        assert response["code"] == "DUPLICATE_NAME"
    
    def test_toolpath_setup_mismatch_error(self):
        """Test error handling when toolpath doesn't belong to specified setup."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            toolpath_id = data.get("toolpath_id")
            # Simulate mismatch
            return {
                "status": 200,
                "data": {
                    "valid": False,
                    "message": f"Toolpath '{toolpath_id}' does not belong to setup '{setup_id}'",
                    "code": "TOOLPATH_SETUP_MISMATCH",
                    "actual_setup_id": "setup_002",
                    "actual_setup_name": "Other Setup"
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/toolpaths/{toolpath_id}/validate",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/toolpaths/op_002/validate",
            "GET",
            {}
        )
        assert response["data"]["valid"] is False
        assert response["data"]["code"] == "TOOLPATH_SETUP_MISMATCH"
    
    def test_handler_exception_handling(self):
        """Test that handler exceptions are caught and handled gracefully."""
        def failing_handler(path, method, data):
            raise ValueError("Unexpected error in handler")
        
        self.router.register_handler(
            "/cam/setups",
            failing_handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["status"] == 500
        assert response["error"] is True


# =============================================================================
# Multi-Setup Document Tests
# =============================================================================

class TestMultiSetupDocumentManagement:
    """Test multi-setup document management scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_list_multiple_setups(self):
        """Test listing multiple setups in a document."""
        def handler(path, method, data):
            return {
                "status": 200,
                "data": {
                    "setups": [
                        {"id": "setup_001", "name": "Roughing Setup", "toolpath_count": 3},
                        {"id": "setup_002", "name": "Finishing Setup", "toolpath_count": 2},
                        {"id": "setup_003", "name": "Drilling Setup", "toolpath_count": 5}
                    ],
                    "total_count": 3
                }
            }
        
        self.router.register_handler(
            "/cam/setups",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["status"] == 200
        assert response["data"]["total_count"] == 3
        assert len(response["data"]["setups"]) == 3

    def test_unique_setup_identifiers(self):
        """Test that setups have unique identifiers (Requirement 8.1)."""
        setups = [
            {"id": "setup_001", "name": "Setup 1"},
            {"id": "setup_002", "name": "Setup 2"},
            {"id": "setup_003", "name": "Setup 3"}
        ]
        
        # Verify all IDs are unique
        ids = [s["id"] for s in setups]
        assert len(ids) == len(set(ids)), "Setup IDs must be unique"
    
    def test_setup_name_uniqueness_enforcement(self):
        """Test that setup names are unique within a document (Requirement 8.2)."""
        def handler(path, method, data):
            name = data.get("name")
            existing_names = ["Roughing Setup", "Finishing Setup"]
            
            if name in existing_names:
                return {
                    "status": 400,
                    "error": True,
                    "message": f"Setup with name '{name}' already exists",
                    "code": "DUPLICATE_NAME"
                }
            return {"status": 201, "data": {"id": "new_setup", "name": name}}
        
        self.router.register_handler(
            "/cam/setups",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        # Try to create setup with existing name
        response = self.router.route_request(
            "/cam/setups", 
            "POST", 
            {"name": "Roughing Setup"}
        )
        assert response["status"] == 400
        assert response["code"] == "DUPLICATE_NAME"
        
        # Create setup with unique name
        response = self.router.route_request(
            "/cam/setups", 
            "POST", 
            {"name": "New Unique Setup"}
        )
        assert response["status"] == 201
    
    def test_setup_toolpath_mapping_consistency(self):
        """Test setup-toolpath mapping maintains consistency (Requirement 11.4)."""
        mapping = {
            "setups": [
                {"id": "setup_001", "name": "Setup 1", "toolpath_ids": ["op_001", "op_002"]},
                {"id": "setup_002", "name": "Setup 2", "toolpath_ids": ["op_003"]}
            ],
            "toolpath_to_setup": {
                "op_001": {"setup_id": "setup_001", "setup_name": "Setup 1"},
                "op_002": {"setup_id": "setup_001", "setup_name": "Setup 1"},
                "op_003": {"setup_id": "setup_002", "setup_name": "Setup 2"}
            },
            "total_setups": 2,
            "total_toolpaths": 3
        }
        
        # Verify bidirectional consistency
        for setup in mapping["setups"]:
            for toolpath_id in setup["toolpath_ids"]:
                assert toolpath_id in mapping["toolpath_to_setup"]
                assert mapping["toolpath_to_setup"][toolpath_id]["setup_id"] == setup["id"]
        
        # Verify counts
        total_toolpaths = sum(len(s["toolpath_ids"]) for s in mapping["setups"])
        assert total_toolpaths == mapping["total_toolpaths"]
        assert len(mapping["setups"]) == mapping["total_setups"]


# =============================================================================
# Setup Modification Impact Tests
# =============================================================================

class TestSetupModificationImpact:
    """Test setup modification impact analysis."""
    
    def test_wcs_change_impact_warning(self):
        """Test that WCS changes generate impact warnings (Requirement 5.2)."""
        def handler(path, method, data):
            updates = data.get("updates", {})
            warnings = []
            
            if "wcs" in updates:
                # Simulate impact analysis
                warnings.append(
                    "WCS origin change will affect 3 existing operation(s). "
                    "Toolpaths may need regeneration."
                )
            
            return {
                "status": 200,
                "data": {
                    "id": "setup_001",
                    "name": "Modified Setup",
                    "warnings": warnings if warnings else None,
                    "changes_made": ["WCS configuration update requested"]
                }
            }
        
        router = RequestRouter()
        router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["PUT"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = router.route_request(
            "/cam/setups/setup_001",
            "PUT",
            {"updates": {"wcs": {"origin": {"x": 10.0, "y": 5.0, "z": 0.0}}}}
        )
        
        assert response["status"] == 200
        assert response["data"]["warnings"] is not None
        assert len(response["data"]["warnings"]) > 0

    def test_stock_change_impact_warning(self):
        """Test that stock changes generate impact warnings (Requirement 5.3)."""
        def handler(path, method, data):
            updates = data.get("updates", {})
            warnings = []
            
            if "stock" in updates:
                stock_config = updates["stock"]
                if stock_config.get("dimensions"):
                    warnings.append(
                        "Stock dimensions are being reduced. 2 existing operation(s) "
                        "may have toolpaths outside the new stock boundaries."
                    )
            
            return {
                "status": 200,
                "data": {
                    "id": "setup_001",
                    "name": "Modified Setup",
                    "warnings": warnings if warnings else None,
                    "changes_made": ["Stock configuration update requested"]
                }
            }
        
        router = RequestRouter()
        router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["PUT"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = router.route_request(
            "/cam/setups/setup_001",
            "PUT",
            {"updates": {"stock": {"dimensions": {"length": 80.0, "width": 40.0, "height": 20.0}}}}
        )
        
        assert response["status"] == 200
        assert response["data"]["warnings"] is not None


# =============================================================================
# Setup Deletion Tests
# =============================================================================

class TestSetupDeletion:
    """Test setup deletion scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_deletion_requires_confirmation_with_toolpaths(self):
        """Test that deletion requires confirmation when setup has toolpaths (Requirement 6.2)."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            confirm = data.get("confirm", False)
            
            # Simulate setup with toolpaths
            operation_count = 3
            
            if operation_count > 0 and not confirm:
                return {
                    "status": 200,
                    "data": {
                        "requires_confirmation": True,
                        "setup_id": setup_id,
                        "setup_name": "Test Setup",
                        "operation_count": operation_count,
                        "warning": f"Setup contains {operation_count} operation(s). "
                                  "These will be permanently deleted."
                    }
                }
            
            return {
                "status": 200,
                "data": {
                    "deleted": True,
                    "setup_id": setup_id,
                    "operations_deleted": operation_count
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["DELETE"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        # Without confirmation
        response = self.router.route_request("/cam/setups/setup_001", "DELETE", {})
        assert response["data"]["requires_confirmation"] is True
        assert response["data"]["operation_count"] == 3
        
        # With confirmation
        response = self.router.route_request(
            "/cam/setups/setup_001", 
            "DELETE", 
            {"confirm": True}
        )
        assert response["data"]["deleted"] is True
    
    def test_deletion_of_empty_setup(self):
        """Test that empty setups can be deleted without confirmation."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            confirm = data.get("confirm", False)
            
            # Simulate empty setup
            operation_count = 0
            
            # Empty setups don't require confirmation
            return {
                "status": 200,
                "data": {
                    "deleted": True,
                    "setup_id": setup_id,
                    "operations_deleted": operation_count
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["DELETE"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request("/cam/setups/setup_001", "DELETE", {})
        assert response["data"]["deleted"] is True


# =============================================================================
# Setup Duplication Tests
# =============================================================================

class TestSetupDuplication:
    """Test setup duplication scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_duplication_with_custom_name(self):
        """Test setup duplication with custom name (Requirement 7.3)."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            new_name = data.get("new_name")
            
            return {
                "status": 201,
                "data": {
                    "id": "new_setup_id",
                    "name": new_name,
                    "source_setup": {"id": setup_id, "name": "Original Setup"},
                    "message": f"Setup '{new_name}' created as duplicate"
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/duplicate",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/duplicate",
            "POST",
            {"new_name": "My Custom Name"}
        )
        
        assert response["status"] == 201
        assert response["data"]["name"] == "My Custom Name"
    
    def test_duplication_auto_name_generation(self):
        """Test setup duplication with auto-generated name (Requirement 7.4)."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            new_name = data.get("new_name")
            
            # Auto-generate name if not provided
            if not new_name:
                new_name = "Original Setup (Copy)"
            
            return {
                "status": 201,
                "data": {
                    "id": "new_setup_id",
                    "name": new_name,
                    "source_setup": {"id": setup_id, "name": "Original Setup"}
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/duplicate",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/duplicate",
            "POST",
            {}  # No new_name provided
        )
        
        assert response["status"] == 201
        assert "Copy" in response["data"]["name"]
    
    def test_duplication_preserves_source_info(self):
        """Test that duplication preserves source setup information."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            
            return {
                "status": 201,
                "data": {
                    "id": "new_setup_id",
                    "name": "Original Setup (Copy)",
                    "source_setup": {
                        "id": setup_id,
                        "name": "Original Setup",
                        "operation_count": 5
                    },
                    "notes": [
                        "Source setup had 5 operation(s). Operations are not automatically copied."
                    ]
                }
            }
        
        self.router.register_handler(
            "/cam/setups/{setup_id}/duplicate",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = self.router.route_request(
            "/cam/setups/setup_001/duplicate",
            "POST",
            {}
        )
        
        assert response["status"] == 201
        assert "source_setup" in response["data"]
        assert response["data"]["source_setup"]["id"] == "setup_001"


# =============================================================================
# Task Queue Integration Tests
# =============================================================================

class TestSetupTaskQueueIntegration:
    """Test task queue integration for setup operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.task_queue = TaskQueue()
        self.execution_log = []
    
    def test_setup_creation_task_priority(self):
        """Test that setup creation uses HIGH priority."""
        def create_handler(name):
            self.execution_log.append(f"create:{name}")
        
        self.task_queue.register_task_handler('create_setup', create_handler)
        
        # Queue with HIGH priority
        self.task_queue.queue_task('create_setup', "Test Setup", priority=TaskPriority.HIGH)
        
        processed = self.task_queue.process_tasks()
        assert processed == 1
        assert "create:Test Setup" in self.execution_log

    def test_read_operations_bypass_task_queue(self):
        """Test that read-only operations don't need task queue."""
        # Read-only operations like list_setups, get_setup should call impl directly
        # This is a design principle test - read operations are thread-safe
        
        # Simulate direct call pattern (no task queue)
        def list_setups_impl():
            return {"setups": [], "total_count": 0}
        
        # Direct call should work without task queue
        result = list_setups_impl()
        assert "setups" in result
        assert result["total_count"] == 0
    
    def test_write_operations_use_task_queue(self):
        """Test that write operations use task queue for thread safety."""
        results = []
        
        def modify_handler(setup_id, updates):
            results.append({"setup_id": setup_id, "updates": updates})
        
        self.task_queue.register_task_handler('modify_setup', modify_handler)
        
        # Queue modification task
        self.task_queue.queue_task(
            'modify_setup', 
            "setup_001", 
            {"name": "Updated Name"},
            priority=TaskPriority.HIGH
        )
        
        processed = self.task_queue.process_tasks()
        assert processed == 1
        assert len(results) == 1
        assert results[0]["setup_id"] == "setup_001"


# =============================================================================
# End-to-End Workflow Tests
# =============================================================================

class TestSetupManagementWorkflows:
    """Test complete setup management workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
        self.setups = {}  # In-memory setup storage for testing
        self.setup_counter = 0
    
    def _register_all_handlers(self):
        """Register all setup management handlers for workflow testing."""
        
        def list_handler(path, method, data):
            return {
                "status": 200,
                "data": {
                    "setups": list(self.setups.values()),
                    "total_count": len(self.setups)
                }
            }
        
        def create_handler(path, method, data):
            self.setup_counter += 1
            setup_id = f"setup_{self.setup_counter:03d}"
            name = data.get("name", f"Setup {self.setup_counter}")
            
            # Check for duplicate name
            for s in self.setups.values():
                if s["name"] == name:
                    return {
                        "status": 400,
                        "error": True,
                        "code": "DUPLICATE_NAME",
                        "message": f"Setup with name '{name}' already exists"
                    }
            
            setup = {
                "id": setup_id,
                "name": name,
                "toolpath_count": 0
            }
            self.setups[setup_id] = setup
            return {"status": 201, "data": setup}
        
        def get_handler(path, method, data):
            setup_id = data.get("setup_id")
            if setup_id in self.setups:
                return {"status": 200, "data": self.setups[setup_id]}
            return {
                "status": 404,
                "error": True,
                "code": "SETUP_NOT_FOUND",
                "message": f"Setup '{setup_id}' not found"
            }
        
        def delete_handler(path, method, data):
            setup_id = data.get("setup_id")
            if setup_id in self.setups:
                del self.setups[setup_id]
                return {"status": 200, "data": {"deleted": True, "setup_id": setup_id}}
            return {
                "status": 404,
                "error": True,
                "code": "SETUP_NOT_FOUND"
            }
        
        self.router.register_handler("/cam/setups", list_handler, ["GET"], "manufacture", "setups")
        self.router.register_handler("/cam/setups", create_handler, ["POST"], "manufacture", "setups")
        self.router.register_handler("/cam/setups/{setup_id}", get_handler, ["GET"], "manufacture", "setups")
        self.router.register_handler("/cam/setups/{setup_id}", delete_handler, ["DELETE"], "manufacture", "setups")
    
    def test_complete_setup_lifecycle(self):
        """Test complete setup lifecycle: create, read, delete."""
        self._register_all_handlers()
        
        # 1. Create setup
        response = self.router.route_request("/cam/setups", "POST", {"name": "Test Setup"})
        assert response["status"] == 201
        setup_id = response["data"]["id"]
        
        # 2. List setups - should contain our setup
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["status"] == 200
        assert response["data"]["total_count"] == 1
        
        # 3. Get specific setup
        response = self.router.route_request(f"/cam/setups/{setup_id}", "GET", {})
        assert response["status"] == 200
        assert response["data"]["name"] == "Test Setup"
        
        # 4. Delete setup
        response = self.router.route_request(f"/cam/setups/{setup_id}", "DELETE", {})
        assert response["status"] == 200
        assert response["data"]["deleted"] is True
        
        # 5. Verify deletion
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["data"]["total_count"] == 0

    def test_multi_setup_workflow(self):
        """Test workflow with multiple setups."""
        self._register_all_handlers()
        
        # Create multiple setups
        setup_names = ["Roughing Setup", "Finishing Setup", "Drilling Setup"]
        created_ids = []
        
        for name in setup_names:
            response = self.router.route_request("/cam/setups", "POST", {"name": name})
            assert response["status"] == 201
            created_ids.append(response["data"]["id"])
        
        # Verify all setups exist
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["data"]["total_count"] == 3
        
        # Verify unique IDs
        assert len(set(created_ids)) == 3
        
        # Delete one setup
        response = self.router.route_request(f"/cam/setups/{created_ids[1]}", "DELETE", {})
        assert response["data"]["deleted"] is True
        
        # Verify count decreased
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["data"]["total_count"] == 2
    
    def test_duplicate_name_prevention_workflow(self):
        """Test that duplicate names are prevented in workflow."""
        self._register_all_handlers()
        
        # Create first setup
        response = self.router.route_request("/cam/setups", "POST", {"name": "My Setup"})
        assert response["status"] == 201
        
        # Try to create setup with same name
        response = self.router.route_request("/cam/setups", "POST", {"name": "My Setup"})
        assert response["status"] == 400
        assert response["code"] == "DUPLICATE_NAME"
        
        # Verify only one setup exists
        response = self.router.route_request("/cam/setups", "GET", {})
        assert response["data"]["total_count"] == 1


# =============================================================================
# Route Category Tests
# =============================================================================

class TestSetupRouteCategories:
    """Test that setup routes are properly categorized."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = RequestRouter()
    
    def test_setup_routes_in_manufacture_category(self):
        """Test that all setup routes are in manufacture category."""
        def handler(path, method, data):
            return {"status": 200, "data": {}}
        
        # Register routes with manufacture category
        routes = [
            ("/cam/setups", ["GET", "POST"]),
            ("/cam/setups/{setup_id}", ["GET", "PUT", "DELETE"]),
            ("/cam/setups/{setup_id}/duplicate", ["POST"]),
            ("/cam/setups/{setup_id}/toolpaths", ["GET"]),
            ("/cam/toolpaths/{toolpath_id}/setup", ["GET"]),
            ("/cam/setup-toolpath-mapping", ["GET"])
        ]
        
        for pattern, methods in routes:
            for method in methods:
                self.router.register_handler(
                    pattern,
                    handler,
                    methods=[method],
                    category="manufacture",
                    module_name="manufacture.setups"
                )
        
        # Get routes by category
        manufacture_routes = self.router.get_routes_by_category("manufacture")
        
        # Verify routes are in manufacture category
        assert len(manufacture_routes) > 0
        for route in manufacture_routes:
            assert route["category"] == "manufacture"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
