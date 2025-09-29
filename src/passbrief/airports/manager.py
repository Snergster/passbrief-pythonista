#!/usr/bin/env python3
"""
Airport Manager for SR22T Briefing Tool

SAFETY-CRITICAL MAGNETIC VARIATION COMPONENT:

WHY MAGNETIC VARIATION MATTERS FOR AVIATION SAFETY:
- OurAirports database provides TRUE headings, but METAR weather provides MAGNETIC wind directions
- Mixing these reference systems causes incorrect wind component calculations
- Can lead to wrong runway performance calculations and poor decision-making

SOLUTION IMPLEMENTED: Three-tier magnetic variation system
1. BEST: NOAA WMM API with WMM2025 (aviation-grade accuracy ±0.5°)
2. GOOD: Manual user input from NOAA calculator (user-verified accuracy)
3. ACCEPTABLE: Regional approximation (±3-5° accuracy with safety warnings)

AVIATION CONTEXT: All runway headings in aviation are MAGNETIC unless specifically
noted as TRUE. Wind directions in METAR are always MAGNETIC. This tool converts
OurAirports TRUE headings to MAGNETIC for consistent calculations.

FORMULA: Magnetic_Heading = True_Heading - Magnetic_Variation
WHERE: Positive variation = East (subtract from true to get magnetic)
       Negative variation = West (add to true to get magnetic)
"""

from __future__ import annotations

import csv
import logging
import requests
import time
from datetime import datetime
from io import StringIO
from typing import Optional

from ..io import ConsoleIO


LOGGER = logging.getLogger(__name__)

