import psutil

def run(intent, target):
    if intent == "get_cpu_usage":
        usage = psutil.cpu_percent(interval=1)
        return f"The CPU is at {usage}% usage."
    
    if intent == "get_memory_usage":
        memory = psutil.virtual_memory()
        return f"Your system has {memory.percent}% memory usage."

    if intent == "get_battery_status":
        battery = psutil.sensors_battery()
        if battery:
            return f"The battery is at {battery.percent}% and charging status is {battery.power_plugged}."
        else:
            return "I couldn't find a battery on this system."

    return None
