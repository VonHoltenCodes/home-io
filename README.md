# Home-IO: Custom Home Automation Hub

Home-IO is a modular, extensible, and open-source home automation system designed to run on a Small Form Factor (SFF) PC connected to a wall-mounted touchscreen. It provides a unified interface for controlling and monitoring smart home devices using a fully custom software stack, without relying on third-party home automation platforms.

> **IMPORTANT**: This project is currently in MVP (Minimum Viable Product) development status and is intended for educational and recreational purposes only. It is not yet ready for production use.

## Features

- **Modular Architecture**: Easily extendable with plugins for different IoT protocols and device types
- **Customizable UI**: React-based frontend with a menu-board style interface
- **Local-First**: Runs locally on your network for privacy and reliability
- **Open Source**: Full control over your data and system behavior
- **Device Support**: Z-Wave, Zigbee, Wi-Fi, and API-based IoT devices
- **Automation Engine**: Create rules for automated actions based on device states and sensor readings

## Integration Strategy

Home-IO uses a dual-track approach to device integration:

### Production-Ready Open Standards (Core Platform)
- **Z-Wave**: Local control via USB dongle, no cloud dependencies
- **Zigbee**: Local control via USB coordinator, no cloud dependencies
- **MQTT**: Local message broker for custom sensors and devices
- **DIY Sensors**: Direct USB or GPIO connections for custom hardware

### Development/Demo API Integrations (Optional)
- **Tuya API**: For development/testing with Tuya-compatible devices
- **Honeywell API**: For development/testing with Honeywell thermostats
- **Other vendor APIs**: Implemented as plugins, not core dependencies

> **Note**: The proprietary vendor APIs are provided for development convenience and demonstration purposes only. The long-term vision for Home-IO is to prioritize open standards (Z-Wave, Zigbee) for production deployments to ensure independence from third-party cloud services.

## System Architecture

The Home-IO system consists of:

1. **Backend Server**:
   - FastAPI-based REST API for device communication and system management
   - SQLite database for device state, configuration, and logging
   - Plugin system for extensibility
   - Secure authentication and authorization

2. **Frontend UI**:
   - React web application with touch-optimized interface
   - Material UI components for a modern, responsive design
   - Real-time updates from devices
   - Customizable dashboard with draggable tiles

3. **IoT Integration**:
   - Z-Wave and Zigbee support via USB dongles
   - Direct API integration with popular smart device brands
   - MQTT support for DIY sensors and devices
   - Extensible plugin architecture for adding new device types

## Directory Structure

```
home-io/
├── api/                  # API routes and models
│   ├── models/           # Pydantic data models for API
│   └── routes/           # FastAPI route handlers
├── core/                 # Core system components
│   ├── config_manager.py # Configuration management
│   ├── db_manager.py     # Database operations
│   └── plugin_manager.py # Plugin system
├── plugins/              # Plugin modules
│   ├── zwave/            # Z-Wave integration (core)
│   ├── zigbee/           # Zigbee integration (core)
│   ├── tuya/             # Tuya API integration (development)
│   ├── honeywell/        # Honeywell API integration (development)
├── utils/                # Utility functions
├── config/               # Configuration files
├── data/                 # Database and persistent data
├── home-io-test/         # React frontend application
│   ├── public/           # Static assets
│   └── src/              # React source code
├── main.py               # Main application entry point
└── requirements.txt      # Python dependencies
```

## Installation

### Prerequisites

- Small Form Factor PC with Linux (Ubuntu/Debian recommended)
- Python 3.10 or higher
- Node.js 16 or higher (for UI development)
- Z-Wave and/or Zigbee USB dongles (recommended for production)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/VonHoltenCodes/home-io.git
   cd home-io
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   ```bash
   # Create a .env file for API credentials (not tracked by git)
   touch .env
   # Add your credentials if using API integrations
   # TUYA_API_KEY=your_key
   # TUYA_API_SECRET=your_secret
   # HONEYWELL_CLIENT_ID=your_id
   # HONEYWELL_CLIENT_SECRET=your_secret
   ```

5. Start the all-in-one development server:
   ```bash
   ./start.sh
   ```

### Hardware Configuration

1. Connect your hardware:
   - Z-Wave dongle (typically `/dev/ttyUSB0`)
   - Zigbee coordinator (typically `/dev/ttyUSB1`)

2. Update configuration:
   - Edit `config/config.json` to update hardware paths
   - Set `mock_network` to `false` for protocols with actual hardware

## Hardware Setup

### Recommended Hardware

- **SFF PC**: Intel NUC or similar with 4+ core CPU, 16GB RAM, 256GB SSD
- **Display**: 24"-32" touchscreen with HDMI input and USB touch output
- **IoT Dongles**: Aeotec Z-Stick (Z-Wave) and/or ConBee II (Zigbee)
- **Sensors**: BME280 (temperature/humidity/pressure), MQ-135 (air quality)

### Installation

1. Mount the touchscreen on the wall using a VESA mount
2. Connect the SFF PC to the touchscreen via HDMI/DisplayPort and USB
3. Attach Z-Wave/Zigbee dongles to USB ports
4. Connect any additional sensors via USB or GPIO
5. Install Linux and the Home-IO software stack
6. Configure the system to auto-start on boot

## Development

### Adding a New Plugin

1. Create a new directory in `plugins/` with your plugin name
2. Implement the required plugin interface (see `plugins/zwave/` for example)
3. Register your plugin in the configuration

### API Documentation

Once the server is running, access the Swagger UI documentation at:
```
http://localhost:8000/docs
```

## Security Considerations

- API keys and credentials should never be committed to the repository
- Store sensitive configuration in the `.env` file (which is git-ignored)
- For production deployment, enable authentication and use HTTPS
- Restrict access to the system from outside your local network

## License

This project is licensed under the MIT License - see the LICENSE file for details.

For educational and recreational purposes only. Not intended for commercial use at this time.

## Credits

- **Created by**: VonHoltenCodes
- **Assisted by**: Claude AI (Anthropic)

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.