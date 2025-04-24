from core.plugin_manager import PluginInterface
from typing import Dict, Any, List, Optional
import logging
import asyncio
import json
import os
import time
import hashlib
import hmac
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

logger = logging.getLogger("home-io.tuya")

class TuyaPlugin(PluginInterface):
    """
    Plugin for Tuya device integration using the Tuya IoT Platform API
    
    This plugin requires registering as a developer at iot.tuya.com to get API credentials.
    """
    
    plugin_name = "tuya"
    plugin_version = "0.1.0"
    plugin_description = "Tuya smart device integration"
    
    # API endpoints
    BASE_URL = "https://openapi.tuyaus.com"  # US data center, might need to be changed based on region
    TOKEN_API = "/v1.0/token"
    DEVICES_API = "/v1.0/devices"
    DEVICE_STATUS_API = "/v1.0/devices/{device_id}/status"
    DEVICE_COMMANDS_API = "/v1.0/devices/{device_id}/commands"
    
    def __init__(self):
        self.config = {}
        self.devices = {}
        self.access_token = None
        self.token_expires_at = None
        self.running = False
        self.event_listeners = []
        self._event_loop = None
        
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the Tuya plugin with configuration"""
        self.config = config or {}
        
        # Get API credentials from config
        self.api_key = self.config.get("api_key")
        self.api_secret = self.config.get("api_secret")
        self.data_center = self.config.get("data_center", "us")
        
        # Debug mode for development
        self.debug_mode = self.config.get("debug_mode", False)
        
        # Mock mode for development without actual Tuya credentials
        self.mock_mode = self.config.get("mock_mode", True)
        
        if not self.mock_mode and (not self.api_key or not self.api_secret):
            logger.error("Tuya API credentials not provided")
            return False
        
        # If in mock mode, load mock devices
        if self.mock_mode:
            logger.info("Initializing Tuya plugin in mock mode")
            self._load_mock_devices()
        else:
            # Get access token
            success = self._get_access_token()
            if not success:
                logger.error("Failed to get Tuya access token")
                return False
                
            # Discover devices
            success = self._discover_devices()
            if not success:
                logger.error("Failed to discover Tuya devices")
                return False
        
        # Start event processing for device updates
        self._start_event_processing()
        
        logger.info("Tuya plugin initialized successfully")
        return True
    
    def shutdown(self) -> bool:
        """Shutdown the Tuya plugin"""
        logger.info("Shutting down Tuya plugin")
        
        # Stop event processing
        self._stop_event_processing()
        
        logger.info("Tuya plugin shutdown complete")
        return True
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all Tuya devices"""
        return list(self.devices.values())
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Tuya device"""
        return self.devices.get(device_id)
    
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to a Tuya device"""
        params = params or {}
        
        if device_id not in self.devices:
            return {"success": False, "error": "Device not found"}
        
        device = self.devices[device_id]
        
        if self.mock_mode:
            # Mock command handling
            logger.info(f"Sending mock command to Tuya device {device_id}: {command} with params {params}")
            
            # Update mock device state based on command
            if command == "switch":
                value = params.get("value", False)
                # For smart plugs, update the power state
                if device.get("category") == "sp":
                    for idx, status in enumerate(device["status"]):
                        if status["code"] == "switch_1":
                            device["status"][idx]["value"] = value
                            
            elif command == "brightness":
                value = params.get("value", 100)
                # For lights, update the brightness
                if device.get("category") == "dj":
                    for idx, status in enumerate(device["status"]):
                        if status["code"] == "bright_value":
                            device["status"][idx]["value"] = value
            
            return {
                "success": True, 
                "device_id": device_id,
                "command": command,
                "params": params,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Real API request
            try:
                # Ensure token is valid
                if not self._ensure_access_token():
                    return {"success": False, "error": "Failed to get access token"}
                
                # Map command and params to Tuya API format
                commands = self._map_command_to_tuya_format(command, params)
                
                # Make API request
                endpoint = self.DEVICE_COMMANDS_API.format(device_id=device_id)
                headers = self._get_request_headers()
                
                response = requests.post(
                    f"{self.BASE_URL}{endpoint}",
                    headers=headers,
                    json={"commands": commands}
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": f"API error: {response.status_code}"}
                
                response_data = response.json()
                
                if response_data.get("success", False):
                    # Update local device state if command was successful
                    self._refresh_device_status(device_id)
                    
                    return {
                        "success": True,
                        "device_id": device_id,
                        "command": command,
                        "params": params,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": response_data.get("msg", "Unknown error")}
                    
            except Exception as e:
                logger.error(f"Error sending command to Tuya device: {str(e)}")
                return {"success": False, "error": str(e)}
    
    def add_event_listener(self, callback):
        """Add a callback for Tuya device events"""
        self.event_listeners.append(callback)
        
    def remove_event_listener(self, callback):
        """Remove a callback for Tuya device events"""
        if callback in self.event_listeners:
            self.event_listeners.remove(callback)
    
    def _load_mock_devices(self):
        """Load mock Tuya devices for development"""
        mock_devices = [
            {
                "id": "tuya_switch_1",
                "name": "Living Room Plug",
                "category": "sp",  # Smart Plug
                "product_name": "Smart Plug",
                "status": [
                    {"code": "switch_1", "value": True},
                    {"code": "countdown_1", "value": 0}
                ],
                "online": True,
                "icon_url": "",
                "product_id": "mock_product_1"
            },
            {
                "id": "tuya_switch_2",
                "name": "Bedroom Plug",
                "category": "sp",  # Smart Plug
                "product_name": "Smart Plug",
                "status": [
                    {"code": "switch_1", "value": False},
                    {"code": "countdown_1", "value": 0}
                ],
                "online": True,
                "icon_url": "",
                "product_id": "mock_product_1"
            },
            {
                "id": "tuya_light_1",
                "name": "Dining Room Light",
                "category": "dj",  # Light
                "product_name": "Smart Light",
                "status": [
                    {"code": "switch_led", "value": True},
                    {"code": "bright_value", "value": 75},
                    {"code": "temp_value", "value": 50}
                ],
                "online": True,
                "icon_url": "",
                "product_id": "mock_product_2"
            }
        ]
        
        # Store mock devices
        for device in mock_devices:
            self.devices[device["id"]] = device
            
        logger.info(f"Loaded {len(mock_devices)} mock Tuya devices")
    
    def _get_access_token(self) -> bool:
        """Get access token from Tuya API"""
        if not self.api_key or not self.api_secret:
            return False
            
        try:
            timestamp = int(time.time() * 1000)
            payload = f"{self.api_key}{timestamp}"
            
            # Create signature
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                msg=payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest().upper()
            
            # Make request
            headers = {
                "client_id": self.api_key,
                "sign": signature,
                "sign_method": "HMAC-SHA256",
                "t": str(timestamp),
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.BASE_URL}{self.TOKEN_API}", headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get token: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("success", False):
                result = data.get("result", {})
                self.access_token = result.get("access_token")
                expires_in = result.get("expire_time", 7200)
                
                # Set token expiry time (with 5 minute buffer)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                return bool(self.access_token)
            else:
                logger.error(f"Token error: {data.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return False
    
    def _ensure_access_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if needed"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            return self._get_access_token()
        return True
    
    def _get_request_headers(self) -> Dict[str, str]:
        """Get headers for Tuya API requests"""
        timestamp = int(time.time() * 1000)
        
        headers = {
            "client_id": self.api_key,
            "t": str(timestamp),
            "sign_method": "HMAC-SHA256",
            "access_token": self.access_token,
            "Content-Type": "application/json"
        }
        
        # Create signature
        str_to_sign = f"{self.api_key}{self.access_token}{timestamp}"
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        
        headers["sign"] = signature
        
        return headers
    
    def _discover_devices(self) -> bool:
        """Discover Tuya devices"""
        if not self._ensure_access_token():
            return False
            
        try:
            headers = self._get_request_headers()
            
            # Get devices
            response = requests.get(f"{self.BASE_URL}{self.DEVICES_API}", headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get devices: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("success", False):
                devices = data.get("result", [])
                
                # Store devices and get their status
                for device in devices:
                    device_id = device.get("id")
                    if device_id:
                        self.devices[device_id] = device
                        self._refresh_device_status(device_id)
                
                logger.info(f"Discovered {len(devices)} Tuya devices")
                return True
            else:
                logger.error(f"Device discovery error: {data.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error discovering devices: {str(e)}")
            return False
    
    def _refresh_device_status(self, device_id: str) -> bool:
        """Refresh a device's status"""
        if not self._ensure_access_token():
            return False
            
        if device_id not in self.devices:
            return False
            
        try:
            headers = self._get_request_headers()
            
            # Get device status
            endpoint = self.DEVICE_STATUS_API.format(device_id=device_id)
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get device status: {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("success", False):
                status = data.get("result", [])
                
                # Update device status
                self.devices[device_id]["status"] = status
                return True
            else:
                logger.error(f"Device status error: {data.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting device status: {str(e)}")
            return False
    
    def _map_command_to_tuya_format(self, command: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map Home-IO commands to Tuya API format"""
        commands = []
        
        if command == "switch":
            commands.append({
                "code": "switch_1",
                "value": params.get("value", False)
            })
        elif command == "brightness":
            commands.append({
                "code": "bright_value",
                "value": params.get("value", 100)
            })
        elif command == "temperature":
            commands.append({
                "code": "temp_value",
                "value": params.get("value", 50)
            })
        elif command == "color":
            commands.append({
                "code": "colour_data_v2",
                "value": params.get("value", {"h": 0, "s": 0, "v": 100})
            })
        elif command == "raw":
            # For sending raw commands directly
            raw_commands = params.get("commands", [])
            commands.extend(raw_commands)
            
        return commands
    
    def _start_event_processing(self):
        """Start processing Tuya events"""
        if self.running:
            return
            
        self.running = True
        
        if self.mock_mode:
            # For mock mode, create a background task that simulates events
            self._event_loop = asyncio.new_event_loop()
            asyncio.run_coroutine_threadsafe(self._simulate_events(), self._event_loop)
        else:
            # In a real implementation, we would set up polling or a websocket connection
            # for real-time updates
            self._event_loop = asyncio.new_event_loop()
            asyncio.run_coroutine_threadsafe(self._poll_device_status(), self._event_loop)
    
    def _stop_event_processing(self):
        """Stop processing Tuya events"""
        self.running = False
        
        if self._event_loop:
            self._event_loop.stop()
            self._event_loop.close()
            self._event_loop = None
    
    async def _simulate_events(self):
        """Simulate Tuya events for the mock mode"""
        while self.running:
            # Wait for a random interval (5-15 seconds)
            await asyncio.sleep(10)
            
            # Don't send events if no listeners
            if not self.event_listeners:
                continue
                
            # Pick a random device
            if not self.devices:
                continue
                
            device_ids = list(self.devices.keys())
            device_id = device_ids[int(time.time()) % len(device_ids)]
            device = self.devices[device_id]
            
            # Simulate a state change event
            if device.get("category") == "sp":  # Smart plug
                # Find the switch status
                for idx, status in enumerate(device["status"]):
                    if status["code"] == "switch_1":
                        # Toggle the switch
                        new_value = not status["value"]
                        device["status"][idx]["value"] = new_value
                        
                        # Create event
                        event = {
                            "type": "device_update",
                            "device_id": device_id,
                            "timestamp": datetime.now().isoformat(),
                            "data": {
                                "status": device["status"]
                            }
                        }
                        
                        # Notify listeners
                        for listener in self.event_listeners:
                            try:
                                listener(event)
                            except Exception as e:
                                logger.error(f"Error in event listener: {str(e)}")
                                
                        break
    
    async def _poll_device_status(self):
        """Poll device status for real-time updates"""
        while self.running:
            # Poll every 30 seconds
            await asyncio.sleep(30)
            
            # Don't poll if no listeners
            if not self.event_listeners:
                continue
                
            # Refresh status for all devices
            for device_id in self.devices:
                try:
                    old_status = self.devices[device_id].get("status", [])
                    
                    # Get new status
                    self._refresh_device_status(device_id)
                    
                    new_status = self.devices[device_id].get("status", [])
                    
                    # Check if status changed
                    if new_status != old_status:
                        # Create event
                        event = {
                            "type": "device_update",
                            "device_id": device_id,
                            "timestamp": datetime.now().isoformat(),
                            "data": {
                                "status": new_status
                            }
                        }
                        
                        # Notify listeners
                        for listener in self.event_listeners:
                            try:
                                listener(event)
                            except Exception as e:
                                logger.error(f"Error in event listener: {str(e)}")
                                
                except Exception as e:
                    logger.error(f"Error polling device {device_id}: {str(e)}")