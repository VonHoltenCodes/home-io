import React, { useState } from 'react';
import { setThermostatTemperature, setThermostatMode } from '../../utils/api';
import './ThermostatTile.css';

const ThermostatTile = ({ thermostat, onUpdate }) => {
  const [temperature, setTemperature] = useState(
    thermostat.mode === 'cool' 
      ? thermostat.cool_setpoint 
      : thermostat.heat_setpoint
  );
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const handleTemperatureChange = (e) => {
    setTemperature(parseInt(e.target.value, 10));
  };
  
  const handleSetTemperature = async () => {
    setLoading(true);
    try {
      await setThermostatTemperature(
        thermostat.id, 
        temperature, 
        thermostat.mode
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
    setLoading(true);
    try {
      await setThermostatMode(thermostat.id, mode);
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
  const isActive = thermostat.state !== 'idle';
  
  return (
    <div className={`thermostat-tile ${isActive ? 'active' : ''}`}>
      <div className="thermostat-name">{thermostat.name}</div>
      <div className="thermostat-temperature">
        {thermostat.current_temperature}°
      </div>
      
      <div className="thermostat-details">
        <div className="thermostat-humidity">
          {thermostat.current_humidity ? `${thermostat.current_humidity}% Humidity` : ''}
        </div>
        
        <div className="thermostat-mode">
          Mode: <span className={`mode-${thermostat.mode}`}>{thermostat.mode}</span>
        </div>
      </div>
      
      <div className="thermostat-setpoint">
        {isEditing ? (
          <div className="temperature-editor">
            <input 
              type="range" 
              min="60" 
              max="85" 
              value={temperature} 
              onChange={handleTemperatureChange}
            />
            <div className="temperature-value">{temperature}°</div>
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
        ) : (
          <div 
            className="setpoint-display" 
            onClick={() => setIsEditing(true)}
          >
            <span className="setpoint-label">Target: </span>
            <span className="setpoint-value">
              {thermostat.mode === 'cool' 
                ? `${thermostat.cool_setpoint}°` 
                : `${thermostat.heat_setpoint}°`}
            </span>
          </div>
        )}
      </div>
      
      <div className="thermostat-controls">
        <button 
          className={`mode-button ${thermostat.mode === 'heat' ? 'active' : ''}`}
          onClick={() => handleModeChange('heat')}
          disabled={loading || thermostat.mode === 'heat'}
        >
          Heat
        </button>
        <button 
          className={`mode-button ${thermostat.mode === 'cool' ? 'active' : ''}`}
          onClick={() => handleModeChange('cool')}
          disabled={loading || thermostat.mode === 'cool'}
        >
          Cool
        </button>
        <button 
          className={`mode-button ${thermostat.mode === 'off' ? 'active' : ''}`}
          onClick={() => handleModeChange('off')}
          disabled={loading || thermostat.mode === 'off'}
        >
          Off
        </button>
      </div>
      
      {thermostat.has_room_sensors && (
        <div className="room-sensors-badge">
          {thermostat.room_sensors_count} Room Sensors
        </div>
      )}
    </div>
  );
};

export default ThermostatTile;