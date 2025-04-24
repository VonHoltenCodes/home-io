import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

def calculate_moving_average(values: List[float], window_size: int = 5) -> List[float]:
    """
    Calculate the moving average of a list of values
    
    Args:
        values: List of numerical values
        window_size: Size of the moving window
        
    Returns:
        List of moving averages
    """
    if not values:
        return []
        
    if len(values) < window_size:
        window_size = len(values)
        
    result = []
    
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        avg = sum(window) / window_size
        result.append(avg)
        
    return result

def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
    """
    Detect outliers in a list of values using Z-score
    
    Args:
        values: List of numerical values
        threshold: Z-score threshold for outlier detection
        
    Returns:
        Indices of outliers in the input list
    """
    if not values or len(values) < 3:
        return []
        
    mean = sum(values) / len(values)
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        return []  # No variation in data
        
    # Find outliers
    outliers = []
    for i, value in enumerate(values):
        z_score = abs((value - mean) / std_dev)
        if z_score > threshold:
            outliers.append(i)
            
    return outliers

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between different units
    
    Args:
        value: Temperature value to convert
        from_unit: Source unit ('C', 'F', or 'K')
        to_unit: Target unit ('C', 'F', or 'K')
        
    Returns:
        Converted temperature value
    """
    # Convert to Celsius as intermediate step
    if from_unit == 'C':
        celsius = value
    elif from_unit == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit == 'K':
        celsius = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")
        
    # Convert from Celsius to target unit
    if to_unit == 'C':
        return celsius
    elif to_unit == 'F':
        return celsius * 9/5 + 32
    elif to_unit == 'K':
        return celsius + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")

def calculate_heat_index(temperature: float, humidity: float, temp_unit: str = 'C') -> float:
    """
    Calculate the heat index (feels like temperature) based on temperature and humidity
    
    Args:
        temperature: Temperature value
        humidity: Relative humidity (0-100)
        temp_unit: Temperature unit ('C' or 'F')
        
    Returns:
        Heat index in the same unit as input temperature
    """
    # Convert to Fahrenheit for calculation
    if temp_unit == 'C':
        temp_f = temperature * 9/5 + 32
    elif temp_unit == 'F':
        temp_f = temperature
    else:
        raise ValueError(f"Unsupported temperature unit: {temp_unit}")
        
    # Check if the temperature is in the valid range for the formula
    if temp_f < 80:
        result_f = temp_f  # Below 80°F, the heat index equals the temperature
    else:
        # Heat index formula (Rothfusz regression)
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi -= 0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
        hi -= 5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
        hi += 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2
        result_f = hi
        
    # Convert back to original unit if needed
    if temp_unit == 'C':
        return (result_f - 32) * 5/9
    else:
        return result_f

def calculate_dew_point(temperature: float, humidity: float, temp_unit: str = 'C') -> float:
    """
    Calculate the dew point based on temperature and humidity
    
    Args:
        temperature: Temperature value
        humidity: Relative humidity (0-100)
        temp_unit: Temperature unit ('C' or 'F')
        
    Returns:
        Dew point in the same unit as input temperature
    """
    # Convert to Celsius for calculation
    if temp_unit == 'F':
        temp_c = (temperature - 32) * 5/9
    elif temp_unit == 'C':
        temp_c = temperature
    else:
        raise ValueError(f"Unsupported temperature unit: {temp_unit}")
        
    # Magnus formula for dew point
    b = 17.27
    c = 237.7
    
    gamma = math.log(humidity / 100) + (b * temp_c) / (c + temp_c)
    dew_point_c = (c * gamma) / (b - gamma)
    
    # Convert back to original unit if needed
    if temp_unit == 'F':
        return dew_point_c * 9/5 + 32
    else:
        return dew_point_c

def process_air_quality_reading(
    reading: Dict[str, Any],
    previous_readings: List[Dict[str, Any]] = None,
    aqi_standard: str = 'us'
) -> Dict[str, Any]:
    """
    Process air quality sensor reading to calculate AQI and other relevant metrics
    
    Args:
        reading: Current air quality reading with sensor values
        previous_readings: List of previous readings (optional)
        aqi_standard: AQI standard to use ('us' or 'eu')
        
    Returns:
        Processed reading with calculated metrics
    """
    processed = reading.copy()
    
    # Calculate Air Quality Index based on PM2.5 and PM10
    if 'pm25' in reading and 'pm10' in reading:
        if aqi_standard == 'us':
            # US EPA standard
            processed['aqi'] = calculate_us_aqi(reading['pm25'], reading['pm10'])
        else:
            # EU standard
            processed['aqi'] = calculate_eu_aqi(reading['pm25'], reading['pm10'])
            
    # Add air quality category
    if 'aqi' in processed:
        processed['category'] = get_aqi_category(processed['aqi'], aqi_standard)
        
    # Calculate trend if previous readings are provided
    if previous_readings and len(previous_readings) > 1:
        # Extract recent readings (last 3 hours)
        recent_readings = [r for r in previous_readings 
                           if datetime.fromisoformat(r['timestamp']) > 
                              datetime.fromisoformat(reading['timestamp']) - timedelta(hours=3)]
        
        if 'pm25' in reading and recent_readings:
            pm25_values = [r.get('pm25', 0) for r in recent_readings]
            processed['pm25_trend'] = calculate_trend(pm25_values)
            
        if 'pm10' in reading and recent_readings:
            pm10_values = [r.get('pm10', 0) for r in recent_readings]
            processed['pm10_trend'] = calculate_trend(pm10_values)
            
    return processed

def calculate_us_aqi(pm25: float, pm10: float) -> int:
    """
    Calculate US EPA Air Quality Index based on PM2.5 and PM10 values
    
    Args:
        pm25: PM2.5 concentration (μg/m³)
        pm10: PM10 concentration (μg/m³)
        
    Returns:
        US AQI value
    """
    # PM2.5 breakpoints and corresponding AQI values
    pm25_breakpoints = [
        (0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]
    
    # PM10 breakpoints and corresponding AQI values
    pm10_breakpoints = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500)
    ]
    
    # Calculate AQI for PM2.5
    pm25_aqi = 0
    for low_conc, high_conc, low_aqi, high_aqi in pm25_breakpoints:
        if low_conc <= pm25 <= high_conc:
            pm25_aqi = ((high_aqi - low_aqi) / (high_conc - low_conc)) * (pm25 - low_conc) + low_aqi
            break
    
    # Calculate AQI for PM10
    pm10_aqi = 0
    for low_conc, high_conc, low_aqi, high_aqi in pm10_breakpoints:
        if low_conc <= pm10 <= high_conc:
            pm10_aqi = ((high_aqi - low_aqi) / (high_conc - low_conc)) * (pm10 - low_conc) + low_aqi
            break
    
    # Return the higher of the two AQI values
    return int(max(pm25_aqi, pm10_aqi))

def calculate_eu_aqi(pm25: float, pm10: float) -> int:
    """
    Calculate EU Air Quality Index based on PM2.5 and PM10 values
    
    Args:
        pm25: PM2.5 concentration (μg/m³)
        pm10: PM10 concentration (μg/m³)
        
    Returns:
        EU AQI value
    """
    # EU index is simpler but with different thresholds
    # PM2.5 breakpoints
    pm25_breakpoints = [
        (0, 10, 0, 20),
        (10, 20, 20, 40),
        (20, 25, 40, 60),
        (25, 50, 60, 80),
        (50, 75, 80, 100),
        (75, 800, 100, 100)
    ]
    
    # PM10 breakpoints
    pm10_breakpoints = [
        (0, 20, 0, 20),
        (20, 40, 20, 40),
        (40, 50, 40, 60),
        (50, 100, 60, 80),
        (100, 150, 80, 100),
        (150, 1200, 100, 100)
    ]
    
    # Calculate index for PM2.5
    pm25_index = 0
    for low_conc, high_conc, low_idx, high_idx in pm25_breakpoints:
        if low_conc <= pm25 <= high_conc:
            pm25_index = ((high_idx - low_idx) / (high_conc - low_conc)) * (pm25 - low_conc) + low_idx
            break
    
    # Calculate index for PM10
    pm10_index = 0
    for low_conc, high_conc, low_idx, high_idx in pm10_breakpoints:
        if low_conc <= pm10 <= high_conc:
            pm10_index = ((high_idx - low_idx) / (high_conc - low_conc)) * (pm10 - low_conc) + low_idx
            break
    
    # Return the higher of the two index values
    return int(max(pm25_index, pm10_index))

def get_aqi_category(aqi: int, standard: str = 'us') -> str:
    """
    Get the air quality category based on the AQI value
    
    Args:
        aqi: Air Quality Index value
        standard: 'us' for EPA standard, 'eu' for European standard
        
    Returns:
        Air quality category description
    """
    if standard == 'us':
        if 0 <= aqi <= 50:
            return "Good"
        elif 51 <= aqi <= 100:
            return "Moderate"
        elif 101 <= aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif 151 <= aqi <= 200:
            return "Unhealthy"
        elif 201 <= aqi <= 300:
            return "Very Unhealthy"
        elif 301 <= aqi <= 500:
            return "Hazardous"
        else:
            return "Unknown"
    else:  # EU standard
        if 0 <= aqi <= 20:
            return "Very Good"
        elif 21 <= aqi <= 40:
            return "Good"
        elif 41 <= aqi <= 60:
            return "Moderate"
        elif 61 <= aqi <= 80:
            return "Poor"
        elif 81 <= aqi <= 100:
            return "Very Poor"
        else:
            return "Extremely Poor"

def calculate_trend(values: List[float]) -> str:
    """
    Calculate the trend direction based on a series of values
    
    Args:
        values: List of values to analyze
        
    Returns:
        Trend direction: 'rising', 'falling', or 'stable'
    """
    if not values or len(values) < 2:
        return "stable"
        
    # Simple linear regression to determine trend
    n = len(values)
    indices = list(range(n))
    
    # Calculate means
    mean_x = sum(indices) / n
    mean_y = sum(values) / n
    
    # Calculate slope
    numerator = sum((indices[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    denominator = sum((indices[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return "stable"
        
    slope = numerator / denominator
    
    # Determine trend based on slope magnitude
    if abs(slope) < 0.1 * (max(values) - min(values)) / n:
        return "stable"
    elif slope > 0:
        return "rising"
    else:
        return "falling"