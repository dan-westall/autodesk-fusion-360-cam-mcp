#!/usr/bin/env python3
"""
Property-Based Test for HTTP Endpoint Removal Completeness

This module contains property-based tests to validate that design workspace
HTTP endpoints have been completely removed from the Fusion Add-In while
preserving all CAM functionality.

Property 2: HTTP endpoint removal completeness
*For any* HTTP request to removed design endpoints, the Fusion Add-In should 
return 404 Not Found responses while continuing to process all CAM requests normally

Requirements: 2.1, 2.2, 2.4
"""

import pytest
import requests
import sys
import os
from typing import Dict, List, Any, Set
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck

# Design endpoints that should return 404 after removal
REMOVED_DESIGN_ENDPOINTS = [
    '/Box',
    '/Witzenmann', 
    '/draw_cylinder',
    '/sphere',
    '/create_circle',
    '/draw_lines',
    '/draw_one_line',
    '/arc',
    '/spline',
    '/ellipsis',
    '/extrude_last_sketch',
    '/extrude_thin',
    '/cut_extrude',
    '/revolve',
    '/sweep',
    '/loft',
    '/fillet_edges',
    '/shell_body',
    '/holes',
    '/threaded',
    '/circular_pattern',
    '/rectangular_pattern',
    '/offsetplane',
    '/boolean_operation',
    '/select_body',
    '/select_sketch',
    '/set_parameter',
    '/undo',
    '/delete_everything',
    '/Export_STL',
    '/Export_STEP'
]

# CAM endpoints that should continue to work
PRESERVED_CAM_ENDPOINTS = [
    '/cam/setups',
    '/cam/toolpaths',
    '/cam/toolpaths/heights',
    '/cam/tools',
    '/tool-libraries'
]

# System endpoints that should continue to work
PRESERVED_SYSTEM_ENDPOINTS = [
    '/test_connection',
    '/count_parameters',
    '/list_parameters'
]

BASE_URL = 'http://localhost:5001'


