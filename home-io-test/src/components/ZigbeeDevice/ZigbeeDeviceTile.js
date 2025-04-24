import React, { useState } from 'react';
import './ZigbeeDeviceTile.css';

const ZigbeeDeviceTile = ({ device, onSendCommand }) => {
  const [loading, setLoading] = useState(false);
  
  const handleCommand = async (command, params = {}) => {
    setLoading(true);
    try {
      await onSendCommand(device.id, command, params);
    } catch (error) {
      console.error('Error sending command:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Render different controls based on device type
  const renderDeviceControls = () => {
    switch (device.type) {
      case 'light':
        return (
          <div className="zigbee-controls">
            <button 
              className={`control-button ${device.state === 'on' ? 'on' : 'off'}`}
              onClick={() => handleCommand('switch', { state: device.state === 'on' ? 'off' : 'on' })}
              disabled={loading}
            >
              {device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            
            {device.supported_features.includes('brightness') && (
              <div className="slider-control">
                <label>Brightness</label>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={device.brightness || 0}
                  onChange={(e) => handleCommand('brightness', { level: parseInt(e.target.value, 10) })}
                  disabled={loading || device.state === 'off'}
                />
                <span>{device.brightness || 0}%</span>
              </div>
            )}
            
            {device.supported_features.includes('color_temp') && (
              <div className="slider-control">
                <label>Color Temp</label>
                <input 
                  type="range" 
                  min="150" 
                  max="500" 
                  value={device.color_temp || 370}
                  onChange={(e) => handleCommand('color_temp', { value: parseInt(e.target.value, 10) })}
                  disabled={loading || device.state === 'off'}
                />
              </div>
            )}
          </div>
        );
        
      case 'switch':
        return (
          <div className="zigbee-controls">
            <button 
              className={`control-button ${device.state === 'on' ? 'on' : 'off'}`}
              onClick={() => handleCommand('switch', { state: device.state === 'on' ? 'off' : 'on' })}
              disabled={loading}
            >
              {device.state === 'on' ? 'Turn Off' : 'Turn On'}
            </button>
            
            {device.supported_features.includes('power_monitoring') && (
              <div className="power-info">
                Current: {device.power}W | Total: {device.energy}kWh
              </div>
            )}
          </div>
        );
        
      case 'sensor':
      case 'contact':
        return (
          <div className="zigbee-info">
            <div className="sensor-data">
              {device.motion !== undefined && (
                <div className="sensor-value">
                  Motion: <span className={device.motion ? 'active' : 'inactive'}>
                    {device.motion ? 'Detected' : 'Clear'}
                  </span>
                </div>
              )}
              
              {device.temperature !== undefined && (
                <div className="sensor-value">
                  Temp: {device.temperature}°F
                </div>
              )}
              
              {device.humidity !== undefined && (
                <div className="sensor-value">
                  Humidity: {device.humidity}%
                </div>
              )}
              
              {device.state !== undefined && device.type === 'contact' && (
                <div className="sensor-value">
                  State: <span className={device.state === 'open' ? 'active' : 'inactive'}>
                    {device.state}
                  </span>
                </div>
              )}
              
              {device.illuminance !== undefined && (
                <div className="sensor-value">
                  Light: {device.illuminance} lux
                </div>
              )}
            </div>
            
            {device.battery !== undefined && (
              <div className={`battery-indicator ${device.battery < 20 ? 'low' : ''}`}>
                Battery: {device.battery}%
              </div>
            )}
          </div>
        );
        
      case 'thermostat':
        return (
          <div className="zigbee-controls thermostat-controls">
            <div className="temperature-display">
              {device.temperature}°F
              {device.humidity !== undefined && <span> | {device.humidity}% RH</span>}
            </div>
            
            <div className="setpoint-controls">
              <div className="setpoint">
                <label>Heat</label>
                <button 
                  className="setpoint-button"
                  onClick={() => handleCommand('temperature', { 
                    value: (device.heat_setpoint || 70) - 1,
                    mode: 'heat'
                  })}
                  disabled={loading}
                >-</button>
                <span>{device.heat_setpoint || 70}°</span>
                <button 
                  className="setpoint-button"
                  onClick={() => handleCommand('temperature', { 
                    value: (device.heat_setpoint || 70) + 1,
                    mode: 'heat'
                  })}
                  disabled={loading}
                >+</button>
              </div>
              
              <div className="setpoint">
                <label>Cool</label>
                <button 
                  className="setpoint-button"
                  onClick={() => handleCommand('temperature', { 
                    value: (device.cool_setpoint || 75) - 1,
                    mode: 'cool'
                  })}
                  disabled={loading}
                >-</button>
                <span>{device.cool_setpoint || 75}°</span>
                <button 
                  className="setpoint-button"
                  onClick={() => handleCommand('temperature', { 
                    value: (device.cool_setpoint || 75) + 1,
                    mode: 'cool'
                  })}
                  disabled={loading}
                >+</button>
              </div>
            </div>
            
            <div className="mode-controls">
              <button 
                className={`mode-button ${device.mode === 'heat' ? 'active' : ''}`}
                onClick={() => handleCommand('mode', { mode: 'heat' })}
                disabled={loading}
              >
                Heat
              </button>
              <button 
                className={`mode-button ${device.mode === 'cool' ? 'active' : ''}`}
                onClick={() => handleCommand('mode', { mode: 'cool' })}
                disabled={loading}
              >
                Cool
              </button>
              <button 
                className={`mode-button ${device.mode === 'off' ? 'active' : ''}`}
                onClick={() => handleCommand('mode', { mode: 'off' })}
                disabled={loading}
              >
                Off
              </button>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="zigbee-info">
            <div className="device-details">
              <pre>{JSON.stringify(device, null, 2)}</pre>
            </div>
          </div>
        );
    }
  };
  
  // Define icon based on device type
  const getDeviceIcon = () => {
    switch (device.type) {
      case 'light':
        return '💡';
      case 'switch':
        return '🔌';
      case 'sensor':
        return '📊';
      case 'contact':
        return device.state === 'open' ? '🚪' : '🔒';
      case 'thermostat':
        return '🌡️';
      default:
        return '📱';
    }
  };
  
  return (
    <div className={`zigbee-device-tile ${device.type}`}>
      <div className="device-header">
        <div className="device-title">
          <div className="device-name">{device.name}</div>
          <div className="device-type">{device.manufacturer} {device.model}</div>
        </div>
        <div className="device-icon">
          {getDeviceIcon()}
        </div>
      </div>
      
      {renderDeviceControls()}
      
      <div className="device-actions">
        <button 
          className="identify-button"
          onClick={() => handleCommand('identify')}
          disabled={loading}
        >
          Identify
        </button>
      </div>
    </div>
  );
};

export default ZigbeeDeviceTile;