import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [systemInfo, setSystemInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch system information from the API
    fetch('/api/system')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setSystemInfo(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  // Mock data for demonstration
  const mockDevices = [
    { id: 'light_1', name: 'Living Room Light', type: 'light', location: 'Living Room', state: { power: 'on', brightness: 80 } },
    { id: 'thermo_1', name: 'Main Thermostat', type: 'thermostat', location: 'Hallway', state: { temperature: 72, mode: 'heat' } },
    { id: 'sensor_1', name: 'Indoor Air Quality', type: 'sensor', location: 'Living Room', state: { temperature: 73, humidity: 45, aqi: 35 } },
    { id: 'lock_1', name: 'Front Door', type: 'lock', location: 'Front Door', state: { locked: true } },
  ];

  // Function to render a device tile based on type
  const renderDeviceTile = (device) => {
    const { id, name, type, location, state } = device;
    
    let tileContent;
    let tileClass = `device-tile ${type}`;
    
    switch (type) {
      case 'light':
        tileContent = (
          <>
            <div className="device-icon">💡</div>
            <div className="device-state">
              {state.power === 'on' ? `On - ${state.brightness}%` : 'Off'}
            </div>
          </>
        );
        break;
        
      case 'thermostat':
        tileContent = (
          <>
            <div className="device-icon">🌡️</div>
            <div className="device-state">
              {state.temperature}°F - {state.mode === 'heat' ? 'Heating' : 'Cooling'}
            </div>
          </>
        );
        break;
        
      case 'sensor':
        tileContent = (
          <>
            <div className="device-icon">📊</div>
            <div className="device-state">
              {state.temperature}°F, {state.humidity}% RH
              {state.aqi && <div>AQI: {state.aqi}</div>}
            </div>
          </>
        );
        break;
        
      case 'lock':
        tileContent = (
          <>
            <div className="device-icon">{state.locked ? '🔒' : '🔓'}</div>
            <div className="device-state">
              {state.locked ? 'Locked' : 'Unlocked'}
            </div>
          </>
        );
        break;
        
      default:
        tileContent = (
          <>
            <div className="device-icon">📱</div>
            <div className="device-state">
              {JSON.stringify(state)}
            </div>
          </>
        );
    }
    
    return (
      <div key={id} className={tileClass}>
        <div className="device-name">{name}</div>
        <div className="device-location">{location}</div>
        {tileContent}
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Home-IO Hub</h1>
        <div className="system-info">
          {loading ? (
            <p>Loading system information...</p>
          ) : error ? (
            <p>Error: {error}</p>
          ) : (
            <p>
              {systemInfo.name} v{systemInfo.version}
            </p>
          )}
        </div>
      </header>
      
      <main className="App-content">
        <section className="device-grid">
          <h2>Devices</h2>
          <div className="device-tiles">
            {mockDevices.map(device => renderDeviceTile(device))}
          </div>
        </section>
        
        <section className="automation-section">
          <h2>Automations</h2>
          <div className="automation-placeholder">
            <p>Automation rules will be displayed here</p>
          </div>
        </section>
      </main>
      
      <footer className="App-footer">
        <p>Home-IO - A Custom Home Automation Hub</p>
      </footer>
    </div>
  );
}

export default App;