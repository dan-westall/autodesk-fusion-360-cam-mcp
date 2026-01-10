# Fusion MCP Manufacturing Integration


https://github.com/user-attachments/assets/46c8140e-377d-4618-a304-03861cb3d7d9


## 🎯 About

Fusion MCP Manufacturing Integration bridges AI assistants with Autodesk Fusion 360's MANUFACTURE workspace through the Model Context Protocol (MCP). This enables:

- 🏭 **Conversational CAM** - Manage CAM operations using natural language
- 🤖 **AI-Driven Manufacturing** - Automate CAM setup and toolpath management
- 🔧 **Toolpath Control** - Dynamically inspect and modify manufacturing parameters
- 🎓 **Accessible Manufacturing** - Lower the barrier for CAM workflow automation

> **Note:** This is designed as an assistive tool and educational project, not a replacement for professional CAM workflows.
> Projects like this can assist people with automating manufacturing workflows in Fusion 360.

> **Goal:** Enable conversational CAM and AI-driven manufacturing automation in Fusion 360.

---


# Setup

**I highly recommend to do everything inside Visual Studio Code or another IDE**

---

## Requirements
| Requirement | Link |
|------------|------|
| Python 3.10+ | https://python.org |
| uv (Python package manager) | https://docs.astral.sh/uv/getting-started/installation/ |
| Autodesk Fusion 360 | https://autodesk.com/fusion360 |
| Claude Desktop or Kiro CLI | https://claude.ai/download |
| VS Code (optional) | https://code.visualstudio.com |

---

## Clone Repository
```bash
git clone https://github.com/JustusBraitinger/FusionMCP
cd FusionMCP
```

> **Important:** Do **NOT** start the Add-In yet.

---

## Install Dependencies

Use `uv sync` to install all dependencies and set up the virtual environment automatically:

```bash
uv sync
```

This will:
- Create a virtual environment if one doesn't exist
- Install all required dependencies (fastmcp, uvicorn, requests)
- Lock versions in `uv.lock` for reproducible builds

---

## Installing the MCP Add-In for Fusion 360

### For Development (Recommended)
Creates a symbolic link for live editing without reinstalling:
```bash
uv run install-fusion-plugin --dev
```

### For Distribution
Copies files to the add-in directory:
```bash
uv run install-fusion-plugin
```

> **Development Tip:** Use the `--dev` flag during development. Any code changes will be immediately available in Fusion after restarting the add-in.

---

## Connect to Kiro CLI

For Kiro CLI, create or edit your agent configuration file:

```json
{
  "mcpServers": {
    "FusionMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/FusionMCP",
        "run",
        "python3",
        "Server/MCP_Server.py",
        "--server_type",
        "stdio"
      ]
    }
  },
  "allowedTools": ["@FusionMCP/*"]
}
```

---

## Connect to Claude Desktop

In Claude Desktop go to:
**Settings → Developer → Edit Config**

Add this block (change the path for your system):

**macOS:**
```json
{
  "mcpServers": {
    "FusionMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/FusionMCP",
        "run",
        "python3",
        "Server/MCP_Server.py",
        "--server_type",
        "stdio"
      ]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "FusionMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\yourname\\path\\to\\FusionMCP",
        "run",
        "python3",
        "Server/MCP_Server.py",
        "--server_type",
        "stdio"
      ]
    }
  }
}
```
> **Note:** Windows paths require double backslashes `\\`

Claude will automatically start and stop the MCP server when needed.

### Alternative: Using fastmcp install

You can also use the fastmcp CLI to auto-configure Claude:

```bash
uv run fastmcp install Server/MCP_Server.py --name Fusion
```

### Using the MCP in Claude
1. Restart Claude if needed (force close if not visible)
2. Click **➕ Add** (bottom left of chat)
3. Select **Add from Fusion**
4. Choose a Fusion MCP prompt

---

## Use MCP in VS Code (Copilot)

VS Code uses HTTP transport, so you need to start the server manually with the `--sse` flag:

