#!/bin/zsh
cd "$(dirname "$0")"
echo "Killing previous MainKt run (plain 'run' task, not hot-reload-enabled)..."
pkill -f "MainKt" 2>/dev/null
sleep 2
echo "Launching ./gradlew hotRunDesktop in background..."
nohup ./gradlew --console=plain hotRunDesktop > app_run.log 2>&1 &
disown
echo "Started with PID $!"
sleep 3
