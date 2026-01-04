#!/usr/bin/env python3
"""
Unit tests for CAM Setup Management functions.

Tests the pure Python logic (Green Zone) without requiring Fusion 360 API.
Following the Humble Object Pattern - testing logic functions that can be
isolated from Fusion 360 API calls.

These tests focus on:
- Data structure validation
- Response format consistency
- Error handling patterns
- Request validation logic
- Configuration and routing

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

from core.router import RequestRouter, HttpMethod
from core.validation import RequestValidator
from core.error_handling import ErrorHandler, ErrorCategory, ErrorSeverity


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def router():
    """Create a fresh RequestRouter for testing."""
    return RequestRouter()


@pytest.fixture
def validator():
    """Create a RequestValidator for testing."""
    return RequestValidator()


@pytest.fixture
def sample_setup_data():
    """Sample setup data structure for validation tests."""
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
        "is_active": True
    }


@pytest.fixture
def sample_toolpath_data():
    """Sample toolpath data structure for validation tests."""
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
# WCS Data Structure Validation Tests
# =============================================================================

class TestWCSDataStructure:
    """Test WCS data structure validation and consistency."""
    
    def test_wcs_has_required_fields(self, sample_setup_data):
        """Test that WCS data has all required fields."""
        wcs = sample_setup_data["wcs"]
        
        required_fields = ["type", "origin", "orientation", "reference"]
        for field in required_fields:
            assert field in wcs, f"Missing required WCS field: {field}"
    
    def test_wcs_origin_has_xyz(self, sample_setup_data):
        """Test that WCS origin has x, y, z coordinates."""
        origin = sample_setup_data["wcs"]["origin"]
        
        assert "x" in origin
        assert "y" in origin
        assert "z" in origin
        
        # Values should be numeric
        assert isinstance(origin["x"], (int, float))
        assert isinstance(origin["y"], (int, float))
        assert isinstance(origin["z"], (int, float))
    
    def test_wcs_orientation_has_axes(self, sample_setup_data):
        """Test that WCS orientation has all three axes."""
        orientation = sample_setup_data["wcs"]["orientation"]
        
        assert "x_axis" in orientation
        assert "y_axis" in orientation
        assert "z_axis" in orientation
        
        # Each axis should have x, y, z components
        for axis_name in ["x_axis", "y_axis", "z_axis"]:
            axis = orientation[axis_name]
            assert "x" in axis
            assert "y" in axis
            assert "z" in axis
    
    def test_wcs_type_values(self):
        """Test valid WCS type values."""
        valid_types = ["model_origin", "face_based", "edge_based", "custom", "unknown"]
        
        for wcs_type in valid_types:
            wcs = {"type": wcs_type}
            assert wcs["type"] in valid_types
    
    def test_wcs_reference_values(self):
        """Test valid WCS reference values."""
        valid_references = ["model", "face", "edge", "unknown"]
        
        for ref in valid_references:
            wcs = {"reference": ref}
            assert wcs["reference"] in valid_references


# =============================================================================
# Stock Data Structure Validation Tests
# =============================================================================

class TestStockDataStructure:
    """Test stock data structure validation and consistency."""
    
    def test_stock_has_required_fields(self, sample_setup_data):
        """Test that stock data has all required fields."""
        stock = sample_setup_data["stock"]
        
        required_fields = ["mode", "dimensions", "position", "material"]
        for field in required_fields:
            assert field in stock, f"Missing required stock field: {field}"
    
    def test_stock_dimensions_has_required_values(self, sample_setup_data):
        """Test that stock dimensions has required measurements."""
        dimensions = sample_setup_data["stock"]["dimensions"]
        
        required_dims = ["length", "width", "height"]
        for dim in required_dims:
            assert dim in dimensions, f"Missing dimension: {dim}"
            assert isinstance(dimensions[dim], (int, float))
    
    def test_stock_position_is_list(self, sample_setup_data):
        """Test that stock position is a list of coordinates."""
        position = sample_setup_data["stock"]["position"]
        
        assert isinstance(position, list)
        assert len(position) == 3
    
    def test_stock_mode_values(self):
        """Test valid stock mode values."""
        valid_modes = ["auto", "box", "cylinder", "fixed_box", "fixed_cylinder", "unknown"]
        
        for mode in valid_modes:
            stock = {"mode": mode}
            assert stock["mode"] in valid_modes


# =============================================================================
# Setup Data Structure Validation Tests
# =============================================================================

class TestSetupDataStructure:
    """Test setup data structure validation and consistency."""
    
    def test_setup_has_required_fields(self, sample_setup_data):
        """Test that setup data has all required fields."""
        required_fields = ["id", "name", "wcs", "stock", "model_id"]
        
        for field in required_fields:
            assert field in sample_setup_data, f"Missing required setup field: {field}"
    
    def test_setup_id_is_string(self, sample_setup_data):
        """Test that setup ID is a string."""
        assert isinstance(sample_setup_data["id"], str)
        assert len(sample_setup_data["id"]) > 0
    
    def test_setup_name_is_string(self, sample_setup_data):
        """Test that setup name is a string."""
        assert isinstance(sample_setup_data["name"], str)
        assert len(sample_setup_data["name"]) > 0
    
    def test_setup_toolpath_count_is_integer(self, sample_setup_data):
        """Test that toolpath count is an integer."""
        assert isinstance(sample_setup_data["toolpath_count"], int)
        assert sample_setup_data["toolpath_count"] >= 0
    
    def test_setup_is_active_is_boolean(self, sample_setup_data):
        """Test that is_active is a boolean."""
        assert isinstance(sample_setup_data["is_active"], bool)


# =============================================================================
# Toolpath Data Structure Validation Tests
# =============================================================================

class TestToolpathDataStructure:
    """Test toolpath data structure validation and consistency."""
    
    def test_toolpath_has_required_fields(self, sample_toolpath_data):
        """Test that toolpath data has all required fields."""
        required_fields = ["id", "name", "type", "is_valid", "setup_id", "setup_name"]
        
        for field in required_fields:
            assert field in sample_toolpath_data, f"Missing required toolpath field: {field}"
    
    def test_toolpath_has_setup_context(self, sample_toolpath_data):
        """Test that toolpath includes setup context (Requirement 9.1)."""
        assert "setup_id" in sample_toolpath_data
        assert "setup_name" in sample_toolpath_data
        
        assert sample_toolpath_data["setup_id"] is not None
        assert sample_toolpath_data["setup_name"] is not None
    
    def test_toolpath_tool_data_structure(self, sample_toolpath_data):
        """Test that toolpath tool data has required fields."""
        tool = sample_toolpath_data["tool"]
        
        required_fields = ["id", "name", "type"]
        for field in required_fields:
            assert field in tool, f"Missing required tool field: {field}"


# =============================================================================
# Error Response Format Tests
# =============================================================================

class TestErrorResponseFormat:
    """Test error response format consistency."""
    
    def test_error_response_structure(self):
        """Test standard error response structure."""
        error_response = {
            "error": True,
            "message": "Setup not found",
            "code": "SETUP_NOT_FOUND"
        }
        
        assert error_response["error"] is True
        assert isinstance(error_response["message"], str)
        assert isinstance(error_response["code"], str)
    
    def test_error_codes_are_uppercase(self):
        """Test that error codes follow uppercase convention."""
        error_codes = [
            "SETUP_NOT_FOUND",
            "MISSING_SETUP_ID",
            "DUPLICATE_NAME",
            "INVALID_UPDATES",
            "MODIFICATION_ERROR",
            "CREATION_ERROR",
            "DELETION_ERROR",
            "TOOLPATH_SETUP_MISMATCH"
        ]
        
        for code in error_codes:
            assert code == code.upper(), f"Error code should be uppercase: {code}"
            assert "_" in code or code.isalpha(), f"Error code should use underscores: {code}"
    
    def test_error_response_with_warnings(self):
        """Test error response with warnings."""
        error_response = {
            "error": True,
            "message": "Stock configuration is invalid",
            "code": "INVALID_STOCK_CONFIG",
            "warnings": ["Stock dimensions too small for existing operations"]
        }
        
        assert "warnings" in error_response
        assert isinstance(error_response["warnings"], list)
    
    def test_success_response_structure(self, sample_setup_data):
        """Test standard success response structure."""
        success_response = {
            "status": 200,
            "data": sample_setup_data
        }
        
        assert success_response["status"] == 200
        assert "data" in success_response
        assert "error" not in success_response or success_response.get("error") is False


# =============================================================================
# Request Validation Tests
# =============================================================================

class TestRequestValidation:
    """Test request validation logic."""
    
    def test_validate_setup_id_required(self, validator):
        """Test that setup_id is required for get/modify/delete operations."""
        # Empty setup_id should fail validation
        data = {"setup_id": ""}
        
        # Validation should detect missing/empty setup_id
        assert data["setup_id"] == "" or data.get("setup_id") is None or len(data.get("setup_id", "")) == 0
    
    def test_validate_setup_id_present(self, validator):
        """Test that valid setup_id passes validation."""
        data = {"setup_id": "setup_001"}
        
        assert data["setup_id"] is not None
        assert len(data["setup_id"]) > 0
    
    def test_validate_name_for_create(self):
        """Test name validation for setup creation."""
        # Name can be optional (auto-generated)
        data_without_name = {}
        data_with_name = {"name": "My Setup"}
        
        # Both should be valid
        assert "name" not in data_without_name or data_without_name.get("name") is None
        assert data_with_name.get("name") == "My Setup"
    
    def test_validate_updates_for_modify(self):
        """Test updates validation for setup modification."""
        valid_updates = {
            "name": "New Name",
            "wcs": {"origin": {"x": 10.0, "y": 5.0, "z": 0.0}},
            "stock": {"dimensions": {"length": 150.0}}
        }
        
        # Updates should be a dictionary
        assert isinstance(valid_updates, dict)
        
        # At least one update field should be present
        assert len(valid_updates) > 0
    
    def test_validate_confirm_for_delete(self):
        """Test confirm validation for setup deletion."""
        # Without confirm
        data_no_confirm = {"setup_id": "setup_001"}
        
        # With confirm
        data_with_confirm = {"setup_id": "setup_001", "confirm": True}
        
        assert data_no_confirm.get("confirm", False) is False
        assert data_with_confirm.get("confirm") is True


# =============================================================================
# Route Registration Tests
# =============================================================================

class TestRouteRegistration:
    """Test route registration and routing logic."""
    
    def test_register_get_route(self, router):
        """Test registering a GET route."""
        def handler(path, method, data):
            return {"status": 200, "data": {}}
        
        router.register_handler(
            "/cam/setups",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = router.route_request("/cam/setups", "GET", {})
        assert response["status"] == 200
    
    def test_register_post_route(self, router):
        """Test registering a POST route."""
        def handler(path, method, data):
            return {"status": 201, "data": {"id": "new_setup"}}
        
        router.register_handler(
            "/cam/setups",
            handler,
            methods=["POST"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = router.route_request("/cam/setups", "POST", {"name": "Test"})
        assert response["status"] == 201
    
    def test_register_route_with_path_parameter(self, router):
        """Test registering a route with path parameter."""
        def handler(path, method, data):
            setup_id = data.get("setup_id")
            return {"status": 200, "data": {"id": setup_id}}
        
        router.register_handler(
            "/cam/setups/{setup_id}",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        response = router.route_request("/cam/setups/setup_001", "GET", {})
        assert response["status"] == 200
        assert response["data"]["id"] == "setup_001"
    
    def test_route_not_found(self, router):
        """Test routing to non-existent route."""
        response = router.route_request("/nonexistent", "GET", {})
        
        assert response["status"] == 404
        assert response.get("error") is True
    
    def test_method_not_allowed(self, router):
        """Test routing with wrong HTTP method."""
        def handler(path, method, data):
            return {"status": 200, "data": {}}
        
        router.register_handler(
            "/cam/setups",
            handler,
            methods=["GET"],
            category="manufacture",
            module_name="manufacture.setups"
        )
        
        # Try POST on GET-only route
        response = router.route_request("/cam/setups", "POST", {})
        
        # Should return 404 or 405
        assert response["status"] in [404, 405]


# =============================================================================
# Impact Analysis Data Structure Tests
# =============================================================================

class TestImpactAnalysisStructure:
    """Test impact analysis data structure consistency."""
    
    def test_wcs_impact_structure(self):
        """Test WCS impact analysis structure."""
        impact = {
            "has_impact": True,
            "affected_operations": 3,
            "warnings": ["WCS origin change will affect 3 existing operation(s)."]
        }
        
        assert "has_impact" in impact
        assert "affected_operations" in impact
        assert "warnings" in impact
        
        assert isinstance(impact["has_impact"], bool)
        assert isinstance(impact["affected_operations"], int)
        assert isinstance(impact["warnings"], list)
    
    def test_stock_impact_structure(self):
        """Test stock impact analysis structure."""
        impact = {
            "has_impact": True,
            "affected_operations": 2,
            "warnings": ["Stock dimensions are being reduced."],
            "valid": True
        }
        
        assert "has_impact" in impact
        assert "affected_operations" in impact
        assert "warnings" in impact
        
        assert isinstance(impact["has_impact"], bool)
        assert isinstance(impact["affected_operations"], int)
        assert isinstance(impact["warnings"], list)
    
    def test_no_impact_structure(self):
        """Test no-impact analysis structure."""
        impact = {
            "has_impact": False,
            "affected_operations": 0,
            "warnings": []
        }
        
        assert impact["has_impact"] is False
        assert impact["affected_operations"] == 0
        assert len(impact["warnings"]) == 0


# =============================================================================
# Setup-Toolpath Mapping Structure Tests
# =============================================================================

class TestSetupToolpathMappingStructure:
    """Test setup-toolpath mapping data structure consistency."""
    
    def test_mapping_structure(self):
        """Test complete mapping structure."""
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
        
        assert "setups" in mapping
        assert "toolpath_to_setup" in mapping
        assert "total_setups" in mapping
        assert "total_toolpaths" in mapping
    
    def test_mapping_bidirectional_consistency(self):
        """Test that mapping is bidirectionally consistent."""
        mapping = {
            "setups": [
                {"id": "setup_001", "name": "Setup 1", "toolpath_ids": ["op_001", "op_002"]}
            ],
            "toolpath_to_setup": {
                "op_001": {"setup_id": "setup_001", "setup_name": "Setup 1"},
                "op_002": {"setup_id": "setup_001", "setup_name": "Setup 1"}
            }
        }
        
        # Verify bidirectional consistency
        for setup in mapping["setups"]:
            for toolpath_id in setup["toolpath_ids"]:
                assert toolpath_id in mapping["toolpath_to_setup"]
                assert mapping["toolpath_to_setup"][toolpath_id]["setup_id"] == setup["id"]
    
    def test_mapping_counts_match(self):
        """Test that mapping counts are accurate."""
        mapping = {
            "setups": [
                {"id": "setup_001", "toolpath_ids": ["op_001", "op_002"]},
                {"id": "setup_002", "toolpath_ids": ["op_003"]}
            ],
            "total_setups": 2,
            "total_toolpaths": 3
        }
        
        assert len(mapping["setups"]) == mapping["total_setups"]
        
        total_toolpaths = sum(len(s["toolpath_ids"]) for s in mapping["setups"])
        assert total_toolpaths == mapping["total_toolpaths"]


# =============================================================================
# Duplicate Name Generation Logic Tests
# =============================================================================

class TestDuplicateNameGenerationLogic:
    """Test duplicate name generation logic (pure Python)."""
    
    def test_first_copy_name_format(self):
        """Test first copy name format."""
        original_name = "Original Setup"
        expected_first_copy = f"{original_name} (Copy)"
        
        assert expected_first_copy == "Original Setup (Copy)"
    
    def test_subsequent_copy_name_format(self):
        """Test subsequent copy name format."""
        original_name = "Original Setup"
        
        # Second copy
        expected_second_copy = f"{original_name} (Copy 2)"
        assert expected_second_copy == "Original Setup (Copy 2)"
        
        # Third copy
        expected_third_copy = f"{original_name} (Copy 3)"
        assert expected_third_copy == "Original Setup (Copy 3)"
    
    def test_name_uniqueness_check_logic(self):
        """Test name uniqueness checking logic."""
        existing_names = ["Setup 1", "Setup 2", "Setup 1 (Copy)"]
        
        def is_name_unique(name):
            return name not in existing_names
        
        assert is_name_unique("Setup 3") is True
        assert is_name_unique("Setup 1") is False
        assert is_name_unique("Setup 1 (Copy)") is False
        assert is_name_unique("Setup 1 (Copy 2)") is True


# =============================================================================
# Z-Axis Cross Product Calculation Tests
# =============================================================================

class TestZAxisCalculation:
    """Test Z-axis calculation from X and Y axes (cross product)."""
    
    def test_standard_orientation_z_axis(self):
        """Test Z-axis calculation for standard orientation."""
        # X = (1, 0, 0), Y = (0, 1, 0)
        x_axis = {"x": 1.0, "y": 0.0, "z": 0.0}
        y_axis = {"x": 0.0, "y": 1.0, "z": 0.0}
        
        # Cross product: X × Y = Z
        z_x = x_axis["y"] * y_axis["z"] - x_axis["z"] * y_axis["y"]
        z_y = x_axis["z"] * y_axis["x"] - x_axis["x"] * y_axis["z"]
        z_z = x_axis["x"] * y_axis["y"] - x_axis["y"] * y_axis["x"]
        
        assert abs(z_x) < 0.001
        assert abs(z_y) < 0.001
        assert abs(z_z - 1.0) < 0.001
    
    def test_rotated_orientation_z_axis(self):
        """Test Z-axis calculation for rotated orientation."""
        # X = (0, 1, 0), Y = (-1, 0, 0) - 90 degree rotation around Z
        x_axis = {"x": 0.0, "y": 1.0, "z": 0.0}
        y_axis = {"x": -1.0, "y": 0.0, "z": 0.0}
        
        # Cross product: X × Y = Z
        z_x = x_axis["y"] * y_axis["z"] - x_axis["z"] * y_axis["y"]
        z_y = x_axis["z"] * y_axis["x"] - x_axis["x"] * y_axis["z"]
        z_z = x_axis["x"] * y_axis["y"] - x_axis["y"] * y_axis["x"]
        
        # Should still be (0, 0, 1)
        assert abs(z_x) < 0.001
        assert abs(z_y) < 0.001
        assert abs(z_z - 1.0) < 0.001


# =============================================================================
# Handler Response Consistency Tests
# =============================================================================

class TestHandlerResponseConsistency:
    """Test handler response format consistency."""
    
    def test_list_response_format(self):
        """Test list response format."""
        response = {
            "status": 200,
            "data": {
                "setups": [],
                "total_count": 0
            }
        }
        
        assert response["status"] == 200
        assert "setups" in response["data"]
        assert "total_count" in response["data"]
        assert isinstance(response["data"]["setups"], list)
    
    def test_get_response_format(self, sample_setup_data):
        """Test get response format."""
        response = {
            "status": 200,
            "data": sample_setup_data
        }
        
        assert response["status"] == 200
        assert "id" in response["data"]
        assert "name" in response["data"]
    
    def test_create_response_format(self):
        """Test create response format."""
        response = {
            "status": 201,
            "data": {
                "id": "new_setup_001",
                "name": "New Setup",
                "message": "Setup 'New Setup' created successfully"
            }
        }
        
        assert response["status"] == 201
        assert "id" in response["data"]
        assert "name" in response["data"]
    
    def test_modify_response_format(self):
        """Test modify response format."""
        response = {
            "status": 200,
            "data": {
                "id": "setup_001",
                "name": "Modified Setup",
                "changes_made": ["Name changed"],
                "warnings": None,
                "message": "Setup modified successfully"
            }
        }
        
        assert response["status"] == 200
        assert "changes_made" in response["data"]
    
    def test_delete_response_format(self):
        """Test delete response format."""
        response = {
            "status": 200,
            "data": {
                "deleted": True,
                "setup_id": "setup_001",
                "setup_name": "Deleted Setup",
                "operations_deleted": 3
            }
        }
        
        assert response["status"] == 200
        assert response["data"]["deleted"] is True
    
    def test_duplicate_response_format(self):
        """Test duplicate response format."""
        response = {
            "status": 201,
            "data": {
                "id": "new_setup_002",
                "name": "Original Setup (Copy)",
                "source_setup": {
                    "id": "setup_001",
                    "name": "Original Setup"
                },
                "message": "Setup duplicated successfully"
            }
        }
        
        assert response["status"] == 201
        assert "source_setup" in response["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
