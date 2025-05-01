/*
 * Home-IO Teensy 4.0 BME280 Sensor Integration (Final)
 * 
 * This sketch reads data from a Waveshare BME280 sensor and sends it to the Home-IO platform
 * when requested via serial commands.
 * 
 * Hardware:
 * - Teensy 4.0
 * - Waveshare BME280 sensor connected via I2C
 *   - Connect VCC to Teensy 3.3V
 *   - Connect GND to Teensy GND
 *   - Connect SCL/SCK to Teensy pin 19 (SCL0)
 *   - Connect SDA/MOSI to Teensy pin 18 (SDA0)
 *   - Connect ADDR/MISO to GND for address 0x76 or 3.3V for address 0x77
 *   - Leave CS unconnected or connect to 3.3V (check Waveshare BME280 documentation)
 * 
 * Required Libraries:
 * - Adafruit BME280 Library
 * - Adafruit Unified Sensor Library
 * - ArduinoJson (v6.x)
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ArduinoJson.h>

// BME280 sensor
Adafruit_BME280 bme;

// LED pin for status indication
const int ledPin = 13;

// Command buffer
String commandBuffer = "";
bool commandComplete = false;

// Sensor status
bool sensorInitialized = false;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Wait a bit for serial to be ready
  delay(1000);
  
  // Initialize LED pin
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);  // Turn on LED during setup
  
  // Initialize I2C
  Wire.begin();
  delay(100); // Give I2C time to initialize
  
  // Initialize BME280 sensor
  Serial.println("{\"status\":\"info\", \"message\":\"Attempting BME280 initialization\"}");
  
  // Try both I2C addresses
  if (bme.begin(0x76, &Wire)) {
    Serial.println("{\"status\":\"info\", \"message\":\"BME280 found at address 0x76\"}");
    sensorInitialized = true;
  } else if (bme.begin(0x77, &Wire)) {
    Serial.println("{\"status\":\"info\", \"message\":\"BME280 found at address 0x77\"}");
    sensorInitialized = true;
  } else {
    // Sensor not found - scan I2C bus to help with debugging
    scanI2CBus();
  }
  
  // Setup complete
  digitalWrite(ledPin, LOW);  // Turn off LED
  
  // Send ready message with wiring instructions if sensor not found
  if (!sensorInitialized) {
    Serial.println("{\"status\":\"error\", \"message\":\"BME280 not found - check wiring as follows:\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"VCC → Teensy 3.3V\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"GND → Teensy GND\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"SCL/SCK → Teensy Pin 19\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"SDA/MOSI → Teensy Pin 18\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"ADDR/MISO → GND (for 0x76) or 3.3V (for 0x77)\"}");
    Serial.println("{\"status\":\"info\", \"message\":\"CS → Leave unconnected or connect to 3.3V\"}");
  }
  
  // Final ready message
  Serial.print("{\"status\":\"ready\", \"device\":\"Teensy BME280 Sensor\", \"version\":\"1.0.0\", \"sensor_initialized\":");
  Serial.print(sensorInitialized ? "true" : "false");
  Serial.println("}");
}

void scanI2CBus() {
  // Scan the I2C bus for devices to help with debugging
  Serial.println("{\"status\":\"info\", \"message\":\"Scanning I2C bus for devices\"}");
  byte error, address;
  int deviceCount = 0;
  
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("{\"status\":\"info\", \"message\":\"I2C device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      Serial.println("\"}");
      deviceCount++;
    }
  }
  
  if (deviceCount == 0) {
    Serial.println("{\"status\":\"error\", \"message\":\"No I2C devices found - check wiring and pull-up resistors\"}");
  } else {
    Serial.println("{\"status\":\"info\", \"message\":\"Found " + String(deviceCount) + " I2C device(s), but none at BME280 addresses (0x76, 0x77)\"}");
  }
}

void loop() {
  // Check for serial commands
  while (Serial.available()) {
    char c = Serial.read();
    
    // Handle newline
    if (c == '\n' || c == '\r') {
      if (commandBuffer.length() > 0) {
        commandComplete = true;
      }
    } else {
      // Add character to buffer
      commandBuffer += c;
    }
  }
  
  // Process command if complete
  if (commandComplete) {
    processCommand(commandBuffer);
    commandBuffer = "";
    commandComplete = false;
  }
  
  // Blink LED occasionally to show the system is running
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 5000) {  // Every 5 seconds
    digitalWrite(ledPin, HIGH);
    delay(50);
    digitalWrite(ledPin, LOW);
    lastBlink = millis();
  }
}

void processCommand(String command) {
  // Save original command for error reporting
  String originalCommand = command;
  
  // Convert command to uppercase for case-insensitive comparison
  command.toUpperCase();
  
  // Remove spaces from command
  command.replace(" ", "");
  
  // Handle different commands
  if (command == "GET_SENSOR_DATA") {
    sendSensorData();
  } else if (command == "IDENTIFY") {
    identifyDevice();
  } else if (command == "RESET") {
    resetDevice();
  } else if (command == "SCAN_I2C") {
    scanI2CBus();
  } else if (command.startsWith("{")) {
    // Try to parse as JSON command
    processJsonCommand(originalCommand);
  } else {
    // Unknown command
    sendErrorResponse("Unknown command: " + originalCommand);
  }
}

void processJsonCommand(String jsonString) {
  // Allocate the JSON document
  JsonDocument doc;
  
  // Parse JSON
  DeserializationError error = deserializeJson(doc, jsonString);
  
  if (error) {
    sendErrorResponse("Invalid JSON: " + String(error.c_str()));
    return;
  }
  
  // Extract command
  if (!doc["command"].is<String>()) {
    sendErrorResponse("JSON missing 'command' field");
    return;
  }
  
  String command = doc["command"];
  command.toUpperCase();
  
  // Process command
  if (command == "GET_SENSOR_DATA") {
    sendSensorData();
  } else if (command == "IDENTIFY") {
    identifyDevice();
  } else if (command == "RESET") {
    resetDevice();
  } else if (command == "SCAN_I2C") {
    scanI2CBus();
  } else if (command == "SET_LED") {
    // Extract parameters
    if (doc["params"].is<JsonObject>() && doc["params"]["state"].is<bool>()) {
      bool state = doc["params"]["state"];
      digitalWrite(ledPin, state ? HIGH : LOW);
      
      // Send response
      Serial.print("{\"status\":\"success\", \"command\":\"SET_LED\", \"led_state\":");
      Serial.print(state ? "true" : "false");
      Serial.println("}");
    } else {
      sendErrorResponse("Missing LED state parameter");
    }
  } else {
    sendErrorResponse("Unknown command: " + command);
  }
}

void sendSensorData() {
  // Allocate the JSON document
  JsonDocument doc;
  
  if (sensorInitialized) {
    // Read sensor data
    float temperature = bme.readTemperature();
    float humidity = bme.readHumidity();
    float pressure = bme.readPressure() / 100.0F;  // Convert Pa to hPa
    
    // Add sensor readings to JSON
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["pressure"] = pressure;
    doc["timestamp"] = millis();
    doc["status"] = "success";
    
    // Blink LED to indicate sensor read
    digitalWrite(ledPin, HIGH);
    delay(50);
    digitalWrite(ledPin, LOW);
  } else {
    // Sensor not initialized
    doc["error"] = "BME280 sensor not initialized";
    doc["status"] = "error";
    doc["timestamp"] = millis();
    doc["help"] = "Check wiring per setup instructions. Use SCAN_I2C for diagnostics.";
  }
  
  // Send JSON response
  serializeJson(doc, Serial);
  Serial.println();
}

void identifyDevice() {
  // Blink LED rapidly for identification
  for (int i = 0; i < 10; i++) {
    digitalWrite(ledPin, HIGH);
    delay(100);
    digitalWrite(ledPin, LOW);
    delay(100);
  }
  
  // Send response
  Serial.println("{\"status\":\"success\", \"command\":\"IDENTIFY\"}");
}

void resetDevice() {
  // Send response before reset
  Serial.println("{\"status\":\"success\", \"command\":\"RESET\"}");
  delay(100);  // Wait for serial to finish sending
  
  // Reset the device
  SCB_AIRCR = 0x05FA0004;  // System reset
}

void sendErrorResponse(String errorMessage) {
  // Allocate the JSON document
  JsonDocument doc;
  
  // Add error information
  doc["status"] = "error";
  doc["message"] = errorMessage;
  
  // Send JSON response
  serializeJson(doc, Serial);
  Serial.println();
}