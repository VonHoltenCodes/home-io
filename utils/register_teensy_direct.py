#!/usr/bin/env python3
"""
Direct registration of Teensy device to Home-IO system
This script bypasses the web UI and API to directly register a device
"""

import serial
import time
import json
import uuid
import os
import sys
import sqlite3
from datetime import datetime

# Path to database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/home_io.db")

def test_serial_connection(port="/dev/ttyACM0", baud_rate=115200, timeout=2.0):
    """Test serial connection to Teensy"""
    print(f"Testing connection to {port} at {baud_rate} baud...")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=port, 
            baudrate=baud_rate,
            timeout=timeout
        )
        
        # Allow Teensy to reset if needed
        time.sleep(2)
        
        # Flush any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send command to get data
        command = "GET_SENSOR_DATA\n"
        print(f"Sending command: {command.strip()}")
        ser.write(command.encode())
        
        # Read response
        print("Reading response...")
        responses = []
        
        # Try to read multiple lines for up to timeout seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                line = ser.readline().strip().decode('utf-8')
                if line:
                    responses.append(line)
                    print(f"Received: {line}")
            time.sleep(0.1)
        
        # Close connection
        ser.close()
        
        if responses:
            # Check if we got valid JSON data
            for response in responses:
                try:
                    data = json.loads(response)
                    if "temperature" in data and "humidity" in data and "pressure" in data:
                        print("✅ Serial communication successful!")
                        print(f"Temperature: {data['temperature']}°C")
                        print(f"Humidity: {data['humidity']}%")
                        print(f"Pressure: {data['pressure']} hPa")
                        return True, data
                except json.JSONDecodeError:
                    continue
            
            print("⚠️ Received data but not in expected format")
            return False, None
        else:
            print("❌ No response from device")
            return False, None
    
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False, None

def register_device_in_db(db_path, device_info):
    """Register a device directly in the database"""
    print(f"Registering device in database at {db_path}...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Generate device ID
        device_id = f"teensy_{uuid.uuid4().hex[:8]}"
        
        # Create state, capabilities, and config as JSON strings
        state = json.dumps({
            "online": True,
            "last_seen": datetime.now().isoformat(),
            "properties": device_info.get("sensor_data", {})
        })
        
        capabilities = json.dumps(["read", "write", "usb_serial", "hid"])
        
        config = json.dumps({
            "teensy_config": {
                "port": device_info["port"],
                "baud_rate": device_info["baud_rate"],
                "timeout": device_info.get("timeout", 1.0),
                "mqtt_topic": f"home_io/sensors/{device_info['location'].lower().replace(' ', '_')}",
                "reading_interval": device_info.get("reading_interval", 60),
                "interface_type": "serial",
                "board_type": device_info.get("board_type", "teensy_4.0")
            }
        })
        
        # Get current timestamp
        now = datetime.now().isoformat()
        
        # Insert device into database
        cursor.execute('''
        INSERT INTO devices (
            id, name, type, protocol, location, manufacturer, model,
            firmware_version, state, capabilities, config, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_id,
            device_info["name"],
            device_info["type"],
            "teensy",
            device_info["location"],
            device_info.get("manufacturer", "PJRC"),
            device_info.get("model", "Teensy 4.0"),
            None,  # firmware_version
            state,
            capabilities,
            config,
            now,
            now
        ))
        
        # Commit changes
        conn.commit()
        
        # Close connection
        conn.close()
        
        print(f"✅ Device registered successfully with ID: {device_id}")
        return True, device_id
    
    except Exception as e:
        print(f"❌ Error registering device: {e}")
        return False, None

def main():
    # Get device information
    port = input("Enter serial port (default: /dev/ttyACM0): ") or "/dev/ttyACM0"
    baud_rate = int(input("Enter baud rate (default: 115200): ") or "115200")
    name = input("Enter device name (default: Teensy BME280 Sensor): ") or "Teensy BME280 Sensor"
    location = input("Enter device location (default: Office): ") or "Office"
    
    # Test connection
    success, sensor_data = test_serial_connection(port, baud_rate)
    
    if not success:
        print("Failed to communicate with the device. Registration aborted.")
        return 1
    
    # Prepare device info
    device_info = {
        "name": name,
        "type": "environmental_sensor",
        "location": location,
        "manufacturer": "PJRC",
        "model": "Teensy 4.0",
        "port": port,
        "baud_rate": baud_rate,
        "reading_interval": 30,
        "board_type": "teensy_4.0",
        "sensor_data": sensor_data
    }
    
    # Register in database
    db_success, device_id = register_device_in_db(DB_PATH, device_info)
    
    if db_success:
        print("\n===== DEVICE REGISTRATION SUCCESSFUL =====")
        print(f"Device ID: {device_id}")
        print(f"Name: {name}")
        print(f"Location: {location}")
        print(f"Port: {port}")
        print(f"Data: {json.dumps(sensor_data, indent=2)}")
        print("\nYou should now see this device in the Home-IO interface.\n")
        
        return 0
    else:
        print("Failed to register device in database.")
        return 1

if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at {DB_PATH}")
        print("Make sure the Home-IO system is initialized before running this script.")
        sys.exit(1)
    
    sys.exit(main())