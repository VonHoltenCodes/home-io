/**
 * Teensy Device API Functions
 */

import { fetchApi } from './api';

/**
 * Get all Teensy devices
 */
export const getTeensyDevices = () => fetchApi('teensy');

/**
 * Get a specific Teensy device
 * 
 * @param {string} deviceId - Device ID
 */
export const getTeensyDevice = (deviceId) => fetchApi(`teensy/${deviceId}`);

/**
 * Discover available Teensy devices (ports)
 */
export const discoverTeensyDevices = () => fetchApi('teensy/discover');

/**
 * Register a new Teensy device
 * 
 * @param {Object} deviceConfig - Device configuration
 */
export const registerTeensyDevice = (deviceConfig) => {
  return fetchApi('teensy', {
    method: 'POST',
    body: JSON.stringify(deviceConfig),
  });
};

/**
 * Update a Teensy device
 * 
 * @param {string} deviceId - Device ID
 * @param {Object} deviceConfig - Device configuration
 */
export const updateTeensyDevice = (deviceId, deviceConfig) => {
  return fetchApi(`teensy/${deviceId}`, {
    method: 'PUT',
    body: JSON.stringify(deviceConfig),
  });
};

/**
 * Delete a Teensy device
 * 
 * @param {string} deviceId - Device ID
 */
export const deleteTeensyDevice = (deviceId) => {
  return fetchApi(`teensy/${deviceId}`, {
    method: 'DELETE',
  });
};

/**
 * Send command to Teensy device
 * 
 * @param {string} deviceId - Device ID
 * @param {string} command - Command name
 * @param {Object} params - Command parameters
 */
export const sendTeensyCommand = (deviceId, command, params = {}) => {
  return fetchApi(`teensy/${deviceId}/command`, {
    method: 'POST',
    body: JSON.stringify({
      command: command,
      params: params
    }),
  });
};