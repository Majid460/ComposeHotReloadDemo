# Compose Hot Reload Demo (MCP-Enabled)

A Compose Multiplatform (Desktop) demonstration project featuring a sophisticated **Hot Reload** mechanism and **Model Context Protocol (MCP)** integration. This project is designed to be fully interactive and "AI-Agent-Ready," allowing for real-time UI manipulation and inspection via standardized tools.

## 🚀 Key Features

*   **Compose Multiplatform for Desktop:** Built using the latest Jetpack Compose for Desktop (JVM).
*   **Live Hot Reload:** Apply code changes (UI updates, logic fixes) instantly without restarting the application process.
*   **AI-Driven via MCP:** Includes a built-in MCP server that exposes tools for:
    *   📸 Taking screenshots.
    *   🌳 Inspecting the Semantic/Accessibility tree.
    *   🖱️ Simulating clicks, typing, and scrolling.
    *   🔄 Triggering hot reloads remotely.
    *   📊 Monitoring app logs and status.
*   **Sample Screens:**
    *   **Counter:** A simple state management example.
    *   **Task List:** A functional Todo-style list demonstrating list state and input handling.

## 🛠️ Project Structure

*   `composeApp/`: The main Kotlin source code for the Desktop application.
    *   `src/desktopMain/kotlin/`: Contains `Main.kt`, `CounterScreen.kt`, and `TaskListScreen.kt`.
*   `scripts/`: Automation and daemon scripts.
    *   `mcp_daemon.py`: A Python-based MCP client that bridges the Gradle MCP server to the environment.
*   `article-assets/`: Directory where screenshots taken by the MCP tools are saved.
*   `mcp_queue/`: A communication bridge for the daemon to process tool calls and responses.

## 🏁 Getting Started

### Prerequisites

*   **JDK 17 or later**
*   **Python 3.x** (for the MCP daemon)

### 1. Launch the Application

Run the application using the provided script or Gradle:

```bash
./1_run_app.command
# OR
./gradlew run
```

This will start the Compose Desktop window.

### 2. Start the MCP Daemon

To enable AI agent interaction, start the MCP bridge:

```bash
./2_start_mcp_daemon.command
# OR
python3 scripts/mcp_daemon.py
```

The daemon will launch the `hotMcpServer` Gradle task and prepare the tool environment.

## 🤖 MCP Toolset

The project exposes a rich set of tools to any connected MCP client (like an AI agent):

| Tool | Description |
| :--- | :--- |
| `status` | Check if the app is connected and get reload state. |
| `reload` | Recompile and apply source changes to the live app. |
| `take_screenshot` | Capture the current UI (saved to `article-assets/`). |
| `get_semantic_tree` | Get a JSON representation of the UI hierarchy. |
| `click` / `type_text` | Interact with UI elements by ID. |
| `get_logs` | Retrieve recent application runtime logs. |

## 📝 Helper Scripts

*   `1_run_app.command`: Starts the app in the background.
*   `2_start_mcp_daemon.command`: Starts the MCP bridge.
*   `3_list_tasks.command`: Utility to list available Gradle tasks.
*   `4_relaunch_hotrun.command`: Relaunches the app if needed.

## 💡 How it Works

The project uses a custom Gradle task `hotMcpServerDesktop` which embeds a server into the application process. This server communicates over `stdio` using the Model Context Protocol. The Python daemon acts as a relay, allowing external agents to send JSON-RPC commands to inspect or modify the running app.
