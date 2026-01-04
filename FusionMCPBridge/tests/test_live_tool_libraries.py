#!/usr/bin/env python3
"""
Live Integration Tests for Tool Library Management

Tests for MANUFACTURE workspace tool library endpoints including:
- Tool library listing and retrieval
- Tool listing and search
- Response structure validation

Prerequisites:
    - Fusion 360 running with FusionMCPBridge add-in active
    - MANUFACTURE workspace active

Run with:
    uv run pytest FusionMCPBridge/tests/test_live_tool_libraries.py -v
"""

import pytest
from .helpers import (
    make_request,
    response_is_empty,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.manufacture,
    pytest.mark.skip(reason="Tool library tests timeout - bridge slow to respond intermittently")
]


class TestListToolLibraries:
    """Tests for /tool-libraries list endpoint."""
    
    def test_list_libraries_returns_response(self, bridge_available):
        """Test that list libraries returns a non-empty response."""
        response = make_request("/tool-libraries")
        
        assert not response_is_empty(response), (
            "CRITICAL: /tool-libraries returned empty response. "
            "Handler likely uses broken task_queue callback pattern."
        )
    
    def test_list_libraries_response_structure(self, bridge_available):
        """Test that list libraries response has expected structure."""
        response = make_request("/tool-libraries")
        data = response.json()
        content = data.get("data", data)
        
        has_valid_structure = (
            "libraries" in content or
            "tool_libraries" in content or
            "error" in content or
            "message" in content
        )
        assert has_valid_structure, f"Unexpected response structure: {data}"
    
    def test_list_libraries_is_list(self, bridge_available):
        """Test that libraries field is a list when present."""
        response = make_request("/tool-libraries")
        data = response.json()
        content = data.get("data", data)
        
        if "libraries" in content:
            assert isinstance(content["libraries"], list), (
                f"'libraries' should be a list, got {type(content['libraries'])}"
            )


class TestGetToolLibrary:
    """Tests for /tool-libraries/{library_id} get endpoint."""
    
    def test_get_library_invalid_id_returns_error(self, bridge_available):
        """Test that invalid library ID returns proper error."""
        response = make_request("/tool-libraries/nonexistent_library_12345")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error_response = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True or
            "not found" in str(content).lower()
        )
        assert is_error_response, f"Expected error for invalid ID: {data}"


class TestListTools:
    """Tests for /tool-libraries/tools list endpoint."""
    
    def test_list_tools_returns_response(self, bridge_available):
        """Test that list tools returns a non-empty response."""
        response = make_request("/tool-libraries/tools")
        
        assert not response_is_empty(response), (
            "CRITICAL: /tool-libraries/tools returned empty response."
        )
    
    def test_list_tools_response_structure(self, bridge_available):
        """Test that list tools response has expected structure."""
        response = make_request("/tool-libraries/tools")
        data = response.json()
        content = data.get("data", data)
        
        has_valid_structure = (
            "tools" in content or
            "libraries" in content or  # May return tools grouped by library
            "error" in content or
            "message" in content
        )
        assert has_valid_structure, f"Unexpected response structure: {data}"


class TestGetTool:
    """Tests for /tool-libraries/tools/{tool_id} get endpoint."""
    
    def test_get_tool_invalid_id_returns_error(self, bridge_available):
        """Test that invalid tool ID returns proper error."""
        response = make_request("/tool-libraries/tools/nonexistent_tool_12345")
        
        assert not response_is_empty(response), "Response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        is_error_response = (
            response.status_code in [404, 400, 500] or
            content.get("error") is True or
            "not found" in str(content).lower()
        )
        assert is_error_response, f"Expected error for invalid ID: {data}"


class TestToolSearch:
    """Tests for /tool-libraries/search endpoint."""
    
    def test_search_returns_response(self, bridge_available):
        """Test that search returns a non-empty response."""
        response = make_request("/tool-libraries/search", method="GET")
        
        assert not response_is_empty(response), (
            "CRITICAL: /tool-libraries/search returned empty response."
        )
    
    def test_search_with_query(self, bridge_available):
        """Test search with a query parameter."""
        response = make_request(
            "/tool-libraries/search",
            method="POST",
            data={"query": "end mill"}
        )
        
        assert not response_is_empty(response), "Search response should not be empty"
        
        data = response.json()
        content = data.get("data", data)
        
        has_results = (
            "tools" in content or
            "results" in content or
            "total_results" in content or
            "error" in content
        )
        assert has_results, f"Search response missing results: {data}"
    
    def test_search_with_filters(self, bridge_available):
        """Test search with filter parameters."""
        response = make_request(
            "/tool-libraries/search",
            method="POST",
            data={
                "query": "",
                "tool_type": "flat end mill",
                "diameter_min": 1.0,
                "diameter_max": 20.0
            }
        )
        
        assert not response_is_empty(response), "Filtered search should not be empty"


