import React, { useEffect, useRef } from 'react';
import { useTheme } from '../../utils/ThemeContext';
import './RetroVUMeter.css';

const RetroVUMeter = ({ level = -20, peak = -10, showPeakHold = true }) => {
  const { theme } = useTheme();
  const canvasRef = useRef(null);
  const peakHoldRef = useRef(peak);
  const animationRef = useRef(null);
  
  // Convert dB to percentage for drawing
  const dbToPercent = (db) => {
    // Scale from -60dB to 0dB
    const minDb = -60;
    const maxDb = 6;
    const limitedDb = Math.max(minDb, Math.min(maxDb, db));
    return (limitedDb - minDb) / (maxDb - minDb);
  };

  // Get gradient color based on level and theme
  const getLevelColor = (percent) => {
    if (theme === 'night') {
      // Night theme (green-based)
      if (percent < 0.6) return '#00cc00';
      if (percent < 0.8) return '#aaff00';
      return '#ff0000';
    } else if (theme === 'retro') {
      // Retro theme (orange-based)
      if (percent < 0.6) return '#ff8c69';
      if (percent < 0.8) return '#ffcc00';
      return '#ff0000';
    } else {
      // Default theme
      if (percent < 0.6) return 'green';
      if (percent < 0.8) return 'yellow';
      return 'red';
    }
  };
  
  useEffect(() => {
    // Update peak hold value
    if (peak > peakHoldRef.current) {
      peakHoldRef.current = peak;
    }
    
    // Setup decay for peak hold
    const decayInterval = setInterval(() => {
      if (peakHoldRef.current > peak) {
        peakHoldRef.current -= 0.5;
      }
    }, 1000);
    
    return () => {
      clearInterval(decayInterval);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [peak]);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    const draw = () => {
      // Clear canvas
      ctx.clearRect(0, 0, width, height);
      
      // Calculate level and peak positions
      const levelPercent = dbToPercent(level);
      const peakPercent = dbToPercent(peak);
      const peakHoldPercent = dbToPercent(peakHoldRef.current);
      
      const levelWidth = width * levelPercent;
      const peakWidth = width * peakPercent;
      const peakHoldWidth = width * peakHoldPercent;
      
      // Draw border and background
      if (theme === 'retro') {
        // Draw retro theme border
        ctx.fillStyle = '#2d2d2d';
        ctx.fillRect(0, 0, width, height);
        
        // Draw meter background (dark)
        ctx.fillStyle = '#0f0f0f';
        ctx.fillRect(4, 4, width - 8, height - 8);
        
        // Add tick marks
        ctx.fillStyle = '#4d4d4d';
        const tickCount = 10;
        for (let i = 1; i < tickCount; i++) {
          const x = 4 + (width - 8) * (i / tickCount);
          ctx.fillRect(x, 4, 1, height - 8);
        }
        
        // Draw level meter (gradient)
        if (levelWidth > 4) {
          const levelColor = getLevelColor(levelPercent);
          ctx.fillStyle = levelColor;
          ctx.fillRect(4, 4, levelWidth - 4, height - 8);
        }
        
        // Draw peak indicator
        if (peakWidth > 4) {
          ctx.fillStyle = 'white';
          ctx.fillRect(peakWidth - 1, 4, 2, height - 8);
        }
        
        // Draw peak hold indicator
        if (showPeakHold && peakHoldWidth > 4) {
          ctx.fillStyle = 'red';
          ctx.fillRect(peakHoldWidth - 1, 4, 2, height - 8);
        }
        
        // Add labels at important levels
        ctx.fillStyle = 'white';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Labels at -20dB, -10dB, -3dB, 0dB
        const labelPositions = [
          { db: -20, label: '-20' },
          { db: -10, label: '-10' },
          { db: -3, label: '-3' },
          { db: 0, label: '0' },
          { db: 3, label: '+3' }
        ];
        
        labelPositions.forEach(pos => {
          const x = 4 + (width - 8) * dbToPercent(pos.db);
          ctx.fillText(pos.label, x, height / 2);
        });
      } else {
        // Modern theme
        // Draw background
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(0, 0, width, height);
        
        // Draw level meter
        if (levelWidth > 0) {
          const gradient = ctx.createLinearGradient(0, 0, width, 0);
          gradient.addColorStop(0, 'green');
          gradient.addColorStop(0.6, 'yellow');
          gradient.addColorStop(0.8, 'orange');
          gradient.addColorStop(1, 'red');
          
          ctx.fillStyle = gradient;
          ctx.fillRect(0, 0, levelWidth, height);
        }
        
        // Draw peak indicator
        if (peakWidth > 0) {
          ctx.fillStyle = 'white';
          ctx.fillRect(peakWidth - 1, 0, 2, height);
        }
        
        // Draw peak hold indicator
        if (showPeakHold && peakHoldWidth > 0) {
          ctx.fillStyle = 'red';
          ctx.fillRect(peakHoldWidth - 1, 0, 2, height);
        }
      }
      
      // Continue animation
      animationRef.current = requestAnimationFrame(draw);
    };
    
    // Start animation
    draw();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [level, peak, showPeakHold, theme]);
  
  // Determine class based on theme
  const meterClass = theme === 'retro' ? 'retro-vu-meter' : 'vu-meter';
  
  return (
    <div className={meterClass}>
      <canvas ref={canvasRef} width="200" height="40" />
      <div className="level-indicator">{Math.round(level)}dB</div>
    </div>
  );
};

export default RetroVUMeter;