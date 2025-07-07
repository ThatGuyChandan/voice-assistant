# assistant_core.py

import os
import socket
import pyttsx3
import re
import speech_recognition as sr
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

# === Text-to-Speech ===
engine = pyttsx3.init()

def speak(text):
    print(f"[EGO]: {text}")
    engine.say(text)
    engine.runAndWait()

# === Internet Check ===
def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

# === NLP Intent Matching ===
nlp_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
intents = {
    "open_chrome": ["open chrome", "launch browser", "start google"],
    "youtube_search": ["search youtube for", "play on youtube", "find on youtube"],
    "get_time": ["what time is it", "tell me the time", "current time"],
    "exit": ["exit", "quit", "close jarvis", "stop running"]
}

def get_intent(user_input):
    user_embedding = nlp_model.encode(user_input, convert_to_tensor=True)
    best_score = -1
    best_intent = None

    for intent, examples in intents.items():
        example_embeddings = nlp_model.encode(examples, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(user_embedding, example_embeddings)
        max_score = scores.max().item()
        if max_score > best_score:
            best_score = max_score
            best_intent = intent

    return best_intent if best_score > 0.6 else None

# === Execute Intent ===
def perform_action(intent, user_text):
    if intent == "open_chrome":
        os.system("start chrome")
        speak("Opening Chrome")
    elif intent == "youtube_search":
        query = re.sub(r"(search|play|find).*youtube(for)?", "", user_text, flags=re.I).strip().replace(" ", "+")
        os.system(f"start https://www.youtube.com/results?search_query={query}")
        speak(f"Searching YouTube for {query.replace('+', ' ')}")
    elif intent == "get_time":
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
    elif intent == "exit":
        speak("Goodbye!")
        os._exit(0)
    else:
        speak("I don't know how to do that.")

# === Speech Recognition ===
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        audio = recognizer.listen(source, timeout=5)
        try:
            return recognizer.recognize_google(audio)
        except:
            return ""

# === Wake Word Detection Loop ===
def wake_word_listener():
    while True:
        print("🔁 Waiting for wake word 'EGO'...")
        text = recognize_speech().lower()
        if "ego" in text:
            speak("Yes?")
            user_cmd = recognize_speech()
            print("🗣 You said:", user_cmd)
            intent = get_intent(user_cmd)
            if intent:
                perform_action(intent, user_cmd)
            else:
                speak("I didn't understand that.")
