#!/usr/bin/env python3
"""
Test script to check Teensy device via the API
"""

import requests
import json
import sys

def get_teensy_devices(api_base_url="http://localhost:8000"):
    """Get all Teensy devices via API"""
    
    try:
        # Make API request
        print(f"Fetching Teensy devices from {api_base_url}/api/teensy/")
        response = requests.get(f"{api_base_url}/api/teensy/")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
        # Parse response
        devices = response.json()
        
        if devices:
            print(f"Found {len(devices)} device(s):")
            for device in devices:
                print(f"ID: {device.get('id')}")
                print(f"Name: {device.get('name')}")
                print(f"Type: {device.get('type')}")
                print(f"Location: {device.get('location')}")
                
                # Print properties if available
                if 'state' in device and 'properties' in device['state']:
                    print("Latest readings:")
                    for key, value in device['state'].get('properties', {}).items():
                        if key != 'timestamp' and key != 'status':
                            print(f"  - {key}: {value}")
                
                print("-" * 50)
        else:
            print("No devices found")
        
        return devices
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_available_ports(api_base_url="http://localhost:8000"):
    """Get available Teensy ports via API"""
    
    try:
        # Make API request
        print(f"Fetching available ports from {api_base_url}/api/teensy/discover")
        response = requests.get(f"{api_base_url}/api/teensy/discover")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
        # Parse response
        ports = response.json()
        
        if ports:
            print(f"Found {len(ports)} port(s):")
            for port in ports:
                print(f"Port: {port.get('port')}")
                print(f"Description: {port.get('description')}")
                print(f"Board Type: {port.get('board_type')}")
                print("-" * 50)
        else:
            print("No ports found")
        
        return ports
    
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Get API base URL from command line if provided
    api_base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("======= TEENSY DEVICES =======")
    get_teensy_devices(api_base_url)
    
    print("\n======= AVAILABLE PORTS =======")
    get_available_ports(api_base_url)