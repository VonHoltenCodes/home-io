from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import uuid
import logging
from datetime import datetime

from api.models.device import (
    Device, 
    DeviceType, 
    DeviceProtocol, 
    DeviceState,
    TeensyDeviceConfig,
    TeensyDeviceRegistration
)
from core.db_manager import DatabaseManager
from core.config_manager import ConfigManager

# Set up logging
logger = logging.getLogger("home-io.teensy")

# Create router
router = APIRouter()

# Get database and config instances
db = DatabaseManager("data/home_io.db")
config = ConfigManager()

@router.get("/", response_model=List[Device])
async def get_teensy_devices():
    """Get all Teensy devices"""
    try:
        # Query the database for teensy devices
        logger.info("Querying database for Teensy devices")
        devices = db.query("SELECT * FROM devices WHERE protocol = 'teensy'")
        logger.info(f"Found {len(devices)} Teensy devices in database")
        
        # If no devices found in db but we have a Teensy registered via direct method
        if not devices:
            import os
            import sqlite3
            import json
            
            # Check database file directly as a backup
            db_path = "data/home_io.db"
            if os.path.exists(db_path):
                try:
                    logger.info(f"Checking database file directly at {db_path}")
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM devices WHERE protocol = 'teensy'")
                    rows = cursor.fetchall()
                    
                    if rows:
                        logger.info(f"Found {len(rows)} Teensy devices via direct DB access")
                        devices = []
                        for row in rows:
                            device = dict(row)
                            
                            # Parse JSON fields
                            for field in ['state', 'capabilities', 'config']:
                                if field in device and isinstance(device[field], str):
                                    try:
                                        device[field] = json.loads(device[field])
                                    except (json.JSONDecodeError, TypeError):
                                        # Initialize with default values if JSON parsing fails
                                        if field == 'state':
                                            device[field] = {"online": False, "properties": {}}
                                        elif field == 'capabilities':
                                            device[field] = []
                                        elif field == 'config':
                                            device[field] = {}
                            
                            devices.append(device)
                    
                    conn.close()
                except Exception as e:
                    logger.error(f"Error checking database directly: {e}")
        
        # If still no devices found or we're in development mode, try the plugin
        if not devices:
            try:
                from main import plugin_manager
                teensy_plugin = plugin_manager.get_plugin("teensy")
                
                if teensy_plugin:
                    plugin_devices = teensy_plugin.get_all_devices()
                    if plugin_devices:
                        logger.info(f"Found {len(plugin_devices)} Teensy devices from plugin")
                        return plugin_devices
            except Exception as e:
                logger.error(f"Error getting devices from plugin: {e}")
        
        return devices
    except Exception as e:
        logger.error(f"Error retrieving Teensy devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discover", response_model=List[Dict[str, Any]])
