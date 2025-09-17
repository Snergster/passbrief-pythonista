# PassBrief Documentation

Welcome to the PassBrief SR22T Flight Briefing Tool documentation.

## Documentation Contents

- [`architecture.md`](architecture.md) - Project architecture and module organization
- [`api-reference.md`](api-reference.md) - Comprehensive API reference for all modules
- [`deployment.md`](deployment.md) - Deployment guide for Pythonista iOS

## Quick Links

- [Project Root](../README.md) - Main project documentation
- [Source Code](../src/passbrief/) - Source code directory
- [Tests](../tests/) - Test suite directory

## Project Overview

PassBrief is a comprehensive SR22T flight briefing tool designed for Cirrus aircraft operations. It provides:

- **Safety-critical performance calculations** based on POH data
- **METAR weather integration** with automatic unit conversion
- **Garmin Pilot PDF briefing parsing** and route analysis
- **Magnetic variation handling** for accurate wind component calculations
- **CAPS altitude integration** for emergency procedures
- **AI-powered flight plan analysis** and passenger briefings

## Aviation Safety Notice

⚠️ **SAFETY-CRITICAL SOFTWARE**

This application handles aviation performance calculations that directly affect flight safety. All calculations are based on embedded Pilot's Operating Handbook (POH) tables and follow conservative aviation practices. Users are responsible for verifying all performance data against official sources.