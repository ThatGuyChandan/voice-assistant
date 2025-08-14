import wikipedia

def run(intent, target):
    if intent == "get_wikipedia":
        try:
            summary = wikipedia.summary(target, sentences=2)
            return summary
        except Exception as e:
            return f"Could not fetch Wikipedia summary: {e}"
    return None 