```bash
uv run start-mcp-server --sse
```

Then create or edit the file:

**Windows:** `%APPDATA%\Code\User\globalStorage\github.copilot-chat\mcp.json`
**macOS:** `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/mcp.json`

Paste:
```json
{
  "servers": {
    "FusionMCP": {
      "url": "http://127.0.0.1:8000/sse",
      "type": "http"
    }
  },
  "inputs": []
}
```

### Alternative Setup in VS Code
1. Press **CTRL + SHIFT + P** (or **CMD + SHIFT + P** on macOS)
2. Search **MCP** → choose **Add MCP**
3. Select **HTTP**
4. Enter: `http://127.0.0.1:8000/sse`
5. Name your MCP **`FusionMCP`**

---

## Try It Out 😄

1. Activate the Fusion Add-In inside Fusion 360
2. Start the MCP server (if using VS Code or manual testing):
   ```bash
   cd Server && python3 MCP_Server.py --server_type sse
   ```

### In VS Code
Type `/mcp.FusionMCP` to see a list of predetermined prompts.

### In Claude
Just open Claude and ask for the FusionMCP tools.

---

## 🐛 Development & Debugging

### Remote Add-in Control (Development)

For development workflow, you can install a debugger add-in that allows remote control of the main FusionMCPBridge add-in:

```bash
# Manually copy the debugger add-in folder to Fusion's add-ins directory
# macOS: ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/
# Windows: %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\

cp -r FusionMCPBridgeDebugger ~/Library/Application\ Support/Autodesk/Autodesk\ Fusion\ 360/API/AddIns/
```

**Available endpoints:**
```bash
# Restart the main add-in (most common for development)
curl http://localhost:5002/addon/restart

# Stop the main add-in
curl http://localhost:5002/addon/stop

# Start the main add-in
curl http://localhost:5002/addon/start

# Check add-in status
curl http://localhost:5002/addon/status
```

**Usage:** After making code changes, run `curl http://localhost:5002/addon/restart` to restart the main add-in without manually using the Scripts & Add-ins dialog. Check Fusion 360's Text Commands window for restart confirmation messages.

### Development Workflow

1. **Make code changes** to files in `FusionMCPBridge/`
2. **Restart the add-in** remotely:
   ```bash
   curl http://localhost:5002/addon/restart
   ```
3. **Test your changes** with MCP endpoints:
   ```bash
   # Test basic connectivity
   curl http://localhost:5001/test-connection
   
   # Test tool libraries
   curl http://localhost:5001/tool-libraries
   
   # Test specific library tools
   curl http://localhost:5001/tool-libraries/library_0/tools
   ```
4. **Check logs** in Fusion 360's Text Commands window for debug output
5. **Repeat** as needed during development

### When to Restart

**Always restart after:**
- Method signature changes
- New module imports
- Class definition changes
- Adding new endpoints

**No restart needed for:**
- Simple code changes within existing methods
- Parameter value changes
- Logic updates in existing functions

---

## 🧪 Testing

### Unit Tests (No Fusion Required)
Run unit tests that don't require Fusion 360:

```bash
# Server tests
uv run pytest Server/tests/ -v

# Bridge tests (excluding live tests)
uv run pytest FusionMCPBridge/tests/ -v -m "not live"
```

### Live Integration Tests (Fusion Required)
These tests make real HTTP requests to the running add-in and catch issues that unit tests can't detect (like the task_queue callback pattern bug).

**Prerequisites:**
1. Fusion 360 running
2. FusionMCPBridge add-in active
3. A CAM document open (for CAM-specific tests)

```bash
# Run all live tests
uv run pytest FusionMCPBridge/tests/test_live_integration.py -v

# Run only smoke tests (quick validation)
uv run pytest FusionMCPBridge/tests/test_live_integration.py::TestSmokeTests -v

# Run empty response detection tests (catches task_queue bugs)
uv run pytest FusionMCPBridge/tests/test_live_integration.py::TestEmptyResponseDetection -v
```

