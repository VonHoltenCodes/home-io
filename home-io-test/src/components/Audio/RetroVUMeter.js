import React, { useEffect, useRef } from 'react';
import { useTheme } from '../../utils/ThemeContext';
import './RetroVUMeter.css';

const RetroVUMeter = ({ level = -20, peak = -10, showPeakHold = true }) => {
  const { theme } = useTheme();
  const canvasRef = useRef(null);
  const peakHoldRef = useRef(peak);
  const animationRef = useRef(null);
  const needlePosRef = useRef(level); // Track needle position for smoothing
  
  // Convert dB to percentage for drawing
  const dbToPercent = (db) => {
    // Scale from -60dB to 0dB
    const minDb = -60;
    const maxDb = 6;
    const limitedDb = Math.max(minDb, Math.min(maxDb, db));
    return (limitedDb - minDb) / (maxDb - minDb);
  };
  
  // Convert percentage to needle angle
  const percentToAngle = (percent) => {
    // Needle will sweep from -45 degrees (min) to 45 degrees (max)
    return -45 + (percent * 90);
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
      
      // Calculate peak hold position
      const peakHoldPercent = dbToPercent(peakHoldRef.current);
      
      // Smooth needle movement (lagging behind the actual level with a bit of bounce)
      const needleTarget = level;
      // Simulate bounce physics - this creates a slight overshoot and oscillation
      const distanceToTarget = needleTarget - needlePosRef.current;
      const acceleration = distanceToTarget * 0.08; // Spring factor
      
      // Apply acceleration with some damping
      needlePosRef.current += acceleration;
      
      const needlePercent = dbToPercent(needlePosRef.current);
      const needleAngle = percentToAngle(needlePercent);
      
      if (theme === 'retro') {
        // Draw retro theme border and background
        ctx.fillStyle = '#2d2d2d';
        ctx.fillRect(0, 0, width, height);
        
        // Draw meter background (dark)
        ctx.fillStyle = '#0f0f0f';
        ctx.fillRect(4, 4, width - 8, height - 8);
        
        // Draw the semi-circular meter face
        ctx.save();
        
        // Create meter face with subtle gradient
        const arcGradient = ctx.createLinearGradient(0, height/2, width, height/2);
        arcGradient.addColorStop(0, '#111');
        arcGradient.addColorStop(0.5, '#1a1a1a');
        arcGradient.addColorStop(1, '#222');
        
        ctx.fillStyle = arcGradient;
        ctx.beginPath();
        ctx.arc(width/2, height-10, height-20, Math.PI, 0, false);
        ctx.fill();
        
        // Add tick marks and labels around the arc
        ctx.strokeStyle = '#444';
        ctx.lineWidth = 1;
        
        // Labels at important dB levels
        const labelPositions = [
          { db: -50, label: '-50' },
          { db: -35, label: '-35' },
          { db: -20, label: '-20' },
          { db: -10, label: '-10' },
          { db: -3, label: '-3' },
          { db: 0, label: '0' },
          { db: 3, label: '+3' }
        ];
        
        // Create arc tick marks
        for (let i = 0; i <= 10; i++) {
          const angle = Math.PI - (Math.PI * i / 10);
          const tickLength = i % 2 === 0 ? 10 : 5;
          
          const startX = width/2 + Math.cos(angle) * (height - 22);
          const startY = height-10 + Math.sin(angle) * (height - 22);
          const endX = width/2 + Math.cos(angle) * (height - 22 - tickLength);
          const endY = height-10 + Math.sin(angle) * (height - 22 - tickLength);
          
          ctx.beginPath();
          ctx.moveTo(startX, startY);
          ctx.lineTo(endX, endY);
          ctx.stroke();
        }
        
        // Add labels
        ctx.fillStyle = '#aaa';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        labelPositions.forEach(pos => {
          const percent = dbToPercent(pos.db);
          const angle = Math.PI - (Math.PI * percent);
          const labelX = width/2 + Math.cos(angle) * (height - 35);
          const labelY = height-10 + Math.sin(angle) * (height - 35);
          
          ctx.fillText(pos.label, labelX, labelY);
        });
        
        // Draw the pivot point
        ctx.fillStyle = '#555';
        ctx.beginPath();
        ctx.arc(width/2, height-10, 6, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw glossy effect on pivot
        ctx.fillStyle = '#777';
        ctx.beginPath();
        ctx.arc(width/2-1, height-11, 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Prepare to draw the needle
        ctx.save();
        
        // Set needle pivot point and rotation
        ctx.translate(width/2, height-10);
        ctx.rotate((needleAngle * Math.PI) / 180);
        
        // Orange glow effect
        ctx.shadowColor = '#ff6600';
        ctx.shadowBlur = 12;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Draw the needle
        const needleLength = height - 24;
        
        // Create a gradient for the needle
        const needleGradient = ctx.createLinearGradient(0, -needleLength, 0, 0);
        needleGradient.addColorStop(0, '#ff9500');
        needleGradient.addColorStop(0.7, '#ff6600');
        needleGradient.addColorStop(1, '#ff4400');
        
        // Draw the main needle body
        ctx.fillStyle = needleGradient;
        ctx.beginPath();
        ctx.moveTo(-1, 0);   // Needle base left
        ctx.lineTo(1, 0);    // Needle base right
        ctx.lineTo(0.5, -needleLength);  // Needle tip
        ctx.lineTo(-0.5, -needleLength); // Needle tip
        ctx.closePath();
        ctx.fill();
        
        // Add a highlight line to the needle
        ctx.strokeStyle = '#ffcc00';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, -needleLength);
        ctx.stroke();
        
        // Add needle tip
        ctx.fillStyle = '#ffcc00';
        ctx.beginPath();
        ctx.arc(0, -needleLength, 1, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore(); // Restore from needle drawing
        
        // Draw peak hold indicator as a small tick mark
        if (showPeakHold && peakHoldPercent > 0) {
          const peakAngle = percentToAngle(peakHoldPercent) * Math.PI / 180;
          
          ctx.save();
          ctx.translate(width/2, height-10);
          
          ctx.strokeStyle = '#ff0000';
          ctx.lineWidth = 2;
          
          const peakTickLength = 8;
          const peakTickStart = height - 24;
          const peakTickEnd = peakTickStart - peakTickLength;
          
          ctx.beginPath();
          ctx.moveTo(
            Math.cos(peakAngle) * peakTickStart,
            Math.sin(peakAngle) * peakTickStart
          );
          ctx.lineTo(
            Math.cos(peakAngle) * peakTickEnd,
            Math.sin(peakAngle) * peakTickEnd
          );
          ctx.stroke();
          
          ctx.restore();
        }
        
        ctx.restore(); // Restore from VU meter face drawing
      } else {
        // Modern theme
        // Draw background
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(0, 0, width, height);
        
        // Draw meter face
        ctx.fillStyle = '#f5f5f5';
        ctx.beginPath();
        ctx.arc(width/2, height-10, height-20, Math.PI, 0, false);
        ctx.fill();
        
        // Add tick marks
        ctx.strokeStyle = '#999';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= 10; i++) {
          const angle = Math.PI - (Math.PI * i / 10);
          const tickLength = i % 2 === 0 ? 10 : 5;
          
          const startX = width/2 + Math.cos(angle) * (height - 22);
          const startY = height-10 + Math.sin(angle) * (height - 22);
          const endX = width/2 + Math.cos(angle) * (height - 22 - tickLength);
          const endY = height-10 + Math.sin(angle) * (height - 22 - tickLength);
          
          ctx.beginPath();
          ctx.moveTo(startX, startY);
          ctx.lineTo(endX, endY);
          ctx.stroke();
        }
        
        // Add colored zones
        const greenZone = ctx.createLinearGradient(width * 0.3, 0, width * 0.7, 0);
        greenZone.addColorStop(0, 'rgba(0, 180, 0, 0.2)');
        greenZone.addColorStop(1, 'rgba(180, 180, 0, 0.2)');
        
        const redZone = ctx.createLinearGradient(width * 0.7, 0, width * 0.9, 0);
        redZone.addColorStop(0, 'rgba(180, 180, 0, 0.2)');
        redZone.addColorStop(1, 'rgba(180, 0, 0, 0.2)');
        
        // Draw green zone
        ctx.fillStyle = greenZone;
        ctx.beginPath();
        ctx.arc(width/2, height-10, height-22, Math.PI, Math.PI * 0.3, false);
        ctx.lineTo(width/2, height-10);
        ctx.closePath();
        ctx.fill();
        
        // Draw red zone
        ctx.fillStyle = redZone;
        ctx.beginPath();
        ctx.arc(width/2, height-10, height-22, Math.PI * 0.3, 0, false);
        ctx.lineTo(width/2, height-10);
        ctx.closePath();
        ctx.fill();
        
        // Add labels
        ctx.fillStyle = '#555';
        ctx.font = '8px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const modernLabels = [
          { value: 0, label: '-50' },
          { value: 0.25, label: '-20' },
          { value: 0.5, label: '-10' },
          { value: 0.75, label: '-3' },
          { value: 0.9, label: '0' },
          { value: 1, label: '+3' }
        ];
        
        modernLabels.forEach(pos => {
          const angle = Math.PI - (Math.PI * pos.value);
          const labelX = width/2 + Math.cos(angle) * (height - 35);
          const labelY = height-10 + Math.sin(angle) * (height - 35);
          
          ctx.fillText(pos.label, labelX, labelY);
        });
        
        // Draw the pivot point
        ctx.fillStyle = '#333';
        ctx.beginPath();
        ctx.arc(width/2, height-10, 4, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw the needle
        ctx.save();
        ctx.translate(width/2, height-10);
        ctx.rotate((needleAngle * Math.PI) / 180);
        
        // Draw needle
        ctx.fillStyle = '#cc0000';
        ctx.beginPath();
        ctx.moveTo(-1, 0);
        ctx.lineTo(1, 0);
        ctx.lineTo(0, -height+24);
        ctx.closePath();
        ctx.fill();
        
        ctx.restore();
        
        // Draw peak hold indicator
        if (showPeakHold && peakHoldPercent > 0) {
          const peakAngle = percentToAngle(peakHoldPercent) * Math.PI / 180;
          
          ctx.save();
          ctx.translate(width/2, height-10);
          
          ctx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
          ctx.lineWidth = 2;
          
          const peakTickLength = 6;
          const peakTickStart = height - 25;
          const peakTickEnd = peakTickStart - peakTickLength;
          
          ctx.beginPath();
          ctx.moveTo(
            Math.cos(peakAngle) * peakTickStart,
            Math.sin(peakAngle) * peakTickStart
          );
          ctx.lineTo(
            Math.cos(peakAngle) * peakTickEnd,
            Math.sin(peakAngle) * peakTickEnd
          );
          ctx.stroke();
          
          ctx.restore();
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
      <canvas ref={canvasRef} width="200" height="120" />
      <div className="level-indicator">{Math.round(level)}dB</div>
    </div>
  );
};

export default RetroVUMeter;