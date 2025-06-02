#!/usr/bin/env python3
"""
🚀 Wi-Fi Lag Switch Simulator v2 🚀

- Tkinter GUI with upgraded controls:
  • Slider (0–50) for “Lag Intensity”
  • Manual entry box for any custom thread count
  • Live Active-Threads counter
  • Start / Stop button + status updates

- Spawns background threads to repeatedly download a 10MB test file,
  creating real network load so you can test how jittery your video calls get.

Dependencies:
    pip install requests
"""

import threading
import tkinter as tk
from tkinter import ttk, font
import time
import requests

# 10MB test file (from ThinkBroadband). Swap this URL if you want a different file.
TEST_FILE_URL = "http://ipv4.download.thinkbroadband.com/10MB.zip"

class LagThread(threading.Thread):
    """Thread that keeps downloading a test file to generate network load."""
    def __init__(self, stop_event: threading.Event, idx: int):
        super().__init__(daemon=True)
        self.stop_event = stop_event
        self.idx = idx

    def run(self):
        session = requests.Session()
        while not self.stop_event.is_set():
            try:
                with session.get(TEST_FILE_URL, stream=True, timeout=10) as resp:
                    # Read & discard in 64KB chunks
                    for chunk in resp.iter_content(chunk_size=64 * 1024):
                        if self.stop_event.is_set():
                            break
                        # Just drop the chunk
                        pass
                time.sleep(0.05)  # Brief pause before next download
            except requests.RequestException:
                time.sleep(1)  # If something breaks, wait a sec and retry

class LagGUI:
    """Main Tkinter application for the Wi-Fi Lag Simulator v2."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌐 Wi-Fi Lag Switch Simulator v2")
        self.root.geometry("450x280")
        self.root.resizable(False, False)

        # Use a slightly larger default font for clarity
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)

        self.stop_event = None
        self.threads = []

        # --- Top Instruction Label ---
        self.intro_label = ttk.Label(
            root,
            text="🚦 Stress Your Wi-Fi & Watch Video Calls Stutter 🚦",
            justify="center",
            wraplength=400,
            font=("Helvetica", 11, "bold"),
            foreground="#333"
        )
        self.intro_label.pack(pady=(10, 5))

        # --- Frame for Controls ---
        controls_frame = ttk.LabelFrame(root, text="Lag Controls", padding=(15, 10))
        controls_frame.pack(fill="x", padx=20, pady=10)

        # 1) Slider Label + Widget
        ttk.Label(controls_frame, text="Lag Intensity (Slider):").grid(row=0, column=0, sticky="w")
        self.slider = ttk.Scale(controls_frame, from_=0, to=50, orient="horizontal")
        self.slider.set(0)
        self.slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,8))
        controls_frame.columnconfigure(1, weight=1)

        # 2) Manual Entry Label + Widget
        ttk.Label(controls_frame, text="Manual Thread Count:").grid(row=2, column=0, sticky="w", pady=(5,0))
        self.manual_entry_var = tk.StringVar()
        self.manual_entry = ttk.Entry(controls_frame, textvariable=self.manual_entry_var, width=10)
        self.manual_entry.grid(row=2, column=1, sticky="w", pady=(5,0))
        ttk.Label(controls_frame, text="(Overrides slider if valid)").grid(row=3, column=0, columnspan=2, sticky="w")

        # 3) Active Threads Counter
        ttk.Label(controls_frame, text="Active Threads:").grid(row=4, column=0, sticky="w", pady=(10,0))
        self.active_count_var = tk.StringVar(value="0")
        self.active_count_label = ttk.Label(controls_frame, textvariable=self.active_count_var, foreground="#0055AA")
        self.active_count_label.grid(row=4, column=1, sticky="w", pady=(10,0))

        # --- Start / Stop Button ---
        self.btn_text = tk.StringVar(value="▶ Start Lagging")
        self.start_stop_btn = ttk.Button(
            root,
            textvariable=self.btn_text,
            command=self.toggle_lag,
            style="Accent.TButton"
        )
        self.start_stop_btn.pack(pady=(10, 5))

        # --- Status Label ---
        self.status_var = tk.StringVar(value="Idle. Choose slider or enter a number, then press Start.")
        self.status_label = ttk.Label(root, textvariable=self.status_var, foreground="green", wraplength=400)
        self.status_label.pack(pady=(0, 10))

    def toggle_lag(self):
        if self.stop_event and not self.stop_event.is_set():
            # If already running → stop
            self.stop_lag()
        else:
            # Else → start
            self.start_lag()

    def start_lag(self):
        # 1) Check manual entry first
        raw_manual = self.manual_entry_var.get().strip()
        num_threads = 0

        if raw_manual:
            # Try parsing manual input as positive integer
            try:
                requested = int(raw_manual)
                if requested < 0:
                    raise ValueError
                num_threads = requested
            except ValueError:
                self.status_var.set("❗ Manual entry invalid. Use a positive integer or slider.")
                self.status_label.configure(foreground="red")
                return
        else:
            # Fallback to slider
            num_threads = int(self.slider.get())

        if num_threads <= 0:
            self.status_var.set("Pick a number > 0 (slider or manual). 🤓")
            self.status_label.configure(foreground="orange")
            return

        # Setup stop_event and thread list
        self.stop_event = threading.Event()
        self.threads = []

        # Update UI to “starting” state
        self.status_var.set(f"Starting {num_threads} lag threads… 🏃💨")
        self.status_label.configure(foreground="orange")
        self.btn_text.set("⏹ Stop Lagging")

        # Spawn threads
        for i in range(num_threads):
            t = LagThread(self.stop_event, idx=i)
            t.start()
            self.threads.append(t)
            # Update active-count display
            self.active_count_var.set(str(len(self.threads)))

        # After a short delay, update status to “running”
        self.root.after(500, lambda: self.status_var.set(f"Lagging with {num_threads} threads! 🔥"))

    def stop_lag(self):
        if self.stop_event:
            self.stop_event.set()

        self.status_var.set("Stopping all lag threads… ✋")
        self.status_label.configure(foreground="red")
        self.btn_text.set("▶ Start Lagging")

        # Let threads exit, then clean up
        self.root.after(500, self._cleanup_threads)

    def _cleanup_threads(self):
        # Join threads with a tiny timeout
        for t in self.threads:
            t.join(timeout=0.1)

        # Reset counters & status
        self.threads = []
        self.stop_event = None
        self.active_count_var.set("0")
        self.status_var.set("All done! Wi-Fi is chill again. 😌")
        self.status_label.configure(foreground="green")

def main():
    root = tk.Tk()

    # Configure a custom style for the button (if you’re on a newer Tkinter version)
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("Accent.TButton", foreground="white", background="#007ACC")

    app = LagGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
