# PassBrief API Reference

## Quick Start

```python
import passbrief

# Create a briefing generator instance
briefing_gen = passbrief.create_briefing_generator()

# Or import components directly
from passbrief import (
    BriefingGenerator,
    PerformanceCalculator,
    WeatherManager,
    AirportManager
)
```

## Main Package (`passbrief`)

### Convenience Functions

#### `create_briefing_generator()`
Creates a new BriefingGenerator instance - the main entry point for the application.

**Returns:**
- `BriefingGenerator`: Ready-to-use briefing generator instance

#### `get_version()`
Returns the current version of PassBrief.

**Returns:**
- `str`: Version string (e.g., "1.0.0")

### Public API Classes

All classes are available directly from the main package:

```python
from passbrief import (
    Config,
    EMBEDDED_SR22T_PERFORMANCE,
    PerformanceCalculator,
    WeatherManager,
    AirportManager,
    GarminPilotBriefingManager,
    SIDManager,
    CAPSManager,
    FlavorTextManager,
    ChatGPTAnalysisManager,
    BriefingGenerator
)
```

## Core Components

### Configuration (`passbrief.Config`)

Application configuration constants:

```python
class Config:
    METAR_MAX_AGE_MINUTES = 70
    PRESSURE_ALTITUDE_ROUND = 10
    DENSITY_ALTITUDE_ROUND = 50
    PERFORMANCE_DISTANCE_ROUND = 50
    FOREFLIGHT_FILE_MAX_AGE_HOURS = 24
    GARMIN_PILOT_FILE_MAX_AGE_HOURS = 24
```

### Performance System

#### `passbrief.EMBEDDED_SR22T_PERFORMANCE`
Complete embedded performance data from SR22T POH including:
- Takeoff distances (pressure altitude × temperature matrix)
- Landing distances (pressure altitude × temperature matrix)
- Climb gradients at 91 KIAS and 120 KIAS
- V-speeds and configuration data

#### `passbrief.PerformanceCalculator`

**Safety-critical aviation performance calculations.**

##### Key Methods

**`calculate_pressure_altitude(altimeter_inhg, field_elevation_ft)`**
Calculate pressure altitude from altimeter setting.
- `altimeter_inhg`: Altimeter setting in inches of mercury
- `field_elevation_ft`: Field elevation in feet MSL
- Returns: Pressure altitude in feet

**`calculate_density_altitude(pressure_altitude_ft, temperature_c, round_to=50)`**
Calculate density altitude for performance calculations.
- `pressure_altitude_ft`: Pressure altitude in feet
- `temperature_c`: Temperature in Celsius
- `round_to`: Rounding interval (default: 50 feet)
- Returns: Density altitude in feet

**`calculate_wind_components(wind_dir, wind_speed, runway_heading)`**
Calculate headwind and crosswind components.
- `wind_dir`: Wind direction in degrees magnetic
- `wind_speed`: Wind speed in knots
- `runway_heading`: Runway heading in degrees magnetic
- Returns: Dict with 'headwind' and 'crosswind' components

**`calculate_climb_gradients(pressure_altitude_ft, temperature_c, wind_dir, wind_speed, runway_heading)`**
Calculate climb performance and gradients.
- Returns: Dict with TAS, ground speeds, and climb gradients for 91 and 120 KIAS

### Weather System

#### `passbrief.WeatherManager`

**METAR weather data integration.**

##### Key Methods

**`fetch_metar(icao_code)`**
Fetch current METAR data for an airport.
- `icao_code`: 4-letter ICAO airport code
- Returns: Dict with parsed weather data or None if failed

**`parse_manual_weather(temp_c, altimeter_inhg, wind_dir, wind_speed)`**
Create weather data structure from manual input.
- Returns: Standardized weather data dict

### Airport System

#### `passbrief.AirportManager`

**Airport data with safety-critical magnetic variation handling.**

##### Key Methods

**`get_airport_data(icao_code, runway=None)`**
Get comprehensive airport and runway data.
- `icao_code`: 4-letter ICAO airport code
- `runway`: Optional specific runway (e.g., "09", "27L")
- Returns: Dict with airport data including magnetic variation