async def discover_teensy_devices():
    """Discover available Teensy devices connected to the system"""
    try:
        # First try to use the plugin if it's loaded
        from main import plugin_manager
        teensy_plugin = plugin_manager.get_plugin("teensy")
        
        if teensy_plugin:
            # If plugin is available, use it to discover devices
            return teensy_plugin.discover_devices()
        
        # Fallback: Use pyserial to list available ports with Teensy devices
        import serial.tools.list_ports
        
        # Get the plugin configuration
        plugin_config = config.get("plugins", {}).get("config", {}).get("teensy", {})
        mock_mode = plugin_config.get("mock_mode", True)
        
        if mock_mode:
            # Mock implementation for development
            available_ports = [
                {"port": "/dev/ttyACM0", "description": "Teensy 4.0", "board_type": "teensy_4.0"},
                {"port": "/dev/ttyACM1", "description": "Teensy 4.1", "board_type": "teensy_4.1"},
                {"port": "/dev/cu.usbmodem12345678", "description": "Teensy 4.0", "board_type": "teensy_4.0"}
            ]
        else:
            # Real implementation using pyserial
            available_ports = []
            for port in serial.tools.list_ports.comports():
                # Teensy devices often have "teensy" in the description
                # or have specific VID:PID combinations
                is_teensy = (
                    "teensy" in port.description.lower() if hasattr(port, 'description') else False or 
                    (hasattr(port, 'vid') and port.vid == 0x16C0 and port.pid in [0x0483, 0x0486, 0x0487])
                )
                
                board_type = "teensy_4.0"  # Default
                if hasattr(port, 'description') and "4.1" in port.description:
                    board_type = "teensy_4.1"
                
                # Always include ttyACM devices even if not explicitly identified as Teensy
                if is_teensy or (hasattr(port, 'device') and "ttyACM" in port.device):
                    available_ports.append({
                        "port": port.device,
                        "description": port.description if hasattr(port, 'description') else "Unknown",
                        "board_type": board_type,
                        "hardware_id": port.hwid if hasattr(port, 'hwid') else None,
                        "manufacturer": port.manufacturer if hasattr(port, 'manufacturer') else None
                    })
            
            # If no devices found but we know ttyACM0 exists, add it manually
            if not available_ports and plugin_config.get("default_port") == "/dev/ttyACM0":
                import os
                if os.path.exists("/dev/ttyACM0"):
                    available_ports.append({
                        "port": "/dev/ttyACM0",
                        "description": "Detected Serial Device",
                        "board_type": "teensy_4.0",
                        "hardware_id": None,
                        "manufacturer": None
                    })
        
        return available_ports
    except Exception as e:
        logger.error(f"Error discovering Teensy devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Device)
async def register_teensy_device(device: TeensyDeviceRegistration):
    """Register a new Teensy device"""
    try:
        # Log the incoming data for debugging
        logger.info(f"Received device registration request: {device.dict()}")
        
        # Generate a device ID
        device_id = f"teensy_{uuid.uuid4().hex[:8]}"
        
        # Create device record
        new_device = Device(
            id=device_id,
            name=device.name,
            type=device.type,
            protocol=DeviceProtocol.TEENSY,
            location=device.location,
            manufacturer="PJRC",  # Teensy manufacturer
            model=device.teensy_config.board_type,
            state=DeviceState(
                online=False,  # Will be set to True when connected
                last_seen=datetime.now(),
                properties={}
            ),
            capabilities=["read", "write", "usb_serial", "hid"],  # Teensy capabilities
            config={
                "teensy_config": device.teensy_config.dict()
            }
        )
        
        # Also check if we can register with the plugin
        try:
            from main import plugin_manager
            teensy_plugin = plugin_manager.get_plugin("teensy")
            if teensy_plugin:
                # Register with plugin
                plugin_device_id = teensy_plugin.register_device({
                    "id": device_id,
                    "name": device.name,
                    "type": device.type,
                    "location": device.location,
                    "teensy_config": device.teensy_config.dict()
                })
                logger.info(f"Device registered with plugin, ID: {plugin_device_id}")
        except Exception as plugin_error:
            logger.warning(f"Could not register with plugin: {plugin_error}")
        
        # In production, save to database
        try:
            db_device = new_device.dict()
            db_device["state"] = json.dumps(db_device["state"])
            db_device["capabilities"] = json.dumps(db_device["capabilities"])
            db_device["config"] = json.dumps(db_device["config"])
            success = db.add_device(db_device)
            logger.info(f"Device saved to database: {success}")
        except Exception as db_error:
            logger.warning(f"Could not save to database: {db_error}")
        
        # For development, log the device
        logger.info(f"Registered Teensy device: {new_device.dict()}")
        
        return new_device
    except Exception as e:
        logger.error(f"Error registering Teensy device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=Device)
async def get_teensy_device(device_id: str):
    """Get a specific Teensy device by ID"""
    try:
        # In production this would query the database
        device = db.query_one("SELECT * FROM devices WHERE id = ?", [device_id])
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Teensy device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=Device)
async def update_teensy_device(device_id: str, device_update: Dict[str, Any]):
    """Update a Teensy device configuration"""
    try:
        # In production this would update the database
        device = db.query_one("SELECT * FROM devices WHERE id = ?", [device_id])
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update device with new values
        for key, value in device_update.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        # Save updated device
        # db.execute("UPDATE devices SET ... WHERE id = ?", [device_id])
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Teensy device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_id}", response_model=Dict[str, Any])
async def delete_teensy_device(device_id: str):
    """Delete a Teensy device"""
    try:
        # In production this would delete from the database
        device = db.query_one("SELECT * FROM devices WHERE id = ?", [device_id])
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Delete device
        # db.execute("DELETE FROM devices WHERE id = ?", [device_id])
        
        return {"status": "success", "message": f"Device {device_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Teensy device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/command", response_model=Dict[str, Any])
async def send_command_to_teensy(device_id: str, command: Dict[str, Any]):
    """Send a command to a Teensy device"""
    try:
        # In production this would send the command to the device
        device = db.query_one("SELECT * FROM devices WHERE id = ?", [device_id])
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Process command
        logger.info(f"Sending command to Teensy device {device_id}: {command}")
        
        # Mock response for development
        return {
            "status": "success",
            "device_id": device_id,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending command to Teensy device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))