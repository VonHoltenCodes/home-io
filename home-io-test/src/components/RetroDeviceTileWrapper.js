import React from 'react';
import { useTheme } from '../utils/ThemeContext';

const generateRandomID = () => {
  const hexChars = '0123456789ABCDEF';
  let id = '0x';
  for (let i = 0; i < 6; i++) {
    id += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
  }
  return id;
};

const RetroDeviceTileWrapper = ({ children, deviceName, deviceType }) => {
  const { theme } = useTheme();
  const deviceID = generateRandomID();
  
  // Only apply wrapper if in retro theme
  if (theme !== 'retro') {
    return children;
  }
  
  return (
    <div className="device-tile-wrapper">
      {/* Apply styling directly to children - in this case, the device tile */}
      <React.Fragment>
        {/* Corner label for device type */}
        <div className="device-corner-label">{deviceType || 'DEVICE'}</div>
        
        {/* Name wrapper with device ID */}
        <div className="device-name-wrapper" data-device-id={deviceID}>
          <div className="device-name">{deviceName || 'UNKNOWN DEVICE'}</div>
        </div>
        
        {/* Pass through all children */}
        {children}
      </React.Fragment>
    </div>
  );
};

export default RetroDeviceTileWrapper;