#!/bin/zsh
cd "$(dirname "$0")"
./gradlew --console=plain tasks --all > tasks_list.log 2>&1
echo "done"
