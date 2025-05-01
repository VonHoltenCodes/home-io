#!/usr/bin/env python3
"""
Teensy Communication Test Script
This script tests direct communication with a Teensy board running the BME280 sketch.
"""

import json
import time
import argparse
import sys
import os

# Import serial module
try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("Error: pyserial module not found.")
    print("Please install it with: sudo apt-get install python3-serial")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Test communication with Teensy board')
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--timeout', type=float, default=1.0, help='Serial timeout in seconds (default: 1.0)')
    parser.add_argument('--command', default='GET_SENSOR_DATA', help='Command to send (default: GET_SENSOR_DATA)')
    args = parser.parse_args()

    # Check if port exists
    if not os.path.exists(args.port):
        print(f"Error: Port {args.port} does not exist")
        print("Available ports:")
        try:
            for port in list_ports.comports():
                print(f"  {port.device} - {port.description if hasattr(port, 'description') else 'Unknown'}")
        except Exception as e:
            print(f"  Error listing ports: {e}")
        return 1

    print(f"Connecting to Teensy on {args.port} at {args.baud} baud...")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            timeout=args.timeout
        )
        
        # Wait for connection to establish
        time.sleep(2)
        
        # Discard any data in the input buffer
        ser.reset_input_buffer()
        
        # Send command
        print(f"Sending command: {args.command}")
        ser.write(f"{args.command}\n".encode('utf-8'))
        
        # Read response
        start_time = time.time()
        response = ''
        
        # Wait for response with timeout
        while time.time() - start_time < 5:  # 5 second timeout
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    response = line
                    break
            time.sleep(0.1)
        
        if response:
            print("Raw response:")
            print(response)
            
            try:
                # Try to parse as JSON
                data = json.loads(response)
                print("\nParsed data:")
                print(json.dumps(data, indent=2))
                
                # Check for specific sensor data
                if 'temperature' in data:
                    print(f"\nTemperature: {data['temperature']}°C")
                if 'humidity' in data:
                    print(f"Humidity: {data['humidity']}%")
                if 'pressure' in data:
                    print(f"Pressure: {data['pressure']} hPa")
                
            except json.JSONDecodeError as e:
                print(f"\nWarning: Response is not valid JSON: {e}")
        else:
            print("No response received")
        
        # Close serial connection
        ser.close()
        print("\nConnection closed")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    
    return 0

if __name__ == "__main__":
    sys.exit(main())