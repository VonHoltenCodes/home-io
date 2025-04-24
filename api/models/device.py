from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DeviceType(str, Enum):
    """Enum for device types"""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    SENSOR = "sensor"
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