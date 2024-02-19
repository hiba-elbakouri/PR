#!/bin/bash

# Granting execute permissions to necessary scripts
chmod +x "$(dirname "$0")/start_project_linux.sh"
chmod +x "$(dirname "$0")/openai_server/start_linux.sh"

# Get the directory where the script is located
PROJECT_ROOT="$(dirname "$0")"

# Navigating to the project root directory
cd "$PROJECT_ROOT"

# Installing openai extension requirements and Starting the OpenAI server
echo "Setting openai server... "
pip install -r openai_server/extensions/openai/requirements.txt
./openai_server/start_linux.sh &


echo "Openai server is well set"

