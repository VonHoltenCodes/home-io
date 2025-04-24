import React, { useState, useEffect } from 'react';
import { useTheme } from '../../utils/ThemeContext';
import RetroDeviceTileWrapper from '../RetroDeviceTileWrapper';
import { sendAudioZoneCommand, getAudioSources } from '../../utils/api';
import './ZoneControlTile.css';

const ZoneControlTile = ({ zone }) => {
  const { theme } = useTheme();
  const [volume, setVolume] = useState(zone?.volume || 0);
  const [power, setPower] = useState(zone?.power === 'on');
  const [currentSource, setCurrentSource] = useState(zone?.current_source || '');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Load available sources
  useEffect(() => {
    const loadSources = async () => {
      try {
        setLoading(true);
        const sourcesData = await getAudioSources();
        setSources(sourcesData);
      } catch (error) {
        console.error('Failed to load audio sources:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadSources();
  }, []);
  
  // Update state when zone props change
  useEffect(() => {
    if (zone) {
      setVolume(zone.volume || 0);
      setPower(zone.power === 'on');
      setCurrentSource(zone.current_source || '');
    }
  }, [zone]);
  
  const handleVolumeChange = (e) => {
    const newVolume = parseInt(e.target.value, 10);
    setVolume(newVolume);
    
    if (zone?.id) {
      setActionLoading(true);
      sendAudioZoneCommand(zone.id, 'volume', { level: newVolume })
        .catch(error => console.error('Failed to set volume:', error))
        .finally(() => setActionLoading(false));
    }
  };
  
  const handlePowerToggle = () => {
    const newPower = !power;
    setPower(newPower);
    
    if (zone?.id) {
      setActionLoading(true);
      sendAudioZoneCommand(zone.id, 'power', { state: newPower ? 'on' : 'off' })
        .catch(error => console.error('Failed to toggle power:', error))
        .finally(() => setActionLoading(false));
    }
  };
  
  const handleSourceChange = (sourceId) => {
    setCurrentSource(sourceId);
    
    if (zone?.id) {
      setActionLoading(true);
      sendAudioZoneCommand(zone.id, 'source', { source_id: sourceId })
        .catch(error => console.error('Failed to change source:', error))
        .finally(() => setActionLoading(false));
    }
  };
  
  // Render source selection elements
  const renderSourceSelection = () => {
    if (loading) {
      return <div className="source-loading">Loading sources...</div>;
    }
    
    if (theme === 'retro') {
      return (
        <div className="retro-source-selection">
          <div className="retro-source-label">SOURCE</div>
          <div className="retro-source-buttons">
            {sources.map(source => (
              <button
                key={source.id}
                className={`retro-source-button ${currentSource === source.id ? 'active' : ''}`}
                onClick={() => handleSourceChange(source.id)}
              >
                <div className="retro-source-led"></div>
                <div className="retro-source-name">{source.name}</div>
              </button>
            ))}
          </div>
        </div>
      );
    }
    
    return (
      <div className="source-selection">
        <label>Source</label>
        <select
          value={currentSource}
          onChange={(e) => handleSourceChange(e.target.value)}
          disabled={!power}
        >
          <option value="">Select Source</option>
          {sources.map(source => (
            <option key={source.id} value={source.id}>
              {source.name}
            </option>
          ))}
        </select>
      </div>
    );
  };
  
  // Main render
  return (
    <RetroDeviceTileWrapper deviceName={zone?.name || 'Audio Zone'} deviceType="ZONE">
      <div className={`zone-control ${power ? 'powered-on' : 'powered-off'} ${actionLoading ? 'loading' : ''}`}>
        {actionLoading && <div className="loading-overlay"><div className="loading-spinner"></div></div>}
        {theme === 'retro' ? (
          <div className="retro-zone-container">
            <div className="retro-zone-power">
              <button 
                className={`retro-zone-power-button ${power ? 'on' : 'off'}`}
                onClick={handlePowerToggle}
              >
                <div className="retro-zone-power-led"></div>
              </button>
              <div className="retro-zone-power-label">POWER</div>
            </div>
            
            <div className="retro-zone-volume">
              <div className="retro-zone-volume-display">
                <div className="retro-zone-volume-value">{volume}</div>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={handleVolumeChange}
                disabled={!power}
                className="retro-zone-volume-slider"
              />
              <div className="retro-zone-volume-label">VOLUME</div>
            </div>
            
            {renderSourceSelection()}
          </div>
        ) : (
          <div className="modern-zone-container">
            <div className="zone-header">
              <button 
                className={`zone-power-button ${power ? 'on' : 'off'}`}
                onClick={handlePowerToggle}
              >
                {power ? 'Turn Off' : 'Turn On'}
              </button>
            </div>
            
            <div className="zone-controls">
              <div className="zone-volume">
                <label>Volume: {volume}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={handleVolumeChange}
                  disabled={!power}
                />
              </div>
              
              {renderSourceSelection()}
            </div>
          </div>
        )}
      </div>
    </RetroDeviceTileWrapper>
  );
};

export default ZoneControlTile;