# assistant_gui.py

import tkinter as tk
import threading
import time
from ego_core import wake_word_listener, speak

# Shared state for orb animation
class OrbState:
    def __init__(self):
        self.state = 'idle'  # idle, listening, speaking, processing
        self.lock = threading.Lock()
    def set_state(self, new_state):
        with self.lock:
            self.state = new_state
    def get_state(self):
        with self.lock:
            return self.state

global_orb_state = OrbState()

def set_orb_state(new_state):
    global_orb_state.set_state(new_state)

# Animated orb on canvas
class AnimatedOrb(tk.Canvas):
    def __init__(self, master, orb_state, **kwargs):
        super().__init__(master, width=512, height=512, bg='black', highlightthickness=0, **kwargs)
        self.orb_state = orb_state
        self.radius = 120
        self.pulse = 0
        self.pulse_dir = 1
        self.color_map = {
            'idle': '#3a3aff',
            'listening': '#00ffea',
            'speaking': '#ffb300',
            'processing': '#ff3a3a',
        }
        self.after(0, self.animate)

    def animate(self):
        state = self.orb_state.get_state()
        color = self.color_map.get(state, '#3a3aff')
        self.pulse += self.pulse_dir * (2 if state != 'idle' else 0.5)
        if self.pulse > 30 or self.pulse < 0:
            self.pulse_dir *= -1
        r = self.radius + self.pulse
        self.delete('all')
        # Draw glow
        for i in range(10, 0, -1):
            self.create_oval(
                256 - r - i*4, 256 - r - i*4,
                256 + r + i*4, 256 + r + i*4,
                fill=color, outline='', stipple='gray50'
            )
        # Draw main orb
        self.create_oval(
            256 - r, 256 - r,
            256 + r, 256 + r,
            fill=color, outline='white', width=4
        )
        self.after(30, self.animate)

def launch_gui():
    root = tk.Tk()
    root.title("EGO")
    root.geometry("512x512")
    root.configure(bg="black")

    orb = AnimatedOrb(root, global_orb_state)
    orb.pack(expand=True, fill='both')

    # Start wake-word listener in the background
    threading.Thread(target=wake_word_listener, daemon=True).start()

    root.mainloop()

def set_gui_state(state):
    set_orb_state(state)

if __name__ == "__main__":
    speak("EGO online and listening...")
    launch_gui()
