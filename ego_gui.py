# assistant_gui.py

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
from ego_core import wake_word_listener, speak

def launch_gui():
    root = tk.Tk()
    root.title("EGO")
    root.geometry("512x512")
    root.configure(bg="black")

    # Load animated GIF into frames
    gif = Image.open("ego_orb.gif")
    frames = [ImageTk.PhotoImage(frame.copy().resize((512, 512))) for frame in ImageSequence.Iterator(gif)]
    label = tk.Label(root, bg="black")
    label.pack()

    # Animate the GIF at ~20 FPS
    def animate(index=0):
        label.config(image=frames[index])
        root.after(50, animate, (index + 1) % len(frames))
    animate()

    # Start wake-word listener in the background
    threading.Thread(target=wake_word_listener, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    speak("EGO online and listening...")
    launch_gui()
