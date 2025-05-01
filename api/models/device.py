from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DeviceType(str, Enum):
    """Enum for device types"""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    SENSOR = "sensor"
    ENVIRONMENTAL_SENSOR = "environmental_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    PRESSURE_SENSOR = "pressure_sensor"
    AIR_QUALITY_SENSOR = "air_quality_sensor"
    LOCK = "lock"
    CAMERA = "camera"
    SWITCH = "switch"
    OUTLET = "outlet"
    AUDIO_RECEIVER = "audio_receiver"
    AUDIO_AMPLIFIER = "audio_amplifier"
    AUDIO_SPEAKERS = "speakers"
    AUDIO_TURNTABLE = "turntable"
    OTHER = "other"


class DeviceProtocol(str, Enum):
    """Enum for device communication protocols"""
    ZWAVE = "zwave"
    ZIGBEE = "zigbee"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    API = "api"
    MQTT = "mqtt"
    USB = "usb"
    TEENSY = "teensy"
    OTHER = "other"


class DeviceState(BaseModel):
    """Model for device state data"""
    online: bool = True
    last_seen: datetime = Field(default_factory=datetime.now)
    properties: Dict[str, Any] = {}


class Device(BaseModel):
    """Base model for all devices"""
    id: str
    name: str
    type: DeviceType
    protocol: DeviceProtocol
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    state: DeviceState = Field(default_factory=DeviceState)
    capabilities: List[str] = []
    config: Dict[str, Any] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "id": "light_living_room_1",
                "name": "Living Room Main Light",
                "type": "light",
                "protocol": "zigbee",
                "location": "Living Room",
                "manufacturer": "Philips",
                "model": "Hue White and Color",
                "firmware_version": "1.2.3",
                "state": {
                    "online": True,
                    "last_seen": "2025-04-23T12:34:56",
                    "properties": {
                        "power": "on",
                        "brightness": 80,
                        "color_temp": 4000
                    }
                },
                "capabilities": ["on_off", "brightness", "color_temp", "rgb"],
                "config": {
                    "auto_off_minutes": 30
                }
            }
        }


class SensorReading(BaseModel):
    """Model for sensor readings"""
    timestamp: datetime = Field(default_factory=datetime.now)
    value: float
    unit: str
    type: str
    device_id: str


class DeviceCommand(BaseModel):
    """Model for device commands"""
    device_id: str
    command: str
    parameters: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class DeviceRegistration(BaseModel):
    """Model for registering a new device"""
    name: str
    type: DeviceType
    protocol: DeviceProtocol
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    config: Dict[str, Any] = {}


class TeensyDeviceConfig(BaseModel):
    """Configuration for Teensy devices"""
    port: str
    baud_rate: int = 115200  # Teensy typically uses higher baud rates
    timeout: float = 1.0
    mqtt_topic: Optional[str] = None
    mqtt_broker: Optional[str] = None
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    reading_interval: int = 60  # seconds between readings
    interface_type: str = "serial"  # serial, midi, hid, etc.
    firmware_version: Optional[str] = None
    board_type: str = "teensy_4.0"  # teensy_4.0, teensy_4.1, etc.


class TeensyDeviceRegistration(DeviceRegistration):
    """Model for registering a Teensy device"""
    protocol: DeviceProtocol = DeviceProtocol.TEENSY
    teensy_config: TeensyDeviceConfig

    class Config:
        schema_extra = {
            "example": {
                "name": "Workshop Environmental Sensor",
                "type": "environmental_sensor",
                "protocol": "teensy",
                "location": "Workshop",
                "manufacturer": "PJRC",
                "model": "Teensy 4.0",
                "teensy_config": {
                    "port": "/dev/ttyACM0",
                    "baud_rate": 115200,
                    "timeout": 1.0,
                    "mqtt_topic": "home_io/sensors/workshop",
                    "reading_interval": 60,
                    "interface_type": "serial",
                    "board_type": "teensy_4.0"
                }
            }
        }