**What Live Tests Catch:**
- Empty `{}` responses from broken task_queue patterns
- HTTP endpoint routing issues
- Response structure validation
- Real API behavior vs mocked behavior

**Development Workflow with Live Tests:**
1. Make code changes
2. Restart add-in: `curl http://localhost:5002/addon/restart`
3. Run smoke tests: `uv run pytest FusionMCPBridge/tests/test_live_integration.py::TestSmokeTests -v`
4. If smoke tests pass, run full live test suite

---

## 🛠️ Available Tools

---

### 🏭 CAM & Manufacturing Tools

| Tool | Description |
| :--- | :--- |
| **List CAM Setups** | Lists all CAM setups in the current document with details. |
| **Get Setup Details** | Retrieves detailed information about a specific CAM setup. |
| **List Toolpaths** | Lists all toolpaths in the current document or specific setup. |
| **Get Toolpath Details** | Gets detailed information about a specific toolpath. |
| **List Tools** | Lists all cutting tools used in CAM operations. |
| **Get Tool Details** | Retrieves detailed information about a specific cutting tool. |
| **List Tool Libraries** | Lists all available tool libraries in Fusion 360. |
| **Get Library Tools** | Lists all tools in a specific tool library. |
| **Find Tool by ID** | Finds a specific tool by its ID in the tool libraries. |

---

### 📏 Analysis & Control

| Tool | Description |
| :--- | :--- |
| **Count** | Counts the total number of all **model parameters**. |
| **List parameters** | Lists all defined **model parameters** in detail. |
| **Change parameter** | Changes the value of an existing named parameter in the model. |
| **Test connection** | Tests the communication link to the Fusion 360 server. |
| **Undo** | **Undoes** the last operation in Fusion 360. |
| **Delete all** | **Deletes all objects** in the current Fusion 360 session (`destroy`). |

---

### 💾 Export

| Tool | Description |
| :--- | :--- |
| **Export STEP** | **Exports** the model as a **STEP** file. |
| **Export STL** | **Exports** the model as an **STL** file. |


## Architecture

### Server Module (Server/MCP_Server.py)
- **ONLY** MCP server implementation in this project
- Defines MCP server, tools, and prompts
- Handles HTTP calls to Fusion add-in
- Includes CAM functionality and tool library management

### Fusion Add-In (FusionMCPBridge/)
- Runs inside Fusion 360
- HTTP server on port 5001 that receives requests from MCP server
- Because the Fusion API is not thread-safe, this uses:
  - Custom event handler
  - Task queue
- Modules:
  - `FusionMCPBridge.py` - HTTP routing and request handling
  - `handlers/manufacture/` - MANUFACTURE workspace (CAM) functionality
  - `tool_library.py` - Tool library management using Fusion 360 CAM API

---
### Why This Architecture?

The Fusion 360 API is **not thread-safe** and requires all operations to run on the main UI thread. Our solution:

1. **Event-Driven Design** - Use Fusion's CustomEvent system
2. **Task Queue** - Queue operations for sequential execution
3. **Async Bridge** - HTTP server handles async MCP requests

   
## Security Considerations 🔒
- Local execution → safe by default
- Currently HTTP (OK locally, insecure on networks)
- Validate tool inputs to avoid prompt injection
- Real security depends on tool implementation

---

### This is NOT

- ❌ A production-ready tool
- ❌ A replacement for professional CAM software
- ❌ Suitable for critical manufacturing work
- ❌ Officially supported by Autodesk

### This IS

- ✅ A proof-of-concept
- ✅ An educational project
- ✅ A demonstration of MCP capabilities
- ✅ A tool for rapid prototyping and CAM workflow automation

---

**This is a proof-of-concept, not production software.**


# If you want it to build yourself   
- Use Websocket instead of plain HTTP
- Find a way to tell the llm the retarded faceindecies and body names
- 



## Contact
justus@braitinger.org
