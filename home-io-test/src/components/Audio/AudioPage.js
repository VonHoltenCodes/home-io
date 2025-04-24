import React, { useState, useEffect } from 'react';
import { getAudioDevices, getAudioZones } from '../../utils/api';
import RetroStereoInterface from './RetroStereoInterface';
import ZoneControlTile from './ZoneControlTile';
import './AudioPage.css';

const AudioPage = () => {
  const [audioDevices, setAudioDevices] = useState([]);
  const [audioZones, setAudioZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAudioComponents = async () => {
    setLoading(true);
    try {
      // Fetch audio devices and zones in parallel
      const [devices, zones] = await Promise.all([
        getAudioDevices(),
        getAudioZones()
      ]);
      
      setAudioDevices(devices || []);
      setAudioZones(zones || []);
      setError(null);
    } catch (error) {
      console.error('Error fetching audio components:', error);
      setError('Failed to load audio components. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudioComponents();
    
    // Set up polling for device updates every 30 seconds
    const interval = setInterval(fetchAudioComponents, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Filter devices by type
  const receivers = audioDevices.filter(device => 
    device.type === 'yamaha_receiver' || 
    device.type === 'denon_receiver' || 
    device.type === 'audio_receiver'
  );

  return (
    <div className="audio-page">
      {loading && audioDevices.length === 0 && audioZones.length === 0 ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your audio devices...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={fetchAudioComponents}>Try Again</button>
        </div>
      ) : (
        <>
          {receivers.length > 0 && (
            <section className="device-section">
              <h2>Audio Receivers</h2>
              <div className="device-grid">
                {receivers.map(receiver => (
                  <RetroStereoInterface
                    key={receiver.id}
                    device={receiver}
                  />
                ))}
              </div>
            </section>
          )}
          
          {audioZones.length > 0 && (
            <section className="device-section">
              <h2>Audio Zones</h2>
              <div className="device-grid">
                {audioZones.map(zone => (
                  <ZoneControlTile
                    key={zone.id}
                    zone={zone}
                  />
                ))}
              </div>
            </section>
          )}
          
          {audioDevices.length === 0 && audioZones.length === 0 && (
            <div className="empty-state">
              <p>No audio devices found. Add some audio devices to get started.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AudioPage;