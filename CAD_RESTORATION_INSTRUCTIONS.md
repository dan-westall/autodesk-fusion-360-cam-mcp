# CAD Functionality Restoration Instructions

**Created:** January 10, 2026  
**Purpose:** Complete instructions for restoring CAD functionality if needed  
**Requirements:** 8.3, 8.4, 8.5  

## Overview

This document provides step-by-step instructions for restoring CAD functionality to the Fusion 360 MCP Server after it has been removed. The restoration process uses version control tags and the comprehensive component inventory to ensure complete functionality recovery.

## Pre-Restoration System State

### Current System State (Before Removal)
- **Git Tag:** `pre-cad-removal-backup`
- **Branch:** `feat/manufacturing-setups`
- **Commit:** e7c9a24 (CAD component inventory added)
- **CAD Status:** Fully functional
- **CAM Status:** Fully functional

### System Components Present
- ✅ All CAD tools in `Server/tools/cad/`
- ✅ All design handlers in `FusionMCPBridge/handlers/design/`
- ✅ All design-related HTTP endpoints operational
- ✅ All CAD-related test files present
- ✅ Complete configuration with CAD endpoints

## Restoration Methods

### Method 1: Complete Restoration (Recommended)

This method restores the entire system to the pre-removal state.

```bash
# 1. Check current status
git status
git log --oneline -5

# 2. Create backup of current work (if needed)
git stash push -m "Work in progress before CAD restoration"

# 3. Checkout the backup tag
git checkout pre-cad-removal-backup

# 4. Create new restoration branch
git checkout -b restore-cad-functionality

# 5. Verify CAD functionality is present
ls -la Server/tools/cad/
ls -la FusionMCPBridge/handlers/design/

# 6. Test system functionality
cd Server
python3 MCP_Server.py --server_type sse &
curl http://localhost:5001/test_connection
```

### Method 2: Selective Restoration

This method allows restoring specific CAD components while keeping other changes.

```bash
# 1. Identify specific files to restore from inventory
# See CAD_REMOVAL_INVENTORY.md for complete file list

# 2. Restore specific directories
git checkout pre-cad-removal-backup -- Server/tools/cad/
git checkout pre-cad-removal-backup -- FusionMCPBridge/handlers/design/

# 3. Restore configuration files
git checkout pre-cad-removal-backup -- Server/core/config.py
git checkout pre-cad-removal-backup -- Server/config.py

# 4. Restore test files
git checkout pre-cad-removal-backup -- Server/tests/test_cad_*.py
git checkout pre-cad-removal-backup -- FusionMCPBridge/tests/test_live_design.py

# 5. Restore import statements
git checkout pre-cad-removal-backup -- Server/tools/__init__.py
git checkout pre-cad-removal-backup -- FusionMCPBridge/handlers/__init__.py
```

### Method 3: Cherry-Pick Restoration

This method allows applying specific commits while maintaining current branch.

```bash
# 1. Find commits that added CAD functionality
git log --oneline --grep="CAD" --grep="design" --grep="geometry"

# 2. Cherry-pick specific commits
git cherry-pick <commit-hash>

# 3. Resolve any conflicts
git status
# Edit conflicted files
git add .
git cherry-pick --continue
```

## Component Restoration Checklist

### Server Components
- [ ] `Server/tools/cad/__init__.py`
- [ ] `Server/tools/cad/geometry.py`
- [ ] `Server/tools/cad/sketching.py`
- [ ] `Server/tools/cad/modeling.py`
- [ ] `Server/tools/cad/features.py`
- [ ] `Server/tools/__init__.py` (CAD imports)
- [ ] `Server/core/config.py` (CAD endpoints)

### Fusion Add-In Components
- [ ] `FusionMCPBridge/handlers/design/__init__.py`
- [ ] `FusionMCPBridge/handlers/design/geometry.py`
- [ ] `FusionMCPBridge/handlers/design/geometry_impl.py`
- [ ] `FusionMCPBridge/handlers/design/geometry_impl2.py`
- [ ] `FusionMCPBridge/handlers/design/sketching.py`
- [ ] `FusionMCPBridge/handlers/design/modeling.py`
- [ ] `FusionMCPBridge/handlers/design/features.py`
- [ ] `FusionMCPBridge/handlers/design/utilities.py`
- [ ] `FusionMCPBridge/handlers/__init__.py` (design imports)

### Test Components
- [ ] `Server/tests/test_cad_server_loading.py`
- [ ] `Server/tests/test_cad_integration.py`
- [ ] `Server/tests/test_cad_modernization.py`
- [ ] `Server/tests/test_cad_response_interception.py`
- [ ] `Server/tests/test_cad_end_to_end_compatibility.py`
- [ ] `FusionMCPBridge/tests/test_live_design.py`
- [ ] `FusionMCPBridge/tests/conftest.py` (design fixtures)

## Post-Restoration Validation

### System Startup Validation
```bash
# 1. Test MCP Server startup
cd Server
python3 MCP_Server.py --server_type sse

# 2. Test Fusion Add-In connectivity
curl http://localhost:5001/test_connection

# 3. Test CAD endpoints
curl -X POST http://localhost:5001/draw_cylinder \
  -H "Content-Type: application/json" \
  -d '{"radius": 5, "height": 10, "x": 0, "y": 0, "z": 0, "plane": "XY"}'
```

