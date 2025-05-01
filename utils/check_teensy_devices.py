#!/usr/bin/env python3
"""
Check Teensy devices registered in the database
"""

import sqlite3
import json
import os
import sys

# Path to database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/home_io.db")

def check_devices():
    """Check Teensy devices in the database"""
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query for Teensy devices
        cursor.execute("SELECT * FROM devices WHERE protocol = 'teensy'")
        devices = cursor.fetchall()
        
        if not devices:
            print("No Teensy devices found in the database.")
            return
        
        print(f"Found {len(devices)} Teensy device(s):")
        print("=" * 50)
        
        for device in devices:
            device_dict = dict(device)
            
            # Parse JSON fields
            state = json.loads(device_dict.get('state', '{}'))
            config = json.loads(device_dict.get('config', '{}'))
            capabilities = json.loads(device_dict.get('capabilities', '[]'))
            
            print(f"ID: {device_dict.get('id')}")
            print(f"Name: {device_dict.get('name')}")
            print(f"Type: {device_dict.get('type')}")
            print(f"Location: {device_dict.get('location')}")
            print(f"Port: {config.get('teensy_config', {}).get('port')}")
            
            # Print properties if available
            if 'properties' in state:
                print("Latest readings:")
                for key, value in state.get('properties', {}).items():
                    if key != 'timestamp' and key != 'status':
                        print(f"  - {key}: {value}")
            
            print("=" * 50)
            
        # Close connection
        conn.close()
    
    except Exception as e:
        print(f"Error checking devices: {e}")

if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        sys.exit(1)
    
    check_devices()