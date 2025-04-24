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
            {/* Current Temperature Display */}
            <div className="temperature-display">
              <div className="current-value">{device.temperature}°F</div>
              {device.humidity !== undefined && 
                <div className="humidity-value">{device.humidity}% RH</div>
              }
            </div>
            
            {/* Current Mode Indicator */}
            <div className="current-mode">
              <span className="mode-label">Current Mode: </span>
              <span className={`mode-value mode-${device.mode || 'off'}`}>
                {device.mode ? device.mode.toUpperCase() : 'OFF'}
              </span>
              {device.state && 
                <span className={`state-value ${device.state !== 'idle' ? 'active' : ''}`}>
                  ({device.state !== 'idle' ? 'RUNNING' : 'IDLE'})
                </span>
              }
            </div>
            
            {/* Temperature Setpoints with Improved +/- Controls */}
            <div className="setpoint-controls">
              <div className="setpoint-section">
                <div className="setpoint-header">Temperature Control</div>
                
                <div className="setpoint-row">
                  <label className="setpoint-label">Heat:</label>
                  <div className="setpoint-buttons">
                    <button 
                      className="setpoint-button minus"
                      onClick={() => handleCommand('temperature', { 
                        value: (device.heat_setpoint || 70) - 1,
                        mode: 'heat'
                      })}
                      disabled={loading || device.mode === 'off'}
                      aria-label="Decrease heat setpoint"
                    >−</button>
                    <span className="setpoint-value">{device.heat_setpoint || 70}°</span>
                    <button 
                      className="setpoint-button plus"
                      onClick={() => handleCommand('temperature', { 
                        value: (device.heat_setpoint || 70) + 1,
                        mode: 'heat'
                      })}
                      disabled={loading || device.mode === 'off'}
                      aria-label="Increase heat setpoint"
                    >+</button>
                  </div>
                </div>
                
                <div className="setpoint-row">
                  <label className="setpoint-label">Cool:</label>
                  <div className="setpoint-buttons">
                    <button 
                      className="setpoint-button minus"
                      onClick={() => handleCommand('temperature', { 
                        value: (device.cool_setpoint || 75) - 1,
                        mode: 'cool'
                      })}
                      disabled={loading || device.mode === 'off'}
                      aria-label="Decrease cool setpoint"
                    >−</button>
                    <span className="setpoint-value">{device.cool_setpoint || 75}°</span>
                    <button 
                      className="setpoint-button plus"
                      onClick={() => handleCommand('temperature', { 
                        value: (device.cool_setpoint || 75) + 1,
                        mode: 'cool'
                      })}
                      disabled={loading || device.mode === 'off'}
                      aria-label="Increase cool setpoint"
                    >+</button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Mode Selection Buttons */}
            <div className="mode-controls-section">
              <div className="mode-header">Mode Selection</div>
              <div className="mode-controls">
                <button 
                  className={`mode-button heat ${device.mode === 'heat' ? 'active' : ''}`}
                  onClick={() => handleCommand('mode', { mode: 'heat' })}
                  disabled={loading || device.mode === 'heat'}
                >
                  Heat
                </button>
                <button 
                  className={`mode-button cool ${device.mode === 'cool' ? 'active' : ''}`}
                  onClick={() => handleCommand('mode', { mode: 'cool' })}
                  disabled={loading || device.mode === 'cool'}
                >
                  Cool
                </button>
                <button 
                  className={`mode-button off ${device.mode === 'off' ? 'active' : ''}`}
                  onClick={() => handleCommand('mode', { mode: 'off' })}
                  disabled={loading || device.mode === 'off'}
                >
                  Off
                </button>
              </div>
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