### Functionality Validation
```bash
# 1. Run CAD-specific tests
cd Server
python -m pytest tests/test_cad_*.py -v

# 2. Run design workspace tests
cd FusionMCPBridge
python -m pytest tests/test_live_design.py -v --integration

# 3. Run full test suite
python -m pytest tests/ -v
```

### Configuration Validation
```bash
# 1. Verify CAD endpoints in configuration
python3 -c "
from Server.core.config import get_endpoints
cad_endpoints = get_endpoints('cad')
print(f'CAD endpoints restored: {len(cad_endpoints)}')
for name, url in cad_endpoints.items():
    print(f'  {name}: {url}')
"

# 2. Verify import statements
python3 -c "
from Server.tools.cad import geometry, sketching, modeling, features
print('All CAD modules imported successfully')
"
```

## Troubleshooting Common Issues

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'tools.cad'`
**Solution:**
```bash
# Ensure all CAD modules are restored
git checkout pre-cad-removal-backup -- Server/tools/cad/
git checkout pre-cad-removal-backup -- Server/tools/__init__.py
```

### Missing Endpoints
**Problem:** CAD endpoints return 404 errors
**Solution:**
```bash
# Restore design handlers and configuration
git checkout pre-cad-removal-backup -- FusionMCPBridge/handlers/design/
git checkout pre-cad-removal-backup -- FusionMCPBridge/handlers/__init__.py
git checkout pre-cad-removal-backup -- Server/core/config.py
```

### Test Failures
**Problem:** CAD tests fail after restoration
**Solution:**
```bash
# Restore all test files and fixtures
git checkout pre-cad-removal-backup -- Server/tests/test_cad_*.py
git checkout pre-cad-removal-backup -- FusionMCPBridge/tests/test_live_design.py
git checkout pre-cad-removal-backup -- FusionMCPBridge/tests/conftest.py
```

### Configuration Conflicts
**Problem:** Configuration merge conflicts
**Solution:**
```bash
# Manual merge of configuration files
git checkout pre-cad-removal-backup -- Server/core/config.py
# Edit file to merge CAD endpoints with current configuration
# Test configuration validity
python3 -c "from Server.core.config import validate_configuration; print(validate_configuration())"
```

## Verification Commands

### Quick Verification Script
```bash
#!/bin/bash
# CAD Restoration Verification Script

echo "=== CAD Restoration Verification ==="

# Check CAD modules exist
echo "Checking CAD modules..."
if [ -d "Server/tools/cad" ]; then
    echo "✅ CAD tools directory exists"
    ls -la Server/tools/cad/
else
    echo "❌ CAD tools directory missing"
fi

# Check design handlers exist
echo "Checking design handlers..."
if [ -d "FusionMCPBridge/handlers/design" ]; then
    echo "✅ Design handlers directory exists"
    ls -la FusionMCPBridge/handlers/design/
else
    echo "❌ Design handlers directory missing"
fi

# Test imports
echo "Testing imports..."
python3 -c "
try:
    from Server.tools.cad import geometry, sketching, modeling, features
    print('✅ All CAD modules import successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Test configuration
echo "Testing configuration..."
python3 -c "
try:
    from Server.core.config import get_endpoints
    cad_endpoints = get_endpoints('cad')
    print(f'✅ CAD configuration loaded: {len(cad_endpoints)} endpoints')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

echo "=== Verification Complete ==="
```

## Emergency Recovery

### If Restoration Fails
1. **Reset to known good state:**
   ```bash
   git reset --hard pre-cad-removal-backup
   git clean -fd
   ```

2. **Start fresh restoration:**
   ```bash
   git checkout -b emergency-cad-restore
   # Follow Method 1: Complete Restoration
   ```

3. **Contact support with:**
   - Current git status output
   - Error messages encountered
   - Steps attempted before failure

## Maintenance Notes

### Keeping Restoration Instructions Updated
- Update this document when CAD functionality changes
- Update backup tags when significant CAD improvements are made
- Test restoration process periodically
- Document any new restoration scenarios encountered

### Future Backup Strategy
- Create backup tags before major CAD modifications
- Maintain component inventory for new CAD features
- Document restoration procedures for new components
- Test restoration process in development environment

## Summary

This restoration guide provides multiple methods for recovering CAD functionality:

1. **Complete restoration** using git tags (fastest, most reliable)
2. **Selective restoration** for specific components
3. **Cherry-pick restoration** for granular control

The process is designed to be safe and reversible, with comprehensive validation steps to ensure full functionality recovery.

**Key Files for Restoration:**
- `CAD_REMOVAL_INVENTORY.md` - Complete component list
- `pre-cad-removal-backup` - Git tag with full CAD functionality
- This document - Step-by-step restoration instructions

**Success Criteria:**
- All CAD tools accessible via MCP server
- All design endpoints responding correctly
- All CAD tests passing
- System starts without import errors
- CAM functionality remains unaffected