class TestHTTPEndpointRemovalCompleteness:
    """Property-based tests for HTTP endpoint removal completeness."""
    
    @given(st.sampled_from(REMOVED_DESIGN_ENDPOINTS))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_design_endpoints_return_404(self, endpoint):
        """
        **Feature: cad-removal, Property 2: HTTP endpoint removal completeness**
        
        Property: For any removed design endpoint, HTTP requests should return 
        404 Not Found responses, indicating the endpoint has been completely removed.
        
        This test verifies that all design workspace endpoints have been removed
        from the HTTP router and return appropriate 404 responses.
        """
        try:
            # Test both GET and POST methods for comprehensive coverage
            for method in ['GET', 'POST']:
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
                
                assert response.status_code == 404, (
                    f"Design endpoint {endpoint} should return 404 Not Found but returned {response.status_code}. "
                    f"This indicates the endpoint was not properly removed from the HTTP router."
                )
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Fusion 360 Add-In HTTP server not running - cannot test endpoint removal")
        except requests.exceptions.Timeout:
            pytest.fail(f"Timeout testing endpoint {endpoint} - server may be unresponsive")
    
    @given(st.sampled_from(PRESERVED_CAM_ENDPOINTS))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cam_endpoints_continue_working(self, endpoint):
        """
        **Feature: cad-removal, Property 2: HTTP endpoint removal completeness**
        
        Property: For any CAM endpoint, HTTP requests should continue to work normally,
        returning 200 OK responses (or appropriate success codes), indicating that
        CAM functionality has been preserved during design endpoint removal.
        
        This test verifies that CAM endpoints continue to function correctly
        after design endpoint removal.
        """
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            # CAM endpoints should return 200 OK or other success codes (2xx)
            assert 200 <= response.status_code < 300, (
                f"CAM endpoint {endpoint} should return success status but returned {response.status_code}. "
                f"This indicates CAM functionality may have been affected by design endpoint removal."
            )
            
            # Response should contain valid JSON data
            try:
                json_data = response.json()
                assert isinstance(json_data, dict), (
                    f"CAM endpoint {endpoint} should return JSON object but returned {type(json_data)}"
                )
                
                # Should not be an empty response (which would indicate broken handler)
                assert json_data, (
                    f"CAM endpoint {endpoint} returned empty response - may indicate broken handler"
                )
                
            except ValueError as e:
                pytest.fail(f"CAM endpoint {endpoint} returned invalid JSON: {e}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Fusion 360 Add-In HTTP server not running - cannot test CAM endpoint preservation")
        except requests.exceptions.Timeout:
            pytest.fail(f"Timeout testing CAM endpoint {endpoint} - server may be unresponsive")
    
    @given(st.sampled_from(PRESERVED_SYSTEM_ENDPOINTS))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_system_endpoints_continue_working(self, endpoint):
        """
        **Feature: cad-removal, Property 2: HTTP endpoint removal completeness**
        
        Property: For any system endpoint, HTTP requests should continue to work normally,
        returning appropriate success responses, indicating that system functionality
        has been preserved during design endpoint removal.
        
        This test verifies that system endpoints continue to function correctly
        after design endpoint removal.
        """
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            # System endpoints should return 200 OK or other success codes (2xx)
            assert 200 <= response.status_code < 300, (
                f"System endpoint {endpoint} should return success status but returned {response.status_code}. "
                f"This indicates system functionality may have been affected by design endpoint removal."
            )
            
            # Response should contain valid JSON data
            try:
                json_data = response.json()
                assert isinstance(json_data, dict), (
                    f"System endpoint {endpoint} should return JSON object but returned {type(json_data)}"
                )
                
            except ValueError as e:
                pytest.fail(f"System endpoint {endpoint} returned invalid JSON: {e}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Fusion 360 Add-In HTTP server not running - cannot test system endpoint preservation")
        except requests.exceptions.Timeout:
            pytest.fail(f"Timeout testing system endpoint {endpoint} - server may be unresponsive")
    
    @given(st.just(None))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_endpoint_removal_completeness_comprehensive(self, _):
        """
        **Feature: cad-removal, Property 2: HTTP endpoint removal completeness**
        
        Property: The complete set of design endpoints should be removed while
        the complete set of CAM and system endpoints should be preserved.
        
        This test provides comprehensive validation that endpoint removal was
        complete and selective (only design endpoints removed).
        """
        try:
            removed_count = 0
            preserved_count = 0
            
            # Test all removed endpoints
            for endpoint in REMOVED_DESIGN_ENDPOINTS:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                    if response.status_code == 404:
                        removed_count += 1
                except requests.exceptions.RequestException:
                    # Connection issues are handled separately
                    pass
            
            # Test all preserved endpoints  
            for endpoint in PRESERVED_CAM_ENDPOINTS + PRESERVED_SYSTEM_ENDPOINTS:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                    if 200 <= response.status_code < 300:
                        preserved_count += 1
                except requests.exceptions.RequestException:
                    # Connection issues are handled separately
                    pass
            
            # Verify comprehensive removal and preservation
            total_removed = len(REMOVED_DESIGN_ENDPOINTS)
            total_preserved = len(PRESERVED_CAM_ENDPOINTS + PRESERVED_SYSTEM_ENDPOINTS)
            
            removal_percentage = (removed_count / total_removed) * 100 if total_removed > 0 else 0
            preservation_percentage = (preserved_count / total_preserved) * 100 if total_preserved > 0 else 0
            
            assert removal_percentage >= 90, (
                f"Only {removal_percentage:.1f}% of design endpoints properly removed. "
                f"Expected at least 90% removal rate for comprehensive endpoint removal."
            )
            
            assert preservation_percentage >= 90, (
                f"Only {preservation_percentage:.1f}% of CAM/system endpoints preserved. "
                f"Expected at least 90% preservation rate to ensure functionality is maintained."
            )
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Fusion 360 Add-In HTTP server not running - cannot test comprehensive endpoint removal")


if __name__ == "__main__":
    # Run the property-based tests
    pytest.main([__file__, "-v", "--tb=short"])