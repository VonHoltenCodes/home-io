import React, { useState, useEffect } from 'react';
import { getZigbeeDevices, sendZigbeeCommand, identifyZigbeeDevice } from '../utils/api';
import ZigbeeDevicesGrid from './ZigbeeDevice/ZigbeeDevicesGrid';
import './ZigbeePage.css';

const ZigbeePage = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchDevices = async () => {
    setLoading(true);
    try {
      const data = await getZigbeeDevices();
      setDevices(data || []);
      setError(null);
    } catch (error) {
      console.error('Error fetching Zigbee devices:', error);
      setError('Failed to load Zigbee devices. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchDevices();
    
    // Set up polling every 30 seconds
    const interval = setInterval(fetchDevices, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  const handleSendCommand = async (deviceId, command, params) => {
    try {
      await sendZigbeeCommand(deviceId, command, params);
      // Refresh device list after command
      fetchDevices();
    } catch (error) {
      console.error(`Error sending command to device ${deviceId}:`, error);
      // Handle error (could show a toast notification)
    }
  };
  
  const handleIdentify = async (deviceId) => {
    try {
      await identifyZigbeeDevice(deviceId);
      // No need to refresh since identify doesn't change device state
    } catch (error) {
      console.error(`Error identifying device ${deviceId}:`, error);
    }
  };
  
  return (
    <div className="zigbee-page">
      <div className="page-header">
        <h1>Zigbee Devices</h1>
        <button 
          className="refresh-button"
          onClick={fetchDevices}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      
      {loading && devices.length === 0 ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading Zigbee devices...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={fetchDevices}>Try Again</button>
        </div>
      ) : (
        <ZigbeeDevicesGrid 
          devices={devices}
          onSendCommand={handleSendCommand}
          onRefresh={fetchDevices}
        />
      )}
    </div>
  );
};

export default ZigbeePage;