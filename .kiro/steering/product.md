# Fusion MCP Manufacturing Integration

## Overview
Fusion MCP Manufacturing Integration bridges AI assistants (Claude Desktop, VS Code Copilot, Kiro CLI) with Autodesk Fusion 360 through the Model Context Protocol (MCP). This enables conversational CAM - creating and manipulating CAM operations, toolpaths, and manufacturing workflows using natural language.

## Purpose
- **Conversational CAM**: Manage CAM operations and toolpaths via natural language commands
- **AI-Driven Manufacturing**: Automate CAM setup, toolpath management, and manufacturing workflows
- **Toolpath Control**: Dynamically inspect and modify manufacturing parameters (heights, passes, linking)
- **Tool Library Management**: Search, access, and manage cutting tools across libraries
- **Accessible Manufacturing**: Lower the barrier for CAM workflow automation in Fusion 360

## Status
Proof-of-concept / Educational project - not production software. Designed as an assistive tool for automating manufacturing workflows in Fusion 360.

## Key Capabilities
- **CAM Operations**: List setups, toolpaths, operations, and cutting tools
- **Parameter Control**: Modify heights, passes, and linking parameters
- **Tool Libraries**: Access and search tool libraries, manage cutting tools
- **Design Integration**: Basic 2D sketching and 3D modeling operations
- **Export Functions**: STEP and STL file export
- **System Utilities**: Parameter management, undo operations, connection testing

## Architecture
Two-component system:
1. **MCP Server** (`Server/`): FastMCP server exposing tools to AI assistants via stdio/SSE transport
2. **Fusion Add-In** (`FusionMCPBridge/`): HTTP server running inside Fusion 360, executing CAD/CAM operations

Communication flow: AI Assistant → MCP Server → HTTP → Fusion Add-In → Fusion 360 API

## Target Users
- CAM engineers looking to automate repetitive workflows
- Developers exploring AI-CAD integration
- Educational users learning conversational manufacturing
- Researchers in AI-assisted design and manufacturing