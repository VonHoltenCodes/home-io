import React, { useState } from 'react';
import { setSmartPlugState } from '../../utils/api';
import RetroDeviceTileWrapper from '../RetroDeviceTileWrapper';
import { useTheme } from '../../utils/ThemeContext';
import './SmartPlugTile.css';

const SmartPlugTile = ({ smartPlug, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const { theme } = useTheme();
  
  const handleToggle = async () => {
    setLoading(true);
    try {
      await setSmartPlugState(smartPlug.id, !smartPlug.state);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to toggle smart plug:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <RetroDeviceTileWrapper 
      deviceName={theme === 'retro' ? null : smartPlug.name}
      deviceType="SMART-PLUG"
    >
      <div className={`smart-plug-tile ${smartPlug.state ? 'on' : 'off'}`}>
        {theme === 'retro' ? null : (
          <div className="smart-plug-name">{smartPlug.name}</div>
        )}
        
        <div className="smart-plug-icon">
          {smartPlug.state ? '🔌' : '⚪'}
        </div>
        
        <div className="smart-plug-state">
          {smartPlug.state ? 'On' : 'Off'}
        </div>
        
        <div className="smart-plug-info">
          <div className="manufacturer">
            {smartPlug.manufacturer} {smartPlug.model}
          </div>
          <div className="connection-status">
            {smartPlug.online ? '🟢 Online' : '🔴 Offline'}
          </div>
        </div>
        
        <button 
          className={`toggle-button ${smartPlug.state ? 'on' : 'off'}`}
          onClick={handleToggle}
          disabled={loading || !smartPlug.online}
        >
          {loading ? 'Updating...' : (smartPlug.state ? 'Turn Off' : 'Turn On')}
        </button>
      </div>
    </RetroDeviceTileWrapper>
  );
};

export default SmartPlugTile;