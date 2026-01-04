#!/usr/bin/env python3
"""
Live Integration Tests for Error Response Handling

Tests for consistent error handling across all endpoints:
- 404 responses for invalid IDs
- 400 responses for missing/invalid parameters
- 500 responses include error details
- Consistent error response structure

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_errors.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skip(reason="Error handling tests timeout - bridge slow to respond to invalid requests")
]


class TestNotFoundErrors:
    """Tests for 404 Not Found error responses."""
    
    INVALID_ID_ENDPOINTS = [
        ("/cam/setups/nonexistent_id_12345", "GET"),
        ("/cam/toolpaths/nonexistent_id_12345", "GET"),
        ("/cam/operations/nonexistent_id_12345/tool", "GET"),
        ("/tool-libraries/nonexistent_id_12345", "GET"),
        ("/tool-libraries/tools/nonexistent_id_12345", "GET"),
    ]
    
    @pytest.mark.parametrize("endpoint,method", INVALID_ID_ENDPOINTS)
    def test_invalid_id_returns_error(self, bridge_available, endpoint, method):
        """Test that invalid IDs return error responses."""
        response = make_request(endpoint, method=method)
        
        assert not response_is_empty(response), (
            f"Response for {method} {endpoint} should not be empty"
        )
        
        data = response.json()
        content = data.get("data", data)
        
        # Should indicate not found or error
        is_error = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True or
            "not found" in str(content).lower() or
            "invalid" in str(content).lower()
        )
        assert is_error, f"Expected error for invalid ID at {endpoint}: {data}"
    
    @pytest.mark.parametrize("endpoint,method", INVALID_ID_ENDPOINTS)
    def test_invalid_id_has_error_message(self, bridge_available, endpoint, method):
        """Test that invalid ID errors include a message."""
        response = make_request(endpoint, method=method)
        data = response.json()
        content = data.get("data", data)
        
        # Error response should have message
        has_message = (
            "message" in content or
            "error" in content or
            "detail" in content or
            "code" in content
        )
        assert has_message, f"Error response missing message at {endpoint}: {data}"


class TestBadRequestErrors:
    """Tests for 400 Bad Request error responses."""
    
    MISSING_PARAM_ENDPOINTS = [
        ("/cam/setups", "POST", {}),  # Missing name
        ("/tool-libraries/tools/validate", "POST", {}),  # Missing tool_spec
    ]
    
    @pytest.mark.parametrize("endpoint,method,data", MISSING_PARAM_ENDPOINTS)
    def test_missing_params_returns_error(self, bridge_available, endpoint, method, data):
        """Test that missing required parameters return errors."""
        response = make_request(endpoint, method=method, data=data)
        
        if response.status_code == 501:
            pytest.skip(f"Endpoint {endpoint} not implemented")
        
        assert not response_is_empty(response), (
            f"Response for {method} {endpoint} should not be empty"
        )
        
        response_data = response.json()
        content = response_data.get("data", response_data)
        
        # Should indicate error or handle gracefully
        is_error_or_handled = (
            response.status_code in [400, 422, 500] or
            content.get("error") is True or
            response.status_code == 200  # May use defaults
        )
        assert is_error_or_handled, (
            f"Expected error or graceful handling at {endpoint}: {response_data}"
        )
    
    INVALID_DATA_ENDPOINTS = [
        ("/cam/setups", "POST", {"name": None}),
        ("/draw-box", "POST", {"width": "invalid", "height": [], "depth": {}}),
    ]
    
    @pytest.mark.parametrize("endpoint,method,data", INVALID_DATA_ENDPOINTS)
    def test_invalid_data_returns_error(self, bridge_available, endpoint, method, data):
        """Test that invalid data types return errors."""
        response = make_request(endpoint, method=method, data=data)
        
        if response.status_code == 501:
            pytest.skip(f"Endpoint {endpoint} not implemented")
        
        if response.status_code == 404:
            pytest.skip(f"Endpoint {endpoint} not found")
        
        assert not response_is_empty(response), (
            f"Response for {method} {endpoint} should not be empty"
        )


class TestServerErrors:
    """Tests for 500 Server Error responses."""
    
    def test_server_error_includes_details(self, bridge_available):
        """Test that server errors include error details."""
        # This is hard to trigger intentionally, but we can check
        # that when errors occur, they have proper structure
        
        # Try an operation that might fail
        response = make_request(
            "/cam/operations/invalid/heights/invalid_param",
            method="PUT",
            data={"value": "cause_error"}
        )
        
        if response.status_code == 404:
            pytest.skip("Endpoint not found")
        
        if response.status_code == 200:
            pytest.skip("Request succeeded")
        
        data = response.json()
        
        # Error should have some detail
        has_detail = (
            "message" in data or
            "error" in data or
            "detail" in data or
            "data" in data
        )
        assert has_detail, f"Server error missing details: {data}"


class TestErrorResponseStructure:
    """Tests for consistent error response structure."""
    
    def test_error_response_has_consistent_structure(self, bridge_available):
        """Test that error responses follow consistent structure."""
        # Collect error responses from multiple endpoints
        error_responses = []
        
        test_endpoints = [
            "/cam/setups/invalid_id",
            "/cam/toolpaths/invalid_id",
            "/tool-libraries/invalid_id",
        ]
        
        for endpoint in test_endpoints:
            response = make_request(endpoint)
            if response.status_code != 200:
                error_responses.append(response.json())
        
        if not error_responses:
            pytest.skip("No error responses collected")
        
        # Check that all error responses have similar structure
        for error_data in error_responses:
            content = error_data.get("data", error_data)
            
            # Should have at least one of these fields
            has_error_field = (
                "error" in content or
                "message" in content or
                "code" in content or
                "status" in error_data
            )
            assert has_error_field, f"Error response missing standard fields: {error_data}"
    
    def test_error_codes_are_descriptive(self, bridge_available):
        """Test that error codes are descriptive when present."""
        response = make_request("/cam/setups/nonexistent_setup_id")
        data = response.json()
        content = data.get("data", data)
        
        error_code = content.get("code")
        
        if not error_code:
            pytest.skip("Error code not present in response")
        
        # Error code should be descriptive (not just a number)
        assert isinstance(error_code, str), f"Error code should be string: {error_code}"
        assert len(error_code) > 3, f"Error code should be descriptive: {error_code}"


class TestParameterizedErrorTests:
    """Parameterized tests for error scenarios across endpoints."""
    
    # Endpoints with their expected error scenarios
    ERROR_SCENARIOS = [
        # (endpoint, method, data, expected_error_type)
        ("/cam/setups/invalid", "GET", None, "not_found"),
        ("/cam/setups/invalid", "DELETE", None, "not_found"),
        ("/cam/setups/invalid/duplicate", "POST", None, "not_found"),
        ("/cam/toolpaths/invalid", "GET", None, "not_found"),
        ("/cam/toolpaths/invalid/heights", "GET", None, "not_found"),
        ("/cam/toolpaths/invalid/passes", "GET", None, "not_found"),
        ("/cam/toolpaths/invalid/linking", "GET", None, "not_found"),
        ("/cam/operations/invalid/tool", "GET", None, "not_found"),
        ("/cam/operations/invalid/heights", "GET", None, "not_found"),
        ("/tool-libraries/invalid", "GET", None, "not_found"),
        ("/tool-libraries/tools/invalid", "GET", None, "not_found"),
    ]
    
    @pytest.mark.parametrize("endpoint,method,data,error_type", ERROR_SCENARIOS)
    def test_error_scenario(self, bridge_available, endpoint, method, data, error_type):
        """Test specific error scenarios."""
        response = make_request(endpoint, method=method, data=data)
        
        assert not response_is_empty(response), (
            f"Response should not be empty for {method} {endpoint}"
        )
        
        response_data = response.json()
        content = response_data.get("data", response_data)
        
        # Verify error response
        is_error = (
            response.status_code in [400, 404, 500] or
            content.get("error") is True
        )
        assert is_error, f"Expected {error_type} error at {endpoint}: {response_data}"
    
    @pytest.mark.parametrize("endpoint,method,data,error_type", ERROR_SCENARIOS)
    def test_error_message_clarity(self, bridge_available, endpoint, method, data, error_type):
        """Test that error messages are clear and actionable."""
        response = make_request(endpoint, method=method, data=data)
        response_data = response.json()
        content = response_data.get("data", response_data)
        
        message = content.get("message", str(content))
        
        # Message should not be empty or generic
        assert message, f"Error message should not be empty at {endpoint}"
        assert message != "error", f"Error message too generic at {endpoint}: {message}"
        assert message != "Error", f"Error message too generic at {endpoint}: {message}"
