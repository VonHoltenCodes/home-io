import React from 'react';
import { useTheme } from '../utils/ThemeContext';
import './ThemeDemo.css';

const ThemeDemo = () => {
  const { theme, setTheme } = useTheme();
  
  return (
    <div className="theme-demo">
      <h2>Theme Demo and Customization</h2>
      
      <div className="theme-selector">
        <h3>Available Themes</h3>
        <div className="theme-options">
          <button 
            className={`theme-option ${theme === 'default' ? 'active' : ''}`}
            onClick={() => setTheme('default')}
          >
            <div className="theme-preview default-preview">
              <div className="grid-lines"></div>
            </div>
            <span>Default</span>
          </button>
          
          <button 
            className={`theme-option ${theme === 'night' ? 'active' : ''}`}
            onClick={() => setTheme('night')}
          >
            <div className="theme-preview night-preview">
              <div className="grid-lines"></div>
            </div>
            <span>Night Ops</span>
          </button>
          
          <button 
            className={`theme-option ${theme === 'retro' ? 'active' : ''}`}
            onClick={() => setTheme('retro')}
          >
            <div className="theme-preview retro-preview">
              <div className="grid-lines"></div>
            </div>
            <span>Retro</span>
          </button>
        </div>
      </div>
      
      <div className="theme-features">
        <h3>Current Theme Features</h3>
        <div className="feature-list">
          <div className="feature-item">
            <div className="feature-icon">🌐</div>
            <div className="feature-details">
              <h4>Background Grid</h4>
              <p>Consistent grid pattern across all themes with theme-specific coloring</p>
            </div>
          </div>
          
          <div className="feature-item">
            <div className="feature-icon">📺</div>
            <div className="feature-details">
              <h4>Scan Lines</h4>
              <p>Subtle CRT-inspired scan line effect for authentic visual feedback</p>
            </div>
          </div>
          
          <div className="feature-item">
            <div className="feature-icon">✨</div>
            <div className="feature-details">
              <h4>Theme-Specific Styling</h4>
              <p>Custom component styling tailored to each theme's aesthetic</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="theme-preview-box">
        <h3>Live Theme Preview</h3>
        <div className="preview-component">
          <div className="preview-device-tile">
            <div className="preview-device-header">
              <h4>Sample Device</h4>
              <div className="preview-device-status">Online</div>
            </div>
            <div className="preview-device-body">
              <div className="preview-meter">
                <div className="preview-meter-level" style={{ width: '70%' }}></div>
              </div>
              <div className="preview-controls">
                <button className="preview-button">Control</button>
                <div className="preview-indicator"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemeDemo;