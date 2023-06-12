# NAO Script for python2 and python3 
This project enables interaction with the NAO humanoid robot using Python 2 and Python 3. The script uses Docker to launch the Python 2 container and a Flask API to enable communication between Python 2 and Python 3.

## Requirements:
To run the script, you need the following prerequisites:

- Docker installed on your system.
- Visual Studio Code (VS Code) with the Docker and Remote - Containers extensions installed.
- Access to the humanoid robot NAO (WIFI).
- A laptop or computer with a working microphone.
- Internet access for communication with the ChatGPT API.

## Installation:
- Open the repository in VS Code. (nao_script)
- Install the Docker and Remote Containers extensions.
- Restart VS Code and open the repository in a remote container. You will be prompted to select the Python 2 container.
- In VS Code, open the "python2" folder.
- Create a virtual environment (venv) with the following command: **python -m venv venv**
- Activate the virtual environment: **For Windows: .\venv\Scripts\activate** and **for macOS/Linux: source venv/bin/activate**
- Install the required Python packages and dependencies with the following command: **pip install -r requirements.txt**
- In the python2/main.py file, adjust the BASE_API variable to set the URL of the Flask API in Python 3. (second IP from your Terminal Debug)

## Usage:
- Make sure the NAO robot is set up and connected correctly.
- Start the Python 3 part of the app by running the Flask API with the python3 python3/main.py command.
- Launch the Docker container for Python 2 by opening the Docker extension repository in VS Code and selecting the Python 2 container.
- In VS Code, open the "python2" folder in the nao_script folder.
- Activate the virtual environment (venv) with the command source venv/bin/activate.
- Start the Python 3 script with the python main.py command.
- Type your question or message loudly and clearly into your laptop's microphone.
- The Python 2 script sends the text to the Flask API in Python 3 and receives a response.
- The NAO robot plays back the answer using its built-in voice output system.
