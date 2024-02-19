#!/bin/bash

# Granting execute permissions to necessary scripts
chmod +x "$(dirname "$0")/start_project_linux.sh"
chmod +x "$(dirname "$0")/openai_server/start_linux.sh"

# Get the directory where the script is located
PROJECT_ROOT="$(dirname "$0")"

# Navigating to the project root directory
cd "$PROJECT_ROOT"



# Creating and setting up the user_interface environment
echo "Setting up the user interface environment..."
cd user_interface
python3 -m venv user_interface_env
source user_interface_env/bin/activate
pip install -r requirements.txt
deactivate
cd ..


echo "The user interface environment have been set and all the needed packages are installed."

