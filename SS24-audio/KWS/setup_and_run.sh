#!/bin/bash

# Define name of virtual environment
VENV_DIR=".venv"

# Check if required Python version is available
if ! python3.9 --version &>/dev/null; then
    echo "Python 3.9 is not installed. Please install Python 3.9 and try again."
    exit 1
fi

# Create virtual environment if not already existing
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3.9 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate


# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install system dependencies for PyAudio, Tflite, and Librosa
echo "Installing system dependencies for PyAudio, Tflite, and Librosa..."

# Install PortAudio (dependency for PyAudio)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install portaudio
fi

# Install the required dependecies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please ensure it exists in same directory as this script."
    exit 1
fi

# If alexa.py not yet executable, change the permissions
if [ ! -x "alexa.py" ]; then
    echo "Making alexa.py executable..."
    chmod +x alexa.py
fi

# Run the alexa.py script
echo "Running alexa.py..."
python alexa.py

# Deactivate the environment after script finished running
deactivate

echo "Script stopped."