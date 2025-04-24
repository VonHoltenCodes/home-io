import React from 'react';
import './Navigation.css';

const Navigation = ({ activePage, onChangePage }) => {
  return (
    <nav className="main-navigation">
      <button 
        className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
        onClick={() => onChangePage('dashboard')}
      >
        Dashboard
      </button>
      
      <button 
        className={`nav-item ${activePage === 'zigbee' ? 'active' : ''}`}
        onClick={() => onChangePage('zigbee')}
      >
        Zigbee
      </button>
      
      <button 
        className={`nav-item ${activePage === 'audio' ? 'active' : ''}`}
        onClick={() => onChangePage('audio')}
      >
        Audio
      </button>
      
      <button 
        className={`nav-item ${activePage === 'thermostat' ? 'active' : ''}`}
        onClick={() => onChangePage('thermostat')}
      >
        Thermostats
      </button>
      
      <button 
        className={`nav-item ${activePage === 'smartplug' ? 'active' : ''}`}
        onClick={() => onChangePage('smartplug')}
      >
        Smart Plugs
      </button>
    </nav>
  );
};

export default Navigation;