**`fetch_runway_data(icao_code)`**
Fetch runway specifications from OurAirports database.
- Returns: List of runway data dicts

### Garmin Integration

#### `passbrief.GarminPilotBriefingManager`

**Garmin Pilot PDF briefing parsing and analysis.**

##### Key Methods

**`find_and_parse_briefing_files()`**
Automatically discover and parse Garmin Pilot briefing files.
- Returns: Dict with parsed flight plan data or None

**`parse_pdf_briefing(file_path)`**
Parse a specific Garmin Pilot PDF briefing file.
- `file_path`: Path to PDF briefing file
- Returns: Dict with parsed briefing data

### Briefing Components

#### `passbrief.SIDManager`
**Standard Instrument Departure analysis**

#### `passbrief.CAPSManager`
**CAPS (Cirrus Airframe Parachute System) calculations**

##### Key Methods

**`get_caps_info(airport_elevation_ft, density_altitude_ft)`**
Get CAPS deployment information and emergency briefing.
- Returns: Dict with CAPS altitudes and emergency procedures

#### `passbrief.FlavorTextManager`
**Enhanced takeoff briefings with phased emergency procedures**

##### Key Methods

**`generate_takeoff_briefing_phases(airport_data, results, caps_data)`**
Generate phased takeoff briefing with specific altitude gates.
- Returns: Dict with emergency phases and procedures

#### `passbrief.ChatGPTAnalysisManager`
**AI-powered flight plan analysis and briefing generation**

##### Key Methods

**`generate_briefing_analysis(flight_plan_data, operation, airport_data, weather_data, results)`**
Generate comprehensive AI analysis of flight conditions.
- Returns: Dict with hazard analysis and passenger briefings

### Main Application

#### `passbrief.BriefingGenerator`

**Primary application orchestrator coordinating all briefing activities.**

##### Key Methods

**`get_user_inputs()`**
Interactive workflow for gathering flight information.
- Returns: Dict with complete flight planning inputs

**`generate_briefing(inputs)`**
Generate comprehensive flight briefing from inputs.
- `inputs`: Flight planning data from get_user_inputs()
- Returns: Formatted briefing string

## Usage Examples

### Basic Briefing Generation

```python
import passbrief

# Create briefing generator
briefing_gen = passbrief.create_briefing_generator()

# Interactive workflow
while True:
    inputs = briefing_gen.get_user_inputs()
    if not inputs:
        break

    briefing = briefing_gen.generate_briefing(inputs)
    print(briefing)

    if input("Another briefing? (y/n): ").lower() != 'y':
        break
```

### Performance Calculations

```python
from passbrief import PerformanceCalculator

calc = PerformanceCalculator()

# Calculate density altitude
pressure_alt = calc.calculate_pressure_altitude(29.92, 4500)
density_alt = calc.calculate_density_altitude(pressure_alt, 25)

print(f"Density altitude: {density_alt} feet")

# Wind components
components = calc.calculate_wind_components(270, 15, 090)
print(f"Headwind: {components['headwind']} kt")
print(f"Crosswind: {components['crosswind']} kt")
```

### Weather Data

```python
from passbrief import WeatherManager

weather_manager = WeatherManager()
weather = weather_manager.fetch_metar("KSLC")
if weather:
    print(f"Temperature: {weather['temp_c']}°C")
    print(f"Wind: {weather['wind_dir']}°/{weather['wind_speed']}kt")
    print(f"Altimeter: {weather['altimeter']} inHg")
```

### CAPS Information

```python
from passbrief import CAPSManager

caps_info = CAPSManager.get_caps_info(4500, 5200)
print(f"CAPS minimum: {caps_info['minimum_msl']} ft MSL")
print(f"CAPS recommended: {caps_info['recommended_msl']} ft MSL")
```

## Error Handling

All API methods include appropriate error handling and will return `None` or empty results rather than raising exceptions for expected failure modes (network issues, missing data, etc.). Always check return values before using results.

## Aviation Safety Note

⚠️ **This API handles safety-critical aviation data. Always verify performance calculations against official POH sources and use conservative judgment in flight planning decisions.**
