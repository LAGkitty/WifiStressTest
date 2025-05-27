# WiFi Stress Test Tool

**FOR EXPERIMENTING PURPOSES ONLY**

A Python-based network performance testing tool with an intuitive GUI interface designed for stress testing WiFi connections and network infrastructure. This tool helps network administrators, developers, and enthusiasts analyze network performance under various load conditions.

## Features

- **User-Friendly GUI**: Clean, intuitive interface built with tkinter
- **Configurable Test Parameters**: Adjust intensity, concurrent connections, and request delays
- **Real-Time Statistics**: Live monitoring of request rates, errors, and performance metrics
- **Multi-Threaded Testing**: Concurrent connection testing with customizable thread counts
- **Visual Status Indicators**: Color-coded status indicators for test state monitoring
- **Safe Testing Endpoints**: Uses public testing APIs that can handle traffic loads

## Screenshots

The application features:
- Intensity slider (10-100%) for controlling test aggression
- Configurable concurrent connections (1-50 threads)
- Adjustable request delays (10-1000ms)
- Real-time statistics display with timestamps
- Start/Stop controls with visual status indicators

## Installation

### Prerequisites

- Python 3.6 or higher
- Internet connection for network testing

### Required Dependencies

Install the required Python packages using pip:

```bash
pip install requests
```

The tool also uses the following built-in Python modules:
- `tkinter` (usually included with Python)
- `threading`
- `socket`
- `time`
- `concurrent.futures`
- `urllib.parse`
- `random`

### Quick Setup

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install requests
   ```
3. Run the application:
   ```bash
   python WifiStressTest.py
   ```

## Usage

### Basic Operation

1. **Launch the Application**:
   ```bash
   python WifiStressTest.py
   ```

2. **Configure Test Parameters**:
   - **Test Intensity**: Use the slider to set intensity from 10% to 100%
   - **Concurrent Connections**: Set the number of simultaneous connections (1-50)
   - **Request Delay**: Configure delay between requests in milliseconds (10-1000ms)

3. **Start Testing**:
   - Click "Start Test" to begin the stress test
   - Monitor real-time statistics in the bottom panel
   - Observe the status indicator (Green = Running, Orange = Stopping, Gray = Idle)

4. **Stop Testing**:
   - Click "Stop Test" to gracefully terminate the test
   - Review final statistics and performance metrics

### Test Configuration Options

| Parameter | Range | Description |
|-----------|-------|-------------|
| Intensity | 10-100% | Controls overall test aggression and resource usage |
| Concurrent Connections | 1-50 | Number of simultaneous network connections |
| Request Delay | 10-1000ms | Delay between individual requests |

### Understanding the Statistics

The statistics panel displays:
- **Request Count**: Total number of HTTP requests sent
- **Error Count**: Number of failed requests
- **Request Rate**: Requests per second (req/s)
- **Elapsed Time**: Total test duration
- **Timestamps**: All events are timestamped for analysis

## Test Endpoints

The tool uses the following safe, public testing endpoints:

- `httpbin.org/bytes/1024` - Downloads 1KB of data
- `httpbin.org/delay/0.1` - Introduces minimal server delay
- `jsonplaceholder.typicode.com/posts` - JSON API endpoint
- `httpbin.org/stream/10` - Streaming data endpoint

These endpoints are specifically designed to handle testing traffic and provide consistent responses.

## Technical Details

### Architecture

- **GUI Framework**: tkinter for cross-platform compatibility
- **HTTP Client**: requests library for reliable HTTP operations
- **Concurrency**: ThreadPoolExecutor for efficient multi-threading
- **Thread Safety**: Proper event synchronization and UI updates

### Performance Considerations

- Thread count automatically adjusts based on intensity settings
- Request delays scale inversely with intensity (higher intensity = shorter delays)
- Memory-efficient session reuse for HTTP connections
- Graceful shutdown handling to prevent resource leaks

## Safety and Responsible Use

⚠️ **Important Guidelines**:

- This tool is designed FOR EXPERIMENTING purposes only
- Use only on networks you own or have explicit permission to test
- Do not use against production systems without proper authorization
- Be mindful of bandwidth usage and network impact
- Respect rate limits and terms of service of target endpoints

## Troubleshooting

### Common Issues

**Missing requests module**:
```bash
pip install requests
```

**GUI not displaying properly**:
- Ensure tkinter is installed (usually comes with Python)
- On Linux: `sudo apt-get install python3-tk`

**Network connectivity issues**:
- Verify internet connection
- Check firewall settings
- Ensure target endpoints are accessible

### Error Handling

The application includes comprehensive error handling for:
- Network timeouts and connection failures
- Invalid configuration parameters
- Thread synchronization issues
- GUI update conflicts

## Contributing

This is an experimental tool designed for learning and testing purposes. Feel free to:
- Report bugs and issues
- Suggest new features or improvements
- Submit pull requests with enhancements
- Share testing results and use cases

## License

This project is provided as-is for educational and experimental purposes. Users are responsible for ensuring compliance with applicable laws and network policies.

## Disclaimer

This tool is intended for legitimate network testing and educational purposes only. Users must ensure they have proper authorization before testing any network infrastructure. The developers are not responsible for any misuse or damage caused by this tool.
