# Fusion 360 MCP Manufacturing Bridge Documentation

This directory contains comprehensive documentation for the Fusion 360 MCP Manufacturing Bridge project, focused on CAM (Computer-Aided Manufacturing) operations and toolpath management.

## What You'll Find Here

This documentation is designed primarily for human readers (developers, users, researchers) with secondary consideration for LLM consumption. Each section serves a specific purpose in understanding and working with the system.

## Documentation Structure

```
docs/
├── architecture/           # System architecture and design
│   ├── MODULAR_ARCHITECTURE.md
│   ├── DATA_FLOW.md
│   ├── MODULE_INTERFACE_REFERENCE.md
│   └── MODULAR_SYSTEM_IMPLEMENTATION.md
│
├── guides/                 # Developer and user guides
│   ├── DEVELOPER_ONBOARDING.md
│   ├── CAM_SETUP_MANAGEMENT.md
│   ├── ERROR_HANDLING.md
│   └── CONFIGURATION_MANAGEMENT.md
│
├── research/               # API research and findings
│   ├── CAM_SETUP_API_RESEARCH.md
│   ├── PART_POSITION_API_RESEARCH.md
│   └── TERMINOLOGY_UPDATE_SUMMARY.md
│
├── testing/                # Testing documentation
│   ├── README.md
│   ├── INTEGRATION_TEST_SUMMARY.md
│   └── BACKWARD_COMPATIBILITY_SUMMARY.md
│
└── README.md               # This navigation guide
```
```

## Quick Navigation

### For New Developers
**Start here:** [Developer Onboarding Guide](guides/DEVELOPER_ONBOARDING.md)

### For System Understanding
- [Modular Architecture](architecture/MODULAR_ARCHITECTURE.md) - High-level system design and component relationships
- [Data Flow](architecture/DATA_FLOW.md) - How requests and responses move through the system
- [Module Interfaces](architecture/MODULE_INTERFACE_REFERENCE.md) - API reference for all system modules

### For Implementation Details
- [System Implementation](architecture/MODULAR_SYSTEM_IMPLEMENTATION.md) - Technical implementation specifics
- [CAM Setup Management](guides/CAM_SETUP_MANAGEMENT.md) - Complete guide to CAM operations
- [Error Handling](guides/ERROR_HANDLING.md) - Error patterns and troubleshooting
- [Configuration Management](guides/CONFIGURATION_MANAGEMENT.md) - System configuration

### For Research and Background
- [CAM Setup API Research](research/CAM_SETUP_API_RESEARCH.md) - Fusion 360 CAM API investigation
- [Part Position API Research](research/PART_POSITION_API_RESEARCH.md) - Part positioning API findings
- [Terminology Updates](research/TERMINOLOGY_UPDATE_SUMMARY.md) - Fusion 360 terminology standards

### For Testing and Quality
- [Testing Overview](testing/README.md) - Test suite documentation and strategy
- [Integration Tests](testing/INTEGRATION_TEST_SUMMARY.md) - Integration test results and analysis
- [Backward Compatibility](testing/BACKWARD_COMPATIBILITY_SUMMARY.md) - Compatibility testing results

## External Resources

- [Fusion 360 API Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- [Fusion 360 CAM API](https://help.autodesk.com/view/fusion360/ENU/?contextId=CAM-WORKSPACE)
- [Project README](../README.md)
