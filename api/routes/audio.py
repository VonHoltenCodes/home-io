from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_audio_devices():
    """
    Get all audio devices from audio plugin
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        return []
        
    devices = audio_plugin.get_devices()
    return devices

@router.get("/zones")
async def get_audio_zones():
    """
    Get all audio zones
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        return []
        
    zones = audio_plugin.get_zones()
    return zones

@router.get("/sources")
async def get_audio_sources():
    """
    Get all available audio sources
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        return []
        
    sources = audio_plugin.get_sources()
    return sources

@router.get("/streaming")
async def get_streaming_services():
    """
    Get all available streaming services
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        return []
        
    services = audio_plugin.get_streaming_services()
    return services

@router.get("/devices/{device_id}")
async def get_audio_device(device_id: str):
    """
    Get a specific audio device by ID
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        raise HTTPException(status_code=404, detail="Audio plugin not found")
    
    device = audio_plugin.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Audio device not found")
    
    return device

@router.get("/zones/{zone_id}")
async def get_audio_zone(zone_id: str):
    """
    Get a specific audio zone by ID
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        raise HTTPException(status_code=404, detail="Audio plugin not found")
    
    zone = audio_plugin.get_zone(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Audio zone not found")
    
    return zone

@router.post("/devices/{device_id}/command")
async def send_device_command(
    device_id: str,
    command: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Send a command to an audio device
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        raise HTTPException(status_code=404, detail="Audio plugin not found")
    
    result = audio_plugin.send_command(device_id, command, params or {})
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=f"Command failed: {result.get('error', 'Unknown error')}"
        )
    
    return result

@router.post("/zones/{zone_id}/command")
async def send_zone_command(
    zone_id: str,
    command: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Send a command to an audio zone
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        raise HTTPException(status_code=404, detail="Audio plugin not found")
    
    result = audio_plugin.send_zone_command(zone_id, command, params or {})
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=f"Command failed: {result.get('error', 'Unknown error')}"
        )
    
    return result

@router.post("/streaming/{service_id}/command")
async def control_streaming(
    service_id: str,
    command: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Control a streaming service
    """
    from main import plugin_manager
    
    audio_plugin = plugin_manager.get_plugin("audio")
    if not audio_plugin:
        raise HTTPException(status_code=404, detail="Audio plugin not found")
    
    result = audio_plugin.control_streaming(service_id, command, params or {})
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=f"Command failed: {result.get('error', 'Unknown error')}"
        )
    
    return result