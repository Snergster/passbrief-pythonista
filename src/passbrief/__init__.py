#!/usr/bin/env python3
"""
PassBrief - SR22T Flight Briefing Tool

A comprehensive departure/arrival briefing tool designed for Cirrus SR22T aircraft operations.
Provides performance calculations, weather integration, Garmin Pilot flight briefing parsing,
and climb gradient analysis for professional flight planning.

Key Features:
- Safety-critical performance calculations based on POH data
- METAR weather integration with automatic unit conversion
- Garmin Pilot PDF briefing parsing and route analysis
- Magnetic variation handling for accurate wind component calculations
- CAPS (Cirrus Airframe Parachute System) altitude integration
- SID (Standard Instrument Departure) analysis
- AI-powered flight plan analysis and passenger briefings
- Professional takeoff briefing with phased emergency procedures

Aviation Safety Notice:
This software handles safety-critical aviation performance data. All calculations
are based on embedded Pilot's Operating Handbook (POH) tables and follow
conservative aviation practices.
"""

# Configuration
from .config import Config

# Performance calculations
from .performance import EMBEDDED_SR22T_PERFORMANCE, PerformanceCalculator

# Weather data
from .weather import WeatherManager

# Airport data with magnetic variation
from .airports import AirportManager

# Garmin Pilot integration
from .garmin import GarminPilotBriefingManager

# Briefing generation components
from .briefing import (
    SIDManager,
    CAPSManager,
    FlavorTextManager,
    ChatGPTAnalysisManager,
    BriefingGenerator
)

# Public API
__all__ = [
    # Configuration
    'Config',

    # Performance
    'EMBEDDED_SR22T_PERFORMANCE',
    'PerformanceCalculator',

    # Weather
    'WeatherManager',

    # Airports
    'AirportManager',

    # Garmin Integration
    'GarminPilotBriefingManager',

    # Briefing Components
    'SIDManager',
    'CAPSManager',
    'FlavorTextManager',
    'ChatGPTAnalysisManager',
    'BriefingGenerator'
]

# Version info
__version__ = "1.0.0"
__author__ = "PassBrief Development Team"
__license__ = "Private"

# Quick access to main functionality
def create_briefing_generator():
    """
    Create a new BriefingGenerator instance - the main entry point for the application.

    Returns:
        BriefingGenerator: Ready-to-use briefing generator instance
    """
    return BriefingGenerator()

def get_version():
    """Return the current version of PassBrief."""
    return __version__