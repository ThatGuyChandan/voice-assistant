# assistant_core.py

import os
import socket
import pyttsx3
import re
import speech_recognition as sr
from datetime import datetime
# from sentence_transformers import SentenceTransformer, util  # Removed
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import importlib.util
import glob
try:
    from ego_gui import set_gui_state
except ImportError:
    def set_gui_state(state):
        pass  # fallback if GUI is not running

try:
    import pyautogui
except ImportError:
    pyautogui = None

# === Text-to-Speech ===
engine = pyttsx3.init()

def speak(text):
    set_gui_state('speaking')
    print(f"[EGO]: {text}")
    engine.say(text)
    engine.runAndWait()
    set_gui_state('idle')

# === Internet Check ===
def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

# === LLM Setup ===
MODEL_NAME = "microsoft/phi-2"  # You can change to another open model if needed
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
except Exception as e:
    print("[EGO]: Failed to load LLM model:", e)
    tokenizer = None
    model = None

# === Command Learning Storage ===
LEARNED_COMMANDS_FILE = "learned_commands.json"
def load_learned_commands():
    if os.path.exists(LEARNED_COMMANDS_FILE):
        with open(LEARNED_COMMANDS_FILE, "r") as f:
            return json.load(f)
    return {}
def save_learned_commands(cmds):
    with open(LEARNED_COMMANDS_FILE, "w") as f:
        json.dump(cmds, f)
learned_commands = load_learned_commands()

# === LLM Intent Extraction ===
def extract_intent(user_input):
    # Check learned commands first
    for phrase, action in learned_commands.items():
        if phrase.lower() in user_input.lower():
            return action
    # Simple keyword mapping for skills
    if "weather" in user_input.lower():
        return {"intent": "get_weather", "target": user_input.split("in")[-1].strip() if "in" in user_input else None}
    if "wikipedia" in user_input.lower() or "who is" in user_input.lower() or "what is" in user_input.lower():
        topic = user_input.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        return {"intent": "get_wikipedia", "target": topic}
    if not model or not tokenizer:
        return {"intent": None, "target": None}
    prompt = (
        "Extract the intent and target from the following user command. "
        "Reply in JSON with keys 'intent' and 'target'.\n"
        f"User: {user_input}\n"
        "Example 1: User: Open Spotify\n{'intent': 'open_app', 'target': 'Spotify'}\n"
        "Example 2: User: Search for Python tutorials\n{'intent': 'web_search', 'target': 'Python tutorials'}\n"
        "Example 3: User: What time is it?\n{'intent': 'get_time', 'target': null}\n"
        "Now answer:\n"
    )
    set_gui_state('processing')
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=60)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    set_gui_state('idle')
    # Try to extract JSON from response
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0).replace("'", '"'))
        except Exception:
            pass
    return {"intent": None, "target": None}

# === Skill/Plugin System ===
skill_modules = []

def load_skills(skills_dir="skills"):
    global skill_modules
    skill_modules = []
    for skill_path in glob.glob(os.path.join(skills_dir, "*.py")):
        module_name = os.path.splitext(os.path.basename(skill_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, skill_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            skill_modules.append(mod)

load_skills()

# === Execute Intent ===
def perform_action(intent_data, user_text):
    intent = intent_data.get("intent")
    target = intent_data.get("target")
    if intent == "open_app" and target:
        set_gui_state('processing')
        os.system(f'start "" "{target}"')
        speak(f"Opening {target}")
        set_gui_state('idle')
    elif intent == "web_search" and target:
        set_gui_state('processing')
        query = target.replace(' ', '+')
        os.system(f'start https://www.google.com/search?q={query}')
        speak(f"Searching the web for {target}")
        set_gui_state('idle')
    elif intent == "get_time":
        speak(f"The time is {datetime.now().strftime('%H:%M')}")
    elif intent == "tell_joke":
        speak("Why did the computer show up at work late? It had a hard drive!")
    elif intent == "get_weather":
        speak("Fetching the weather...")
        for mod in skill_modules:
            if hasattr(mod, 'run') and mod.run(intent, target):
                break
    elif intent == "get_wikipedia":
        speak(f"Searching Wikipedia for {target}...")
        for mod in skill_modules:
            if hasattr(mod, 'run') and mod.run(intent, target):
                break
    elif intent == "screenshot" and pyautogui:
        pyautogui.screenshot('screenshot.png')
        speak("Screenshot saved.")
    elif intent == "exit":
        speak("Goodbye!")
        set_gui_state('idle')
        os._exit(0)
    elif intent is not None:
        # Try all loaded skills
        for mod in skill_modules:
            try:
                if hasattr(mod, 'run') and mod.run(intent, target):
                    speak(f"Skill '{mod.__name__}' handled the intent '{intent}'.")
                    return
            except Exception as e:
                print(f"Error in skill {mod.__name__}: {e}")
        speak(f"Intent '{intent}' with target '{target}' is not implemented yet.")
    else:
        # Learning mechanism
        speak("I didn't understand that. Would you like to teach me what to do?")
        answer = recognize_speech_auto().lower()
        if "yes" in answer:
            speak("Please describe the action I should perform when you say this command.")
            action = recognize_speech_auto()
            learned_commands[user_text] = {"intent": "custom", "target": action}
            save_learned_commands(learned_commands)
            speak("Learned new command!")
        else:
            speak("Okay, let me know if you want to teach me next time.")

# === Speech Recognition ===
recognizer = sr.Recognizer()

def recognize_speech():
    set_gui_state('listening')
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
        except:
            text = ""
    set_gui_state('idle')
    return text

def recognize_speech_vosk(model_path="model"):  # model_path should point to a Vosk model directory
    """Listen to the microphone and print recognized text using Vosk."""
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        q.put(bytes(indata))

    try:
        model = Model(model_path)
    except Exception as e:
        print(f"Could not load Vosk model from {model_path}: {e}")
        return

    recognizer = KaldiRecognizer(model, 16000)
    print("Listening... (press Ctrl+C to stop)")
    with sd.RawInputStream(samplerate=16000, blocksize = 8000, dtype='int16', channels=1, callback=callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get('text', '')
                if text:
                    print(f"Recognized: {text}")
            else:
                # Partial result can be used for real-time feedback
                pass

# Example usage:
# recognize_speech_vosk("model")
# Download a Vosk model (e.g., from https://alphacephei.com/vosk/models) and extract to a 'model' folder.

def recognize_speech_auto():
    """Try Vosk first, fallback to Google if not available."""
    model_path = "model"
    if os.path.exists(model_path):
        try:
            return recognize_speech_vosk(model_path)
        except Exception as e:
            print(f"Vosk failed: {e}")
    return recognize_speech()

# === Wake Word Detection Loop ===
def wake_word_listener():
    while True:
        set_gui_state('idle')
        print("🔁 Waiting for wake word 'EGO'...")
        text = recognize_speech_auto().lower()
        if "ego" in text:
            speak("Yes?")
            set_gui_state('listening')
            user_cmd = recognize_speech_auto()
            print("🗣️ You said:", user_cmd)
            intent_data = extract_intent(user_cmd)
            perform_action(intent_data, user_cmd)
