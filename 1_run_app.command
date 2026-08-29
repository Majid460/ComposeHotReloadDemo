#!/bin/zsh
cd "$(dirname "$0")"
echo "Project dir: $(pwd)"
java -version 2>&1 | head -3
echo "Launching ./gradlew run in background, logging to app_run.log ..."
nohup ./gradlew --console=plain run > app_run.log 2>&1 &
disown
echo "Started with PID $!"
echo "You can close this window; the app will keep running."
sleep 3
