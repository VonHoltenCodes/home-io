# Teensy 4.0 BME280 Sensor for Home-IO

This Arduino sketch allows a Teensy 4.0 microcontroller with a BME280 sensor to work with the Home-IO platform. It provides temperature, humidity, and pressure readings over a serial USB connection.

## Hardware Requirements

- Teensy 4.0 microcontroller
- BME280 sensor module
- Connecting wires

## Wiring

Connect the BME280 to the Teensy 4.0 as follows:

| BME280 Pin | Teensy 4.0 Pin |
|------------|----------------|
| VCC        | 3.3V           |
| GND        | GND            |
| SCL        | 19 (SCL0)      |
| SDA        | 18 (SDA0)      |

## Libraries

You'll need to install the following libraries in your Arduino IDE:

1. Adafruit BME280 Library
2. Adafruit Unified Sensor Library
3. ArduinoJson (v6.x)

## Installation

1. Install the required libraries via the Arduino Library Manager
2. Connect your Teensy 4.0 to your computer via USB
3. Open the sketch in Arduino IDE
4. Select "Teensy 4.0" from the Tools > Board menu
5. Upload the sketch to your Teensy

## Verifying Communication

1. Open the Serial Monitor in Arduino IDE (baud rate: 115200)
2. You should see a ready message: `{"status":"ready", "device":"Teensy BME280 Sensor", "version":"1.0.0"}`
3. Type `GET_SENSOR_DATA` and press Enter
4. You should see a JSON response with temperature, humidity, and pressure readings

## Home-IO Integration

Once the sketch is running on your Teensy, you can add it in the Home-IO platform:

1. Launch the Home-IO application
2. Go to the "Teensy Sensors" section
3. Click "Add Device"
4. Select your Teensy from the port dropdown
5. Configure it as an Environmental Sensor
6. Click "Register Device"

## Commands

The sketch responds to the following commands:

| Command         | Description                                      | Response                              |
|-----------------|--------------------------------------------------| -------------------------------------|
| GET_SENSOR_DATA | Reads and returns sensor data                    | JSON with temperature, humidity, pressure |
| IDENTIFY        | Blinks LED to help identify the device           | `{"status":"success", "command":"IDENTIFY"}` |
| RESET           | Resets the Teensy                                | `{"status":"success", "command":"RESET"}` |
| JSON Commands   | Same commands but in JSON format                 | JSON response                        |

### Example JSON Command

```json
{"command": "GET_SENSOR_DATA"}
```

## Troubleshooting

- If the LED blinks 5 times during startup, the BME280 sensor was not detected
- Check your wiring, especially the I2C connections
- Some BME280 modules use the 0x77 I2C address instead of 0x76. The code tries both, but if detection fails, check with an I2C scanner sketch
- The LED blinks briefly every 5 seconds to indicate the system is running

## Customization

You can modify the sketch to:

1. Add more sensors
2. Change the LED pin (currently using the built-in LED on pin 13)
3. Add additional commands
4. Change the serial baud rate (make sure to update it in Home-IO as well)