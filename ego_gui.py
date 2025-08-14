import tkinter as tk
import threading
import random
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

def set_gui_state(state):
    global_orb_state.set_state(state)

# Starfield background
class Starfield(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg='#00001a', highlightthickness=0, **kwargs)
        self.stars = []
        for _ in range(200):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            size = random.uniform(0.5, 2.5)
            self.stars.append(self.create_oval(x, y, x+size, y+size, fill='white', outline=''))
        self.after(0, self.animate)

    def animate(self):
        for star in self.stars:
            self.move(star, -0.5, 0.25)
            x1, y1, _, _ = self.coords(star)
            if x1 < 0 or y1 > 1080:
                self.move(star, 1920, -random.randint(0, 1080))
        self.after(30, self.animate)

# Animated orb on canvas
class AnimatedOrb(tk.Canvas):
    def __init__(self, master, orb_state, **kwargs):
        super().__init__(master, bg='#00001a', highlightthickness=0, **kwargs)
        self.orb_state = orb_state
        self.radius = 150
        self.pulse = 0
        self.pulse_dir = 1
        self.rotation = 0
        self.color_map = {
            'idle': '#00bfff',       # DeepSkyBlue
            'listening': '#00ffea',   # Aqua
            'speaking': '#ffc700',    # Gold
            'processing': '#ff4d4d',  # Light Coral
        }
        self.after(0, self.animate)

    def animate(self):
        state = self.orb_state.get_state()
        color = self.color_map.get(state, '#00bfff')
        
        # More dynamic pulsing
        if state == 'idle':
            self.pulse += self.pulse_dir * 0.3
            if not -10 < self.pulse < 10:
                self.pulse_dir *= -1
        else:
            self.pulse += self.pulse_dir * 1.5
            if not -25 < self.pulse < 25:
                self.pulse_dir *= -1

        r = self.radius + self.pulse
        self.delete('all')

        # Draw outer rings
        self.rotation = (self.rotation + 0.5) % 360
        for i in range(3):
            self.create_arc(256-r-i*20, 256-r-i*20, 256+r+i*20, 256+r+i*20,
                            start=self.rotation + i*120, extent=60, 
                            outline=color, width=2, style=tk.ARC)

        # Draw main orb glow
        for i in range(15, 0, -1):
            alpha = 1 - (i / 15)
            glow_color = self._alpha_to_hex(color, alpha * 0.5)
            self.create_oval(256 - r - i*2, 256 - r - i*2, 256 + r + i*2, 256 + r + i*2,
                             fill=glow_color, outline='')

        # Draw main orb
        self.create_oval(256 - r, 256 - r, 256 + r, 256 + r,
                         fill=color, outline='white', width=3)

        self.after(16, self.animate) # ~60 FPS

    def _alpha_to_hex(self, hex_color, alpha):
        # A simple way to simulate alpha by blending with background
        bg_r, bg_g, bg_b = 26, 26, 42 # approx. #00001a
        fg_r = int(hex_color[1:3], 16)
        fg_g = int(hex_color[3:5], 16)
        fg_b = int(hex_color[5:7], 16)
        r = int(fg_r * alpha + bg_r * (1 - alpha))
        g = int(fg_g * alpha + bg_g * (1 - alpha))
        b = int(fg_b * alpha + bg_b * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"

def launch_gui():
    root = tk.Tk()
    root.title("EGO - Your Personal AI")
    root.geometry("512x512")
    root.configure(bg="#00001a")

    # Create a container for stacking canvases
    container = tk.Frame(root)
    container.pack(fill='both', expand=True)

    starfield = Starfield(container)
    starfield.place(relwidth=1, relheight=1)

    orb = AnimatedOrb(container, global_orb_state)
    orb.place(relwidth=1, relheight=1)

    # Start wake-word listener in the background
    threading.Thread(target=wake_word_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    speak("EGO online and listening...")
    launch_gui()
