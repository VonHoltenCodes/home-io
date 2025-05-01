import React, { useState, useEffect } from 'react';
import { useTheme } from '../utils/ThemeContext';
import './TeensyPage.css';

const TeensyPage = () => {
  const { theme } = useTheme();
  const [devices, setDevices] = useState([]);
  const [availablePorts, setAvailablePorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewDeviceForm, setShowNewDeviceForm] = useState(false);
  const [newDevice, setNewDevice] = useState({
    name: '',
    type: 'environmental_sensor',
    protocol: 'teensy',
    location: '',
    manufacturer: 'PJRC',
    model: '',
    teensy_config: {
      port: '',
      baud_rate: 115200,
      timeout: 1.0,
      mqtt_topic: '',
      reading_interval: 60,
      interface_type: 'serial',
      board_type: 'teensy_4.0'
    }
  });

  useEffect(() => {
    // Fetch devices
    fetchDevices();
    
    // Fetch available ports
    fetchAvailablePorts();
    
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      fetchDevices();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      // In a real app, this would call the API
      const response = await fetch('/api/teensy');
      if (!response.ok) {
        throw new Error('Failed to fetch devices');
      }
      const data = await response.json();
      
      // Ensure data is correctly formatted
      const formattedData = data.map(device => {
        // Parse JSON strings if needed
        if (device && typeof device === 'object') {
          // If state is a string, parse it
          if (typeof device.state === 'string') {
            try {
              device.state = JSON.parse(device.state);
            } catch (e) {
              console.error('Error parsing device state:', e);
              device.state = {
                online: false,
                last_seen: new Date().toISOString(),
                properties: {}
              };
            }
          }

          // If capabilities is a string, parse it
          if (typeof device.capabilities === 'string') {
            try {
              device.capabilities = JSON.parse(device.capabilities);
            } catch (e) {
              console.error('Error parsing device capabilities:', e);
              device.capabilities = [];
            }
          }

          // If config is a string, parse it
          if (typeof device.config === 'string') {
            try {
              device.config = JSON.parse(device.config);
            } catch (e) {
              console.error('Error parsing device config:', e);
              device.config = { teensy_config: {} };
            }
          }

          // Ensure state.properties exists
          if (!device.state || !device.state.properties) {
            device.state = device.state || {};
            device.state.properties = {};
          }
        }
        return device;
      }).filter(device => device && device.id); // Filter out items without IDs

      setDevices(formattedData);
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError('Failed to load devices. ' + err.message);
      
      // Mock data for development
      setDevices([
        {
          id: 'teensy_12345678',
          name: 'Workshop Environmental Sensor',
          type: 'environmental_sensor',
          protocol: 'teensy',
          location: 'Workshop',
          manufacturer: 'PJRC',
          model: 'Teensy 4.0',
          state: {
            online: true,
            last_seen: new Date().toISOString(),
            properties: {
              temperature: 22.5,
              humidity: 45,
              pressure: 1013
            }
          },
          capabilities: ['read', 'write', 'usb_serial'],
          config: {
            teensy_config: {
              port: '/dev/ttyACM0',
              baud_rate: 115200,
              mqtt_topic: 'home_io/sensors/workshop',
              reading_interval: 60,
              board_type: 'teensy_4.0'
            }
          }
        },
        {
          id: 'teensy_87654321',
          name: 'Living Room Air Quality',
          type: 'air_quality_sensor',
          protocol: 'teensy',
          location: 'Living Room',
          manufacturer: 'PJRC',
          model: 'Teensy 4.1',
          state: {
            online: false,
            last_seen: new Date(Date.now() - 3600000).toISOString(),
            properties: {
              co2: 450,
              voc: 120
            }
          },
          capabilities: ['read', 'write', 'usb_serial', 'hid'],
          config: {
            teensy_config: {
              port: '/dev/ttyACM1',
              baud_rate: 115200,
              mqtt_topic: 'home_io/sensors/living_room',
              reading_interval: 120,
              board_type: 'teensy_4.1'
            }
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailablePorts = async () => {
    try {
      // In a real app, this would call the API
      const response = await fetch('/api/teensy/discover');
      if (!response.ok) {
        throw new Error('Failed to fetch available ports');
      }
      const data = await response.json();
      setAvailablePorts(data);
    } catch (err) {
      console.error('Error fetching available ports:', err);
      
      // Mock data for development
      setAvailablePorts([
        { port: '/dev/ttyACM0', description: 'Teensy 4.0', board_type: 'teensy_4.0' },
        { port: '/dev/ttyACM1', description: 'Teensy 4.1', board_type: 'teensy_4.1' },
        { port: '/dev/cu.usbmodem12345678', description: 'Teensy 4.0', board_type: 'teensy_4.0' }
      ]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      // Handle nested properties (teensy_config)
      const [parent, child] = name.split('.');
      setNewDevice({
        ...newDevice,
        [parent]: {
          ...newDevice[parent],
          [child]: value
        }
      });
    } else {
      setNewDevice({
        ...newDevice,
        [name]: value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Validate form
      if (!newDevice.name || !newDevice.teensy_config.port) {
        setError('Name and port are required');
        return;
      }
      
      console.log('Submitting device registration:', JSON.stringify(newDevice, null, 2));
      
      // Use the API utility function
      try {
        // Try to use teensy-api.js if available
        const { registerTeensyDevice } = await import('../utils/teensy-api');
        const registeredDevice = await registerTeensyDevice(newDevice);
        console.log('Device registered successfully:', registeredDevice);
        setDevices([...devices, registeredDevice]);
      } catch (apiError) {
        console.warn('Could not use teensy-api.js, falling back to direct fetch:', apiError);
        
        // Direct fetch fallback
        const response = await fetch('/api/teensy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newDevice)
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Registration failed:', errorText);
          throw new Error(`Failed to register device: ${response.status} ${errorText}`);
        }
        
        // Add new device to the list
        const registeredDevice = await response.json();
        console.log('Device registered via direct fetch:', registeredDevice);
        setDevices([...devices, registeredDevice]);
      }
      
      // Reset form
      setNewDevice({
        name: '',
        type: 'environmental_sensor',
        protocol: 'teensy',
        location: '',
        manufacturer: 'PJRC',
        model: '',
        teensy_config: {
          port: '',
          baud_rate: 115200,
          timeout: 1.0,
          mqtt_topic: '',
          reading_interval: 60,
          interface_type: 'serial',
          board_type: 'teensy_4.0'
        }
      });
      
      // Hide form
      setShowNewDeviceForm(false);
    } catch (err) {
      console.error('Error registering device:', err);
      setError('Failed to register device. ' + err.message);
      
      // For development - fake success
      setShowNewDeviceForm(false);
      alert('Registration attempted. Check console for details.');
      fetchDevices();
    }
  };

  const handleRemoveDevice = async (deviceId) => {
    if (!window.confirm('Are you sure you want to remove this device?')) {
      return;
    }
    
    try {
      // In a real app, this would call the API
      const response = await fetch(`/api/teensy/${deviceId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to remove device');
      }
      
      // Remove device from the list
      setDevices(devices.filter(device => device.id !== deviceId));
    } catch (err) {
      console.error('Error removing device:', err);
      setError('Failed to remove device. ' + err.message);
      
      // For development - fake success
      setDevices(devices.filter(device => device.id !== deviceId));
    }
  };

  const handleSendCommand = async (deviceId, command) => {
    try {
      // In a real app, this would call the API
      const response = await fetch(`/api/teensy/${deviceId}/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          command: command,
          params: {}
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send command');
      }
      
      // Update device state
      fetchDevices();
    } catch (err) {
      console.error('Error sending command:', err);
      setError('Failed to send command. ' + err.message);
    }
  };

  return (
    <div className={`teensy-page ${theme}`}>
      <div className="page-header">
        <h2>Teensy Devices</h2>
        <button 
          className="add-device-button"
          onClick={() => setShowNewDeviceForm(!showNewDeviceForm)}
        >
          {showNewDeviceForm ? 'Cancel' : 'Add Device'}
        </button>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {showNewDeviceForm && (
        <div className="new-device-form-container">
          <h3>Register New Teensy Device</h3>
          <form className="new-device-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Device Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={newDevice.name}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="type">Device Type</label>
              <select
                id="type"
                name="type"
                value={newDevice.type}
                onChange={handleInputChange}
                required
              >
                <option value="environmental_sensor">Environmental Sensor</option>
                <option value="temperature_sensor">Temperature Sensor</option>
                <option value="humidity_sensor">Humidity Sensor</option>
                <option value="pressure_sensor">Pressure Sensor</option>
                <option value="air_quality_sensor">Air Quality Sensor</option>
                <option value="sensor">Generic Sensor</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                type="text"
                id="location"
                name="location"
                value={newDevice.location}
                onChange={handleInputChange}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="teensy_config.board_type">Board Type</label>
              <select
                id="teensy_config.board_type"
                name="teensy_config.board_type"
                value={newDevice.teensy_config.board_type}
                onChange={handleInputChange}
                required
              >
                <option value="teensy_4.0">Teensy 4.0</option>
                <option value="teensy_4.1">Teensy 4.1</option>
              </select>
            </div>
            
            <h4>Connection Configuration</h4>
            
            <div className="form-group">
              <label htmlFor="teensy_config.port">Port</label>
              <select
                id="teensy_config.port"
                name="teensy_config.port"
                value={newDevice.teensy_config.port}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a port</option>
                {availablePorts.map(port => (
                  <option key={port.port} value={port.port}>
                    {port.port} - {port.description}
                  </option>
                ))}
              </select>
              <button 
                type="button" 
                className="refresh-button"
                onClick={fetchAvailablePorts}
              >
                Refresh
              </button>
            </div>
            
            <div className="form-group">
              <label htmlFor="teensy_config.baud_rate">Baud Rate</label>
              <select
                id="teensy_config.baud_rate"
                name="teensy_config.baud_rate"
                value={newDevice.teensy_config.baud_rate}
                onChange={handleInputChange}
              >
                <option value="9600">9600</option>
                <option value="19200">19200</option>
                <option value="38400">38400</option>
                <option value="57600">57600</option>
                <option value="115200">115200</option>
                <option value="230400">230400</option>
                <option value="460800">460800</option>
                <option value="921600">921600</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="teensy_config.mqtt_topic">MQTT Topic</label>
              <input
                type="text"
                id="teensy_config.mqtt_topic"
                name="teensy_config.mqtt_topic"
                value={newDevice.teensy_config.mqtt_topic}
                onChange={handleInputChange}
                placeholder="home_io/sensors/[location]"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="teensy_config.reading_interval">Reading Interval (seconds)</label>
              <input
                type="number"
                id="teensy_config.reading_interval"
                name="teensy_config.reading_interval"
                value={newDevice.teensy_config.reading_interval}
                onChange={handleInputChange}
                min="1"
                max="3600"
              />
            </div>
            
            <div className="form-actions">
              <button type="submit" className="submit-button">Register Device</button>
              <button 
                type="button" 
                className="cancel-button"
                onClick={() => setShowNewDeviceForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
      
      {loading ? (
        <div className="loading">Loading devices...</div>
      ) : (
        <div className="devices-container">
          {devices.length === 0 ? (
            <div className="no-devices">
              <p>No Teensy devices registered yet.</p>
              <button 
                className="add-device-button"
                onClick={() => setShowNewDeviceForm(true)}
              >
                Add Your First Device
              </button>
            </div>
          ) : (
            <div className="devices-grid">
              {devices.map(device => {
                // Safety check for required objects and properties
                if (!device || !device.id) return null;
                
                // Ensure state object exists
                const state = device.state || { online: false, properties: {} };
                const isOnline = state.online === true;
                
                // Ensure config and teensy_config objects exist
                const config = device.config || {};
                const teensyConfig = config.teensy_config || {};
                
                return (
                  <div 
                    key={device.id}
                    className={`device-card ${isOnline ? 'online' : 'offline'}`}
                  >
                    <div className="device-header">
                      <h3>{device.name || 'Unnamed Device'}</h3>
                      <span className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
                        {isOnline ? 'Online' : 'Offline'}
                      </span>
                    </div>
                    
                    <div className="device-info">
                      <p><strong>Type:</strong> {(device.type || '').replace('_', ' ')}</p>
                      <p><strong>Location:</strong> {device.location || 'Not specified'}</p>
                      <p><strong>Board:</strong> {(teensyConfig.board_type || '').replace('_', ' ')}</p>
                      <p><strong>Port:</strong> {teensyConfig.port || 'Unknown'}</p>
                      <p><strong>Last Seen:</strong> {state.last_seen ? new Date(state.last_seen).toLocaleString() : 'Never'}</p>
                    </div>
                    
                    <div className="device-readings">
                      <h4>Latest Readings</h4>
                      {state.properties && typeof state.properties === 'object' ? 
                        Object.entries(state.properties).map(([key, value]) => {
                          // Skip non-reading properties
                          if (key === 'last_command' || key === 'timestamp') return null;
                          
                          return (
                            <div key={key} className="reading">
                              <span className="reading-name">{key}:</span>
                              <span className="reading-value">
                                {key === 'temperature' ? `${(value * 9/5 + 32).toFixed(1)}°F` : 
                                 key === 'humidity' ? `${value}%` : 
                                 key === 'pressure' ? `${(value * 0.02953).toFixed(2)} inHg` : 
                                 key === 'co2' ? `${value} ppm` : 
                                 key === 'voc' ? `${value} ppb` : 
                                 value}
                              </span>
                            </div>
                          );
                        })
                        : <p>No readings available</p>
                      }
                    </div>
                    
                    <div className="device-commands">
                      <h4>Commands</h4>
                      <div className="command-buttons">
                        <button 
                          className="command-button"
                          onClick={() => handleSendCommand(device.id, 'GET_SENSOR_DATA')}
                          disabled={!isOnline}
                        >
                          Refresh Data
                        </button>
                        <button 
                          className="command-button"
                          onClick={() => handleSendCommand(device.id, 'IDENTIFY')}
                          disabled={!isOnline}
                        >
                          Identify
                        </button>
                        <button 
                          className="command-button"
                          onClick={() => handleSendCommand(device.id, 'RESET')}
                          disabled={!isOnline}
                        >
                          Reset
                        </button>
                      </div>
                    </div>
                    
                    <div className="device-actions">
                      <button 
                        className="edit-button"
                        onClick={() => alert(`Edit device ${device.id} (not implemented)`)}
                      >
                        Edit
                      </button>
                      <button 
                        className="remove-button"
                        onClick={() => handleRemoveDevice(device.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TeensyPage;