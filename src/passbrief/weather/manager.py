#!/usr/bin/env python3
"""
Weather Manager for SR22T Briefing Tool

Handles METAR data fetching from NOAA Aviation Weather API with:
- Automatic unit conversion (hPa to inHg)
- Age validation for stale weather data
- Manual input fallbacks when API unavailable
- Comprehensive error handling
"""

import requests
from datetime import datetime, timezone
from ..config import Config


class WeatherManager:
    """Manages weather data fetching and processing."""

    @staticmethod
    def fetch_metar(icao_code):
        """Fetch METAR with hPa to inHg conversion"""
        try:
            url = "https://aviationweather.gov/api/data/metar?ids=" + icao_code + "&format=json&taf=false"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    metar_data = data[0]

                    metar_time = datetime.fromisoformat(metar_data['reportTime'].replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    age_minutes = (current_time - metar_time).total_seconds() / 60

                    if age_minutes > Config.METAR_MAX_AGE_MINUTES:
                        return WeatherManager.request_manual_weather()

                    raw_altimeter = metar_data.get('altim', 29.92)
                    if raw_altimeter > 100:
                        altimeter_inhg = round(raw_altimeter * 0.02953, 2)
                        unit_info = "hPa converted to inHg"
                        print("CONVERTING: " + str(raw_altimeter) + " hPa -> " + str(altimeter_inhg) + " inHg")
                    else:
                        altimeter_inhg = round(raw_altimeter, 2)
                        unit_info = "inHg (no conversion)"

                    return {
                        'wind_dir': metar_data.get('wdir', 0),
                        'wind_speed': metar_data.get('wspd', 0),
                        'temp_c': metar_data.get('temp', 15),
                        'altimeter': altimeter_inhg,
                        'altimeter_raw': raw_altimeter,
                        'altimeter_units': unit_info,
                        'metar_time': metar_data['reportTime'],
                        'age_minutes': int(age_minutes),
                        'source': 'NOAA Aviation Weather'
                    }

        except Exception as e:
            print("Weather fetch failed: " + str(e))

        return WeatherManager.request_manual_weather()

    @staticmethod
    def request_manual_weather():
        """Request manual weather input"""
        print("\\nMETAR UNAVAILABLE - Manual input required")
        try:
            wind_dir = int(input("Wind direction (degrees magnetic): "))
            wind_speed = int(input("Wind speed (knots): "))
            temp_c = float(input("Temperature (°C): "))
            altimeter = float(input("Altimeter setting (inHg): "))

            return {
                'wind_dir': wind_dir,
                'wind_speed': wind_speed,
                'temp_c': temp_c,
                'altimeter': altimeter,
                'altimeter_raw': altimeter,
                'altimeter_units': 'Manual input (inHg)',
                'metar_time': 'Manual Input',
                'age_minutes': 0,
                'source': 'Manual Input'
            }
        except:
            return None