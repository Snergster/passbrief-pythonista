# PassBrief Architecture

## Project Structure

PassBrief follows a modern Python project layout with clear separation of concerns:

```
passbrief-pythonista/
├── src/passbrief/          # Main application package
│   ├── __init__.py         # Public API and convenience functions
│   ├── config.py           # Configuration constants
│   ├── performance/        # Performance calculations
│   │   ├── __init__.py
│   │   ├── data.py         # Embedded POH performance tables
│   │   └── calculator.py   # Performance calculation engine
│   ├── weather/            # Weather data handling
│   │   ├── __init__.py
│   │   └── manager.py      # METAR fetching and parsing
│   ├── airports/           # Airport data management
│   │   ├── __init__.py
│   │   └── manager.py      # Airport/runway data with magnetic variation
│   ├── garmin/             # Garmin Pilot integration
│   │   ├── __init__.py
│   │   └── pilot.py        # PDF briefing parsing
│   └── briefing/           # Briefing generation components
│       ├── __init__.py
│       ├── generator.py    # Main application orchestrator
│       ├── sid.py          # Standard Instrument Departure analysis
│       ├── caps.py         # CAPS altitude calculations
│       ├── flavortext.py   # Enhanced takeoff briefings
│       └── chatgpt.py      # AI-powered analysis
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Build and utility scripts
└── artifacts/              # Build outputs for deployment
```

## Module Responsibilities

### Core Infrastructure

#### `src/passbrief/config.py`
- Application configuration constants
- METAR data age limits
- Performance calculation rounding rules
- File age limits for cached data

#### `src/passbrief/__init__.py`
- Public API for the entire package
- Convenience functions for common operations
- Version information and metadata

### Performance System

#### `src/passbrief/performance/`
Safety-critical performance calculations for SR22T aircraft:

- **`data.py`**: Embedded POH performance tables
  - Takeoff/landing distance tables
  - Climb gradient data (91 KIAS and 120 KIAS)
  - V-speeds and configuration data

- **`calculator.py`**: Performance calculation engine
  - Pressure/density altitude calculations
  - Wind component analysis
  - Performance interpolation algorithms
  - Temperature and altitude corrections

### External Data Integration

#### `src/passbrief/weather/manager.py`
- NOAA Aviation Weather API integration
- METAR parsing and validation
- Automatic unit conversions (hPa to inHg)
- Age-based data validation
- Manual weather input fallbacks

#### `src/passbrief/airports/manager.py`
- OurAirports database integration
- Real-time airport/runway data fetching
- **Magnetic variation handling** (safety-critical)
  - Three-tier accuracy system: NOAA WMM API → manual input → regional approximation
  - TRUE to MAGNETIC heading conversion
  - Wind component calculation accuracy

#### `src/passbrief/garmin/pilot.py`
- Garmin Pilot PDF briefing parsing
- Multi-path file discovery across iOS/Pythonista
- Route extraction and analysis
- Weather data parsing from briefings
- Comprehensive diagnostic capabilities

### Briefing Generation

#### `src/passbrief/briefing/generator.py`
Main application orchestrator providing:
- Multi-modal input workflows
- Performance calculation coordination
- Interactive user interface
- Rich briefing formatting
- Workflow-based operation

#### Specialized Briefing Components

- **`sid.py`**: Standard Instrument Departure analysis
- **`caps.py`**: CAPS (Cirrus Airframe Parachute System) altitude calculations
- **`flavortext.py`**: Enhanced takeoff briefings with phased emergency procedures
- **`chatgpt.py`**: AI-powered flight plan analysis and passenger briefings

## Data Flow Architecture

```
User Input → BriefingGenerator → Specialized Managers → Performance Calculator → Formatted Output
    ↓              ↓                      ↓                      ↓
Weather API → WeatherManager → Wind Components → Briefing Generation
    ↓              ↓                      ↓
Airport API → AirportManager → Magnetic Variation → Wind Calculations
    ↓              ↓
Garmin PDF → GarminManager → Route Analysis → AI Analysis
```

## Safety-Critical Design Principles

1. **Conservative Calculations**: All performance estimates err on the side of safety
2. **Data Source Transparency**: Clear identification of POH vs. approximated data
3. **Validation Layers**: Multiple checks on aviation calculations
4. **Offline Capability**: Embedded data ensures operation without internet
5. **User Authority**: Pilot always has final authority over performance decisions

## Deployment Strategy

The modular architecture supports two deployment modes:

1. **Development Mode**: Full modular structure for development and testing
2. **Production Mode**: Single-file deployment for Pythonista using build scripts

This approach maintains code quality during development while meeting Pythonista's deployment constraints.

## Extension Points

The architecture supports easy extension through:

- **New Weather Sources**: Additional weather providers in `weather/` module
- **Additional Aircraft**: Performance data templates in `performance/data.py`
- **New Briefing Components**: Additional managers in `briefing/` module
- **Enhanced AI Features**: Extensions to `chatgpt.py` analysis capabilities