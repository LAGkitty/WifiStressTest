#!/usr/bin/env python3
"""
WiFi Stress Test Tool - Command Line Version
A network performance testing tool for mobile/terminal use
"""

import threading
import socket
import time
import requests
import concurrent.futures
from urllib.parse import urlparse
import random
import argparse
import signal
import sys
from datetime import datetime

class WiFiStressTester:
    def __init__(self):
        # Test state variables
        self.is_running = False
        self.stop_event = threading.Event()
        self.stats_lock = threading.Lock()
        
        # Statistics
        self.request_count = 0
        self.error_count = 0
        self.start_time = None
        self.response_times = []
        self.connection_times = []
        
        # Test targets (public endpoints that can handle traffic)
        self.test_urls = [
            "http://httpbin.org/bytes/1024",
            "http://httpbin.org/delay/0.1", 
            "https://jsonplaceholder.typicode.com/posts",
            "http://httpbin.org/stream/10",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid"
        ]
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping test...")
        self.stop_test()
        
    def print_banner(self):
        """Print application banner"""
        print("=" * 50)
        print("📶 WiFi Stress Test Tool - CLI Version")
        print("=" * 50)
        print()
        
    def print_status(self, message):
        """Print status with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def start_test(self, intensity=50, threads=10, delay=100, duration=None):
        """Start the stress test"""
        self.is_running = True
        self.stop_event.clear()
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.response_times = []
        self.connection_times = []
        
        # Adjust parameters based on intensity
        actual_threads = max(1, int(threads * (intensity / 100)))
        actual_delay = (delay / 1000.0) * (100 / intensity)  # Higher intensity = less delay
        
        self.print_status("🚀 Starting stress test...")
        self.print_status(f"📊 Configuration:")
        print(f"   • Intensity: {intensity}%")
        print(f"   • Threads: {actual_threads}")
        print(f"   • Delay: {actual_delay:.3f}s")
        print(f"   • Duration: {'Unlimited' if not duration else f'{duration}s'}")
        print(f"   • Target URLs: {len(self.test_urls)}")
        print()
        
        # Start statistics display thread
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()
        
        # Start duration timer if specified
        if duration:
            timer_thread = threading.Thread(target=self.duration_timer, args=(duration,), daemon=True)
            timer_thread.start()
        
        # Run the actual stress test
        self.run_stress_test(actual_threads, actual_delay)
        
    def duration_timer(self, duration):
        """Stop test after specified duration"""
        time.sleep(duration)
        if self.is_running:
            self.print_status(f"⏰ Duration limit ({duration}s) reached")
            self.stop_test()
    
    def stop_test(self):
        """Stop the stress test"""
        self.is_running = False
        self.stop_event.set()
        
    def run_stress_test(self, thread_count, delay):
        """Main stress test function"""
        
        def make_requests():
            session = requests.Session()
            
            while not self.stop_event.is_set():
                try:
                    # Choose random test URL
                    url = random.choice(self.test_urls)
                    
                    # Measure connection time
                    start_time = time.time()
                    
                    # Make request with timeout
                    response = session.get(url, timeout=5)
                    
                    # Calculate response time
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    with self.stats_lock:
                        self.request_count += 1
                        self.response_times.append(response_time)
                        # Keep only last 100 response times for memory efficiency
                        if len(self.response_times) > 100:
                            self.response_times.pop(0)
                    
                except requests.exceptions.RequestException as e:
                    with self.stats_lock:
                        self.error_count += 1
                        
                except Exception as e:
                    with self.stats_lock:
                        self.error_count += 1
                    
                if not self.stop_event.is_set():
                    time.sleep(delay)
        
        # Start worker threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(make_requests) for _ in range(thread_count)]
            
            # Wait for stop signal
            while not self.stop_event.is_set():
                time.sleep(0.1)
            
            # Shutdown executor
            executor.shutdown(wait=False)
        
        # Final statistics
        self.print_final_stats()
    
    def display_stats(self):
        """Display live statistics"""
        last_request_count = 0
        
        while self.is_running:
            time.sleep(2)  # Update every 2 seconds
            
            if not self.is_running:
                break
                
            with self.stats_lock:
                current_requests = self.request_count
                current_errors = self.error_count
                avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
                min_response_time = min(self.response_times) if self.response_times else 0
                max_response_time = max(self.response_times) if self.response_times else 0
            
            elapsed = time.time() - self.start_time
            
            if elapsed > 0:
                overall_rate = current_requests / elapsed
                recent_rate = (current_requests - last_request_count) / 2.0  # Rate in last 2 seconds
                
                # Clear line and print stats
                print(f"\r📈 Req: {current_requests:>6} | Err: {current_errors:>4} | "
                      f"Rate: {overall_rate:>5.1f}/s | Recent: {recent_rate:>5.1f}/s | "
                      f"Avg: {avg_response_time:>6.0f}ms | Min: {min_response_time:>6.0f}ms | "
                      f"Max: {max_response_time:>6.0f}ms | Time: {elapsed:>6.1f}s", end="", flush=True)
                
                last_request_count = current_requests
    
    def print_final_stats(self):
        """Print final test statistics"""
        print("\n")  # New line after live stats
        print("=" * 70)
        print("📊 Test Results")
        print("=" * 70)
        
        elapsed = time.time() - self.start_time
        success_rate = ((self.request_count - self.error_count) / self.request_count * 100) if self.request_count > 0 else 0
        
        # Response time statistics
        if self.response_times:
            avg_response = sum(self.response_times) / len(self.response_times)
            min_response = min(self.response_times)
            max_response = max(self.response_times)
            # Calculate median
            sorted_times = sorted(self.response_times)
            n = len(sorted_times)
            median_response = sorted_times[n//2] if n % 2 == 1 else (sorted_times[n//2-1] + sorted_times[n//2]) / 2
        else:
            avg_response = min_response = max_response = median_response = 0
        
        print(f"Total Requests:      {self.request_count}")
        print(f"Successful:          {self.request_count - self.error_count}")
        print(f"Errors:              {self.error_count}")
        print(f"Success Rate:        {success_rate:.1f}%")
        print(f"Duration:            {elapsed:.1f} seconds")
        print(f"Average Rate:        {self.request_count / elapsed:.1f} requests/second" if elapsed > 0 else "N/A")
        print()
        print("📡 Response Time Statistics:")
        print(f"Average:             {avg_response:.0f} ms")
        print(f"Median:              {median_response:.0f} ms")
        print(f"Minimum:             {min_response:.0f} ms")
        print(f"Maximum:             {max_response:.0f} ms")
        print()

def get_user_input():
    """Get test configuration from user interactively"""
    print("🔧 Configure your WiFi stress test:")
    print()
    
    # Test intensity
    while True:
        try:
            print("📊 Test Intensity:")
            print("   • Light (30%) - Gentle testing")
            print("   • Medium (50%) - Balanced testing")  
            print("   • High (80%) - Aggressive testing")
            print("   • Custom - Enter your own value")
            
            choice = input("\nChoose intensity [L/m/h/c]: ").lower().strip()
            
            if choice in ['l', 'light', '']:
                intensity = 30
                break
            elif choice in ['m', 'medium']:
                intensity = 50
                break
            elif choice in ['h', 'high']:
                intensity = 80
                break
            elif choice in ['c', 'custom']:
                intensity = int(input("Enter intensity (e.g., 10-100, or higher): "))
                if intensity > 0:
                    break
                else:
                    print("❌ Please enter a positive value")
            else:
                print("❌ Please choose L, M, H, or C")
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input, please try again")
            
    print()
    
    # Number of threads
    while True:
        try:
            print("🧵 Concurrent Connections:")
            print("   • Few (5) - Low resource usage")
            print("   • Normal (10) - Balanced")
            print("   • Many (20) - High throughput")
            print("   • Custom - Enter your own value")
            
            choice = input("\nChoose thread count [f/N/m/c]: ").lower().strip()
            
            if choice in ['f', 'few']:
                threads = 5
                break
            elif choice in ['n', 'normal', '']:
                threads = 10
                break
            elif choice in ['m', 'many']:
                threads = 20
                break
            elif choice in ['c', 'custom']:
                threads = int(input("Enter thread count (e.g., 1-1000, or higher): "))
                if threads > 0:
                    break
                else:
                    print("❌ Please enter a positive value")
            else:
                print("❌ Please choose F, N, M, or C")
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input, please try again")
            
    print()
    
    # Test duration
    while True:
        try:
            print("⏱️  Test Duration:")
            print("   • Quick (30s) - Fast test")
            print("   • Standard (60s) - Normal test")
            print("   • Long (120s) - Extended test")
            print("   • Unlimited - Run until manually stopped")
            print("   • Custom - Enter your own time")
            
            choice = input("\nChoose duration [q/S/l/u/c]: ").lower().strip()
            
            if choice in ['q', 'quick']:
                duration = 30
                break
            elif choice in ['s', 'standard', '']:
                duration = 60
                break
            elif choice in ['l', 'long']:
                duration = 120
                break
            elif choice in ['u', 'unlimited']:
                duration = None
                break
            elif choice in ['c', 'custom']:
                duration = int(input("Enter duration in seconds (e.g., 30-300, or 0 for unlimited): "))
                if duration == 0:
                    duration = None
                elif duration > 0:
                    break
                else:
                    print("❌ Please enter a positive number or 0")
            else:
                print("❌ Please choose Q, S, L, U, or C")
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Invalid input, please try again")
            
    print()
    
    # Request delay (auto-calculated based on intensity, but allow override)
    delay = 100  # Default delay
    
    advanced = input("🔧 Configure advanced settings? [y/N]: ").lower().strip()
    if advanced in ['y', 'yes']:
        while True:
            try:
                delay = int(input(f"Request delay in ms (e.g., 1-1000, current: {delay}): ") or delay)
                if delay > 0:
                    break
                else:
                    print("❌ Please enter a positive value")
            except ValueError:
                print("❌ Invalid input, please try again")
    
    return intensity, threads, delay, duration

def main():
    parser = argparse.ArgumentParser(
        description="WiFi Stress Test Tool - Test your network performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode (default)
  %(prog)s -i 80 -t 20             # Command line mode: High intensity with 20 threads
  %(prog)s --list-urls             # List test URLs and exit
  
Use --help to see all command line options, or run without arguments for interactive setup.
        """
    )
    
    parser.add_argument('-i', '--intensity', type=int,
                       help='Test intensity percentage (any positive value)')
    parser.add_argument('-t', '--threads', type=int,
                       help='Number of concurrent threads (any positive value)') 
    parser.add_argument('-D', '--delay', type=int, default=100,
                       help='Base delay between requests in ms (any positive value, default: 100)')
    parser.add_argument('-d', '--duration', type=int,
                       help='Test duration in seconds (any positive value)')
    parser.add_argument('--list-urls', action='store_true',
                       help='List test URLs and exit')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Skip interactive setup (use defaults or provided args)')
    
    args = parser.parse_args()
    
    # Check for required modules
    try:
        import requests
    except ImportError:
        print("❌ Error: This tool requires the 'requests' module.")
        print("📦 Install it with: pip install requests")
        sys.exit(1)
    
    # Create tester instance
    tester = WiFiStressTester()
    
    # Handle --list-urls
    if args.list_urls:
        print("📋 Test URLs:")
        for i, url in enumerate(tester.test_urls, 1):
            print(f"  {i}. {url}")
        sys.exit(0)
    
    # Print banner
    tester.print_banner()
    
    # Determine configuration method
    if args.non_interactive or (args.intensity and args.threads):
        # Command line mode
        intensity = args.intensity or 50
        threads = args.threads or 10
        delay = args.delay
        duration = args.duration
        
        # Validate command line arguments
        if intensity < 10 or intensity > 100:
            print("❌ Error: Intensity must be between 10 and 100")
            sys.exit(1)
        if threads < 1:
            print("❌ Error: Thread count must be 1 or higher")
            sys.exit(1)
        if delay < 10 or delay > 1000:
            print("❌ Error: Delay must be between 10 and 1000 ms")
            sys.exit(1)
            
    else:
        # Interactive mode
        try:
            intensity, threads, delay, duration = get_user_input()
        except KeyboardInterrupt:
            print("\n\n👋 Setup cancelled. Goodbye!")
            sys.exit(0)
    
    # Show configuration summary
    print("📋 Test Configuration:")
    print(f"   • Intensity: {intensity}%")
    print(f"   • Threads: {threads}")
    print(f"   • Delay: {delay}ms")
    print(f"   • Duration: {'Unlimited' if not duration else f'{duration}s'}")
    print()
    
    # Show warning for extreme settings
    if intensity > 500 or threads > 100 or delay < 10:
        print("⚠️  WARNING: Extreme settings detected!")
        print("⚠️  This may cause high CPU usage, network congestion, or system instability")
        print("⚠️  Use responsibly and ensure you have permission to test this network")
        
        if not args.non_interactive:
            confirm = input("\nContinue with extreme settings? [y/N]: ").lower().strip()
            if confirm not in ['y', 'yes']:
                print("👋 Test cancelled for safety. Goodbye!")
                sys.exit(0)
        print()
    
    print("💡 Press Ctrl+C to stop the test at any time")
    
    # Give user a moment to read
    if not args.non_interactive:
        input("Press Enter to start the test...")
    
    print()
    
    try:
        # Start the test
        tester.start_test(
            intensity=intensity,
            threads=threads, 
            delay=delay,
            duration=duration
        )
        
    except KeyboardInterrupt:
        pass  # Handled by signal handler
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    main()
