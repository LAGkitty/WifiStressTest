#!/usr/bin/env python3
"""
WiFi Stress Test Tool
A network performance testing tool with GUI controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import time
import requests
import concurrent.futures
from urllib.parse import urlparse
import random

class WiFiStressTester:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Stress Test Tool")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Test state variables
        self.is_running = False
        self.test_threads = []
        self.stop_event = threading.Event()
        
        # Test targets (public endpoints that can handle traffic)
        self.test_urls = [
            "http://httpbin.org/bytes/1024",
            "http://httpbin.org/delay/0.1",
            "https://jsonplaceholder.typicode.com/posts",
            "http://httpbin.org/stream/10"
        ]
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="WiFi Stress Test Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status indicator
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        self.status_label = ttk.Label(self.status_frame, text="Status: Idle", 
                                     font=("Arial", 12))
        self.status_label.grid(row=0, column=0)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=20, height=20)
        self.status_indicator.grid(row=0, column=1, padx=(10, 0))
        self.status_indicator.create_oval(5, 5, 15, 15, fill="gray", outline="")
        
        # Intensity slider
        intensity_frame = ttk.LabelFrame(main_frame, text="Test Intensity", padding="10")
        intensity_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.intensity_var = tk.IntVar(value=50)
        self.intensity_slider = ttk.Scale(intensity_frame, from_=10, to=100, 
                                         orient="horizontal", variable=self.intensity_var,
                                         length=300)
        self.intensity_slider.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.intensity_label = ttk.Label(intensity_frame, text="50%")
        self.intensity_label.grid(row=0, column=1, padx=(10, 0))
        
        # Update label when slider changes
        self.intensity_slider.configure(command=self.update_intensity_label)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="Start Test", 
                                      command=self.toggle_test, style="Success.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Test", 
                                     command=self.stop_test, state="disabled")
        self.stop_button.grid(row=0, column=1)
        
        # Test configuration
        config_frame = ttk.LabelFrame(main_frame, text="Test Configuration", padding="10")
        config_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Thread count
        ttk.Label(config_frame, text="Concurrent Connections:").grid(row=0, column=0, sticky=tk.W)
        self.thread_var = tk.IntVar(value=10)
        thread_spinbox = ttk.Spinbox(config_frame, from_=1, to=50, textvariable=self.thread_var, width=10)
        thread_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Request delay
        ttk.Label(config_frame, text="Request Delay (ms):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.delay_var = tk.IntVar(value=100)
        delay_spinbox = ttk.Spinbox(config_frame, from_=10, to=1000, textvariable=self.delay_var, width=10)
        delay_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.stats_text = tk.Text(stats_frame, height=6, width=50, state="disabled")
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for stats
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        intensity_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        
    def update_intensity_label(self, value):
        self.intensity_label.config(text=f"{int(float(value))}%")
        
    def toggle_test(self):
        if not self.is_running:
            self.start_test()
        else:
            self.stop_test()
            
    def start_test(self):
        self.is_running = True
        self.stop_event.clear()
        
        # Update UI
        self.start_button.config(text="Running...", state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Status: Running")
        self.status_indicator.create_oval(5, 5, 15, 15, fill="green", outline="")
        
        # Clear stats
        self.stats_text.config(state="normal")
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state="disabled")
        
        # Start test thread
        test_thread = threading.Thread(target=self.run_stress_test, daemon=True)
        test_thread.start()
        
        self.log_stats("Test started...")
        
    def stop_test(self):
        self.is_running = False
        self.stop_event.set()
        
        # Update UI
        self.start_button.config(text="Start Test", state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopping...")
        self.status_indicator.create_oval(5, 5, 15, 15, fill="orange", outline="")
        
        # Wait a moment then update to idle
        self.root.after(2000, self.set_idle_status)
        
        self.log_stats("Test stopped.")
        
    def set_idle_status(self):
        if not self.is_running:
            self.status_label.config(text="Status: Idle")
            self.status_indicator.create_oval(5, 5, 15, 15, fill="gray", outline="")
    
    def run_stress_test(self):
        """Main stress test function"""
        intensity = self.intensity_var.get()
        thread_count = self.thread_var.get()
        base_delay = self.delay_var.get() / 1000.0  # Convert to seconds
        
        # Adjust parameters based on intensity
        actual_threads = max(1, int(thread_count * (intensity / 100)))
        actual_delay = base_delay * (100 / intensity)  # Higher intensity = less delay
        
        self.log_stats(f"Using {actual_threads} threads with {actual_delay:.3f}s delay")
        
        request_count = 0
        error_count = 0
        start_time = time.time()
        
        def make_requests():
            nonlocal request_count, error_count
            session = requests.Session()
            
            while not self.stop_event.is_set():
                try:
                    # Choose random test URL
                    url = random.choice(self.test_urls)
                    
                    # Make request with timeout
                    response = session.get(url, timeout=5)
                    request_count += 1
                    
                    if request_count % 10 == 0:  # Update stats every 10 requests
                        elapsed = time.time() - start_time
                        rate = request_count / elapsed if elapsed > 0 else 0
                        self.root.after(0, lambda: self.log_stats(
                            f"Requests: {request_count}, Errors: {error_count}, Rate: {rate:.1f}/s"))
                    
                except Exception as e:
                    error_count += 1
                    
                time.sleep(actual_delay)
        
        # Start worker threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=actual_threads) as executor:
            futures = [executor.submit(make_requests) for _ in range(actual_threads)]
            
            # Wait for stop signal
            while not self.stop_event.is_set():
                time.sleep(0.1)
            
            # Shutdown executor
            executor.shutdown(wait=False)
        
        # Final stats
        elapsed = time.time() - start_time
        rate = request_count / elapsed if elapsed > 0 else 0
        self.root.after(0, lambda: self.log_stats(
            f"Final: {request_count} requests, {error_count} errors in {elapsed:.1f}s (Rate: {rate:.1f}/s)"))
    
    def log_stats(self, message):
        """Add message to stats display"""
        self.stats_text.config(state="normal")
        self.stats_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.stats_text.see(tk.END)
        self.stats_text.config(state="disabled")

def main():
    # Check for required modules
    try:
        import requests
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Module", 
                           "This tool requires the 'requests' module.\n"
                           "Install it with: pip install requests")
        return
    
    root = tk.Tk()
    app = WiFiStressTester(root)
    
    # Handle window close
    def on_closing():
        if app.is_running:
            app.stop_test()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
