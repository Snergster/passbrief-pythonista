# PassBrief - SR22T Flight Briefing Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Private-red.svg)]()
[![Platform](https://img.shields.io/badge/platform-Desktop%20%7C%20Pythonista%20iOS-green.svg)]()

A comprehensive departure/arrival briefing tool designed specifically for **Cirrus SR22T aircraft operations**. PassBrief provides safety-critical performance calculations, weather integration, and AI-powered flight analysis optimized for both desktop development and Pythonista iOS deployment.

## ⚠️ Aviation Safety Notice

**This software handles safety-critical aviation performance data.** All calculations are based on embedded Pilot's Operating Handbook (POH) tables and follow conservative aviation practices. Users are responsible for verifying all performance data against official sources and exercising proper pilot judgment.

## 🚀 Key Features

### Core Capabilities
- **Safety-critical performance calculations** based on embedded SR22T POH data
- **METAR weather integration** with automatic unit conversion and age validation
- **Garmin Pilot PDF briefing parsing** and comprehensive route analysis
- **Magnetic variation handling** with three-tier accuracy system (NOAA WMM API → manual input → regional approximation)
- **CAPS altitude integration** for Cirrus Airframe Parachute System emergency procedures
- **AI-powered flight plan analysis** and passenger briefings using OpenAI GPT

### Advanced Features
- **Phased takeoff emergency briefings** with specific altitude gates and procedures
- **SID (Standard Instrument Departure) analysis** and compliance checking
- **Comprehensive wind component calculations** for accurate performance assessment
- **Multi-modal input workflows** supporting various data sources
- **Professional briefing formatting** with structured output

### Deployment Flexibility
- **Modular development structure** for maintainability and testing
- **Single-file Pythonista deployment** for iOS compatibility
- **Offline operation capability** with embedded performance data
- **Cross-platform compatibility** (Windows, macOS, Linux, iOS)

## 📁 Project Structure

```
passbrief-pythonista/
├── src/passbrief/          # Main application package
│   ├── __init__.py         # Public API and convenience functions
│   ├── config.py           # Configuration constants
│   ├── performance/        # Performance calculations
│   ├── weather/            # Weather data handling
│   ├── airports/           # Airport data with magnetic variation
│   ├── garmin/             # Garmin Pilot integration
│   └── briefing/           # Briefing generation components
├── tests/                  # Comprehensive test suite
├── docs/                   # Documentation
├── scripts/                # Build and utility scripts
├── artifacts/              # Pythonista deployment files
├── pyproject.toml          # Modern Python project configuration
└── README.md               # This file
```

## 🛫 Quick Start

### Desktop Installation

```bash
# Clone the repository
git clone <repository-url>
cd passbrief-pythonista

# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Launch interactive briefing
python -c "import passbrief; briefing_gen = passbrief.create_briefing_generator()"
```

### Logging

Set the `APP_LOG` environment variable to control diagnostic verbosity:

```bash
APP_LOG=full python -m passbrief.briefing.generator
APP_LOG=critical python -m passbrief.briefing.generator  # default
APP_LOG=silent python -m passbrief.briefing.generator
```

### Pythonista iOS Deployment

```bash
# Generate single-file deployment
python scripts/build_for_pythonista.py

# Copy artifacts/passbrief_pythonista.py to your iOS device
# In Pythonista:
import passbrief_pythonista as passbrief
briefing_gen = passbrief.create_briefing_generator()
```

## 💻 Usage Examples

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

# Calculate density altitude for performance
pressure_alt = calc.calculate_pressure_altitude(29.85, 4500)
density_alt = calc.calculate_density_altitude(pressure_alt, 25)

print(f"Pressure altitude: {pressure_alt} ft")
print(f"Density altitude: {density_alt} ft")

# Wind component analysis
components = calc.calculate_wind_components(270, 15, 090)
print(f"Headwind: {components['headwind']} kt")
print(f"Crosswind: {components['crosswind']} kt")
```

### Weather Integration

```python
from passbrief import WeatherManager

weather_manager = WeatherManager()

# Fetch current METAR data
weather = weather_manager.fetch_metar("KSLC")
if weather:
    print(f"Temperature: {weather['temp_c']}°C")
    print(f"Wind: {weather['wind_dir']}°/{weather['wind_speed']}kt")
    print(f"Altimeter: {weather['altimeter']} inHg")
    print(f"Age: {weather['age_minutes']} minutes")
```

### CAPS Emergency Information

```python
from passbrief import CAPSManager

# Get CAPS deployment information
caps_info = CAPSManager.get_caps_info(4500, 5200)
print(f"CAPS minimum altitude: {caps_info['minimum_msl']} ft MSL")
print(f"CAPS recommended altitude: {caps_info['recommended_msl']} ft MSL")

# Emergency briefing points
for point in caps_info['emergency_brief']:
    print(f"• {point}")
```

## 🔧 Development

### Prerequisites

- Python 3.8 or higher
- `requests` library for network operations
- Optional: `numpy` for enhanced performance calculations

### Setting Up Development Environment

```bash
# Clone and enter directory
git clone <repository-url>
cd passbrief-pythonista

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/

# Generate Pythonista deployment
python scripts/build_for_pythonista.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=passbrief --cov-report=html

# Run specific test categories
pytest -m "not slow"          # Skip slow tests
pytest -m "not network"       # Skip network-dependent tests
pytest tests/test_performance/ # Test specific module
```

## 📖 Documentation

- **[Architecture Guide](docs/architecture.md)** - Project structure and design decisions
- **[API Reference](docs/api-reference.md)** - Comprehensive API documentation
- **[Deployment Guide](docs/deployment.md)** - Desktop and Pythonista deployment instructions

## 🛠️ Build System

The project includes sophisticated build tooling for Pythonista deployment:

### Build Script Features
- **Modular to monolithic conversion** - Combines all modules into single file
- **Import resolution** - Handles relative imports and dependencies
- **iOS optimization** - File paths and configurations for Pythonista
- **Validation testing** - Comprehensive test suite for deployment verification

### Deployment Artifacts

The build process generates:
- `passbrief_pythonista.py` - Single-file application (~275KB)
- `test_passbrief_pythonista.py` - Validation test suite
- `README_pythonista.txt` - iOS-specific documentation

## 🔒 Security and Privacy

- **No telemetry or data collection** - All processing performed locally
- **API key management** - Secure handling of OpenAI and weather service keys
- **Local data storage** - Flight information never transmitted externally
- **Network access** - Only for public aviation data (weather, airport information)

## 🎯 Aviation Context

PassBrief is designed specifically for **Cirrus SR22T operations** with deep understanding of:

- **Cirrus-specific procedures** - CAPS deployment altitudes and emergency checklists
- **SR22T performance characteristics** - Based on actual POH performance tables
- **Professional flight operations** - Structured workflows and safety protocols
- **Pilot decision-making** - Conservative calculations and clear go/no-go criteria

## 🤝 Contributing

This is a private project optimized for personal aviation operations. The codebase demonstrates:

- **Modern Python architecture** - Type hints, proper packaging, comprehensive testing
- **Aviation software development** - Safety-critical design patterns and validation
- **Cross-platform deployment** - Desktop development with mobile deployment
- **Professional documentation** - Comprehensive guides and API references

## 📋 Roadmap

- [ ] Enhanced weather source integration (ForeFlight, AOPA)
- [ ] Additional aircraft performance profiles
- [ ] Automated NOTAMs filtering and analysis
- [ ] Enhanced AI briefing capabilities
- [ ] Mobile app development (native iOS/Android)

## ⚖️ License

Private software for personal aviation operations. All rights reserved.

## 📞 Support

For technical issues or feature requests, please refer to the comprehensive documentation in the `docs/` directory or consult the embedded diagnostic capabilities within the application.

---

**🛫 Fly Safe, Fly Smart with PassBrief**

*Comprehensive flight briefing for the modern Cirrus pilot*
