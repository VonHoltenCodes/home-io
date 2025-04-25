# Component Documentation

## Audio Components

### RetroVUMeter

**Location**: `/src/components/Audio/RetroVUMeter.js`

**Purpose**: Displays audio levels with a realistic bouncing needle VU meter.

**Props**:
- `level` (number) - Current audio level in dB (-60 to +6 range)
- `peak` (number) - Peak level in dB
- `showPeakHold` (boolean) - Whether to show peak hold indicator

**Key Features**:
- Semi-circular meter face with tick marks
- Animated needle with physics-based bouncing
- Orange glow effect in retro theme
- Canvas-based rendering

**Usage Example**:
```jsx
<RetroVUMeter level={-20} peak={-10} showPeakHold={true} />
```

### RetroStereoInterface

**Location**: `/src/components/Audio/RetroStereoInterface.js`

**Purpose**: Complete audio device interface with controls and VU meters.

**Props**:
- `device` (object) - Audio device data

**Key Features**:
- Power toggle
- Volume control with knob visualization
- Input source selection
- Dual channel VU meters
- Theme-specific styling

## Thermostat Components

### ThermostatTile

**Location**: `/src/components/Thermostat/ThermostatTile.js`

**Props**:
- `device` (object) - Thermostat device data
- `onUpdate` (function) - Callback for when settings change

**Key Features**:
- Temperature display
- Mode selection (heat, cool, off)
- Temperature adjustment controls
- Current status indicators

## Zigbee Components

### ZigbeeDeviceTile

**Location**: `/src/components/ZigbeeDevice/ZigbeeDeviceTile.js`

**Props**:
- `device` (object) - Zigbee device data
- `onUpdate` (function) - Callback for device updates
- `onIdentify` (function) - Callback to trigger identify mode

**Key Features**:
- Device type detection
- Appropriate controls based on device capabilities
- Status indicators
- Battery level display (if applicable)

### ZigbeeDevicesGrid

**Location**: `/src/components/ZigbeeDevice/ZigbeeDevicesGrid.js`

**Props**:
- `devices` (array) - List of Zigbee devices
- `filter` (string) - Optional filter string
- `onUpdate` (function) - Callback for device updates

**Key Features**:
- Grid layout for devices
- Filtering capability
- Empty state handling
- Responsive design

## Common Components

### RetroDeviceTileWrapper

**Location**: `/src/components/RetroDeviceTileWrapper.js`

**Props**:
- `deviceName` (string) - Name of the device
- `deviceType` (string) - Type identifier for the device
- `children` (node) - Content to wrap

**Purpose**: Provides consistent styling for device tiles in the retro theme

### ThemeToggle

**Location**: `/src/components/ThemeToggle.js`

**Purpose**: Button to cycle between available themes