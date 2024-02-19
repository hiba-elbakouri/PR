#!/bin/bash

# Granting execute permissions to necessary scripts
chmod +x "$(dirname "$0")/openai_server/start_linux.sh"

# Get the directory where the script is located
PROJECT_ROOT="$(dirname "$0")"

# Navigating to the project root directory
cd "$PROJECT_ROOT"

# Installing openai extension requirements and Starting the OpenAI server
echo "Starting OpenAI Server..."
./openai_server/start_linux.sh &


# Launching the user interface
echo "Launching User Interface..."
cd user_interface
source user_interface_env/bin/activate
panel serve ui_app.py --autoreload --show &
deactivate
cd ..

# Launching the Llama Index application
echo "Launching Llama Index Application..."
cd llama_index
source llama_index_env/bin/activate
python llama_index_app.py &
deactivate
cd ..

echo "All components have been started."

