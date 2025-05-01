#!/usr/bin/env python3
"""
Direct test script for Teensy BME280 sensor
This script attempts to communicate directly with the Teensy device
"""

import serial
import time
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Test communication with Teensy BME280 sensor')
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate')
    parser.add_argument('--timeout', type=float, default=2.0, help='Serial timeout in seconds')
    parser.add_argument('--command', default='GET_SENSOR_DATA', help='Command to send')
    args = parser.parse_args()
    
    print(f"Opening serial port {args.port} at {args.baud} baud...")
    try:
        # Open serial connection
        ser = serial.Serial(
            port=args.port, 
            baudrate=args.baud,
            timeout=args.timeout
        )
        
        # Allow Teensy to reset if needed
        time.sleep(2)
        
        # Flush any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send the command
        command = f"{args.command}\n"
        print(f"Sending command: {command.strip()}")
        ser.write(command.encode())
        
        # Read response
        print("Reading response...")
        start_time = time.time()
        responses = []
        
        # Try to read multiple lines for up to timeout seconds
        while time.time() - start_time < args.timeout:
            if ser.in_waiting > 0:
                line = ser.readline().strip().decode('utf-8')
                if line:
                    responses.append(line)
                    print(f"Received: {line}")
            time.sleep(0.1)
        
        # If no response, try direct read
        if not responses:
            print("No line-based response, trying direct read...")
            raw_data = ser.read(1024)
            if raw_data:
                try:
                    # Try to decode as UTF-8
                    decoded = raw_data.decode('utf-8')
                    print(f"Raw data: {decoded}")
                    responses.append(decoded)
                except UnicodeDecodeError:
                    # If not UTF-8, show as hex
                    print(f"Raw hex data: {raw_data.hex()}")
        
        # Parse JSON responses
        for response in responses:
            try:
                data = json.loads(response)
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Not valid JSON: {response}")
        
        # Close serial connection
        ser.close()
        print("Serial port closed")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())