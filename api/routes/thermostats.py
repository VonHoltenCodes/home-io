from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

# Temperature unit conversion
def fahrenheit_to_celsius(temp_f):
    return (temp_f - 32) * 5 / 9

def celsius_to_fahrenheit(temp_c):
    return (temp_c * 9 / 5) + 32

@router.get("/")
async def get_thermostats():
    """
    Get all thermostats from all supported integrations
    """
    from main import plugin_manager
    
    thermostats = []
    
    # Get Honeywell devices
    honeywell_plugin = plugin_manager.get_plugin("honeywell")
    if honeywell_plugin:
        for device in honeywell_plugin.get_devices():
            # Only include thermostat devices
            thermostat = _map_honeywell_device(device)
            if thermostat:
                thermostats.append(thermostat)
    
    # Get Z-Wave thermostats
    zwave_plugin = plugin_manager.get_plugin("zwave")
    if zwave_plugin:
        for device in zwave_plugin.get_devices():
            # Check if device is a thermostat
            if device.get("type") == "thermostat":
                thermostat = _map_zwave_device(device)
                if thermostat:
                    thermostats.append(thermostat)
    
    return thermostats

@router.get("/{thermostat_id}")
async def get_thermostat(thermostat_id: str):
    """
    Get a specific thermostat by ID
    """
    from main import plugin_manager
    
    # Parse thermostat ID to get plugin and device ID
    parts = thermostat_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid thermostat ID format")
    
    plugin_type, device_id = parts
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Get the device
    device = plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Thermostat not found")
    
    # Map device to standardized format
    if plugin_type == "honeywell":
        thermostat = _map_honeywell_device(device)
    elif plugin_type == "zwave":
        thermostat = _map_zwave_device(device)
    else:
        thermostat = device  # Default fallback
    
    if not thermostat:
        raise HTTPException(status_code=404, detail="Device is not a thermostat")
    
    return thermostat

@router.post("/{thermostat_id}/temperature")
async def set_temperature(
    thermostat_id: str, 
    temperature: float,
    mode: Optional[str] = "heat"
):
    """
    Set the target temperature for a thermostat
    """
    from main import plugin_manager
    
    # Parse thermostat ID to get plugin and device ID
    parts = thermostat_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid thermostat ID format")
    
    plugin_type, device_id = parts
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Map to plugin-specific command
    if plugin_type == "honeywell":
        result = plugin.send_command(device_id, "set_target_temperature", {
            "value": temperature,
            "mode": mode
        })
    elif plugin_type == "zwave":
        # For Z-Wave, the command might be different
        result = plugin.send_command(device_id, "temperature", {
            "value": temperature,
            "mode": mode
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported plugin type: {plugin_type}")
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to set temperature: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "thermostat_id": thermostat_id,
        "temperature": temperature,
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/{thermostat_id}/mode")
async def set_mode(
    thermostat_id: str, 
    mode: str
):
    """
    Set the mode for a thermostat (heat, cool, auto, off)
    """
    from main import plugin_manager
    
    if mode not in ["heat", "cool", "auto", "off"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid mode: {mode}. Must be one of: heat, cool, auto, off"
        )
    
    # Parse thermostat ID to get plugin and device ID
    parts = thermostat_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid thermostat ID format")
    
    plugin_type, device_id = parts
    
    # Get the appropriate plugin
    plugin = plugin_manager.get_plugin(plugin_type)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_type} not found")
    
    # Map to plugin-specific command
    if plugin_type == "honeywell":
        result = plugin.send_command(device_id, "set_mode", {
            "mode": mode
        })
    elif plugin_type == "zwave":
        # For Z-Wave, the command might be different
        result = plugin.send_command(device_id, "mode", {
            "value": mode
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported plugin type: {plugin_type}")
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to set mode: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "thermostat_id": thermostat_id,
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{thermostat_id}/sensors")
async def get_thermostat_sensors(thermostat_id: str):
    """
    Get room sensors associated with a thermostat
    """
    from main import plugin_manager
    
    # Parse thermostat ID to get plugin and device ID
    parts = thermostat_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid thermostat ID format")
    
    plugin_type, device_id = parts
    
    # Currently only Honeywell supports room sensors
    if plugin_type != "honeywell":
        return []
    
    # Get the Honeywell plugin
    plugin = plugin_manager.get_plugin("honeywell")
    if not plugin:
        raise HTTPException(status_code=404, detail="Honeywell plugin not found")
    
    # Get the device
    device = plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Thermostat not found")
    
    # Get room sensors
    rooms = device.get("rooms", [])
    return rooms

# Helper functions to map device data to standardized format
def _map_honeywell_device(device):
    """Map Honeywell device to standardized thermostat format"""
    # Check if device has thermostat data
    if "settings" not in device or "status" not in device:
        return None
    
    settings = device.get("settings", {})
    status = device.get("status", {})
    
    return {
        "id": f"honeywell:{device['id']}",
        "name": device.get("name", "Honeywell Thermostat"),
        "manufacturer": "Honeywell",
        "model": device.get("model", "Unknown"),
        "current_temperature": status.get("indoorTemperature"),
        "current_humidity": status.get("humidity"),
        "outdoor_temperature": status.get("outdoorTemperature"),
        "heat_setpoint": settings.get("heatSetpoint"),
        "cool_setpoint": settings.get("coolSetpoint"),
        "mode": settings.get("mode", "off").lower(),
        "fan_mode": settings.get("fanMode", "auto").lower(),
        "has_room_sensors": len(device.get("rooms", [])) > 0,
        "room_sensors_count": len(device.get("rooms", [])),
        "state": "idle",  # Would need to parse operationStatus more carefully
        "last_updated": datetime.now().isoformat()
    }

def _map_zwave_device(device):
    """Map Z-Wave device to standardized thermostat format"""
    # For now, a very simple mapping as our Z-Wave plugin is just a mock
    if device.get("type") != "thermostat":
        return None
    
    return {
        "id": f"zwave:{device['id']}",
        "name": device.get("name", "Z-Wave Thermostat"),
        "manufacturer": device.get("manufacturer", "Unknown"),
        "model": device.get("model", "Unknown"),
        "current_temperature": device.get("temperature", 70),
        "current_humidity": device.get("humidity", 50),
        "heat_setpoint": device.get("heat_setpoint", 68),
        "cool_setpoint": device.get("cool_setpoint", 72),
        "mode": device.get("mode", "off").lower(),
        "fan_mode": device.get("fan_mode", "auto").lower(),
        "has_room_sensors": False,
        "room_sensors_count": 0,
        "state": device.get("state", "idle"),
        "last_updated": datetime.now().isoformat()
    }