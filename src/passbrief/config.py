#!/usr/bin/env python3
"""
Configuration constants for the SR22T briefing application.

These values control various operational parameters including:
- Weather data freshness requirements
- Rounding precision for performance calculations
- File age limits for integration data
"""


class Config:
    """Application configuration constants."""

    # Weather data limits
    METAR_MAX_AGE_MINUTES = 70  # Maximum age for METAR data before considering stale

    # Performance calculation rounding
    PRESSURE_ALTITUDE_ROUND = 10    # Round pressure altitude to nearest 10 ft
    DENSITY_ALTITUDE_ROUND = 50     # Round density altitude to nearest 50 ft
    PERFORMANCE_DISTANCE_ROUND = 50 # Round takeoff/landing distances to nearest 50 ft

    # File integration limits
    FOREFLIGHT_FILE_MAX_AGE_HOURS = 24  # Maximum age for ForeFlight export files
    GARMIN_PILOT_FILE_MAX_AGE_HOURS = 24  # Maximum age for Garmin Pilot files

    # API endpoints
    NOAA_METAR_API_URL = "https://aviationweather.gov/api/data/metar"
    OURAIRPORTS_AIRPORTS_CSV = "https://davidmegginson.github.io/ourairports-data/airports.csv"
    OURAIRPORTS_RUNWAYS_CSV = "https://davidmegginson.github.io/ourairports-data/runways.csv"

    # Magnetic variation calculation
    NOAA_WMM_API_URL = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"

    # Regional magnetic variation approximations (for offline fallback)
    REGIONAL_MAGNETIC_VARIATIONS = {
        'west_coast': 15.0,      # California, Oregon, Washington
        'southwest': 10.0,       # Arizona, Nevada, Utah
        'mountain': 8.0,         # Colorado, Wyoming, Montana
        'midwest': 2.0,          # Kansas, Nebraska, Iowa
        'texas': 4.0,            # Texas region
        'southeast': -5.0,       # Florida, Georgia, Alabama
        'northeast': -15.0,      # Maine, New Hampshire, Vermont
        'great_lakes': -8.0,     # Michigan, Wisconsin, Minnesota
    }