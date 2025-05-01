import logging
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt

logger = logging.getLogger("home-io.plugins.usb_ttl")

class USBTTLPlugin:
    """Plugin for USB-TTL device integration"""
    
    def __init__(self):
        self.name = "usb_ttl"
        self.config = {}
        self.mqtt_client = None
        self.devices = {}  # Stores device configs
        self.active_connections = {}  # Stores serial connections
        self.running = False
        self.task = None
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the USB-TTL plugin"""
        logger.info("Initializing USB-TTL plugin")
        self.config = config.get("usb_ttl", {})
        
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
        self.running = True
        self.task = asyncio.create_task(self._background_loop())
        
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the USB-TTL plugin"""
        logger.info("Shutting down USB-TTL plugin")
        
        # Stop background task
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
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
        """Background task for polling USB-TTL devices"""
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
        """Poll a single USB-TTL device for data"""
        # Skip if not time to poll yet
        last_poll = device_config.get("last_poll", 0)
        interval = device_config.get("usb_config", {}).get("reading_interval", 60)
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
                usb_config = device_config.get("usb_config", {})
                port = usb_config.get("port")
                baud_rate = int(usb_config.get("baud_rate", 9600))
                
                if self.config.get("mock_mode", True):
                    # In mock mode, simulate device data
                    data = self._generate_mock_data(device_config)
                else:
                    # In real mode, read from device
                    conn = serial.Serial(
                        port=port,
                        baudrate=baud_rate,
                        bytesize=int(usb_config.get("data_bits", 8)),
                        parity=usb_config.get("parity", "N"),
                        stopbits=int(usb_config.get("stop_bits", 1)),
                        timeout=float(usb_config.get("timeout", 1.0))
                    )
                    self.active_connections[device_id] = conn
                    
                    # Read data from device
                    conn.write(b"READ\n")
                    data_raw = conn.readline().strip().decode("utf-8")
                    data = json.loads(data_raw)
            
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
                "timestamp": datetime.now().isoformat()
            }
        elif device_type in ["humidity_sensor", "environmental_sensor"]:
            return {
                "humidity": 45 + (uuid.uuid4().int % 10),  # Random around 45%
                "timestamp": datetime.now().isoformat()
            }
        elif device_type in ["pressure_sensor", "environmental_sensor"]:
            return {
                "pressure": 1013 + (uuid.uuid4().int % 10),  # Random around 1013 hPa
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
        logger.debug(f"Received data from device {device_id}: {data}")
        
        # Update device state
        self.devices[device_id]["state"] = {
            "online": True,
            "last_seen": datetime.now().isoformat(),
            "properties": data
        }
        
        # Publish to MQTT if configured
        mqtt_topic = device_config.get("usb_config", {}).get("mqtt_topic")
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
    
    async def register_device(self, device_config: Dict[str, Any]) -> Optional[str]:
        """Register a new USB-TTL device"""
        try:
            device_id = device_config.get("id")
            if not device_id:
                device_id = f"usb_ttl_{uuid.uuid4().hex[:8]}"
                device_config["id"] = device_id
            
            # Store device config
            self.devices[device_id] = device_config
            
            logger.info(f"Registered USB-TTL device {device_id}: {device_config}")
            return device_id
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return None
    
    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    async def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all registered devices"""
        return list(self.devices.values())
    
    async def remove_device(self, device_id: str) -> bool:
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
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available USB-TTL devices"""
        try:
            if self.config.get("mock_mode", True):
                # In mock mode, return sample devices
                return [
                    {"port": "/dev/ttyUSB0", "description": "USB-Serial Controller"},
                    {"port": "/dev/ttyUSB1", "description": "CH340 Serial Controller"},
                    {"port": "/dev/ttyACM0", "description": "Arduino Uno"}
                ]
            else:
                # In real mode, use pyserial to list ports
                devices = []
                for port in serial.tools.list_ports.comports():
                    devices.append({
                        "port": port.device,
                        "description": port.description,
                        "hardware_id": port.hwid,
                        "manufacturer": port.manufacturer if hasattr(port, 'manufacturer') else None
                    })
                return devices
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return []