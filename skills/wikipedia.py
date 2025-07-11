import wikipedia

def run(intent, target):
    if intent == "get_wikipedia":
        try:
            summary = wikipedia.summary(target, sentences=2)
            print(summary)
        except Exception as e:
            print(f"Could not fetch Wikipedia summary: {e}")
        return True
    return False 