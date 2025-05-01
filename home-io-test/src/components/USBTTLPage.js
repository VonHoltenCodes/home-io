import React, { useState, useEffect } from 'react';
import { useTheme } from '../utils/ThemeContext';
import './USBTTLPage.css';

const USBTTLPage = () => {
  const { theme } = useTheme();
  const [devices, setDevices] = useState([]);
  const [availablePorts, setAvailablePorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewDeviceForm, setShowNewDeviceForm] = useState(false);
  const [newDevice, setNewDevice] = useState({
    name: '',
    type: 'environmental_sensor',
    protocol: 'usb_ttl',
    location: '',
    manufacturer: '',
    model: '',
    usb_config: {
      port: '',
      baud_rate: 9600,
      data_bits: 8,
      stop_bits: 1,
      parity: 'N',
      timeout: 1.0,
      mqtt_topic: '',
      reading_interval: 60
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
      const response = await fetch('/api/usb_ttl');
      if (!response.ok) {
        throw new Error('Failed to fetch devices');
      }
      const data = await response.json();
      setDevices(data);
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError('Failed to load devices. ' + err.message);
      
      // Mock data for development
      setDevices([
        {
          id: 'usb_ttl_12345678',
          name: 'Workshop BME280 Sensor',
          type: 'environmental_sensor',
          protocol: 'usb_ttl',
          location: 'Workshop',
          manufacturer: 'Bosch',
          model: 'BME280',
          state: {
            online: true,
            last_seen: new Date().toISOString(),
            properties: {
              temperature: 22.5,
              humidity: 45,
              pressure: 1013
            }
          },
          capabilities: ['read'],
          config: {
            usb_config: {
              port: '/dev/ttyUSB0',
              baud_rate: 9600,
              mqtt_topic: 'home_io/sensors/workshop',
              reading_interval: 60
            }
          }
        },
        {
          id: 'usb_ttl_87654321',
          name: 'Living Room Air Quality',
          type: 'air_quality_sensor',
          protocol: 'usb_ttl',
          location: 'Living Room',
          manufacturer: 'Generic',
          model: 'MQ-135',
          state: {
            online: false,
            last_seen: new Date(Date.now() - 3600000).toISOString(),
            properties: {
              co2: 450,
              voc: 120
            }
          },
          capabilities: ['read'],
          config: {
            usb_config: {
              port: '/dev/ttyUSB1',
              baud_rate: 9600,
              mqtt_topic: 'home_io/sensors/living_room',
              reading_interval: 120
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
      const response = await fetch('/api/usb_ttl/discover');
      if (!response.ok) {
        throw new Error('Failed to fetch available ports');
      }
      const data = await response.json();
      setAvailablePorts(data);
    } catch (err) {
      console.error('Error fetching available ports:', err);
      
      // Mock data for development
      setAvailablePorts([
        { port: '/dev/ttyUSB0', description: 'USB-Serial Controller' },
        { port: '/dev/ttyUSB1', description: 'CH340 Serial Controller' },
        { port: '/dev/ttyACM0', description: 'Arduino Uno' }
      ]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      // Handle nested properties (usb_config)
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
      if (!newDevice.name || !newDevice.usb_config.port) {
        setError('Name and port are required');
        return;
      }
      
      // In a real app, this would call the API
      const response = await fetch('/api/usb_ttl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newDevice)
      });
      
      if (!response.ok) {
        throw new Error('Failed to register device');
      }
      
      // Add new device to the list
      const registeredDevice = await response.json();
      setDevices([...devices, registeredDevice]);
      
      // Reset form
      setNewDevice({
        name: '',
        type: 'environmental_sensor',
        protocol: 'usb_ttl',
        location: '',
        manufacturer: '',
        model: '',
        usb_config: {
          port: '',
          baud_rate: 9600,
          data_bits: 8,
          stop_bits: 1,
          parity: 'N',
          timeout: 1.0,
          mqtt_topic: '',
          reading_interval: 60
        }
      });
      
      // Hide form
      setShowNewDeviceForm(false);
    } catch (err) {
      console.error('Error registering device:', err);
      setError('Failed to register device. ' + err.message);
      
      // For development - fake success
      setShowNewDeviceForm(false);
      alert('Device registered successfully (mock mode)');
      fetchDevices();
    }
  };

  const handleRemoveDevice = async (deviceId) => {
    if (!window.confirm('Are you sure you want to remove this device?')) {
      return;
    }
    
    try {
      // In a real app, this would call the API
      const response = await fetch(`/api/usb_ttl/${deviceId}`, {
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

  return (
    <div className={`usb-ttl-page ${theme}`}>
      <div className="page-header">
        <h2>USB-TTL Devices</h2>
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
          <h3>Register New USB-TTL Device</h3>
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
              <label htmlFor="manufacturer">Manufacturer</label>
              <input
                type="text"
                id="manufacturer"
                name="manufacturer"
                value={newDevice.manufacturer}
                onChange={handleInputChange}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="model">Model</label>
              <input
                type="text"
                id="model"
                name="model"
                value={newDevice.model}
                onChange={handleInputChange}
              />
            </div>
            
            <h4>USB Configuration</h4>
            
            <div className="form-group">
              <label htmlFor="usb_config.port">Port</label>
              <select
                id="usb_config.port"
                name="usb_config.port"
                value={newDevice.usb_config.port}
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
              <label htmlFor="usb_config.baud_rate">Baud Rate</label>
              <select
                id="usb_config.baud_rate"
                name="usb_config.baud_rate"
                value={newDevice.usb_config.baud_rate}
                onChange={handleInputChange}
              >
                <option value="1200">1200</option>
                <option value="2400">2400</option>
                <option value="4800">4800</option>
                <option value="9600">9600</option>
                <option value="19200">19200</option>
                <option value="38400">38400</option>
                <option value="57600">57600</option>
                <option value="115200">115200</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="usb_config.mqtt_topic">MQTT Topic</label>
              <input
                type="text"
                id="usb_config.mqtt_topic"
                name="usb_config.mqtt_topic"
                value={newDevice.usb_config.mqtt_topic}
                onChange={handleInputChange}
                placeholder="home_io/sensors/[location]"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="usb_config.reading_interval">Reading Interval (seconds)</label>
              <input
                type="number"
                id="usb_config.reading_interval"
                name="usb_config.reading_interval"
                value={newDevice.usb_config.reading_interval}
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
              <p>No USB-TTL devices registered yet.</p>
              <button 
                className="add-device-button"
                onClick={() => setShowNewDeviceForm(true)}
              >
                Add Your First Device
              </button>
            </div>
          ) : (
            <div className="devices-grid">
              {devices.map(device => (
                <div 
                  key={device.id}
                  className={`device-card ${device.state.online ? 'online' : 'offline'}`}
                >
                  <div className="device-header">
                    <h3>{device.name}</h3>
                    <span className={`status-indicator ${device.state.online ? 'online' : 'offline'}`}>
                      {device.state.online ? 'Online' : 'Offline'}
                    </span>
                  </div>
                  
                  <div className="device-info">
                    <p><strong>Type:</strong> {device.type.replace('_', ' ')}</p>
                    <p><strong>Location:</strong> {device.location || 'Not specified'}</p>
                    <p><strong>Port:</strong> {device.config.usb_config.port}</p>
                    <p><strong>Last Seen:</strong> {new Date(device.state.last_seen).toLocaleString()}</p>
                  </div>
                  
                  <div className="device-readings">
                    <h4>Latest Readings</h4>
                    {Object.entries(device.state.properties).map(([key, value]) => (
                      <div key={key} className="reading">
                        <span className="reading-name">{key}:</span>
                        <span className="reading-value">
                          {key === 'temperature' ? `${value}°C` : 
                           key === 'humidity' ? `${value}%` : 
                           key === 'pressure' ? `${value} hPa` : 
                           key === 'co2' ? `${value} ppm` : 
                           key === 'voc' ? `${value} ppb` : 
                           value}
                        </span>
                      </div>
                    ))}
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
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default USBTTLPage;