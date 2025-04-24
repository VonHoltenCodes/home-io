import React, { useState, useEffect } from 'react';
import { getThermostats, getSmartPlugs } from '../utils/api';
import ThermostatTile from './Thermostat/ThermostatTile';
import SmartPlugTile from './SmartPlug/SmartPlugTile';
import './Dashboard.css';

const Dashboard = () => {
  const [thermostats, setThermostats] = useState([]);
  const [smartPlugs, setSmartPlugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchDevices = async () => {
    setLoading(true);
    try {
      // Fetch devices in parallel
      const [thermostatData, smartPlugData] = await Promise.all([
        getThermostats(),
        getSmartPlugs()
      ]);
      
      setThermostats(thermostatData || []);
      setSmartPlugs(smartPlugData || []);
      setError(null);
    } catch (error) {
      console.error('Error fetching devices:', error);
      setError('Failed to load devices. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchDevices();
    
    // Set up polling for device updates every 30 seconds
    const interval = setInterval(fetchDevices, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="dashboard">
      {loading && thermostats.length === 0 && smartPlugs.length === 0 ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your smart home devices...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={fetchDevices}>Try Again</button>
        </div>
      ) : (
        <>
          {thermostats.length > 0 && (
            <section className="device-section">
              <h2>Thermostats</h2>
              <div className="device-grid">
                {thermostats.map(thermostat => (
                  <ThermostatTile 
                    key={thermostat.id} 
                    thermostat={thermostat} 
                    onUpdate={fetchDevices}
                  />
                ))}
              </div>
            </section>
          )}
          
          {smartPlugs.length > 0 && (
            <section className="device-section">
              <h2>Smart Plugs</h2>
              <div className="device-grid">
                {smartPlugs.map(smartPlug => (
                  <SmartPlugTile
                    key={smartPlug.id}
                    smartPlug={smartPlug}
                    onUpdate={fetchDevices}
                  />
                ))}
              </div>
            </section>
          )}
          
          {thermostats.length === 0 && smartPlugs.length === 0 && (
            <div className="empty-state">
              <p>No devices found. Add some devices to get started.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;