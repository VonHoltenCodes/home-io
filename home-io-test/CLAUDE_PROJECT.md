# Project Structure and Overview

## Project: Home-IO Test (Frontend)

This is the React frontend for the Home-IO smart home system. It provides interfaces for various smart home devices including audio systems, thermostats, and Zigbee devices.

## Directory Structure

- `/src` - Main source code directory
  - `/components` - React components organized by device type/function
    - `/Audio` - Audio system components including VU meters and zone controls
    - `/SmartPlug` - Smart plug control components
    - `/Thermostat` - Thermostat control components
    - `/ZigbeeDevice` - Zigbee device components
  - `/utils` - Utility functions and context providers
  - `/App.js` - Main application component
  - `/theme.css` - Global theme definitions

## Key Files

- `/src/utils/api.js` - API integration for backend communication
- `/src/utils/ThemeContext.js` - Theme context for managing theme state
- `/src/components/Dashboard.js` - Main dashboard component
- `/src/components/Navigation.js` - Navigation component

## Build Commands

- `npm start` - Start development server
- `npm build` - Create production build
- `npm test` - Run tests

## Git Information

- Main branch: `main`
- Recent features:
  - Audio system integration
  - Theme system (retro, night, default)
  - Thermostat controls
  - Zigbee device integration