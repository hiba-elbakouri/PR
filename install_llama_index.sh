#!/bin/bash

# Granting execute permissions to necessary scripts
chmod +x "$(dirname "$0")/start_project_linux.sh"
chmod +x "$(dirname "$0")/openai_server/start_linux.sh"

# Get the directory where the script is located
PROJECT_ROOT="$(dirname "$0")"

# Navigating to the project root directory
cd "$PROJECT_ROOT"


# Creating and setting up the llama_index environment
echo "Setting up the Llama Index environment..."
cd llama_index
python3 -m venv llama_index_env
source llama_index_env/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Launching the Llama Index application
echo "Launching Llama Index Application..."
cd llama_index
source llama_index_env/bin/activate
python llama_index_app.py &
deactivate
cd ..


echo "Llama Index environment have been set and all the needed packages are installed."

