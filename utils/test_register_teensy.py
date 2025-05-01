#!/usr/bin/env python3
"""
Test script to register a Teensy device using the API directly
"""

import requests
import json
import sys
import time

def register_teensy_device(api_base_url="http://localhost:8000"):
    """Register a new Teensy device with the API"""
    
    # Device configuration
    device_config = {
        "name": "Teensy BME280 Sensor",
        "type": "environmental_sensor",
        "protocol": "teensy",
        "location": "Office",
        "manufacturer": "PJRC",
        "model": "Teensy 4.0",
        "teensy_config": {
            "port": "/dev/ttyACM0",
            "baud_rate": 115200,
            "timeout": 1.0,
            "mqtt_topic": "home_io/sensors/office",
            "reading_interval": 30,
            "interface_type": "serial",
            "board_type": "teensy_4.0"
        }
    }
    
    try:
        # Make API request
        print(f"Sending registration request to {api_base_url}/api/teensy")
        response = requests.post(
            f"{api_base_url}/api/teensy",
            headers={"Content-Type": "application/json"},
            data=json.dumps(device_config)
        )
        
        # Check response
        if response.status_code == 200:
            print("Device registered successfully!")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Get API base URL from command line if provided
    api_base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    register_teensy_device(api_base_url)