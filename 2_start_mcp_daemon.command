#!/bin/zsh
cd "$(dirname "$0")"
echo "Starting MCP daemon (this launches its own hotMcpServer gradle process)..."
nohup python3 scripts/mcp_daemon.py > mcp_daemon_stdout.log 2>&1 &
disown
echo "Started with PID $!"
echo "Check mcp_daemon.log for progress. You can close this window."
sleep 3
