import React, { useState, useEffect } from 'react';
import ZigbeeDeviceTile from './ZigbeeDeviceTile';
import './ZigbeeDevicesGrid.css';

const ZigbeeDevicesGrid = ({ devices, onSendCommand, onRefresh }) => {
  const [filteredDevices, setFilteredDevices] = useState(devices);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    if (filter === 'all') {
      setFilteredDevices(devices);
    } else {
      setFilteredDevices(devices.filter(device => device.type === filter));
    }
  }, [devices, filter]);
  
  // Count devices by type
  const deviceCounts = devices.reduce((counts, device) => {
    const type = device.type || 'unknown';
    counts[type] = (counts[type] || 0) + 1;
    return counts;
  }, {});
  
  // Get total count
  const totalCount = devices.length;
  
  return (
    <div className="zigbee-devices-container">
      <div className="zigbee-filters">
        <button 
          className={`filter-button ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({totalCount})
        </button>
        
        {Object.keys(deviceCounts).map(type => (
          <button 
            key={type}
            className={`filter-button ${filter === type ? 'active' : ''}`}
            onClick={() => setFilter(type)}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)} ({deviceCounts[type]})
          </button>
        ))}
      </div>
      
      <div className="zigbee-devices-grid">
        {filteredDevices.map(device => (
          <ZigbeeDeviceTile 
            key={device.id}
            device={device}
            onSendCommand={onSendCommand}
          />
        ))}
        
        {filteredDevices.length === 0 && (
          <div className="no-devices-message">
            {filter === 'all' 
              ? 'No Zigbee devices found. Add some devices to get started.' 
              : `No ${filter} devices found.`}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZigbeeDevicesGrid;