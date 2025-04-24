import React, { useState, useEffect } from 'react';
import RetroDeviceTileWrapper from '../RetroDeviceTileWrapper';
import RetroVUMeter from './RetroVUMeter';
import { useTheme } from '../../utils/ThemeContext';
import { sendAudioDeviceCommand } from '../../utils/api';
import './RetroStereoInterface.css';

const RetroStereoInterface = ({ device }) => {
  const { theme } = useTheme();
  const [volume, setVolume] = useState(device?.volume || 0);
  const [mute, setMute] = useState(device?.mute || false);
  const [selectedInput, setSelectedInput] = useState(device?.current_input || 'source_tv');
  const [powerState, setPowerState] = useState(device?.power || 'off');
  const [loading, setLoading] = useState(false);
  
  // Audio meters simulation
  const [leftLevel, setLeftLevel] = useState(-30);
  const [rightLevel, setRightLevel] = useState(-30);
  const [leftPeak, setLeftPeak] = useState(-20);
  const [rightPeak, setRightPeak] = useState(-20);
  
  // Update state when device props change
  useEffect(() => {
    if (device) {
      setVolume(device.volume || 0);
      setMute(device.mute || false);
      setSelectedInput(device.current_input || 'source_tv');
      setPowerState(device.power || 'off');
    }
  }, [device]);
  
  // Simulate audio levels when playing
  useEffect(() => {
    if (powerState !== 'on' || mute) {
      setLeftLevel(-60);
      setRightLevel(-60);
      setLeftPeak(-60);
      setRightPeak(-60);
      return;
    }
    
    const interval = setInterval(() => {
      // Generate random VU meter levels based on volume
      const volumeFactor = volume / 100;
      const baseLevel = -30 + (20 * volumeFactor);
      
      // Add some randomness to simulate audio dynamics
      const leftRandom = Math.random() * 10 - 5;
      const rightRandom = Math.random() * 10 - 5;
      
      const newLeftLevel = baseLevel + leftRandom;
      const newRightLevel = baseLevel + rightRandom;
      
      setLeftLevel(newLeftLevel);
      setRightLevel(newRightLevel);
      
      // Update peak if new level is higher
      if (newLeftLevel > leftPeak) {
        setLeftPeak(newLeftLevel);
      }
      
      if (newRightLevel > rightPeak) {
        setRightPeak(newRightLevel);
      }
    }, 100);
    
    return () => clearInterval(interval);
  }, [powerState, volume, mute]);
  
  const handleVolumeChange = (e) => {
    const newVolume = parseInt(e.target.value, 10);
    setVolume(newVolume);
    
    if (device?.id) {
      setLoading(true);
      sendAudioDeviceCommand(device.id, 'volume', { level: newVolume })
        .catch(error => console.error('Failed to set volume:', error))
        .finally(() => setLoading(false));
    }
  };
  
  const handleMuteToggle = () => {
    const newMute = !mute;
    setMute(newMute);
    
    if (device?.id) {
      setLoading(true);
      sendAudioDeviceCommand(device.id, 'mute', { state: newMute })
        .catch(error => console.error('Failed to toggle mute:', error))
        .finally(() => setLoading(false));
    }
  };
  
  const handleInputChange = (input) => {
    setSelectedInput(input);
    
    if (device?.id) {
      setLoading(true);
      sendAudioDeviceCommand(device.id, 'input', { source: input })
        .catch(error => console.error('Failed to change input:', error))
        .finally(() => setLoading(false));
    }
  };
  
  const handlePowerToggle = () => {
    const newPowerState = powerState === 'on' ? 'off' : 'on';
    setPowerState(newPowerState);
    
    if (device?.id) {
      setLoading(true);
      sendAudioDeviceCommand(device.id, 'power', { state: newPowerState })
        .catch(error => console.error('Failed to toggle power:', error))
        .finally(() => setLoading(false));
    }
  };
  
  const isRetroTheme = theme === 'retro';
  
  // Define styles for retro and modern themes
  const knobStyle = isRetroTheme
    ? { transform: `rotate(${(volume / 100) * 270 - 135}deg)` }
    : {};
  
  const wrapperClass = `stereo-interface ${powerState === 'on' ? 'powered-on' : 'powered-off'}`;
  
  // Input buttons for different themes
  const renderInputButtons = () => {
    const inputs = [
      { id: 'source_tv', label: 'TV' },
      { id: 'source_phono', label: 'PHONO' },
      { id: 'source_spotify', label: 'SPOTIFY' },
      { id: 'source_aux', label: 'AUX' }
    ];
    
    if (isRetroTheme) {
      return (
        <div className="retro-input-selector">
          <div className="retro-input-label">INPUT</div>
          <div className="retro-input-buttons">
            {inputs.map(input => (
              <button
                key={input.id}
                className={`retro-input-button ${selectedInput === input.id ? 'active' : ''}`}
                onClick={() => handleInputChange(input.id)}
              >
                <div className="retro-button-led"></div>
                <div className="retro-button-label">{input.label}</div>
              </button>
            ))}
          </div>
        </div>
      );
    }
    
    return (
      <div className="input-selector">
        <label>Input Source</label>
        <div className="input-buttons">
          {inputs.map(input => (
            <button
              key={input.id}
              className={selectedInput === input.id ? 'active' : ''}
              onClick={() => handleInputChange(input.id)}
            >
              {input.label}
            </button>
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <RetroDeviceTileWrapper deviceName={device?.name || 'Audio Receiver'} deviceType="AUDIO">
      <div className={`${wrapperClass} ${loading ? 'loading' : ''}`}>
        {loading && <div className="loading-overlay"><div className="loading-spinner"></div></div>}
        {isRetroTheme ? (
          <div className="retro-stereo-container">
            <div className="retro-control-section">
              <div className="retro-power-section">
                <button className={`retro-power-button ${powerState === 'on' ? 'on' : 'off'}`} onClick={handlePowerToggle}>
                  <div className="power-led"></div>
                </button>
                <div className="retro-power-label">POWER</div>
              </div>
              
              <div className="retro-volume-control">
                <div className="retro-volume-knob" style={knobStyle}>
                  <div className="retro-knob-marker"></div>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={volume} 
                  onChange={handleVolumeChange}
                  className="retro-volume-slider"
                />
                <div className="retro-volume-label">VOLUME</div>
                <button 
                  className={`retro-mute-button ${mute ? 'active' : ''}`}
                  onClick={handleMuteToggle}
                >
                  MUTE
                </button>
              </div>
            </div>
            
            <div className="retro-vu-section">
              <div className="retro-meter-label">LEFT</div>
              <RetroVUMeter level={leftLevel} peak={leftPeak} showPeakHold={true} />
              <div className="retro-meter-label">RIGHT</div>
              <RetroVUMeter level={rightLevel} peak={rightPeak} showPeakHold={true} />
            </div>
            
            {renderInputButtons()}
          </div>
        ) : (
          <div className="modern-stereo-container">
            <div className="control-section">
              <div className="power-control">
                <button 
                  className={`power-button ${powerState === 'on' ? 'on' : 'off'}`}
                  onClick={handlePowerToggle}
                >
                  {powerState === 'on' ? 'Turn Off' : 'Turn On'}
                </button>
              </div>
              
              <div className="volume-control">
                <label>Volume ({volume}%)</label>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={volume} 
                  onChange={handleVolumeChange} 
                />
                <button 
                  className={`mute-button ${mute ? 'active' : ''}`}
                  onClick={handleMuteToggle}
                >
                  {mute ? 'Unmute' : 'Mute'}
                </button>
              </div>
            </div>
            
            <div className="meters-section">
              <div className="meter-container">
                <label>Left Channel</label>
                <RetroVUMeter level={leftLevel} peak={leftPeak} showPeakHold={true} />
              </div>
              <div className="meter-container">
                <label>Right Channel</label>
                <RetroVUMeter level={rightLevel} peak={rightPeak} showPeakHold={true} />
              </div>
            </div>
            
            {renderInputButtons()}
          </div>
        )}
      </div>
    </RetroDeviceTileWrapper>
  );
};

export default RetroStereoInterface;