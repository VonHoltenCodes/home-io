import React, { useState, useEffect } from 'react';
import { setThermostatTemperature, setThermostatMode } from '../../utils/api';
import { useTheme } from '../../utils/ThemeContext';
import RetroDeviceTileWrapper from '../RetroDeviceTileWrapper';
import './ThermostatTile.css';

const ThermostatTile = ({ thermostat, onUpdate }) => {
  // Define safe default values for all properties to handle any missing data
  const safeThermo = {
    id: thermostat?.id || 'unknown',
    name: thermostat?.name || 'Unknown Thermostat',
    mode: thermostat?.mode || 'off',
    state: thermostat?.state || 'idle',
    current_temperature: thermostat?.current_temperature || 70,
    current_humidity: thermostat?.current_humidity || null,
    heat_setpoint: thermostat?.heat_setpoint || 68,
    cool_setpoint: thermostat?.cool_setpoint || 75,
    has_room_sensors: thermostat?.has_room_sensors || false,
    room_sensors_count: thermostat?.room_sensors_count || 0,
    manufacturer: thermostat?.manufacturer || 'Unknown',
    model: thermostat?.model || 'Unknown',
  };
  
  // Determine the current operating mode and initial temperature setpoint
  const initialTemp = safeThermo.mode === 'cool' 
    ? safeThermo.cool_setpoint 
    : (safeThermo.mode === 'heat' ? safeThermo.heat_setpoint : 70);
  
  const [temperature, setTemperature] = useState(initialTemp);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const { theme } = useTheme();
  
  // Update temperature state when thermostat mode changes
  useEffect(() => {
    if (safeThermo.mode === 'cool') {
      setTemperature(safeThermo.cool_setpoint);
    } else if (safeThermo.mode === 'heat') {
      setTemperature(safeThermo.heat_setpoint);
    }
  }, [safeThermo.mode, safeThermo.cool_setpoint, safeThermo.heat_setpoint]);
  
  const handleTemperatureChange = (e) => {
    setTemperature(parseInt(e.target.value, 10));
  };
  
  const handleSetTemperature = async () => {
    // Don't allow temperature updates if in "off" mode
    if (safeThermo.mode === 'off') {
      setIsEditing(false);
      return;
    }
    
    setLoading(true);
    try {
      await setThermostatTemperature(
        safeThermo.id, 
        temperature, 
        safeThermo.mode
      );
      setIsEditing(false);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to set temperature:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleModeChange = async (mode) => {
    if (mode === safeThermo.mode) return; // Already in this mode
    
    setLoading(true);
    try {
      await setThermostatMode(safeThermo.id, mode);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to change mode:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Determine if heating or cooling is active
  const isActive = safeThermo.state !== 'idle';
  
  return (
    <RetroDeviceTileWrapper 
      deviceName={theme === 'retro' ? null : safeThermo.name}
      deviceType="THERMOSTAT"
    >
      <div className={`thermostat-tile ${isActive ? 'active' : ''}`}>
        {theme !== 'retro' && <div className="thermostat-name">{safeThermo.name}</div>}
        
        <div className="thermostat-temperature">
          {safeThermo.current_temperature}°
          {theme === 'retro' && <span className="current-temp-label">CURRENT</span>}
        </div>
        
        <div className="thermostat-details">
          <div className="thermostat-humidity">
            {safeThermo.current_humidity ? `${safeThermo.current_humidity}% Humidity` : ''}
          </div>
          
          <div className="thermostat-mode">
            {theme === 'retro' ? 'STATUS: ' : 'Mode: '}
            <span className={`mode-${safeThermo.mode}`}>{safeThermo.mode}</span>
          </div>
        </div>
        
        {/* Setpoint display - show different UI based on mode */}
        <div className={`thermostat-setpoint ${safeThermo.mode === 'off' ? 'off-mode' : ''}`}>
          {safeThermo.mode === 'off' ? (
            <div className="off-mode-display">
              {theme === 'retro' ? (
                <div className="off-mode-message">SYSTEM OFF - NO TARGET</div>
              ) : (
                <div className="off-mode-message">System is off. No target temperature.</div>
              )}
            </div>
          ) : isEditing ? (
            <div className="temperature-editor">
              {theme === 'retro' && <div className="editor-instruction">ADJUST TARGET TEMPERATURE</div>}
              <input 
                type="range" 
                min="60" 
                max="85" 
                value={temperature} 
                onChange={handleTemperatureChange}
              />
              <div className="temperature-value">{temperature}°</div>
              <div className="editor-buttons">
                <button 
                  onClick={handleSetTemperature} 
                  disabled={loading}
                  className="set-temp-button"
                >
                  {loading ? 'Setting...' : 'Set'}
                </button>
                <button 
                  onClick={() => setIsEditing(false)} 
                  className="cancel-button"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div 
              className="setpoint-display" 
              onClick={() => setIsEditing(true)}
            >
              <span className="setpoint-label">
                {theme === 'retro' ? '' : 'Target: '}
              </span>
              <span className="setpoint-value">
                {safeThermo.mode === 'cool' 
                  ? `${safeThermo.cool_setpoint}°` 
                  : (safeThermo.mode === 'heat' 
                    ? `${safeThermo.heat_setpoint}°` 
                    : '—')}
              </span>
            </div>
          )}
        </div>
        
        {/* Clear mode select buttons */}
        <div className="thermostat-controls">
          <button 
            className={`mode-button heat-button ${safeThermo.mode === 'heat' ? 'active' : ''}`}
            onClick={() => handleModeChange('heat')}
            disabled={loading || safeThermo.mode === 'heat'}
          >
            Heat
          </button>
          <button 
            className={`mode-button cool-button ${safeThermo.mode === 'cool' ? 'active' : ''}`}
            onClick={() => handleModeChange('cool')}
            disabled={loading || safeThermo.mode === 'cool'}
          >
            Cool
          </button>
          <button 
            className={`mode-button off-button ${safeThermo.mode === 'off' ? 'active' : ''}`}
            onClick={() => handleModeChange('off')}
            disabled={loading || safeThermo.mode === 'off'}
          >
            Off
          </button>
        </div>
        
        {/* Display room sensors badge if available */}
        {safeThermo.has_room_sensors && (
          <div className="room-sensors-badge">
            {safeThermo.room_sensors_count} Room Sensors
          </div>
        )}
        
        {/* Add brand info in retro theme */}
        {theme === 'retro' && (
          <div className="thermostat-brand">
            <span className="manufacturer">{safeThermo.manufacturer}</span>
            <span className="model-number">{safeThermo.model}</span>
          </div>
        )}
      </div>
    </RetroDeviceTileWrapper>
  );
};

export default ThermostatTile;