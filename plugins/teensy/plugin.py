import logging
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
from core.plugin_manager import PluginInterface

logger = logging.getLogger("home-io.plugins.teensy")

class TeensyPlugin(PluginInterface):
    """Plugin for Teensy device integration"""
    
    # Class properties required by PluginInterface
    plugin_name = "teensy"
    plugin_version = "0.1.0"
    plugin_description = "Integration for Teensy microcontrollers"
    
    def __init__(self):
        self.name = "teensy"
        self.config = {}
        self.mqtt_client = None
        self.devices = {}  # Stores device configs
        self.active_connections = {}  # Stores serial connections
        self.running = False
        self.task = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the Teensy plugin"""
        logger.info("Initializing Teensy plugin")
        self.config = config.get("teensy", {})
        
        # Set default config values if not provided
        self.config["mock_mode"] = self.config.get("mock_mode", True)
        
        # Initialize MQTT client if needed
        mqtt_broker = self.config.get("mqtt_broker")
        if mqtt_broker:
            try:
                self.mqtt_client = mqtt.Client()
                # Set up auth if provided
                username = self.config.get("mqtt_username")
                password = self.config.get("mqtt_password")
                if username and password:
                    self.mqtt_client.username_pw_set(username, password)
                
                # Connect to MQTT broker
                self.mqtt_client.connect(mqtt_broker, int(self.config.get("mqtt_port", 1883)))
                self.mqtt_client.loop_start()
                logger.info(f"Connected to MQTT broker at {mqtt_broker}")
            except Exception as e:
                logger.error(f"Error connecting to MQTT broker: {e}")
                return False
        
        # Start background task
        try:
            self.running = True
            # Create background event loop for asyncio if needed
            if not asyncio.get_event_loop().is_running():
                asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            self.task = loop.create_task(self._background_loop())
            logger.info("Started Teensy background task")
        except Exception as e:
            logger.error(f"Error starting background task: {e}")
            return False
        
        return True
    
    def shutdown(self) -> bool:
        """Shutdown the Teensy plugin"""
        logger.info("Shutting down Teensy plugin")
        
        # Stop background task
        self.running = False
        if self.task and not self.task.done():
            self.task.cancel()
        
        # Disconnect from MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.mqtt_client = None
        
        # Close all serial connections
        for device_id, conn in self.active_connections.items():
            try:
                if conn and conn.is_open:
                    conn.close()
                    logger.info(f"Closed connection to device {device_id}")
            except Exception as e:
                logger.error(f"Error closing connection to device {device_id}: {e}")
        
        self.active_connections = {}
        return True
    
    async def _background_loop(self):
        """Background task for polling Teensy devices"""
        try:
            while self.running:
                # Poll each device
                for device_id, device_config in self.devices.items():
                    await self._poll_device(device_id, device_config)
                
                # Sleep for a while
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Background task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in background task: {e}")
    
    async def _poll_device(self, device_id: str, device_config: Dict[str, Any]):
        """Poll a single Teensy device for data"""
        # Skip if not time to poll yet
        last_poll = device_config.get("last_poll", 0)
        interval = device_config.get("teensy_config", {}).get("reading_interval", 60)
        current_time = datetime.now().timestamp()
        
        if current_time - last_poll < interval:
            return
        
        # Update last poll time
        self.devices[device_id]["last_poll"] = current_time
        
        try:
            # Get or create serial connection
            conn = self.active_connections.get(device_id)
            if not conn or not conn.is_open:
                # Create new connection
                teensy_config = device_config.get("teensy_config", {})
                port = teensy_config.get("port")
                baud_rate = int(teensy_config.get("baud_rate", 115200))
                
                # Use mock mode only if specifically configured to do so
                if self.config.get("mock_mode", False):
                    # In mock mode, simulate device data
                    data = self._generate_mock_data(device_config)
                    logger.info(f"Using mock data for device {device_id}: {data}")
                else:
                    # In real mode, read from device
                    try:
                        logger.info(f"Connecting to Teensy device at {port} with baud rate {baud_rate}")
                        conn = serial.Serial(
                            port=port,
                            baudrate=baud_rate,
                            timeout=float(teensy_config.get("timeout", 1.0))
                        )
                        self.active_connections[device_id] = conn
                        
                        # Send command to Teensy to get sensor data
                        logger.info(f"Sending GET_SENSOR_DATA command to device {device_id}")
                        conn.write(b"GET_SENSOR_DATA\n")
                        
                        # Read data line by line until empty line or timeout
                        data_raw = conn.readline().strip().decode("utf-8")
                        logger.info(f"Received data from device {device_id}: {data_raw}")
                        
                        try:
                            data = json.loads(data_raw)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON received from device {device_id}: {data_raw}")
                            data = {"error": f"Invalid data format: {data_raw}", "status": "error"}
                    except Exception as e:
                        logger.error(f"Error communicating with device {device_id}: {e}")
                        data = {"error": str(e), "status": "error"}
            
            # Process the data
            await self._process_device_data(device_id, device_config, data)
            
        except Exception as e:
            logger.error(f"Error polling device {device_id}: {e}")
            # Close connection on error
            if conn and conn.is_open:
                conn.close()
                self.active_connections.pop(device_id, None)
    
    def _generate_mock_data(self, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock data for testing"""
        device_type = device_config.get("type", "environmental_sensor")
        
        # Generate sensor readings based on device type
        if device_type in ["environmental_sensor", "temperature_sensor"]:
            return {
                "temperature": 21.5 + (uuid.uuid4().int % 10) / 10,  # Random around 21.5°C
                "humidity": 45 + (uuid.uuid4().int % 10),            # Random around 45%
                "pressure": 1013 + (uuid.uuid4().int % 10),          # Random around 1013 hPa
                "timestamp": datetime.now().isoformat()
            }
        elif device_type in ["air_quality_sensor"]:
            return {
                "co2": 400 + (uuid.uuid4().int % 100),  # Random around 400 ppm
                "voc": 100 + (uuid.uuid4().int % 50),   # Random around 100 ppb
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "value": (uuid.uuid4().int % 100) / 10,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_device_data(self, device_id: str, device_config: Dict[str, Any], data: Dict[str, Any]):
        """Process data received from a device"""
        # Log the data
        logger.debug(f"Received data from Teensy device {device_id}: {data}")
        
        # Update device state
        self.devices[device_id]["state"] = {
            "online": True,
            "last_seen": datetime.now().isoformat(),
            "properties": data
        }
        
        # Publish to MQTT if configured
        mqtt_topic = device_config.get("teensy_config", {}).get("mqtt_topic")
        if self.mqtt_client and mqtt_topic:
            try:
                message = json.dumps({
                    "device_id": device_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                })
                self.mqtt_client.publish(mqtt_topic, message)
                logger.debug(f"Published data to MQTT topic {mqtt_topic}")
            except Exception as e:
                logger.error(f"Error publishing to MQTT: {e}")
    
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Send a command to a Teensy device"""
        try:
            device_config = self.devices.get(device_id)
            if not device_config:
                raise ValueError(f"Device {device_id} not found")
            
            # Get or create serial connection
            conn = self.active_connections.get(device_id)
            if not conn or not conn.is_open:
                # Create new connection
                teensy_config = device_config.get("teensy_config", {})
                port = teensy_config.get("port")
                baud_rate = int(teensy_config.get("baud_rate", 115200))
                
                if self.config.get("mock_mode", False):
                    # In mock mode, just return success
                    return {
                        "status": "success",
                        "device_id": device_id,
                        "command": command,
                        "params": params,
                        "timestamp": datetime.now().isoformat()
                    }
                
                # In real mode, connect to device
                try:
                    logger.info(f"Connecting to Teensy device at {port} with baud rate {baud_rate}")
                    conn = serial.Serial(
                        port=port,
                        baudrate=baud_rate,
                        timeout=float(teensy_config.get("timeout", 1.0))
                    )
                    self.active_connections[device_id] = conn
                except Exception as e:
                    logger.error(f"Error connecting to device {device_id}: {e}")
                    return {
                        "status": "error",
                        "device_id": device_id,
                        "command": command,
                        "error": f"Connection error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Format the command as JSON
            command_json = json.dumps({
                "command": command,
                "params": params
            })
            
            # Send the command
            conn.write(f"{command_json}\n".encode("utf-8"))
            
            # Read the response
            response_raw = conn.readline().strip().decode("utf-8")
            response = json.loads(response_raw)
            
            # Update device state if status is included
            if "status" in response:
                self.devices[device_id]["state"]["properties"]["last_command"] = {
                    "command": command,
                    "status": response["status"],
                    "timestamp": datetime.now().isoformat()
                }
            
            return response
        except Exception as e:
            logger.error(f"Error sending command to device {device_id}: {e}")
            # Close connection on error
            if "conn" in locals() and conn and conn.is_open:
                conn.close()
                self.active_connections.pop(device_id, None)
            
            # Return error response
            return {
                "status": "error",
                "device_id": device_id,
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def register_device(self, device_config: Dict[str, Any]) -> Optional[str]:
        """Register a new Teensy device"""
        try:
            device_id = device_config.get("id")
            if not device_id:
                device_id = f"teensy_{uuid.uuid4().hex[:8]}"
                device_config["id"] = device_id
            
            # Store device config
            self.devices[device_id] = device_config
            
            logger.info(f"Registered Teensy device {device_id}: {device_config}")
            return device_id
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return None
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all registered devices"""
        return list(self.devices.values())
    
    def remove_device(self, device_id: str) -> bool:
        """Remove a device"""
        try:
            if device_id in self.active_connections:
                conn = self.active_connections.pop(device_id)
                if conn and conn.is_open:
                    conn.close()
            
            if device_id in self.devices:
                self.devices.pop(device_id)
                logger.info(f"Removed device {device_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing device {device_id}: {e}")
            return False
    
    def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available Teensy devices"""
        try:
            if self.config.get("mock_mode", True):
                # In mock mode, return sample devices
                return [
                    {"port": "/dev/ttyACM0", "description": "Teensy 4.0", "board_type": "teensy_4.0"},
                    {"port": "/dev/ttyACM1", "description": "Teensy 4.1", "board_type": "teensy_4.1"},
                    {"port": "/dev/cu.usbmodem12345678", "description": "Teensy 4.0", "board_type": "teensy_4.0"}
                ]
            else:
                # In real mode, try to identify Teensy devices
                devices = []
                for port in serial.tools.list_ports.comports():
                    # Teensy devices often have "teensy" in the description
                    # or have specific VID:PID combinations
                    is_teensy = (
                        "teensy" in port.description.lower() or 
                        (hasattr(port, 'vid') and port.vid == 0x16C0 and port.pid in [0x0483, 0x0486, 0x0487])
                    )
                    
                    if is_teensy:
                        board_type = "teensy_4.0"  # Default
                        if "4.1" in port.description:
                            board_type = "teensy_4.1"
                        
                        devices.append({
                            "port": port.device,
                            "description": port.description,
                            "board_type": board_type,
                            "hardware_id": port.hwid if hasattr(port, 'hwid') else None,
                            "manufacturer": port.manufacturer if hasattr(port, 'manufacturer') else None
                        })
                
                return devices
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return []