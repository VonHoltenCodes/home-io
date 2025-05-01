#!/usr/bin/env python3
"""
Test script for Teensy API
Run this script to test the Teensy API endpoints and data handling
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Test Teensy API endpoints')
    parser.add_argument('--host', default='http://localhost:5000', help='API host URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    base_url = args.host
    verbose = args.verbose

    print(f"Testing Teensy API endpoints on {base_url}")
    
    # Test 1: Discover available Teensy devices
    print("\n[TEST 1] Discovering Teensy devices...")
    try:
        response = requests.get(f"{base_url}/api/teensy/discover")
        if response.status_code == 200:
            ports = response.json()
            print(f"✅ Found {len(ports)} ports:")
            for port in ports:
                print(f"  - {port['port']}: {port.get('description', 'Unknown')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Get all Teensy devices
    print("\n[TEST 2] Retrieving all Teensy devices...")
    try:
        response = requests.get(f"{base_url}/api/teensy")
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Found {len(devices)} devices:")
            for device in devices:
                # Validate device structure
                has_valid_state = isinstance(device.get('state'), dict)
                has_valid_config = isinstance(device.get('config'), dict) and isinstance(device.get('config', {}).get('teensy_config'), dict)
                
                print(f"  - {device.get('name', 'Unknown')} (ID: {device.get('id', 'No ID')})")
                print(f"    Online: {device.get('state', {}).get('online', False)}")
                print(f"    Port: {device.get('config', {}).get('teensy_config', {}).get('port', 'Unknown')}")
                
                if verbose:
                    print(f"    Valid state object: {has_valid_state}")
                    print(f"    Valid config object: {has_valid_config}")
                    properties = device.get('state', {}).get('properties', {})
                    if properties:
                        print(f"    Readings: {json.dumps(properties)}")
                
                if not has_valid_state or not has_valid_config:
                    print(f"❌ Warning: Device has invalid data structure:")
                    if not has_valid_state:
                        print(f"    - Invalid state field: {device.get('state')}")
                    if not has_valid_config:
                        print(f"    - Invalid config field: {device.get('config')}")
                        
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # If no devices found, offer to create a test device
    if 'devices' in locals() and not devices:
        print("\nNo devices found. Would you like to register a test device? (y/n)")
        if input().lower() == 'y':
            # Test 3: Register a new Teensy device
            print("\n[TEST 3] Registering a new Teensy device...")
            device_id = register_test_device(base_url)
            if device_id:
                # Test the newly created device
                test_device_commands(base_url, device_id, verbose)
        else:
            print("Skipping device registration.")
    elif 'devices' in locals() and devices:
        # Test commands on the first device
        print("\nWould you like to test commands on the first device? (y/n)")
        if input().lower() == 'y':
            test_device_commands(base_url, devices[0]['id'], verbose)
        else:
            print("Skipping command testing.")
    
    print("\nTest completed.")

def register_test_device(base_url):
    """Register a test Teensy device"""
    try:
        # First get available ports
        response = requests.get(f"{base_url}/api/teensy/discover")
        ports = response.json() if response.status_code == 200 else []
        
        # Create device payload
        port = ports[0]['port'] if ports else "/dev/ttyACM0"
        
        device_data = {
            "name": f"Test Teensy {datetime.now().strftime('%H:%M:%S')}",
            "type": "environmental_sensor",
            "protocol": "teensy",
            "location": "Test Location",
            "manufacturer": "PJRC",
            "model": "Teensy 4.0",
            "teensy_config": {
                "port": port,
                "baud_rate": 115200,
                "timeout": 1.0,
                "mqtt_topic": "home_io/test/teensy",
                "reading_interval": 30,
                "interface_type": "serial",
                "board_type": "teensy_4.0"
            }
        }
        
        # Register the device
        response = requests.post(
            f"{base_url}/api/teensy",
            headers={"Content-Type": "application/json"},
            data=json.dumps(device_data)
        )
        
        if response.status_code == 200:
            device = response.json()
            print(f"✅ Device registered successfully:")
            print(f"  - Name: {device.get('name')}")
            print(f"  - ID: {device.get('id')}")
            print(f"  - Port: {device.get('config', {}).get('teensy_config', {}).get('port')}")
            return device.get('id')
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_device_commands(base_url, device_id, verbose):
    """Test various commands on a device"""
    print(f"\n[TEST] Testing commands on device {device_id}")
    
    # Test 1: Get device details
    print("\n[TEST] Retrieving device details...")
    try:
        response = requests.get(f"{base_url}/api/teensy/{device_id}")
        if response.status_code == 200:
            device = response.json()
            print(f"✅ Device retrieved: {device.get('name')}")
            
            if verbose:
                print(json.dumps(device, indent=2))
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Send GET_SENSOR_DATA command
    print("\n[TEST] Sending GET_SENSOR_DATA command...")
    try:
        response = requests.post(
            f"{base_url}/api/teensy/{device_id}/command",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "command": "GET_SENSOR_DATA",
                "params": {}
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Command sent successfully:")
            print(f"  - Status: {result.get('status')}")
            print(f"  - Timestamp: {result.get('timestamp')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Send IDENTIFY command
    print("\n[TEST] Sending IDENTIFY command...")
    try:
        response = requests.post(
            f"{base_url}/api/teensy/{device_id}/command",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "command": "IDENTIFY",
                "params": {}
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Command sent successfully:")
            print(f"  - Status: {result.get('status')}")
            print(f"  - Timestamp: {result.get('timestamp')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Wait a bit and fetch the device again to see updated state
    print("\nWaiting 2 seconds for state to update...")
    time.sleep(2)
    
    print("\n[TEST] Checking updated device state...")
    try:
        response = requests.get(f"{base_url}/api/teensy/{device_id}")
        if response.status_code == 200:
            device = response.json()
            print(f"✅ Updated device state:")
            print(f"  - Online: {device.get('state', {}).get('online', False)}")
            print(f"  - Last seen: {device.get('state', {}).get('last_seen', 'Unknown')}")
            
            properties = device.get('state', {}).get('properties', {})
            if properties:
                print("  - Latest readings:")
                for key, value in properties.items():
                    if key not in ['last_command', 'timestamp']:
                        print(f"    - {key}: {value}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()