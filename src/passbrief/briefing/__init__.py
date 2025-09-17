"""
Briefing generation module for SR22T operations.

Contains enhanced briefing capabilities including:
- SID (Standard Instrument Departure) analysis
- CAPS (Cirrus Airframe Parachute System) altitudes
- Professional takeoff briefing with phased emergency procedures
- AI-powered flight plan analysis and passenger briefings
- Main briefing generator orchestrating all components
"""

from .sid import SIDManager
from .caps import CAPSManager
from .flavortext import FlavorTextManager
from .chatgpt import ChatGPTAnalysisManager
from .generator import BriefingGenerator

__all__ = [
    'SIDManager',
    'CAPSManager',
    'FlavorTextManager',
    'ChatGPTAnalysisManager',
    'BriefingGenerator'
]