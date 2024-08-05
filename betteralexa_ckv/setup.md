# Project Setup Documentation


This document provides a detailed guide on how to set up and run the project in a virtual environment. Using a virtual environment is a good practice as it isolates the project and its dependencies from other projects.

## Prerequisites

Ensure you have the following installed on your machine:

- Python 3.9
- pip (Python package installer)
- PyAudio (depends on PortAudio)
- Tflite (will be auto-installed later on)
- Librosa (might need to be compiled manually)
- Microsoft Visual C++ 14.0

## Installation

### Step 1: Clone the repository

First, clone the repository from GitHub. Make sure you have `git` installed on your machine.

Open your terminal (on MacOS and Linux) or Command Prompt (on Windows) and run the following command:
```
git clone -b tmpSS24ga-kws https://github.com/Programmierpraktikum-MVA/BetterAlexa.git
```

### Step 2: Navigate to the project directory

After cloning the repository, navigate to the specific project directory:

On MacOS and Linux:
```
cd BetterAlexa/SS24-audio/client_kws_vad
```

On Windows:
```
cd BetterAlexa\SS24-audio\client_kws_vad
```

### Step 2: Create a virtual environment

Create a virtual environment using the `venv` module. This will create a new directory named `myenv` in your project directory. When the virtual environment is activated, Python will use packages in this isolated environment.
```
python3.9 -m venv myenv
```

### Step 4: Activate the virtual environment

Before you can start installing or using packages in the virtual environment, you'll need to activate it. Activating a virtual environment will put the virtual environment-specific `python` and `pip` executables into your shell’s `PATH`.

On MacOS and Linux:
```
source myenv/bin/activate
```

On Windows:
```
.\myenv\Scripts\activate
```

### Step 5: Install dependencies

First, upgrade pip to the latest available version if not already installed:
```
pip install --upgrade pip
```

Install the required Python packages using the requirements file:
```
pip install -r requirements.txt
```

## Running the Project

### Step 6: Launch the application

To run the project, execute the `main.py` script:
```
python main.py
```

After running the script, it will install additional dependencies and download necessary models. This process may take some time, so please be patient. Afterwards you will be prompted to choose a desired input device.

This script starts the application. You can stop the application by pressing `Ctrl+C`.

## Deactivating the Virtual Environment

When you are done working, you can deactivate the virtual environment by running:
```
deactivate
```

This command will revert your shell’s `PATH` to what it was before you activated the virtual environment and return you to your normal shell prompt.