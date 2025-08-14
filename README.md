# EGO - Your Personal AI Assistant

EGO is a personal AI assistant with a visually appealing interface and a modular skill system. It listens for the wake word "EGO" and can perform a variety of tasks based on your voice commands.

## Features

*   **Voice Activated:** Listens for the "EGO" wake word.
*   **GUI:** A modern, animated interface with a dynamic orb that indicates the assistant's status (idle, listening, speaking, processing).
*   **Modular Skill System:** Easily extendable with new skills.
*   **Natural Language Understanding:** Uses a local LLM (GPT-2) to understand your commands.
*   **Offline Speech Recognition:** Can use the Vosk engine for offline speech recognition.
*   **Command Learning:** Can learn new commands and associate them with actions.

## What it can do

EGO can perform a variety of tasks, including:

*   **Telling Jokes:** "EGO, tell me a joke."
*   **Getting News:** "EGO, what's the latest news?"
*   **Opening Websites:** "EGO, open YouTube."
*   **Getting System Information:** "EGO, what's the CPU usage?"
*   **Fetching Weather:** "EGO, what's the weather like in London?"
*   **Searching Wikipedia:** "EGO, who is Albert Einstein?"
*   **Taking Screenshots:** "EGO, take a screenshot."
*   **Getting the Time:** "EGO, what time is it?"
*   **And more!** You can teach EGO new commands.

## How to Start

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download the Vosk model:**
    *   Download a Vosk model from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models).
    *   Extract the model and place it in a folder named `model` in the root of the project.

4.  **Run the application:**
    ```bash
    python ego_gui.py
    ```

## Dependencies

The project uses the following libraries:

*   `requests`
*   `wikipedia`
*   `speechrecognition`
*   `pyttsx3`
*   `pillow`
*   `torch`
*   `transformers`
*   `accelerate`
*   `vosk`
*   `sounddevice`
*   `psutil`
*   `newsapi-python`
*   `pyautogui`
*   `tkinter`

