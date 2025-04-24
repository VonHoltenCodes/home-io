import React, { useState, useEffect } from 'react';
import { getSystemInfo } from './utils/api';
import Dashboard from './components/Dashboard';
import ZigbeePage from './components/ZigbeePage';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  const [systemInfo, setSystemInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');

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
      </header>
      
      <Navigation activePage={activePage} onChangePage={setActivePage} />
      
      <main className="App-content">
        {renderActivePage()}
      </main>
      
      <footer className="App-footer">
        <p>Home-IO - A Custom Home Automation Hub</p>
      </footer>
    </div>
  );
}

export default App;