/**
 * API utility functions for Home-IO frontend
 */

// Base API URL for backend
const API_BASE_URL = '/api';

/**
 * Fetch data from the API with error handling
 * 
 * @param {string} endpoint - API endpoint to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Response data
 */
export const fetchApi = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}/${endpoint.replace(/^\//, '')}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${error.message}`);
    throw error;
  }
};

/**
 * Get system information
 */
export const getSystemInfo = () => fetchApi('system');

/**
 * Get all devices
 * 
 * @param {Object} filters - Optional filters for device list
 */
export const getDevices = (filters = {}) => {
  const queryParams = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, value);
    }
  });
  
  const queryString = queryParams.toString();
  const endpoint = `devices${queryString ? `?${queryString}` : ''}`;
  
  return fetchApi(endpoint);
};

/**
 * Get a specific device by ID
 * 
 * @param {string} deviceId - Device ID
 */
export const getDevice = (deviceId) => fetchApi(`devices/${deviceId}`);

/**
 * Send a command to a device
 * 
 * @param {string} deviceId - Device ID
 * @param {string} command - Command name
 * @param {Object} parameters - Command parameters
 */
export const sendDeviceCommand = (deviceId, command, parameters = {}) => {
  return fetchApi(`devices/${deviceId}/command`, {
    method: 'POST',
    body: JSON.stringify({
      device_id: deviceId,
      command,
      parameters,
    }),
  });
};

/**
 * Get all thermostats
 */
export const getThermostats = () => fetchApi('thermostats');

/**
 * Get a specific thermostat by ID
 * 
 * @param {string} thermostatId - Thermostat ID
 */
export const getThermostat = (thermostatId) => fetchApi(`thermostats/${thermostatId}`);

/**
 * Set thermostat temperature
 * 
 * @param {string} thermostatId - Thermostat ID
 * @param {number} temperature - Target temperature
 * @param {string} mode - Mode (heat, cool, auto)
 */
export const setThermostatTemperature = (thermostatId, temperature, mode = 'heat') => {
  return fetchApi(`thermostats/${thermostatId}/temperature?temperature=${temperature}&mode=${mode}`, {
    method: 'POST',
  });
};

/**
 * Set thermostat mode
 * 
 * @param {string} thermostatId - Thermostat ID
 * @param {string} mode - Mode (heat, cool, auto, off)
 */
export const setThermostatMode = (thermostatId, mode) => {
  return fetchApi(`thermostats/${thermostatId}/mode?mode=${mode}`, {
    method: 'POST',
  });
};

/**
 * Get thermostat sensors
 * 
 * @param {string} thermostatId - Thermostat ID
 */
export const getThermostatSensors = (thermostatId) => {
  return fetchApi(`thermostats/${thermostatId}/sensors`);
};

/**
 * Get all smart plugs
 */
export const getSmartPlugs = () => fetchApi('smart_plugs');

/**
 * Get a specific smart plug by ID
 * 
 * @param {string} plugId - Smart plug ID
 */
export const getSmartPlug = (plugId) => fetchApi(`smart_plugs/${plugId}`);

/**
 * Set smart plug switch state
 * 
 * @param {string} plugId - Smart plug ID
 * @param {boolean} state - Switch state (true=on, false=off)
 */
export const setSmartPlugState = (plugId, state) => {
  return fetchApi(`smart_plugs/${plugId}/switch?state=${state}`, {
    method: 'POST',
  });
};

/**
 * Set smart plug schedule
 * 
 * @param {string} plugId - Smart plug ID
 * @param {string} onTime - Time to turn on (HH:MM)
 * @param {string} offTime - Time to turn off (HH:MM)
 * @param {boolean} enabled - Whether schedule is enabled
 */
export const setSmartPlugSchedule = (plugId, onTime, offTime, enabled = true) => {
  return fetchApi(`smart_plugs/${plugId}/schedule?on_time=${onTime}&off_time=${offTime}&enabled=${enabled}`, {
    method: 'POST',
  });
};