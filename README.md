# EGO - Your Personal AI Assistant

EGO is a personal AI assistant with a visually appealing interface and a modular skill system. It listens for the wake word "EGO" and can perform a variety of tasks based on your voice commands.

## How It Works

EGO follows a state-driven pipeline from wake word detection to intent execution and response.

1. **Initialization** – `ego_gui.py` starts the Tkinter GUI, loads TTS, and loads skills from `/skills`.
2. **Wake Word Detection** – Listens for "EGO" via Vosk STT, orb in `idle` state.
3. **Command Listening** – On wake word, says "Yes?", orb in `listening` state.
4. **Speech-to-Text** – Uses Vosk (offline) or Google STT (online) for transcription.
5. **Intent Extraction** – Checks learned commands → keywords → GPT-2 LLM for fallback.
6. **Action Execution** – Runs built-in commands or matches a `/skills` handler.
7. **Response (TTS)** – Speaks result via pyttsx3, orb returns to `idle`.

## Architecture Flowchart

```mermaid
graph TD
    A[Start ego_gui.py] --> B{Initialize GUI & Core Logic};
    B --> C[Background Thread: Start Wake Word Listener];
    C --> D{Listen for 'EGO' via Vosk STT};
    D -- Wake Word Detected --> E[Speak 'Yes?' & Set State to Listening];
    E --> F[Listen for Full Command];
    F --> G[Transcribe Command (Vosk / Google STT)];
    G --> H[Extract Intent (Keywords / LLM)];
    H -- Set State to Processing --> I{Perform Action};
    I -- Built-in Command --> J[Execute System Action e.g., open app];
    I -- Skill-based Command --> K[Execute Matched Skill from /skills];
    I -- Intent Not Found --> L[Ask User to Learn New Command];
    J --> M[Generate Response Text];
    K --> M;
    L --> C;
    M -- Set State to Speaking --> N[Speak Response via pyttsx3];
    N -- Set State to Idle --> C;

    style D fill:#cde4ff,stroke:#333,stroke-width:2px
    style F fill:#cde4ff,stroke:#333,stroke-width:2px
    style H fill:#fff2cd,stroke:#333,stroke-width:2px
    style I fill:#d4edda,stroke:#333,stroke-width:2px
```
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
