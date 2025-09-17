"""
Airport data management module.

Provides airport and runway data fetching with safety-critical magnetic variation handling.
"""

from .manager import AirportManager

__all__ = ['AirportManager']