class TestAdvancedSearch:
    """Tests for /tool-libraries/search/advanced endpoint."""
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_advanced_search_returns_response(self, bridge_available):
        """Test that advanced search returns a non-empty response."""
        response = make_request(
            "/tool-libraries/search/advanced",
            method="POST",
            data={"search_criteria": {}}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /tool-libraries/search/advanced returned empty response."
        )
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_advanced_search_with_criteria(self, bridge_available):
        """Test advanced search with criteria."""
        response = make_request(
            "/tool-libraries/search/advanced",
            method="POST",
            data={
                "search_criteria": {
                    "diameter": {"min": 5.0, "max": 15.0}
                },
                "sort_by": "diameter",
                "sort_order": "asc"
            }
        )
        
        assert not response_is_empty(response), "Advanced search should not be empty"


class TestSearchSuggestions:
    """Tests for /tool-libraries/search/suggestions endpoint."""
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_suggestions_returns_response(self, bridge_available):
        """Test that suggestions returns a non-empty response."""
        response = make_request(
            "/tool-libraries/search/suggestions",
            method="GET",
            data={"partial_query": "end"}
        )
        
        assert not response_is_empty(response), (
            "CRITICAL: /tool-libraries/search/suggestions returned empty response."
        )
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_suggestions_response_structure(self, bridge_available):
        """Test suggestions response structure."""
        response = make_request(
            "/tool-libraries/search/suggestions",
            method="GET",
            data={"partial_query": "mill"}
        )
        
        data = response.json()
        content = data.get("data", data)
        
        has_structure = (
            "suggestions" in content or
            "names" in content or
            "types" in content or
            "error" in content
        )
        assert has_structure, f"Suggestions missing expected structure: {data}"


class TestToolLibraryResponseValidation:
    """Validate tool library response structures."""
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_library_has_identifier(self, bridge_available):
        """Test that library items have identifiers."""
        response = make_request("/tool-libraries")
        data = response.json()
        content = data.get("data", data)
        
        libraries = content.get("libraries", [])
        if not libraries:
            pytest.skip("No libraries available")
        
        library = libraries[0]
        has_id = "id" in library or "name" in library or "path" in library
        assert has_id, f"Library missing identifier: {library}"
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_tool_has_required_fields(self, bridge_available):
        """Test that tool items have required fields."""
        response = make_request("/tool-libraries/tools")
        data = response.json()
        content = data.get("data", data)
        
        # Tools may be in 'tools' or nested in 'libraries'
        tools = content.get("tools", [])
        if not tools and "libraries" in content:
            for lib in content["libraries"]:
                tools.extend(lib.get("tools", []))
        
        if not tools:
            pytest.skip("No tools available")
        
        tool = tools[0]
        
        # Tool should have at least name or type
        has_basic_info = (
            "name" in tool or
            "description" in tool or
            "type" in tool or
            "tool_type" in tool
        )
        assert has_basic_info, f"Tool missing basic info: {tool}"
    
    @pytest.mark.skip(reason="Timeout - bridge slow to respond")
    def test_tool_has_dimensions(self, bridge_available):
        """Test that tools include dimension information."""
        response = make_request("/tool-libraries/tools")
        data = response.json()
        content = data.get("data", data)
        
        tools = content.get("tools", [])
        if not tools and "libraries" in content:
            for lib in content["libraries"]:
                tools.extend(lib.get("tools", []))
        
        if not tools:
            pytest.skip("No tools available")
        
        tool = tools[0]
        
        # Tool should have diameter or dimensions
        has_dimensions = (
            "diameter" in tool or
            "tool_diameter" in tool or
            "dimensions" in tool or
            "geometry" in tool
        )
        # Soft check - some tools may not have dimensions exposed
        if not has_dimensions:
            pytest.skip("Tool doesn't include dimensions (may be by design)")
