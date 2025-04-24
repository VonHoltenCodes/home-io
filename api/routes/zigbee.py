from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_zigbee_devices():
    """
    Get all Zigbee devices 
    """
    from main import plugin_manager
    
    # Get the Zigbee plugin
    zigbee_plugin = plugin_manager.get_plugin("zigbee")
    if not zigbee_plugin:
        raise HTTPException(status_code=404, detail="Zigbee plugin not available")
    
    # Get all devices
    devices = zigbee_plugin.get_devices()
    
    return devices

@router.get("/{device_id}")
async def get_zigbee_device(device_id: str):
    """
    Get a specific Zigbee device
    """
    from main import plugin_manager
    
    # Get the Zigbee plugin
    zigbee_plugin = plugin_manager.get_plugin("zigbee")
    if not zigbee_plugin:
        raise HTTPException(status_code=404, detail="Zigbee plugin not available")
    
    # Get the device
    device = zigbee_plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Zigbee device not found")
    
    return device

@router.post("/{device_id}/command")
async def send_zigbee_command(
    device_id: str,
    command: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Send a command to a Zigbee device
    """
    from main import plugin_manager
    
    # Get the Zigbee plugin
    zigbee_plugin = plugin_manager.get_plugin("zigbee")
    if not zigbee_plugin:
        raise HTTPException(status_code=404, detail="Zigbee plugin not available")
    
    # Validate the device exists
    device = zigbee_plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Zigbee device not found")
    
    # Execute the command
    result = zigbee_plugin.send_command(device_id, command, params or {})
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Command failed: {result.get('error', 'Unknown error')}"
        )
    
    return result

@router.get("/types/{device_type}")
async def get_zigbee_devices_by_type(device_type: str):
    """
    Get all Zigbee devices of a specific type
    """
    from main import plugin_manager
    
    # Get the Zigbee plugin
    zigbee_plugin = plugin_manager.get_plugin("zigbee")
    if not zigbee_plugin:
        raise HTTPException(status_code=404, detail="Zigbee plugin not available")
    
    # Get all devices
    all_devices = zigbee_plugin.get_devices()
    
    # Filter by type
    filtered_devices = [
        device for device in all_devices 
        if device.get("type", "").lower() == device_type.lower()
    ]
    
    return filtered_devices

@router.post("/{device_id}/identify")
async def identify_zigbee_device(device_id: str):
    """
    Identify a Zigbee device (usually makes it blink or beep)
    """
    from main import plugin_manager
    
    # Get the Zigbee plugin
    zigbee_plugin = plugin_manager.get_plugin("zigbee")
    if not zigbee_plugin:
        raise HTTPException(status_code=404, detail="Zigbee plugin not available")
    
    # Validate the device exists
    device = zigbee_plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Zigbee device not found")
    
    # Execute the identify command
    result = zigbee_plugin.send_command(device_id, "identify", {})
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Identify command failed: {result.get('error', 'Unknown error')}"
        )
    
    return {"success": True, "message": f"Device {device_id} is identifying itself"}