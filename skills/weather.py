import requests

def run(intent, target):
    if intent == "get_weather":
        city = target or ""
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url)
            return response.text
        except Exception as e:
            return f"Could not fetch weather: {e}"
    return None 