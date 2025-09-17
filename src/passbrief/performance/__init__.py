"""
Performance calculation module for SR22T aircraft.

Contains performance data tables and calculation engines for:
- Takeoff and landing distance calculations
- Climb gradient analysis (91 KIAS and 120 KIAS)
- Wind component analysis
- Pressure/density altitude calculations
"""

from .data import EMBEDDED_SR22T_PERFORMANCE
from .calculator import PerformanceCalculator

__all__ = ['EMBEDDED_SR22T_PERFORMANCE', 'PerformanceCalculator']