from core.plugin_manager import PluginInterface
from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import json
import os
import time
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

logger = logging.getLogger("home-io.honeywell")

class HoneywellPlugin(PluginInterface):
    """
    Plugin for Honeywell Home thermostat integration using the Honeywell Home API
    
    This plugin requires registering as a developer at developer.honeywellhome.com
    to get API credentials.
    """
    
    plugin_name = "honeywell"
    plugin_version = "0.1.0"
    plugin_description = "Honeywell Home thermostat integration"
    
    # API endpoints
    AUTH_URL = "https://api.honeywell.com/oauth2/token"
    API_URL = "https://api.honeywell.com/v2/devices"
    LOCATIONS_URL = "https://api.honeywell.com/v2/locations"
    
    def __init__(self):
        self.config = {}
        self.devices = {}
        self.locations = {}
        self.access_token = None
        self.token_expires_at = None
        self.running = False
        self.event_listeners = []
        self._event_loop = None
        
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the Honeywell plugin with configuration"""
        self.config = config or {}
        
        # Get API credentials from config
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.redirect_uri = self.config.get("redirect_uri", "http://localhost:8000/api/callback/honeywell")
        
        # Get authorization code from config (required for initial token generation)
        self.auth_code = self.config.get("auth_code")
        
        # Get refresh token from config (if available from previous runs)
        self.refresh_token = self.config.get("refresh_token")
        
        # Debug mode for development
        self.debug_mode = self.config.get("debug_mode", False)
        
        # Mock mode for development without actual Honeywell credentials
        self.mock_mode = self.config.get("mock_mode", True)
        
        if not self.mock_mode and (not self.client_id or not self.client_secret):
            logger.error("Honeywell API credentials not provided")
            return False
        
        # If in mock mode, load mock devices
        if self.mock_mode:
            logger.info("Initializing Honeywell plugin in mock mode")
            self._load_mock_devices()
        else:
            # Get access token
            success = self._get_access_token()
            if not success:
                logger.error("Failed to get Honeywell access token")
                return False
                
            # Discover locations and devices
            success = self._discover_locations_and_devices()
            if not success:
                logger.error("Failed to discover Honeywell locations and devices")
                return False
        
        # Start event processing for device updates
        self._start_event_processing()
        
        logger.info("Honeywell plugin initialized successfully")
        return True
    
    def shutdown(self) -> bool:
        """Shutdown the Honeywell plugin"""
        logger.info("Shutting down Honeywell plugin")
        
        # Stop event processing
        self._stop_event_processing()
        
        logger.info("Honeywell plugin shutdown complete")
        return True
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all Honeywell devices"""
        return list(self.devices.values())
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Honeywell device"""
        return self.devices.get(device_id)
    
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all Honeywell locations"""
        return list(self.locations.values())
    
    def get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Honeywell location"""
        return self.locations.get(location_id)
    
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to a Honeywell device"""
        params = params or {}
        
        if device_id not in self.devices:
            return {"success": False, "error": "Device not found"}
        
        device = self.devices[device_id]
        
        if self.mock_mode:
            # Mock command handling
            logger.info(f"Sending mock command to Honeywell device {device_id}: {command} with params {params}")
            
            # Update mock device state based on command
            if command == "set_target_temperature":
                value = params.get("value")
                mode = params.get("mode", "heat")
                
                if value is not None:
                    if mode == "heat":
                        device["settings"]["heatSetpoint"] = value
                    elif mode == "cool":
                        device["settings"]["coolSetpoint"] = value
                        
            elif command == "set_mode":
                mode = params.get("mode")
                
                if mode in ["heat", "cool", "off", "auto"]:
                    device["settings"]["mode"] = mode
                    
            elif command == "set_fan_mode":
                fan_mode = params.get("fan_mode")
                
                if fan_mode in ["auto", "on", "circulate"]:
                    device["settings"]["fanMode"] = fan_mode
            
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
                
                # Get device information
                device_id_parts = device_id.split(":")
                if len(device_id_parts) != 2:
                    return {"success": False, "error": "Invalid device ID format"}
                    
                location_id, thermostat_id = device_id_parts
                
                # Map command to Honeywell API request
                if command == "set_target_temperature":
                    success = self._set_temperature(location_id, thermostat_id, params)
                elif command == "set_mode":
                    success = self._set_mode(location_id, thermostat_id, params)
                elif command == "set_fan_mode":
                    success = self._set_fan_mode(location_id, thermostat_id, params)
                else:
                    return {"success": False, "error": f"Unsupported command: {command}"}
                
                if success:
                    # Refresh device state
                    self._refresh_device(location_id, thermostat_id)
                    
                    return {
                        "success": True,
                        "device_id": device_id,
                        "command": command,
                        "params": params,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"success": False, "error": "Command failed"}
                    
            except Exception as e:
                logger.error(f"Error sending command to Honeywell device: {str(e)}")
                return {"success": False, "error": str(e)}
    
    def add_event_listener(self, callback):
        """Add a callback for Honeywell device events"""
        self.event_listeners.append(callback)
        
    def remove_event_listener(self, callback):
        """Remove a callback for Honeywell device events"""
        if callback in self.event_listeners:
            self.event_listeners.remove(callback)
    
    def _load_mock_devices(self):
        """Load mock Honeywell devices for development"""
        # Mock locations
        mock_locations = [
            {
                "id": "1234567",
                "name": "Home",
                "type": "Home",
                "city": "New York",
                "state": "NY",
                "country": "US",
                "zipcode": "10001",
                "timezone": "America/New_York",
                "devices": []
            }
        ]
        
        # Mock devices
        mock_devices = [
            {
                "id": "1234567:T1234567890",
                "location_id": "1234567",
                "device_id": "T1234567890",
                "name": "Main Floor Thermostat",
                "model": "T9",
                "firmware": "1.0.0",
                "settings": {
                    "mode": "heat",
                    "heatSetpoint": 72,
                    "coolSetpoint": 76,
                    "heatCoolMode": "Heat",
                    "fanMode": "auto",
                    "scheduleEnabled": True
                },
                "status": {
                    "temperature": 71,
                    "humidity": 45,
                    "indoorTemperature": 71,
                    "outdoorTemperature": 65,
                    "operationStatus": {
                        "mode": "heat",
                        "fanRequest": False
                    }
                },
                "rooms": [
                    {
                        "id": "R1234567890",
                        "name": "Living Room",
                        "temperature": 71,
                        "humidity": 45,
                        "occupancy": True,
                        "motion": False
                    },
                    {
                        "id": "R1234567891",
                        "name": "Kitchen",
                        "temperature": 72,
                        "humidity": 46,
                        "occupancy": False,
                        "motion": False
                    },
                    {
                        "id": "R1234567892",
                        "name": "Bedroom",
                        "temperature": 70,
                        "humidity": 43,
                        "occupancy": False,
                        "motion": False
                    }
                ]
            }
        ]
        
        # Store mock data
        for location in mock_locations:
            self.locations[location["id"]] = location
            
        for device in mock_devices:
            self.devices[device["id"]] = device
            
            # Add device to location
            location_id = device["location_id"]
            if location_id in self.locations:
                self.locations[location_id]["devices"].append(device["device_id"])
            
        logger.info(f"Loaded {len(mock_locations)} mock locations and {len(mock_devices)} mock devices")
    
    def _get_access_token(self) -> bool:
        """Get access token from Honeywell API"""
        if not self.client_id or not self.client_secret:
            return False
            
        try:
            # If we have a refresh token, use it
            if self.refresh_token:
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            # Otherwise, use auth code
            elif self.auth_code:
                payload = {
                    "grant_type": "authorization_code",
                    "code": self.auth_code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            else:
                logger.error("No refresh token or auth code available")
                return False
                
            # Make request
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(
                self.AUTH_URL,
                headers=headers,
                data=urlencode(payload)
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get token: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            data = response.json()
            
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            expires_in = data.get("expires_in", 3600)
            
            # Set token expiry time (with 5 minute buffer)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            # Save refresh token to config for persistence
            self.config["refresh_token"] = self.refresh_token
            
            return bool(self.access_token)
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return False
    
    def _ensure_access_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if needed"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            return self._get_access_token()
        return True
    
    def _get_request_headers(self) -> Dict[str, str]:
        """Get headers for Honeywell API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _discover_locations_and_devices(self) -> bool:
        """Discover Honeywell locations and devices"""
        if not self._ensure_access_token():
            return False
            
        try:
            headers = self._get_request_headers()
            
            # Get locations
            response = requests.get(self.LOCATIONS_URL, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get locations: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            locations = response.json()
            
            # Store locations and get devices
            for location in locations:
                location_id = location.get("locationID")
                if location_id:
                    # Store location
                    self.locations[location_id] = {
                        "id": location_id,
                        "name": location.get("name"),
                        "type": location.get("type"),
                        "city": location.get("city"),
                        "state": location.get("state"),
                        "country": location.get("country"),
                        "zipcode": location.get("zipcode"),
                        "timezone": location.get("timeZone"),
                        "devices": []
                    }
                    
                    # Get devices for this location
                    devices_url = f"{self.LOCATIONS_URL}/{location_id}/devices"
                    devices_response = requests.get(devices_url, headers=headers)
                    
                    if devices_response.status_code != 200:
                        logger.error(f"Failed to get devices for location {location_id}: {devices_response.status_code}")
                        continue
                        
                    devices = devices_response.json()
                    
                    # Store devices
                    for device in devices:
                        device_id = device.get("deviceID")
                        if device_id:
                            # Create a unique ID for the device
                            unique_id = f"{location_id}:{device_id}"
                            
                            # Store device
                            self.devices[unique_id] = self._process_device_data(device, location_id)
                            
                            # Add to location
                            self.locations[location_id]["devices"].append(device_id)
            
            logger.info(f"Discovered {len(self.locations)} locations and {len(self.devices)} devices")
            return True
                
        except Exception as e:
            logger.error(f"Error discovering locations and devices: {str(e)}")
            return False
    
    def _process_device_data(self, device_data: Dict[str, Any], location_id: str) -> Dict[str, Any]:
        """Process and standardize device data from the API"""
        device_id = device_data.get("deviceID")
        unique_id = f"{location_id}:{device_id}"
        
        # Get room data if available
        rooms = []
        if "rooms" in device_data:
            for room in device_data["rooms"]:
                rooms.append({
                    "id": room.get("id"),
                    "name": room.get("name"),
                    "temperature": room.get("currentTemperature"),
                    "humidity": room.get("currentHumidity"),
                    "occupancy": room.get("occupancyStatus", {}).get("occupancyDetected", False),
                    "motion": room.get("occupancyStatus", {}).get("motionDetected", False)
                })
        
        # Extract settings
        settings = {}
        if "changeableValues" in device_data:
            values = device_data["changeableValues"]
            settings = {
                "mode": values.get("mode"),
                "heatSetpoint": values.get("heatSetpoint"),
                "coolSetpoint": values.get("coolSetpoint"),
                "heatCoolMode": values.get("heatCoolMode"),
                "fanMode": values.get("fan", {}).get("fanMode"),
                "scheduleEnabled": values.get("thermostatSetpointStatus") == "ScheduleEnabled"
            }
        
        # Extract status
        status = {}
        status["temperature"] = device_data.get("displayedOutdoorHumidity")
        status["humidity"] = device_data.get("indoorHumidity")
        status["indoorTemperature"] = device_data.get("indoorTemperature")
        status["outdoorTemperature"] = device_data.get("outdoorTemperature")
        
        # Extract operation status
        operation_status = {}
        if "operationStatus" in device_data:
            op_status = device_data["operationStatus"]
            operation_status = {
                "mode": op_status.get("mode"),
                "fanRequest": op_status.get("fanRequest", False)
            }
        status["operationStatus"] = operation_status
        
        # Construct device object
        processed_device = {
            "id": unique_id,
            "location_id": location_id,
            "device_id": device_id,
            "name": device_data.get("name"),
            "model": device_data.get("deviceModel"),
            "firmware": device_data.get("deviceFirmwareVersion"),
            "settings": settings,
            "status": status,
            "rooms": rooms
        }
        
        return processed_device
    
    def _refresh_device(self, location_id: str, device_id: str) -> bool:
        """Refresh a device's data"""
        if not self._ensure_access_token():
            return False
            
        unique_id = f"{location_id}:{device_id}"
        if unique_id not in self.devices:
            return False
            
        try:
            headers = self._get_request_headers()
            
            # Get device data
            device_url = f"{self.LOCATIONS_URL}/{location_id}/devices/{device_id}"
            response = requests.get(device_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get device data: {response.status_code}")
                return False
                
            device_data = response.json()
            
            # Update device
            self.devices[unique_id] = self._process_device_data(device_data, location_id)
            return True
                
        except Exception as e:
            logger.error(f"Error refreshing device: {str(e)}")
            return False
    
    def _set_temperature(self, location_id: str, device_id: str, params: Dict[str, Any]) -> bool:
        """Set target temperature for a thermostat"""
        if not self._ensure_access_token():
            return False
            
        try:
            headers = self._get_request_headers()
            
            value = params.get("value")
            mode = params.get("mode", "heat")
            
            if value is None:
                return False
                
            # Prepare payload
            payload = {
                "mode": mode.capitalize() if mode != "off" else "Off"
            }
            
            if mode == "heat":
                payload["heatSetpoint"] = value
            elif mode == "cool":
                payload["coolSetpoint"] = value
            elif mode == "auto":
                # In auto mode, both heat and cool setpoints are required
                heat_value = params.get("heat_value", value - 2)
                cool_value = params.get("cool_value", value + 2)
                payload["heatSetpoint"] = heat_value
                payload["coolSetpoint"] = cool_value
                
            # Send command
            device_url = f"{self.LOCATIONS_URL}/{location_id}/devices/{device_id}/thermostat"
            response = requests.post(
                device_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 204]:
                logger.error(f"Failed to set temperature: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            return True
                
        except Exception as e:
            logger.error(f"Error setting temperature: {str(e)}")
            return False
    
    def _set_mode(self, location_id: str, device_id: str, params: Dict[str, Any]) -> bool:
        """Set mode for a thermostat"""
        if not self._ensure_access_token():
            return False
            
        try:
            headers = self._get_request_headers()
            
            mode = params.get("mode")
            
            if not mode or mode not in ["heat", "cool", "off", "auto"]:
                return False
                
            # Prepare payload
            payload = {
                "mode": mode.capitalize() if mode != "off" else "Off"
            }
                
            # Send command
            device_url = f"{self.LOCATIONS_URL}/{location_id}/devices/{device_id}/thermostat"
            response = requests.post(
                device_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 204]:
                logger.error(f"Failed to set mode: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            return True
                
        except Exception as e:
            logger.error(f"Error setting mode: {str(e)}")
            return False
    
    def _set_fan_mode(self, location_id: str, device_id: str, params: Dict[str, Any]) -> bool:
        """Set fan mode for a thermostat"""
        if not self._ensure_access_token():
            return False
            
        try:
            headers = self._get_request_headers()
            
            fan_mode = params.get("fan_mode")
            
            if not fan_mode or fan_mode not in ["auto", "on", "circulate"]:
                return False
                
            # Prepare payload
            payload = {
                "fan": {
                    "fanMode": fan_mode.capitalize()
                }
            }
                
            # Send command
            device_url = f"{self.LOCATIONS_URL}/{location_id}/devices/{device_id}/thermostat"
            response = requests.post(
                device_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 204]:
                logger.error(f"Failed to set fan mode: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
            return True
                
        except Exception as e:
            logger.error(f"Error setting fan mode: {str(e)}")
            return False
    
    def _start_event_processing(self):
        """Start processing Honeywell events"""
        if self.running:
            return
            
        self.running = True
        
        if self.mock_mode:
            # For mock mode, create a background task that simulates events
            self._event_loop = asyncio.new_event_loop()
            asyncio.run_coroutine_threadsafe(self._simulate_events(), self._event_loop)
        else:
            # In a real implementation, we would set up polling for updates
            self._event_loop = asyncio.new_event_loop()
            asyncio.run_coroutine_threadsafe(self._poll_devices(), self._event_loop)
    
    def _stop_event_processing(self):
        """Stop processing Honeywell events"""
        self.running = False
        
        if self._event_loop:
            self._event_loop.stop()
            self._event_loop.close()
            self._event_loop = None
    
    async def _simulate_events(self):
        """Simulate Honeywell events for the mock mode"""
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
            
            # Randomly alter temperature by +/- 0.5 degrees
            old_temp = device["status"]["indoorTemperature"]
            new_temp = old_temp + (0.5 if time.time() % 2 == 0 else -0.5)
            
            # Update device
            device["status"]["indoorTemperature"] = new_temp
            
            # Create event
            event = {
                "type": "device_update",
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "temperature": new_temp,
                    "previous_temperature": old_temp
                }
            }
            
            # Notify listeners
            for listener in self.event_listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"Error in event listener: {str(e)}")
    
    async def _poll_devices(self):
        """Poll devices for updates"""
        while self.running:
            # Poll every 60 seconds
            await asyncio.sleep(60)
            
            # Don't poll if no listeners
            if not self.event_listeners:
                continue
                
            # Refresh all devices
            for device_id in list(self.devices.keys()):
                try:
                    # Get device info
                    device = self.devices[device_id]
                    location_id, thermostat_id = device_id.split(":")
                    
                    # Store old state
                    old_state = json.dumps(device["status"])
                    
                    # Refresh device
                    self._refresh_device(location_id, thermostat_id)
                    
                    # Get new state
                    new_state = json.dumps(self.devices[device_id]["status"])
                    
                    # If state changed, send event
                    if old_state != new_state:
                        # Create event
                        event = {
                            "type": "device_update",
                            "device_id": device_id,
                            "timestamp": datetime.now().isoformat(),
                            "data": self.devices[device_id]["status"]
                        }
                        
                        # Notify listeners
                        for listener in self.event_listeners:
                            try:
                                listener(event)
                            except Exception as e:
                                logger.error(f"Error in event listener: {str(e)}")
                                
                except Exception as e:
                    logger.error(f"Error polling device {device_id}: {str(e)}")