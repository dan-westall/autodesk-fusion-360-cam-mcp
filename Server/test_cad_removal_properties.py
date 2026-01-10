#!/usr/bin/env python3
"""
Property-Based Tests for CAD Removal

This module contains property-based tests to validate the correctness properties
defined in the CAD Removal design document. These tests ensure that the removal
process maintains system integrity and preserves manufacturing functionality.

**Feature: cad-removal, Property 8: API documentation accuracy**
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, assume
from typing import Dict, List, Set
import json
import re

# Add Server to path for imports
server_path = os.path.join(os.path.dirname(__file__), "Server")
if server_path not in sys.path:
    sys.path.insert(0, server_path)

# Import configuration to test API documentation
try:
    from core.config import get_endpoints, get_categories
except ImportError:
    # Fallback for when CAD is removed
    def get_endpoints(category=None):
        return {}
    def get_categories():
        return []


class TestCadRemovalProperties:
    """Property-based tests for CAD removal correctness properties."""

    def test_property_8_api_documentation_accuracy(self):
        """
        **Feature: cad-removal, Property 8: API documentation accuracy**
        **Validates: Requirements 7.3**
        
        Property: For any generated API documentation, the documentation should 
        only include CAM tools and endpoints with no references to removed design capabilities.
        
        This test verifies that after CAD removal, the API configuration and 
        documentation contains only manufacturing-related endpoints and no 
        design/CAD references.
        """
        # Get all endpoint categories
        categories = get_categories()
        
        # Get all endpoints across all categories
        all_endpoints = get_endpoints()  # Get flattened endpoints
        
        # Define CAD/Design-related terms that should NOT appear
        cad_terms = {
            'cad', 'design', 'draw', 'sketch', 'geometry', 'modeling',
            'extrude', 'revolve', 'loft', 'sweep', 'boolean',
            'fillet', 'shell', 'hole', 'thread', 'pattern',
            'cylinder', 'box', 'sphere', 'circle', 'line', 'arc', 'spline',
            'ellipse', 'rectangle', 'text'
        }
        
        # Define CAM/Manufacturing terms that SHOULD appear
        cam_terms = {
            'cam', 'toolpath', 'setup', 'tool', 'manufacture', 'operation',
            'library', 'height', 'pass', 'linking'
        }
        
        # Test 1: No CAD category should exist
        assert 'cad' not in categories, f"CAD category still exists in configuration: {categories}"
        
        # Test 2: CAM category should exist
        assert 'cam' in categories, f"CAM category missing from configuration: {categories}"
        
        # Test 3: No CAD-related endpoints should exist
        cad_endpoints_found = []
        for endpoint_name, endpoint_url in all_endpoints.items():
            endpoint_lower = endpoint_name.lower()
            url_lower = endpoint_url.lower()
            
            # Check if endpoint name or URL contains CAD terms
            for cad_term in cad_terms:
                if cad_term in endpoint_lower or cad_term in url_lower:
                    cad_endpoints_found.append({
                        'name': endpoint_name,
                        'url': endpoint_url,
                        'term': cad_term
                    })
        
        assert len(cad_endpoints_found) == 0, (
            f"Found CAD-related endpoints that should be removed: {cad_endpoints_found}"
        )
        
        # Test 4: CAM endpoints should exist
        cam_endpoints = get_endpoints('cam')
        assert len(cam_endpoints) > 0, "No CAM endpoints found - manufacturing functionality missing"
        
        # Test 5: CAM endpoints should contain manufacturing terms
        cam_terms_found = set()
        for endpoint_name, endpoint_url in cam_endpoints.items():
            endpoint_lower = endpoint_name.lower()
            url_lower = endpoint_url.lower()
            
            for cam_term in cam_terms:
                if cam_term in endpoint_lower or cam_term in url_lower:
                    cam_terms_found.add(cam_term)
        
        # Should find at least some CAM terms in the endpoints
        assert len(cam_terms_found) > 0, (
            f"No CAM terms found in CAM endpoints. Expected terms: {cam_terms}, "
            f"CAM endpoints: {list(cam_endpoints.keys())}"
        )
        
        # Test 6: Utility endpoints should be preserved
        utility_endpoints = get_endpoints('utility')
        assert len(utility_endpoints) > 0, "No utility endpoints found - system functionality missing"
        
        print(f"✅ Property 8 validated:")
        print(f"   - Categories: {categories}")
        print(f"   - CAM endpoints: {len(cam_endpoints)}")
        print(f"   - Utility endpoints: {len(utility_endpoints)}")
        print(f"   - CAM terms found: {cam_terms_found}")
        print(f"   - No CAD endpoints found: ✅")

    @given(st.text(min_size=1, max_size=50))
    def test_property_8_endpoint_name_validation(self, endpoint_name: str):
        """
        Property-based test using generated endpoint names to verify
        that no CAD-related terms would be accepted in endpoint names.
        
        **Feature: cad-removal, Property 8: API documentation accuracy**
        **Validates: Requirements 7.3**
        """
        # Define CAD terms that should not appear in any endpoint names
        forbidden_cad_terms = {
            'draw_cylinder', 'draw_box', 'draw_sphere', 'draw_circle',
            'draw_line', 'draw_arc', 'extrude', 'revolve', 'loft', 'sweep',
            'fillet', 'shell', 'hole', 'thread', 'pattern', 'boolean'
        }
        
        # Normalize the endpoint name for comparison
        normalized_name = endpoint_name.lower().strip()
        
        # Skip empty or whitespace-only names
        assume(len(normalized_name) > 0)
        
        # Check if the generated name contains forbidden CAD terms
        contains_cad_term = any(
            cad_term in normalized_name 
            for cad_term in forbidden_cad_terms
        )
        
        if contains_cad_term:
            # If it contains a CAD term, it should NOT be in our current endpoints
            all_endpoints = get_endpoints()
            assert normalized_name not in [name.lower() for name in all_endpoints.keys()], (
                f"Endpoint '{endpoint_name}' contains CAD terms and should not exist after removal"
            )

    def test_property_8_configuration_structure_validation(self):
        """
        Test that the configuration structure itself reflects manufacturing-only focus.
        
        **Feature: cad-removal, Property 8: API documentation accuracy**
        **Validates: Requirements 7.3**
        """
        categories = get_categories()
        
        # Expected categories after CAD removal
        expected_categories = {'cam', 'utility', 'debug'}
        forbidden_categories = {'cad', 'design'}
        
        # Test category structure
        for forbidden_cat in forbidden_categories:
            assert forbidden_cat not in categories, (
                f"Forbidden category '{forbidden_cat}' still exists: {categories}"
            )
        
        # Test that we have the essential manufacturing categories
        assert 'cam' in categories, f"Essential CAM category missing: {categories}"
        
        # Test that each allowed category has endpoints
        for category in categories:
            if category in expected_categories:
                endpoints = get_endpoints(category)
                assert len(endpoints) > 0, (
                    f"Category '{category}' exists but has no endpoints: {endpoints}"
                )

    def test_property_8_endpoint_url_validation(self):
        """
        Test that endpoint URLs don't contain CAD-related paths.
        
        **Feature: cad-removal, Property 8: API documentation accuracy**
        **Validates: Requirements 7.3**
        """
        all_endpoints = get_endpoints()
        
        # CAD-related URL patterns that should not exist
        forbidden_url_patterns = [
            r'/draw[_-]',  # /draw_cylinder, /draw-box, etc.
            r'/extrude',
            r'/revolve',
            r'/loft',
            r'/sweep',
            r'/boolean',
            r'/fillet',
            r'/shell',
            r'/hole',
            r'/thread',
            r'/pattern',
            r'/geometry',
            r'/sketch'
        ]
        
        forbidden_urls_found = []
        
        for endpoint_name, endpoint_url in all_endpoints.items():
            for pattern in forbidden_url_patterns:
                if re.search(pattern, endpoint_url, re.IGNORECASE):
                    forbidden_urls_found.append({
                        'endpoint': endpoint_name,
                        'url': endpoint_url,
                        'pattern': pattern
                    })
        
        assert len(forbidden_urls_found) == 0, (
            f"Found URLs with forbidden CAD patterns: {forbidden_urls_found}"
        )


if __name__ == "__main__":
    # Run the property tests
    test_instance = TestCadRemovalProperties()
    
    print("Running CAD Removal Property Tests...")
    print("=" * 50)
    
    try:
        # Run Property 8 tests
        test_instance.test_property_8_api_documentation_accuracy()
        test_instance.test_property_8_configuration_structure_validation()
        test_instance.test_property_8_endpoint_url_validation()
        
        print("\n✅ All Property 8 tests passed!")
        print("API documentation accuracy validated.")
        
    except Exception as e:
        print(f"\n❌ Property test failed: {e}")
        sys.exit(1)