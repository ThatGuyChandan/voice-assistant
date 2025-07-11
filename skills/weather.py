import requests

def run(intent, target):
    if intent == "get_weather":
        city = target or ""
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url)
            print(response.text)
        except Exception as e:
            print(f"Could not fetch weather: {e}")
        return True
    return False 