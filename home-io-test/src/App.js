import React, { useState, useEffect } from 'react';
import { getSystemInfo } from './utils/api';
import Dashboard from './components/Dashboard';
import ZigbeePage from './components/ZigbeePage';
import AudioPage from './components/Audio/AudioPage';
import TeensyPage from './components/TeensyPage';
import ThemeDemo from './components/ThemeDemo';
import Navigation from './components/Navigation';
import { ThemeProvider, useTheme } from './utils/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import './App.css';
import './theme.css';

function AppContent() {
  const [systemInfo, setSystemInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');
  const { theme } = useTheme();

  useEffect(() => {
    // Fetch system information from the API
    const fetchSystemInfo = async () => {
      try {
        const data = await getSystemInfo();
        setSystemInfo(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch system info:', error);
        setError('Cannot connect to Home-IO server');
        setLoading(false);
      }
    };
    
    fetchSystemInfo();
  }, []);

  // Render the active page component
  const renderActivePage = () => {
    switch (activePage) {
      case 'zigbee':
        return <ZigbeePage />;
      case 'audio':
        return <AudioPage />;
      case 'teensy':
        return <TeensyPage />;
      case 'themes':
        return <ThemeDemo />;
      case 'dashboard':
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Home-IO Hub</h1>
        <div className="system-info">
          {loading ? (
            <p>Loading system information...</p>
          ) : error ? (
            <p className="error-text">{error}</p>
          ) : (
            <div className="system-details">
              <p>
                {systemInfo.name} v{systemInfo.version}
              </p>
              <div className="plugins-info">
                <span className="plugin-count">
                  {systemInfo.plugins?.active?.length || 0} Active Plugins
                </span>
              </div>
            </div>
          )}
        </div>
        <ThemeToggle />
      </header>
      
      <Navigation activePage={activePage} onChangePage={setActivePage} />
      
      <main className="App-content">
        {renderActivePage()}
      </main>
      
      <footer className="App-footer">
        <p>Home-IO - A Custom Home Automation Hub</p>
        <div className="theme-info">
          {theme === 'retro' && <span>RETRO MODE ACTIVATED</span>}
          {theme === 'night' && <span>NIGHT OPS MODE ENGAGED</span>}
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;