class AirportManager:
    """Manages airport and runway data with accurate magnetic variation handling."""

    # Class variable to track magnetic variation data source
    _last_mag_var_source = 'UNKNOWN'
    _io = ConsoleIO()

    @staticmethod
    def _calculate_magnetic_variation(lat, lon, date=None):
        """
        Calculate magnetic variation using World Magnetic Model (WMM) - SAFETY CRITICAL

        AVIATION SAFETY CONTEXT: Magnetic variation is the angular difference between
        True North and Magnetic North at any location. This varies by geographic location
        and changes over time due to magnetic pole movement.

        WHY ACCURACY MATTERS: Small errors in magnetic variation create large errors
        in wind component calculations, especially in high wind conditions.
        Example: 5° heading error in 20kt wind = 1.7kt wind component error

        THREE-TIER ACCURACY SYSTEM:
        1. WMM2025 calculation (best): Aviation-grade accuracy using World Magnetic Model
        2. Manual user input (good): Allows pilot to use NOAA calculator for verification
        3. Regional approximation (acceptable): Fallback with clear safety warnings

        Args:
            lat (float): Latitude in decimal degrees
            lon (float): Longitude in decimal degrees
            date (datetime, optional): Date for WMM calculation (defaults to now)

        Returns:
            float: Magnetic variation in degrees (positive=East, negative=West)
        """
        if date is None:
            date = datetime.now()

        # TIER 1: Try NOAA WMM API for aviation-grade accuracy (with retries)
        try:
            # Use current date for calculation
            current_date = date if date else datetime.now()

            # NOAA WMM API endpoint with public key
            api_url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"
            params = {
                'lat1': lat,
                'lon1': lon,
                'model': 'WMM',  # World Magnetic Model
                'startYear': current_date.year,
                'startMonth': current_date.month,
                'startDay': current_date.day,
                'resultFormat': 'json',
                'key': 'zNEw7'  # Public API key from NOAA documentation
            }

            # Retry logic: 2 attempts with 5 second timeout each
            for attempt in range(2):
                try:
                    if attempt == 0:
                        AirportManager._io.info(f"   🌐 Requesting WMM2025 data from NOAA API...")
                    else:
                        AirportManager._io.info(f"   🔄 Retrying NOAA API (attempt {attempt + 1}/2)...")

                    response = requests.get(api_url, params=params, timeout=5)

                    if response.status_code == 200:
                        data = response.json()
                        if 'result' in data and len(data['result']) > 0:
                            declination = data['result'][0]['declination']
                            AirportManager._io.info(f"   🧭 Using NOAA WMM2025: Magnetic declination {declination:+.2f}° at {lat:.3f}, {lon:.3f}")
                            # Store source for automatic heading calculations
                            AirportManager._last_mag_var_source = 'NOAA_WMM'
                            return declination
                        else:
                            raise ValueError("No declination data in API response")
                    else:
                        raise ValueError(f"HTTP {response.status_code}")

                except requests.exceptions.Timeout:
                    if attempt == 0:
                        AirportManager._io.info(f"   ⏱️ API timeout (5s) - retrying...")
                        time.sleep(1)  # Brief pause before retry
                    else:
                        raise Exception("API timeout after 2 attempts")

                except Exception as api_error:
                    if attempt == 0:
                        AirportManager._io.info(f"   ⚠️ API error: {api_error} - retrying...")
                        time.sleep(1)  # Brief pause before retry
                    else:
                        raise Exception(f"API failed after 2 attempts: {api_error}")

        except Exception as e:
            AirportManager._io.info(f"   ❌ NOAA WMM API unavailable after retries - falling back to manual input")
            AirportManager._io.info(f"   🔍 Error: {e}")

        # TIER 2: Manual input from pilot using NOAA calculator
        AirportManager._io.info(f"   📍 Location: {lat:.4f}, {lon:.4f}")
        AirportManager._io.info(f"   💡 Get accurate value from: https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml")

        try:
            user_mag_var = float(AirportManager._io.prompt(f"   Enter magnetic variation for this location (degrees, + for East, - for West): "))
            AirportManager._io.info(f"   🧭 Using Manual Input: Magnetic declination {user_mag_var:+.2f}° at {lat:.3f}, {lon:.3f}")
            # Store source for heading calculations
            AirportManager._last_mag_var_source = 'MANUAL_INPUT'
            return user_mag_var
        except (ValueError, EOFError):
            # TIER 3: Regional approximation with safety warnings
            return AirportManager._regional_approximation(lat, lon)

    @staticmethod
    def _regional_approximation(lat, lon):
        """
        Regional approximation of magnetic variation as ultimate fallback

        AVIATION CONTEXT: This provides rough magnetic variation estimates for CONUS
        when neither WMM2025 library nor manual input are available. Accuracy is
        typically ±3-5° which is acceptable for low-wind conditions but requires
        verification for high-wind operations.

        ALGORITHM: Uses linear approximations based on 2025 NOAA magnetic variation
        data across different US regions, with latitude adjustments.

        WHY REGIONAL APPROXIMATION: Magnetic variation changes gradually across
        geographic regions, allowing reasonable linear approximation within regions.

        SAFETY WARNINGS: Clear warnings issued since this is least accurate method.

        Args:
            lat (float): Latitude in decimal degrees
            lon (float): Longitude in decimal degrees

        Returns:
            float: Approximated magnetic variation with safety warnings
        """
        # Regional linear approximations based on 2025 NOAA data
        # WHY REGIONS: Magnetic field changes more rapidly in some areas (East Coast vs West Coast)
        if lon > -75:  # Far East Coast - steepest variation gradient
            mag_var = -18 + (lon + 75) * 0.6
        elif lon > -95:  # Eastern/Central US - moderate variation
            mag_var = -8 + (lon + 95) * 0.3
        elif lon > -115:  # Central/Mountain US - crossing agonic line
            mag_var = 2 + (lon + 115) * 0.4
        else:  # Western US - gentler variation gradient
            mag_var = 12 + (lon + 130) * 0.3

        # Apply latitude adjustment (variation changes with latitude too)
        # WHY LATITUDE ADJUSTMENT: Magnetic poles aren't at geographic poles
        lat_adjustment = (lat - 40) * 0.2  # Using 40°N as reference latitude
        mag_var += lat_adjustment

        # Clamp to reasonable bounds for CONUS
        # WHY CLAMP: Prevents obviously wrong results from calculation errors
        mag_var = max(-25, min(20, mag_var))  # CONUS variation range is roughly -20° to +17°

        AirportManager._io.info(f"   ⚠️ WARNING: Using regional approximation: {mag_var:+.2f}° at {lat:.3f}, {lon:.3f}")
        AirportManager._io.info(f"   🚨 For aviation safety, verify with NOAA calculator!")
        AirportManager._io.info(f"   📏 Accuracy: ±3-5° (acceptable for low wind, verify for high wind)")
        # Store source for heading calculations
        AirportManager._last_mag_var_source = 'REGIONAL_APPROX'
        return mag_var

    @staticmethod
    def _get_accurate_magnetic_heading(runway, true_heading, mag_var):
        """
        Get accurate magnetic heading from user with smart default - USER INTERFACE METHOD

        AVIATION CONTEXT: This provides a user-friendly interface for pilots to verify
        or override the calculated magnetic heading. Combines automated calculation with
        pilot judgment for optimal accuracy.

        WORKFLOW:
        1. Calculate default magnetic heading using current best available variation
        2. Present default to pilot with option to override
        3. Validate pilot input and provide clear confirmation

        WHY USER VERIFICATION: Pilots may have more recent runway heading information
        from charts, NOTAMs, or local knowledge than automated systems.

        Args:
            runway (str): Runway identifier (e.g., "09", "27L")
            true_heading (int): True heading from OurAirports database
            mag_var (float): Magnetic variation for conversion

        Returns:
            int: Verified magnetic heading for runway operations
        """
        # Calculate default magnetic heading using current best available variation
        default_magnetic = AirportManager._true_to_magnetic_heading(true_heading, mag_var)

        try:
            # Auto-use computed magnetic heading when we have accurate NOAA data
            if AirportManager._last_mag_var_source == 'NOAA_WMM':
                AirportManager._io.info(f"   ✅ Auto-using accurate magnetic heading: {default_magnetic:03d}° (NOAA WMM data)")
                return default_magnetic
            else:
                # Prompt for verification when using regional approximation or manual input
                user_input = AirportManager._io.prompt(f"Runway {runway} magnetic heading [{default_magnetic:03d}°]: ").strip()

                if not user_input:
                    # User pressed Enter - accept calculated default
                    AirportManager._io.info(f"   ✅ Using calculated magnetic heading: {default_magnetic:03d}°")
                    return default_magnetic
                else:
                    # User entered a value - validate and use
                    user_heading = int(user_input)
                    if 0 <= user_heading <= 360:
                        AirportManager._io.info(f"   ✅ Using pilot-verified magnetic heading: {user_heading:03d}°")
                        return user_heading
                    else:
                        AirportManager._io.info(f"   ⚠️ Invalid heading {user_heading}°, using calculated {default_magnetic:03d}°")
                        return default_magnetic

        except (ValueError, EOFError):
            # Handle input errors gracefully
            AirportManager._io.info(f"   ✅ Using calculated magnetic heading: {default_magnetic:03d}°")
            return default_magnetic

    @staticmethod
    def _true_to_magnetic_heading(true_heading, mag_var):
        """
        Convert TRUE heading to MAGNETIC heading - SAFETY CRITICAL CALCULATION

        AVIATION CONTEXT: This is the core calculation that fixes the mixed reference
        system bug. OurAirports provides TRUE headings, but all aviation operations
        use MAGNETIC headings, and METAR wind data is MAGNETIC.

        CRITICAL FORMULA: Magnetic_Heading = True_Heading - Magnetic_Variation

        SIGN CONVENTION (AVIATION STANDARD):
        - Positive variation (East): Magnetic compass points east of true north
        - Negative variation (West): Magnetic compass points west of true north

        EXAMPLES:
        - True heading 090°, variation +10° East → Magnetic heading 080°
        - True heading 090°, variation -10° West → Magnetic heading 100°

        WHY THIS MATTERS: Consistent magnetic reference system enables accurate:
        - Wind component calculations (METAR wind vs runway heading)
        - Runway performance chart usage
        - Pilot situational awareness

        Args:
            true_heading (int): True heading from database (0-359°)
            mag_var (float): Magnetic variation (positive=East, negative=West)

        Returns:
            int: Magnetic heading normalized to 0-359° range
        """
        # Apply the critical conversion formula
        magnetic = true_heading - mag_var

        # Normalize to standard 0-359° aviation heading range
        # WHY NORMALIZE: Aviation headings are always 0-359°, not negative or >360°
        while magnetic < 0:
            magnetic += 360
        while magnetic >= 360:
            magnetic -= 360
        return int(magnetic)

    def _test_magnetic_variation_system(self):
        """
        TEST CASE: Comprehensive testing of magnetic variation system - SAFETY CRITICAL

        WHY THESE TESTS MATTER: The magnetic variation system fixes the core safety bug
        where TRUE and MAGNETIC headings were mixed. These tests verify the conversion
        formulas work correctly with known magnetic variation values.
        """
        AirportManager._io.info("🧭 Testing magnetic variation conversion formulas...")

        # Test case 1: Eastern US location (negative/westerly variation)
        # Known: Boston area has approximately -14° variation
        boston_lat, boston_lon = 42.3, -71.0
        regional_var = AirportManager._regional_approximation(boston_lat, boston_lon)
        # Should be negative (westerly) for East Coast
        assert regional_var < -5, f"East Coast variation should be westerly, got {regional_var}°"

        # Test case 2: Western US location (positive/easterly variation)
        # Known: San Francisco area has approximately +13° variation
        sf_lat, sf_lon = 37.6, -122.4
        regional_var = AirportManager._regional_approximation(sf_lat, sf_lon)
        # Should be positive (easterly) for West Coast
        assert regional_var > 5, f"West Coast variation should be easterly, got {regional_var}°"

        # Test case 3: TRUE to MAGNETIC conversion with known values
        # Example: Runway 09 (090° true) with +10° easterly variation → 080° magnetic
        true_heading = 90
        mag_var = 10.0  # Easterly variation
        magnetic = AirportManager._true_to_magnetic_heading(true_heading, mag_var)
        expected_magnetic = 80  # 90° - 10° = 80°
        assert magnetic == expected_magnetic, f"East variation test failed: expected {expected_magnetic}°, got {magnetic}°"

        # Test case 4: TRUE to MAGNETIC conversion with westerly variation
        # Example: Runway 09 (090° true) with -10° westerly variation → 100° magnetic
        mag_var = -10.0  # Westerly variation
        magnetic = AirportManager._true_to_magnetic_heading(true_heading, mag_var)
        expected_magnetic = 100  # 90° - (-10°) = 100°
        assert magnetic == expected_magnetic, f"West variation test failed: expected {expected_magnetic}°, got {magnetic}°"

        # Test case 5: Heading normalization (crossing 360°/0° boundary)
        true_heading = 10  # Close to north
        mag_var = 15.0     # Large easterly variation
        magnetic = AirportManager._true_to_magnetic_heading(true_heading, mag_var)
        expected_magnetic = 355  # 10° - 15° = -5°, normalized to 355°
        assert magnetic == expected_magnetic, f"Normalization test failed: expected {expected_magnetic}°, got {magnetic}°"

        # Test case 6: Reverse normalization (crossing 0°/360° boundary)
        true_heading = 350
        mag_var = -15.0    # Westerly variation
        magnetic = AirportManager._true_to_magnetic_heading(true_heading, mag_var)
        expected_magnetic = 5  # 350° - (-15°) = 365°, normalized to 5°
        assert magnetic == expected_magnetic, f"Reverse normalization test failed: expected {expected_magnetic}°, got {magnetic}°"

        # Test case 7: Verify regional approximation bounds
        # Should never produce values outside reasonable CONUS range
        test_locations = [
            (25.7, -80.2),   # Miami
            (47.4, -122.3),  # Seattle
            (39.1, -104.8),  # Denver
            (44.9, -93.2)    # Minneapolis
        ]

        for lat, lon in test_locations:
            var = AirportManager._regional_approximation(lat, lon)
            assert -25 <= var <= 20, f"Variation {var}° outside CONUS bounds at {lat}, {lon}"

        AirportManager._io.info("✅ Magnetic variation system tests passed")

    def run_magnetic_variation_tests(self):
        """
        COMPREHENSIVE TEST RUNNER for magnetic variation system

        WHY THIS EXISTS: The magnetic variation system is SAFETY CRITICAL because it
        fixes the mixed TRUE/MAGNETIC reference bug that could cause incorrect wind
        component calculations and runway performance errors.

        USAGE: Call this method to verify magnetic variation calculations
        Example: AirportManager().run_magnetic_variation_tests()
        """
        AirportManager._io.info("\\n" + "="*60)
        AirportManager._io.info("🧭 RUNNING MAGNETIC VARIATION SAFETY TESTS")
        AirportManager._io.info("="*60)
        AirportManager._io.info("Testing TRUE→MAGNETIC conversion formulas that fix the critical")
        AirportManager._io.info("reference system bug (OurAirports TRUE vs METAR MAGNETIC)...")
        AirportManager._io.info("\\n⚠️  If any test fails, magnetic heading conversions are incorrect!")
        AirportManager._io.info("-"*60)

        try:
            self._test_magnetic_variation_system()

            AirportManager._io.info("\\n" + "="*60)
            AirportManager._io.info("✅ ALL MAGNETIC VARIATION TESTS PASSED!")
            AirportManager._io.info("🧭 TRUE→MAGNETIC conversion system is working correctly.")
            AirportManager._io.info("🔒 Mixed reference system bug is properly fixed.")
            AirportManager._io.info("="*60)

        except AssertionError as e:
            AirportManager._io.info("\\n" + "🚨"*20)
            AirportManager._io.error("❌ MAGNETIC VARIATION TEST FAILURE!")
            AirportManager._io.info(f"💥 Test failed: {e}")
            AirportManager._io.info("⛔ TRUE→MAGNETIC conversions are incorrect!")
            AirportManager._io.info("🔧 Fix magnetic variation calculations before use!")
            AirportManager._io.warning("🚨"*20)
            raise

        except Exception as e:
            AirportManager._io.info("\\n" + "⚠️ "*20)
            AirportManager._io.info("❓ MAGNETIC VARIATION TEST ERROR!")
            AirportManager._io.info(f"💥 Error: {e}")
            AirportManager._io.info("🔍 Check magnetic variation implementation.")
            AirportManager._io.warning("⚠️ "*20)
            raise

    @staticmethod
    def get_airport_data(icao, runway):
        """Get airport data with automatic runway lookup"""
        AirportManager._io.info(f"\\n🔍 Looking up airport and runway data for {icao} runway {runway}...")

        airport_info = AirportManager._fetch_airport_info(icao)
        if not airport_info:
            return AirportManager._get_manual_data(icao, runway)

        runway_info = AirportManager._fetch_runway_info(icao, runway, airport_info['mag_var'])

        if runway_info:
            # Get accurate magnetic heading from user with smart default
            # Note: Wind data not yet available at this stage, warnings added later if needed
            accurate_magnetic_heading = AirportManager._get_accurate_magnetic_heading(
                runway, runway_info['true_heading'], airport_info['mag_var']
            )

            AirportManager._io.info(f"✅ Using runway {runway}: {runway_info['length']} ft, magnetic heading {accurate_magnetic_heading}°, {runway_info['surface']}")
            return {
                'icao': icao,
                'name': airport_info['name'],
                'elevation_ft': airport_info['elevation_ft'],
                'runway_length_ft': runway_info['length'],
                'runway_heading': accurate_magnetic_heading,
                'surface': runway_info['surface'],
                'source': 'OurAirports + Verified Magnetic Heading'
            }
        else:
            AirportManager._io.info(f"⚠️ Runway {runway} data not found online, requesting manual input...")
            runway_data = AirportManager._get_runway_data(runway)
            if runway_data:
                return {
                    'icao': icao,
                    'name': airport_info['name'],
                    'elevation_ft': airport_info['elevation_ft'],
                    'runway_length_ft': runway_data['length'],
                    'runway_heading': runway_data['heading'],
                    'surface': runway_data['surface'],
                    'source': 'OurAirports + Manual Runway'
                }

        return AirportManager._get_manual_data(icao, runway)

    @staticmethod
    def _fetch_airport_info(icao):
        """Fetch basic airport information"""
        try:
            LOGGER.debug("Fetching airport info from OurAirports")
            response = requests.get("https://davidmegginson.github.io/ourairports-data/airports.csv", timeout=15)

            if response.status_code == 200:
                reader = csv.DictReader(StringIO(response.text))
                for row in reader:
                    if not row:
                        continue
                    if row.get('ident') == icao:
                        try:
                            elevation_ft = int(float(row.get('elevation_ft', '') or 0))
                            lat = float(row.get('latitude_deg', '') or 0.0)
                            lon = float(row.get('longitude_deg', '') or 0.0)
                        except ValueError:
                            elevation_ft = lat = lon = None

                        if elevation_ft is not None and lat is not None and lon is not None:
                            mag_var = AirportManager._calculate_magnetic_variation(lat, lon)
                            LOGGER.info(
                                "Found %s: %s, elevation %s ft",
                                icao,
                                row.get('name', 'Unknown Airport'),
                                elevation_ft,
                            )
                            return {
                                'name': row.get('name', 'Unknown Airport'),
                                'elevation_ft': elevation_ft,
                                'lat': lat,
                                'lon': lon,
                                'mag_var': mag_var
                            }

        except Exception as e:
            LOGGER.warning("Airport lookup failed: %s", e)

        return None

    @staticmethod
    def _fetch_runway_info(icao, runway, mag_var):
        """Fetch runway information from online sources"""
        runway_data = AirportManager._fetch_ourairports_runway_data(icao, runway, mag_var)
        if runway_data:
            return runway_data

        return None

    @staticmethod
    def _fetch_ourairports_runway_data(icao, runway, mag_var):
        """Attempt to fetch runway data from OurAirports runways.csv and convert to magnetic heading"""
        try:
            AirportManager._io.info(f"   📡 Trying OurAirports runways database...")
            response = requests.get("https://davidmegginson.github.io/ourairports-data/runways.csv", timeout=15)

            if response.status_code == 200:
                lines = response.text.split('\\n')

                airport_id = None
                airport_response = requests.get("https://davidmegginson.github.io/ourairports-data/airports.csv", timeout=10)
                if airport_response.status_code == 200:
                    airport_lines = airport_response.text.split('\\n')
                    for line in airport_lines[1:]:
                        if line.strip():
                            data = line.split(',')
                            if len(data) > 1:
                                icao_from_csv = data[1].strip().strip('"')
                                if icao_from_csv == icao:
                                    airport_id = data[0].strip().strip('"')
                                    break

                if not airport_id:
                    return None

                for line in lines[1:]:
                    if line.strip():
                        try:
                            data = line.split(',')
                            if len(data) > 15:
                                rwy_airport_ref = data[1].strip().strip('"')
                                if rwy_airport_ref == airport_id:
                                    le_ident = data[8].strip().strip('"')
                                    he_ident = data[14].strip().strip('"')
                                    length_ft_str = data[3].strip().strip('"')
                                    surface = data[5].strip().strip('"')
                                    le_heading_str = data[12].strip().strip('"')
                                    he_heading_str = data[18].strip().strip('"')

                                    runway_clean = runway.upper().replace('RW', '').replace('RUNWAY', '').strip()

                                    if (le_ident.upper() == runway_clean or he_ident.upper() == runway_clean):
                                        try:
                                            length_ft = int(float(length_ft_str)) if length_ft_str else None
                                            if le_ident.upper() == runway_clean:
                                                true_heading = int(float(le_heading_str)) if le_heading_str else None
                                            else:
                                                true_heading = int(float(he_heading_str)) if he_heading_str else None

                                            if length_ft and true_heading is not None:
                                                # Convert TRUE heading from OurAirports to MAGNETIC heading
                                                magnetic_heading = AirportManager._true_to_magnetic_heading(true_heading, mag_var)

                                                surface_clean = surface.replace('"', '').strip() if surface else 'Unknown'
                                                if not surface_clean or surface_clean.lower() in ['', 'unknown']:
                                                    surface_clean = 'Asphalt'

                                                AirportManager._io.info(f"   ✅ Found runway {runway}: {length_ft} ft, {true_heading}°T→{magnetic_heading}°M, {surface_clean}")
                                                return {
                                                    'length': length_ft,
                                                    'true_heading': true_heading,  # Keep original true heading
                                                    'heading': magnetic_heading,   # Calculated magnetic heading
                                                    'surface': surface_clean
                                                }
                                        except (ValueError, TypeError):
                                            continue
                        except:
                            continue

        except Exception as e:
            AirportManager._io.info(f"   ⚠️ OurAirports runway lookup failed: {e}")

        return None

    @staticmethod
    def _get_runway_data(runway):
        """Get runway data manually"""
        AirportManager._io.info(f"\\nManual runway {runway} data entry:")
        try:
            length = int(AirportManager._io.prompt("Length (ft): "))
            heading = int(AirportManager._io.prompt("Magnetic heading: "))
            surface = AirportManager._io.prompt("Surface [Asphalt]: ") or "Asphalt"
            return {'length': length, 'heading': heading, 'surface': surface}
        except:
            return None

    @staticmethod
    def _get_manual_data(icao, runway):
        """Get all data manually"""
        AirportManager._io.info(f"\\nFull manual entry for {icao}:")
        try:
            name = AirportManager._io.prompt("Airport name: ") or icao + " Airport"
            elevation = int(AirportManager._io.prompt("Field elevation (ft): "))
            length = int(AirportManager._io.prompt(f"Runway {runway} length (ft): "))
            heading = int(AirportManager._io.prompt(f"Runway {runway} heading: "))
            surface = AirportManager._io.prompt("Surface [Asphalt]: ") or "Asphalt"

            return {
                'icao': icao, 'name': name, 'elevation_ft': elevation,
                'runway_length_ft': length, 'runway_heading': heading,
                'surface': surface, 'source': 'Manual Input'
            }
        except:
            return None
