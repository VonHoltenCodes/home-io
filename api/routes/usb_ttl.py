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
    USBTTLDeviceConfig,
    USBTTLDeviceRegistration
)
from core.db_manager import DatabaseManager
from core.config_manager import ConfigManager

# Set up logging
logger = logging.getLogger("home-io.usb_ttl")

# Create router
router = APIRouter()

# Get database and config instances (would be dependency injection in a real app)
db = DatabaseManager("data/home_io.db")
config = ConfigManager()

@router.get("/", response_model=List[Device])
async def get_usb_ttl_devices():
    """Get all USB-TTL devices"""
    try:
        # In production this would query the database
        devices = db.query("SELECT * FROM devices WHERE protocol = 'usb_ttl'")
        return devices
    except Exception as e:
        logger.error(f"Error retrieving USB-TTL devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discover", response_model=List[Dict[str, Any]])
async def discover_usb_ttl_devices():
    """Discover available USB-TTL devices connected to the system"""
    try:
        # This would use pyserial to list available ports
        # Mock implementation for development
        available_ports = [
            {"port": "/dev/ttyUSB0", "description": "USB-Serial Controller"},
            {"port": "/dev/ttyUSB1", "description": "CH340 Serial Controller"},
            {"port": "/dev/ttyACM0", "description": "Arduino Uno"}
        ]
        return available_ports
    except Exception as e:
        logger.error(f"Error discovering USB-TTL devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Device)
async def register_usb_ttl_device(device: USBTTLDeviceRegistration):
    """Register a new USB-TTL device"""
    try:
        # Generate a device ID
        device_id = f"usb_ttl_{uuid.uuid4().hex[:8]}"
        
        # Create device record
        new_device = Device(
            id=device_id,
            name=device.name,
            type=device.type,
            protocol=DeviceProtocol.USB_TTL,
            location=device.location,
            manufacturer=device.manufacturer,
            model=device.model,
            state=DeviceState(
                online=False,  # Will be set to True when connected
                last_seen=datetime.now(),
                properties={}
            ),
            capabilities=["read", "write"],  # Default capabilities
            config={
                "usb_config": device.usb_config.dict()
            }
        )
        
        # In production, save to database
        # db.execute("INSERT INTO devices VALUES (?)", [new_device.dict()])
        
        # For development, log the device
        logger.info(f"Registered USB-TTL device: {new_device.dict()}")
        
        return new_device
    except Exception as e:
        logger.error(f"Error registering USB-TTL device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=Device)
async def get_usb_ttl_device(device_id: str):
    """Get a specific USB-TTL device by ID"""
    try:
        # In production this would query the database
        device = db.query_one("SELECT * FROM devices WHERE id = ?", [device_id])
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving USB-TTL device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=Device)
async def update_usb_ttl_device(device_id: str, device_update: Dict[str, Any]):
    """Update a USB-TTL device configuration"""
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
        logger.error(f"Error updating USB-TTL device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_id}", response_model=Dict[str, Any])
async def delete_usb_ttl_device(device_id: str):
    """Delete a USB-TTL device"""
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
        logger.error(f"Error deleting USB-TTL device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))