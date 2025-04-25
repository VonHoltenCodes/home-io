# API Integration

## Overview

The frontend communicates with the Home-IO backend API for device control and state management. The API integration is primarily handled through functions in `/src/utils/api.js`.

## Base Endpoints

The API is configured to use a proxy to the backend, which is set in `package.json`:

```json
"proxy": "http://localhost:8000"
```

## API Functions

### General Device APIs

```javascript
// Fetch all devices
export const fetchDevices = async () => {
  const response = await fetch('/api/devices');
  if (!response.ok) throw new Error('Failed to fetch devices');
  return response.json();
};

// Fetch a specific device
export const fetchDevice = async (id) => {
  const response = await fetch(`/api/devices/${id}`);
  if (!response.ok) throw new Error('Failed to fetch device');
  return response.json();
};
```

### Audio Device APIs

```javascript
// Send command to audio device
export const sendAudioDeviceCommand = async (deviceId, command, params = {}) => {
  const response = await fetch(`/api/audio/devices/${deviceId}/command/${command}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!response.ok) throw new Error(`Failed to execute command: ${command}`);
  return response.json();
};

// Get audio zones
export const getAudioZones = async () => {
  const response = await fetch('/api/audio/zones');
  if (!response.ok) throw new Error('Failed to fetch audio zones');
  return response.json();
};
```

### Thermostat APIs

```javascript
// Update thermostat settings
export const updateThermostat = async (deviceId, settings) => {
  const response = await fetch(`/api/thermostats/${deviceId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  if (!response.ok) throw new Error('Failed to update thermostat');
  return response.json();
};
```

### Smart Plug APIs

```javascript
// Toggle smart plug state
export const toggleSmartPlug = async (deviceId, state) => {
  const response = await fetch(`/api/smart_plugs/${deviceId}/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state })
  });
  if (!response.ok) throw new Error('Failed to toggle smart plug');
  return response.json();
};
```

### Zigbee Device APIs

```javascript
// Fetch Zigbee devices
export const fetchZigbeeDevices = async () => {
  const response = await fetch('/api/zigbee/devices');
  if (!response.ok) throw new Error('Failed to fetch Zigbee devices');
  return response.json();
};

// Update Zigbee device state
export const updateZigbeeDevice = async (deviceId, state) => {
  const response = await fetch(`/api/zigbee/devices/${deviceId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state)
  });
  if (!response.ok) throw new Error('Failed to update Zigbee device');
  return response.json();
};

// Identify Zigbee device (make it blink/beep)
export const identifyZigbeeDevice = async (deviceId) => {
  const response = await fetch(`/api/zigbee/devices/${deviceId}/identify`, {
    method: 'POST'
  });
  if (!response.ok) throw new Error('Failed to identify device');
  return response.json();
};
```

## Error Handling

API calls use a try/catch pattern for error handling:

```javascript
try {
  const data = await fetchDevices();
  setDevices(data);
} catch (error) {
  setError(error.message);
} finally {
  setLoading(false);
}
```

## Data Models

### Device Object Structure

```javascript
{
  id: "unique_device_id",
  name: "Device Name",
  type: "thermostat|audio|smartplug|zigbee",
  location: "Living Room", 
  status: "online|offline",
  // Additional fields depend on device type
}
```

### Audio Device

```javascript
{
  id: "audio_1",
  name: "Living Room Audio",
  type: "audio",
  power: "on|off",
  volume: 45, // 0-100
  mute: false,
  current_input: "source_tv", // source_tv, source_phono, source_spotify, source_aux
}
```

### Thermostat

```javascript
{
  id: "therm_1",
  name: "Main Thermostat",
  type: "thermostat",
  current_temperature: 72.5,
  set_point: 70,
  mode: "heat|cool|off",
  state: "idle|heating|cooling",
  humidity: 45 // percentage
}
```