from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from api.models.device import (
    Device, 
    DeviceRegistration, 
    DeviceCommand, 
    SensorReading,
    DeviceType
)

router = APIRouter()

# In-memory storage for development (will be replaced with database)
devices_db: Dict[str, Device] = {}


@router.get("/", response_model=List[Device])
async def get_devices(
    device_type: Optional[DeviceType] = None,
    location: Optional[str] = None,
    limit: int = Query(50, gt=0, lt=101),
    offset: int = Query(0, ge=0),
):
    """
    Retrieve a list of all devices with optional filtering
    """
    filtered_devices = devices_db.values()
    
    if device_type:
        filtered_devices = [d for d in filtered_devices if d.type == device_type]
    
    if location:
        filtered_devices = [d for d in filtered_devices if d.location == location]
    
    # Apply pagination
    paginated_devices = list(filtered_devices)[offset:offset + limit]
    
    return paginated_devices


@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """
    Retrieve a specific device by ID
    """
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return devices_db[device_id]


@router.post("/", response_model=Device)
async def create_device(device: DeviceRegistration):
    """
    Register a new device in the system
    """
    device_id = f"{device.type}_{uuid.uuid4().hex[:8]}"
    
    new_device = Device(
        id=device_id,
        name=device.name,
        type=device.type,
        protocol=device.protocol,
        location=device.location,
        manufacturer=device.manufacturer,
        model=device.model,
        config=device.config,
        capabilities=[]  # Default empty capabilities
    )
    
    devices_db[device_id] = new_device
    return new_device


@router.put("/{device_id}", response_model=Device)
async def update_device(device_id: str, device_update: Dict[str, Any]):
    """
    Update device properties
    """
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    current_device = devices_db[device_id]
    
    # Update only the fields provided
    for key, value in device_update.items():
        if hasattr(current_device, key) and key != "id":  # Prevent ID changes
            setattr(current_device, key, value)
    
    return current_device


@router.delete("/{device_id}")
async def delete_device(device_id: str):
    """
    Remove a device from the system
    """
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    del devices_db[device_id]
    return {"success": True, "message": f"Device {device_id} removed"}


@router.post("/{device_id}/command", response_model=Dict[str, Any])
async def send_device_command(device_id: str, command: DeviceCommand):
    """
    Send a command to a device
    """
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Here you would implement actual device command handling
    # This is a placeholder that would be connected to plugin system
    
    # Update the device state for demo purposes
    if "state" in command.parameters:
        devices_db[device_id].state.properties.update(command.parameters["state"])
    
    # Mock response
    return {
        "success": True,
        "device_id": device_id,
        "command": command.command,
        "timestamp": datetime.now(),
        "result": "Command sent successfully"
    }


@router.get("/{device_id}/history", response_model=List[Dict[str, Any]])
async def get_device_history(
    device_id: str,
    limit: int = Query(20, gt=0, lt=101),
):
    """
    Get historical data for a device (placeholder)
    """
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Placeholder mock history data
    history = [
        {
            "timestamp": datetime.now(),
            "type": "state_change",
            "old_state": {"power": "off"},
            "new_state": {"power": "on"}
        }
    ]
    
    return history[:limit]