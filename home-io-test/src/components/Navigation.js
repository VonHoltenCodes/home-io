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
        className={`nav-item ${activePage === 'teensy' ? 'active' : ''}`}
        onClick={() => onChangePage('teensy')}
      >
        Teensy Sensors
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
      
      <button 
        className={`nav-item ${activePage === 'themes' ? 'active' : ''}`}
        onClick={() => onChangePage('themes')}
      >
        Themes
      </button>
    </nav>
  );
};

export default Navigation;