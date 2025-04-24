import React from 'react';
import { useTheme } from '../utils/ThemeContext';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  
  // Determine button label based on current theme
  const getButtonLabel = () => {
    switch(theme) {
      case 'default':
        return 'RETRO MODE';
      case 'retro':
        return 'NIGHT OPS';
      case 'night':
        return 'DEFAULT MODE';
      default:
        return 'CHANGE THEME';
    }
  };
  
  // Get next theme for aria-label
  const getNextTheme = () => {
    switch(theme) {
      case 'default':
        return 'retro';
      case 'retro':
        return 'night ops';
      case 'night':
        return 'default';
      default:
        return 'next';
    }
  };
  
  return (
    <button 
      className="theme-toggle" 
      onClick={toggleTheme}
      aria-label={`Switch to ${getNextTheme()} theme`}
    >
      {getButtonLabel()}
    </button>
  );
};

export default ThemeToggle;