from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_smart_plugs():
    """
    Get all smart plugs from all supported integrations
    """
    from main import plugin_manager
    
    smart_plugs = []
    
    # Get Tuya devices
    tuya_plugin = plugin_manager.get_plugin("tuya")
    if tuya_plugin:
        for device in tuya_plugin.get_devices():
            # Only include smart plug devices
            if device.get("category") == "sp":
                smart_plug = _map_tuya_device(device)
                if smart_plug:
                    smart_plugs.append(smart_plug)
    
    # Get Z-Wave smart plugs
    zwave_plugin = plugin_manager.get_plugin("zwave")
    if zwave_plugin:
        for device in zwave_plugin.get_devices():
            # Check if device is a smart plug
            if device.get("type") == "switch":
                smart_plug = _map_zwave_device(device)
                if smart_plug:
                    smart_plugs.append(smart_plug)
    
    return smart_plugs

@router.get("/{plug_id}")
async def get_smart_plug(plug_id: str):
    """
    Get a specific smart plug by ID
    """
    from main import plugin_manager
    
    # Parse plug ID to get plugin and device ID
    parts = plug_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid smart plug ID format")
    
    plugin_type, device_id = parts
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Get the device
    device = plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Smart plug not found")
    
    # Map device to standardized format
    if plugin_type == "tuya":
        smart_plug = _map_tuya_device(device)
    elif plugin_type == "zwave":
        smart_plug = _map_zwave_device(device)
    else:
        smart_plug = device  # Default fallback
    
    if not smart_plug:
        raise HTTPException(status_code=404, detail="Device is not a smart plug")
    
    return smart_plug

@router.post("/{plug_id}/switch")
async def set_switch_state(
    plug_id: str, 
    state: bool
):
    """
    Turn a smart plug on or off
    """
    from main import plugin_manager
    
    # Parse plug ID to get plugin and device ID
    parts = plug_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid smart plug ID format")
    
    plugin_type, device_id = parts
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Map to plugin-specific command
    if plugin_type == "tuya":
        result = plugin.send_command(device_id, "switch", {
            "value": state
        })
    elif plugin_type == "zwave":
        # For Z-Wave, the command might be different
        result = plugin.send_command(device_id, "switch", {
            "state": "on" if state else "off"
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported plugin type: {plugin_type}")
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to set switch state: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "plug_id": plug_id,
        "state": state,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/{plug_id}/schedule")
async def set_schedule(
    plug_id: str, 
    on_time: str,
    off_time: str,
    enabled: bool = True
):
    """
    Set a schedule for a smart plug (on/off times)
    """
    from main import plugin_manager
    
    # Parse plug ID to get plugin and device ID
    parts = plug_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid smart plug ID format")
    
    plugin_type, device_id = parts
    
    # Validate time formats (should be HH:MM)
    try:
        datetime.strptime(on_time, "%H:%M")
        datetime.strptime(off_time, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM (24-hour format)")
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Map to plugin-specific command
    if plugin_type == "tuya":
        # This would depend on the actual Tuya API capabilities
        result = plugin.send_command(device_id, "raw", {
            "commands": [
                {"code": "time_schedule", "value": {
                    "enabled": enabled,
                    "on_time": on_time,
                    "off_time": off_time
                }}
            ]
        })
    elif plugin_type == "zwave":
        # For Z-Wave, we'd need to implement scheduling in our own database
        # as Z-Wave doesn't directly support this at the protocol level
        raise HTTPException(status_code=501, detail="Scheduling not implemented for Z-Wave devices")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported plugin type: {plugin_type}")
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to set schedule: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "plug_id": plug_id,
        "schedule": {
            "enabled": enabled,
            "on_time": on_time,
            "off_time": off_time
        },
        "timestamp": datetime.now().isoformat()
    }

# Helper functions to map device data to standardized format
def _map_tuya_device(device):
    """Map Tuya device to standardized smart plug format"""
    # Check if device is a smart plug
    if device.get("category") != "sp":
        return None
    
    # Find switch status
    switch_status = False
    for status in device.get("status", []):
        if status.get("code") == "switch_1":
            switch_status = status.get("value", False)
            break
    
    return {
        "id": f"tuya:{device['id']}",
        "name": device.get("name", "Tuya Smart Plug"),
        "manufacturer": "Tuya",
        "model": device.get("product_name", "Smart Plug"),
        "state": switch_status,
        "online": device.get("online", True),
        "features": ["switch"],  # Basic feature
        "last_updated": datetime.now().isoformat()
    }

def _map_zwave_device(device):
    """Map Z-Wave device to standardized smart plug format"""
    # For now, a very simple mapping as our Z-Wave plugin is just a mock
    if device.get("type") != "switch":
        return None
    
    return {
        "id": f"zwave:{device['id']}",
        "name": device.get("name", "Z-Wave Smart Plug"),
        "manufacturer": device.get("manufacturer", "Unknown"),
        "model": device.get("model", "Unknown"),
        "state": device.get("state", "off") == "on",
        "online": True,  # Z-Wave devices report connectivity differently
        "features": ["switch"],  # Basic feature
        "last_updated": datetime.now().isoformat()
    }