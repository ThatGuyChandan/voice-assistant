import webbrowser

def run(intent, target):
    if intent == "open_website":
        if target:
            try:
                webbrowser.open(f"https://{target}")
                return f"Opening {target}"
            except Exception as e:
                return f"I couldn't open the website: {e}"
        else:
            return "Please specify a website to open."
    return None
