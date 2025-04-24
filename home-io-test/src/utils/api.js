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
 * Register a new device
 * 
 * @param {Object} deviceData - Device registration data
 */
export const registerDevice = (deviceData) => {
  return fetchApi('devices', {
    method: 'POST',
    body: JSON.stringify(deviceData),
  });
};

/**
 * Update a device
 * 
 * @param {string} deviceId - Device ID
 * @param {Object} updates - Device updates
 */
export const updateDevice = (deviceId, updates) => {
  return fetchApi(`devices/${deviceId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
};

/**
 * Delete a device
 * 
 * @param {string} deviceId - Device ID
 */
export const deleteDevice = (deviceId) => {
  return fetchApi(`devices/${deviceId}`, {
    method: 'DELETE',
  });
};