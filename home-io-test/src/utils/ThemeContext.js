import React, { createContext, useState, useContext, useEffect } from 'react';

// Create a context for theme management
const ThemeContext = createContext();

// Theme provider component
export const ThemeProvider = ({ children }) => {
  // Check if user previously selected a theme
  const savedTheme = localStorage.getItem('theme') || 'default';
  const [theme, setTheme] = useState(savedTheme);

  // Update theme in localStorage when it changes
  useEffect(() => {
    document.body.className = `theme-${theme}`;
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Toggle between available themes
  const toggleTheme = () => {
    setTheme(prevTheme => {
      switch(prevTheme) {
        case 'default':
          return 'retro';
        case 'retro':
          return 'night';
        case 'night':
        default:
          return 'default';
      }
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook for using the theme context
export const useTheme = () => useContext(ThemeContext);
