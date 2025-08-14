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
import sys
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
def init_tts():
    try:
        # Try to initialize with a specific driver if needed
        try:
            if sys.platform == "win32":
                engine = pyttsx3.init('sapi5')  # Try sapi5 first (Windows)
            else:
                engine = pyttsx3.init()
        except:
            engine = pyttsx3.init()  # Fall back to default
        
        # Set properties
        try:
            voices = engine.getProperty('voices')
            # Try to find a working voice
            voice_preferences = [
                # Try English voices first
                lambda v: 'en' in v.languages and v.gender == 'male',
                lambda v: 'en' in v.languages,
                # Fall back to any voice
                lambda v: True
            ]
            
            for voice_check in voice_preferences:
                for voice in voices:
                    if voice_check(voice):
                        try:
                            engine.setProperty('voice', voice.id)
                            print(f"Using voice: {voice.name}")
                            return engine
                        except Exception as e:
                            print(f"Could not set voice {voice.id}: {e}")
                            continue
        except Exception as e:
            print(f"Error setting up voice: {e}")
        
        return engine
    except Exception as e:
        print(f"Failed to initialize TTS engine: {e}")
        return None

engine = init_tts()
if engine is None:
    print("Warning: Could not initialize TTS engine. Speech output will be disabled.")
    # Create a dummy engine that does nothing
    class DummyEngine:
        def say(self, *args, **kwargs):
            print("[TTS Disabled]", *args)
        def runAndWait(self):
            pass
        def setProperty(self, *args, **kwargs):
            pass
    engine = DummyEngine()

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
MODEL_NAME = "gpt2"  # You can change to another open model if needed
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
    
    # First, check for built-in commands that don't rely on the skill system
    if intent == "open_app" and target:
        set_gui_state('processing')
        os.system(f'start "" "{target}"')
        speak(f"Opening {target}")
        set_gui_state('idle')
        return
    elif intent == "web_search" and target:
        set_gui_state('processing')
        query = target.replace(' ', '+')
        os.system(f'start https://www.google.com/search?q={query}')
        speak(f"Searching the web for {target}")
        set_gui_state('idle')
        return
    elif intent == "get_time":
        speak(f"The time is {datetime.now().strftime('%H:%M')}")
        return
    elif intent == "screenshot" and pyautogui:
        pyautogui.screenshot('screenshot.png')
        speak("Screenshot saved.")
        return
    elif intent == "exit":
        speak("Goodbye!")
        set_gui_state('idle')
        os._exit(0)

    # If not a built-in command, try to find a skill to handle it
    if intent:
        for mod in skill_modules:
            if hasattr(mod, 'run'):
                try:
                    # Pass both intent and target to the skill's run function
                    result = mod.run(intent, target)
                    if result:
                        # If the skill returns a string, speak it
                        if isinstance(result, str):
                            speak(result)
                        # Otherwise, give a generic confirmation
                        else:
                            speak(f"Okay, I've handled that.")
                        return # Exit after the first successful skill
                except Exception as e:
                    print(f"Error in skill {mod.__name__}: {e}")
                    speak(f"I encountered an error trying to use the {mod.__name__} skill.")
                    return

    # If no skill was found or the intent was None
    if intent:
        speak(f"I don't know how to handle the intent '{intent}'.")
    else:
        # Fallback to the learning mechanism if intent is None
        speak("I didn't understand that. Would you like to teach me what to do?")
        try:
            answer = recognize_speech_auto().lower()
            if "yes" in answer:
                speak("Please describe the action I should perform when you say this command.")
                action_description = recognize_speech_auto()
                # For simplicity, we'll create a custom intent and save it
                # A more robust system would ask for a specific JSON structure
                new_intent = f"custom_{user_text.lower().replace(' ', '_')}"
                learned_commands[user_text] = {"intent": new_intent, "target": action_description}
                save_learned_commands(learned_commands)
                speak("I've learned a new command!")
            else:
                speak("Okay, let me know if you change your mind.")
        except Exception as e:
            print(f"Error during learning process: {e}")
            speak("Sorry, something went wrong while I was trying to learn.")

# === Speech Recognition ===
recognizer = sr.Recognizer()

def recognize_speech():
    set_gui_state('listening')
    # Find a working microphone
    mic_index = None
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if mic_list:
            # Heuristic: prefer non-default devices if available, otherwise use default
            # This can help on systems with virtual audio cables.
            for i, name in enumerate(mic_list):
                # A simple heuristic to find a real microphone
                if 'microphone' in name.lower() or 'headset' in name.lower():
                    mic_index = i
                    print(f"Using microphone: {name}")
                    break
            if mic_index is None:
                mic_index = 0 # Fallback to the first one
    except Exception as e:
        print(f"Could not list microphones: {e}")
        set_gui_state('idle')
        return ""

    with sr.Microphone(device_index=mic_index) as source:
        print("🎤 Listening for command...")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            text = ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            text = ""
        except Exception as e:
            print(f"An error occurred during speech recognition: {e}")
            text = ""
    set_gui_state('idle')
    return text

def recognize_speech_vosk(model_path="model"):
    """Listen to the microphone and return recognized text using Vosk."""
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        q.put(bytes(indata))

    try:
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
    except Exception as e:
        print(f"Could not load Vosk model from {model_path}: {e}")
        return ""

    device_index = None
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            raise ValueError("No input audio devices found.")
        # Heuristic to find a real microphone
        for i, d in enumerate(input_devices):
            if 'microphone' in d['name'].lower() or 'headset' in d['name'].lower():
                device_index = d['index']
                print(f"Using device: {d['name']}")
                break
        if device_index is None:
            device_index = input_devices[0]['index'] # Fallback to the first one
    except Exception as e:
        print(f"Could not find a suitable audio device for Vosk: {e}")
        return ""

    set_gui_state('listening')
    print("🎤 Listening for command (Vosk)...")

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback, device=device_index):
            # Listen for a phrase. This is tricky without a proper VAD.
            # We'll listen for a few seconds and see if we get a result.
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < 7: # 7 second timeout
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result).get('text', '')
                    if text:
                        set_gui_state('idle')
                        return text
            # If no full result, get partial result
            result = recognizer.FinalResult()
            text = json.loads(result).get('text', '')
            set_gui_state('idle')
            return text

    except Exception as e:
        print(f"Vosk recognition failed: {e}")
        set_gui_state('idle')
        return ""

def recognize_speech_auto():
    """Try Vosk first, fallback to Google if not available."""
    model_path = "model"
    if os.path.exists(model_path):
        text = recognize_speech_vosk(model_path)
        if text:
            return text
    # Fallback to Google Speech Recognition
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
