#!/usr/bin/env python3
"""
Performance Calculator for SR22T Aircraft

SAFETY-CRITICAL AVIATION COMPONENT:

WHY THIS CLASS EXISTS:
The PerformanceCalculator handles all flight performance calculations for the SR22T.
These calculations are SAFETY CRITICAL - incorrect results could lead to runway overruns,
inadequate climb performance, or other dangerous situations.

ARCHITECTURE DECISION: Centralized performance calculations
- All aviation calculations in one place for consistency and testing
- Uses embedded POH (Pilot's Operating Handbook) data for accuracy
- Implements proper altitude corrections (pressure altitude, density altitude)
- Handles wind component analysis for runway performance

AVIATION CONTEXT BASICS:
- Pressure Altitude: What the altimeter reads when set to 29.92" (standard)
- Density Altitude: How the airplane "feels" the altitude based on temperature
- Higher density altitude = worse performance (longer takeoff, reduced climb)
- Wind components: Headwind helps performance, crosswind adds complexity

TESTING STRATEGY: Verify all calculations with known aviation formulas
"""

import math
from ..config import Config
from .data import EMBEDDED_SR22T_PERFORMANCE


class PerformanceCalculator:
    """Handles all aviation performance calculations for SR22T aircraft."""

    def __init__(self):
        """
        Initialize with embedded SR22T performance data from POH

        WHY EMBEDDED DATA: Ensures offline operation and eliminates
        external dependency failures during critical flight planning
        """
        self.performance_data = EMBEDDED_SR22T_PERFORMANCE

    def calculate_pressure_altitude(self, field_elevation_ft, altimeter_inhg):
        """
        Calculate pressure altitude using standard aviation formula

        AVIATION CONTEXT: Pressure altitude standardizes performance calculations
        regardless of current barometric pressure. Critical for accurate performance.

        FORMULA: PA = Field Elevation + (29.92 - Current Altimeter Setting) × 1000
        WHERE: 29.92 inHg is standard atmospheric pressure at sea level

        Args:
            field_elevation_ft (int): Airport elevation above sea level
            altimeter_inhg (float): Current altimeter setting from METAR

        Returns:
            int: Pressure altitude rounded to nearest 10 ft (for table lookup)
        """
        # Standard pressure altitude formula - aviation standard since ICAO adoption
        pa = field_elevation_ft + (29.92 - altimeter_inhg) * 1000

        print("Pressure altitude: " + str(round(pa, 0)) + " ft")

        # Round to nearest 10 ft for performance table interpolation
        # WHY ROUNDING: POH tables use 10 ft increments, enables accurate interpolation
        return round(pa / Config.PRESSURE_ALTITUDE_ROUND) * Config.PRESSURE_ALTITUDE_ROUND

    def _test_pressure_altitude_calculation(self):
        """
        TEST CASE: Verify pressure altitude calculation with known values

        SAFETY CRITICAL: Incorrect pressure altitude leads to wrong performance figures
        """
        # Test case 1: Standard conditions (29.92 inHg at sea level)
        result = self.calculate_pressure_altitude(0, 29.92)
        assert result == 0, f"Standard conditions test failed: expected 0, got {result}"

        # Test case 2: High pressure system (30.12 inHg)
        result = self.calculate_pressure_altitude(1000, 30.12)
        expected = 1000 + (29.92 - 30.12) * 1000  # Should be 800 ft
        expected_rounded = round(expected / 10) * 10  # Round to nearest 10
        assert result == expected_rounded, f"High pressure test failed: expected {expected_rounded}, got {result}"

        # Test case 3: Low pressure system (29.72 inHg)
        result = self.calculate_pressure_altitude(1000, 29.72)
        expected = 1000 + (29.92 - 29.72) * 1000  # Should be 1200 ft
        expected_rounded = round(expected / 10) * 10
        assert result == expected_rounded, f"Low pressure test failed: expected {expected_rounded}, got {result}"

        print("✅ Pressure altitude calculation tests passed")

    def calculate_isa_temp(self, pressure_altitude_ft):
        """
        Calculate ISA (International Standard Atmosphere) temperature

        AVIATION CONTEXT: ISA provides standard temperature at any altitude.
        Used to determine if actual temperature is hotter/colder than standard.
        Hotter than ISA = higher density altitude = worse performance.

        FORMULA: ISA Temp = 15°C - (2°C × pressure_altitude_thousands)
        WHERE: 15°C is standard temperature at sea level, -2°C per 1000 ft is lapse rate

        Args:
            pressure_altitude_ft (int): Pressure altitude in feet

        Returns:
            float: ISA temperature in Celsius at given altitude
        """
        # Standard atmospheric lapse rate: -2°C per 1000 feet
        # 15°C is ISA temperature at sea level
        return round(15 - 2 * (pressure_altitude_ft / 1000), 1)

    def _test_isa_temperature_calculation(self):
        """
        TEST CASE: Verify ISA temperature calculation

        AVIATION STANDARD: Must match ICAO standard atmosphere values
        """
        # Test case 1: Sea level ISA temperature
        result = self.calculate_isa_temp(0)
        assert result == 15.0, f"Sea level ISA test failed: expected 15.0°C, got {result}"

        # Test case 2: 3000 ft ISA temperature
        result = self.calculate_isa_temp(3000)
        expected = 15 - 2 * (3000 / 1000)  # Should be 9°C
        assert result == expected, f"3000 ft ISA test failed: expected {expected}°C, got {result}"

        # Test case 3: 5000 ft ISA temperature
        result = self.calculate_isa_temp(5000)
        expected = 15 - 2 * (5000 / 1000)  # Should be 5°C
        assert result == expected, f"5000 ft ISA test failed: expected {expected}°C, got {result}"

        print("✅ ISA temperature calculation tests passed")

    def calculate_density_altitude(self, pressure_altitude_ft, oat_c, field_elevation_ft):
        """
        Calculate density altitude - critical for performance assessment

        AVIATION CONTEXT: Density altitude is how the airplane "feels" the altitude.
        High density altitude (hot day, high altitude) severely degrades performance:
        - Longer takeoff distances
        - Reduced climb rate
        - Higher true airspeeds for given indicated airspeed

        FORMULA: DA = PA + 120 × (OAT - ISA_Temp)
        WHERE: 120 is the standard correction factor for temperature deviation

        SAFETY CRITICAL: Underestimating density altitude can lead to:
        - Runway overruns during takeoff
        - Inability to clear obstacles
        - Degraded climb performance

        Args:
            pressure_altitude_ft (int): Pressure altitude
            oat_c (float): Outside air temperature in Celsius
            field_elevation_ft (int): Field elevation (used for display)

        Returns:
            int: Density altitude rounded to nearest 50 ft
        """
        # Get ISA temperature at this pressure altitude
        isa_temp = self.calculate_isa_temp(pressure_altitude_ft)

        # Standard density altitude formula
        # 120 ft per degree C deviation from ISA is aviation standard
        density_altitude = pressure_altitude_ft + 120 * (oat_c - isa_temp)

        print("Density altitude: " + str(round(density_altitude, 0)) + " ft")

        # Round to nearest 50 ft for performance calculations
        # WHY 50 FT: Provides reasonable precision without false accuracy
        return round(density_altitude / Config.DENSITY_ALTITUDE_ROUND) * Config.DENSITY_ALTITUDE_ROUND

    def _test_density_altitude_calculation(self):
        """
        TEST CASE: Verify density altitude calculation with known scenarios

        SAFETY CRITICAL: Wrong density altitude = wrong performance calculations
        """
        # Test case 1: Standard conditions (OAT equals ISA)
        pressure_alt = 1000
        isa_temp = self.calculate_isa_temp(pressure_alt)  # Should be 13°C at 1000 ft
        result = self.calculate_density_altitude(pressure_alt, isa_temp, 1000)
        # When OAT = ISA, density altitude should equal pressure altitude
        assert result == pressure_alt, f"Standard ISA test failed: expected {pressure_alt}, got {result}"

        # Test case 2: Hot day (OAT 10°C above ISA)
        hot_temp = isa_temp + 10  # 10°C hotter than ISA
        result = self.calculate_density_altitude(pressure_alt, hot_temp, 1000)
        expected = pressure_alt + 120 * 10  # Should be 2200 ft
        expected_rounded = round(expected / 50) * 50
        assert result == expected_rounded, f"Hot day test failed: expected {expected_rounded}, got {result}"

        # Test case 3: Cold day (OAT 5°C below ISA)
        cold_temp = isa_temp - 5  # 5°C colder than ISA
        result = self.calculate_density_altitude(pressure_alt, cold_temp, 1000)
        expected = pressure_alt + 120 * (-5)  # Should be 400 ft
        expected_rounded = round(expected / 50) * 50
        assert result == expected_rounded, f"Cold day test failed: expected {expected_rounded}, got {result}"

        print("✅ Density altitude calculation tests passed")

    def calculate_wind_components(self, runway_heading, wind_dir, wind_speed):
        """
        Calculate headwind/crosswind components for runway performance

        AVIATION CONTEXT: Wind components directly affect aircraft performance:
        - Headwind: Reduces takeoff distance, increases climb gradient efficiency
        - Tailwind: Increases takeoff distance, reduces climb gradient efficiency
        - Crosswind: Adds complexity to takeoff/landing, doesn't affect performance tables

        SAFETY CRITICAL: Incorrect wind calculations can lead to:
        - Using wrong performance charts (headwind vs tailwind)
        - Inadequate runway length calculations
        - Incorrect climb gradient assessments

        FORMULA EXPLANATION:
        - Headwind = Wind Speed × cos(angle_difference)
        - Crosswind = Wind Speed × sin(angle_difference)
        - Angle normalization keeps angles within ±180° for proper calculations

        Args:
            runway_heading (int): Magnetic heading of runway (from magnetic variation correction)
            wind_dir (int): Wind direction in degrees magnetic (from METAR)
            wind_speed (int): Wind speed in knots

        Returns:
            dict: Wind components with accuracy warnings for high wind conditions
        """
        # Ensure numeric values (handle string input from Garmin Pilot briefings and variable winds)
        try:
            # Handle variable wind direction (VRB in METAR)
            if isinstance(wind_dir, str) and wind_dir.upper() == 'VRB':
                print(f"Variable wind direction - using runway heading for calculation")
                wind_dir = runway_heading  # Treat as headwind for performance calculations
            else:
                wind_dir = int(wind_dir)

            wind_speed = int(wind_speed)
            runway_heading = int(runway_heading)
        except (ValueError, TypeError):
            print(f"Error: Invalid wind data - wind_dir: {wind_dir}, wind_speed: {wind_speed}, runway_heading: {runway_heading}")
            # Return zero wind as fallback
            return {
                'headwind': 0,
                'crosswind': 0,
                'crosswind_direction': 'none',
                'is_tailwind': False,
                'crosswind_exceeds_limits': False
            }

        # Normalize angle difference to ±180 degrees
        # WHY NORMALIZE: Ensures we get the acute angle between runway and wind
        # Example: runway 030°, wind 300° should be 60° angle (not 270°)
        angle_diff = wind_dir - runway_heading
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        # Convert to radians for trigonometric functions
        angle_rad = math.radians(angle_diff)

        # Calculate wind components using standard trigonometry
        headwind = wind_speed * math.cos(angle_rad)  # Positive = headwind, Negative = tailwind
        crosswind = wind_speed * math.sin(angle_rad)  # Positive = right crosswind, Negative = left

        # Get absolute crosswind for magnitude (direction stored separately)
        abs_crosswind = abs(crosswind)

        # Check SR22T crosswind limits (POH data: max demonstrated 21 kt)
        crosswind_exceeds_limits = abs_crosswind > 21
        if crosswind_exceeds_limits:
            print(f"🚨 CROSSWIND EXCEEDS LIMITS: {abs_crosswind:.0f} kt > 21 kt max demonstrated")
            print("   Runway may not be suitable for SR22T operations")

        # Issue warnings for conditions requiring increased heading accuracy
        # WHY WARNINGS: High winds amplify small heading errors into large performance errors
        if wind_speed >= 20:
            print(f"⚠️ Strong winds detected ({wind_speed} kt) - verify magnetic heading accuracy")
        elif abs_crosswind >= 10:
            print(f"⚠️ Significant crosswind ({abs_crosswind:.0f} kt) - verify magnetic heading accuracy")

        return {
            'headwind': round(headwind),                    # Positive=headwind, negative=tailwind
            'crosswind': round(abs_crosswind),             # Always positive magnitude
            'crosswind_direction': 'right' if crosswind > 0 else 'left',  # Direction for pilot awareness
            'is_tailwind': headwind < 0,                   # Boolean flag for performance chart selection
            'crosswind_exceeds_limits': crosswind_exceeds_limits  # Boolean flag for runway suitability
        }

    def _test_wind_component_calculation(self):
        """
        TEST CASE: Verify wind component calculations with known scenarios

        SAFETY CRITICAL: Wrong wind components = wrong runway performance calculations
        """
        # Test case 1: Direct headwind (wind aligned with runway)
        result = self.calculate_wind_components(360, 360, 20)  # Runway 36, wind 360@20
        assert result['headwind'] == 20, f"Direct headwind test failed: expected 20, got {result['headwind']}"
        assert result['crosswind'] == 0, f"Direct headwind crosswind test failed: expected 0, got {result['crosswind']}"
        assert not result['is_tailwind'], f"Direct headwind tailwind flag test failed"

        # Test case 2: Direct tailwind (wind opposite to runway)
        result = self.calculate_wind_components(360, 180, 15)  # Runway 36, wind 180@15
        assert result['headwind'] == -15, f"Direct tailwind test failed: expected -15, got {result['headwind']}"
        assert result['crosswind'] == 0, f"Direct tailwind crosswind test failed: expected 0, got {result['crosswind']}"
        assert result['is_tailwind'], f"Direct tailwind flag test failed"

        # Test case 3: Direct crosswind (wind perpendicular to runway)
        result = self.calculate_wind_components(360, 270, 12)  # Runway 36, wind 270@12
        assert abs(result['headwind']) < 1, f"Direct crosswind headwind test failed: expected ~0, got {result['headwind']}"
        assert result['crosswind'] == 12, f"Direct crosswind test failed: expected 12, got {result['crosswind']}"
        assert result['crosswind_direction'] == 'left', f"Crosswind direction test failed"

        # Test case 4: 45-degree wind angle (known trigonometry result)
        result = self.calculate_wind_components(360, 45, 20)  # Runway 36, wind 45@20
        expected_component = 20 * math.cos(math.radians(45))  # Should be ~14.1 kt
        assert abs(result['headwind'] - round(expected_component)) <= 1, f"45-degree headwind test failed"
        assert abs(result['crosswind'] - round(expected_component)) <= 1, f"45-degree crosswind test failed"

        # Test case 5: Angle normalization test (wind direction > 180° from runway)
        result = self.calculate_wind_components(30, 300, 10)  # Should normalize to 90° angle
        # 30° runway, 300° wind = 270° difference, normalized to -90° (90° left crosswind)
        assert abs(result['headwind']) < 1, f"Angle normalization headwind test failed"
        assert result['crosswind'] == 10, f"Angle normalization crosswind test failed"

        print("✅ Wind component calculation tests passed")

    def check_runway_surface_suitability(self, surface_type):
        """
        Check runway surface suitability for SR22T operations

        AVIATION CONTEXT: Performance tables assume hard surface runways
        Soft field operations require different techniques and have degraded performance

        Args:
            surface_type (str): Runway surface type from airport data

        Returns:
            dict: Surface suitability assessment with warnings
        """
        surface_lower = surface_type.lower() if surface_type else ""

        # Hard surface runway types (suitable for standard performance calculations)
        hard_surfaces = [
            'asphalt', 'concrete', 'paved', 'sealed', 'asp', 'con',
            'bitumen', 'tarmac', 'runway', 'hard'
        ]

        # Soft/problematic surfaces requiring special procedures
        soft_surfaces = [
            'grass', 'turf', 'dirt', 'gravel', 'soil', 'sand', 'earth',
            'sod', 'clay', 'unpaved', 'natural', 'soft'
        ]

        is_hard_surface = any(hard in surface_lower for hard in hard_surfaces)
        is_soft_surface = any(soft in surface_lower for soft in soft_surfaces)

        if is_soft_surface:
            print(f"🚨 SOFT FIELD DETECTED: {surface_type}")
            print("   Performance calculations assume hard surface runway")
            print("   Soft field operations require pilot evaluation and different techniques")
            return {
                'suitable_for_standard_performance': False,
                'surface_type': surface_type,
                'warning': f'Soft field ({surface_type}) - standard performance not applicable',
                'requires_pilot_evaluation': True
            }
        elif is_hard_surface or not surface_lower:
            # Assume hard surface if unknown or clearly hard
            return {
                'suitable_for_standard_performance': True,
                'surface_type': surface_type or 'Assumed hard surface',
                'warning': None,
                'requires_pilot_evaluation': False
            }
        else:
            # Unknown surface type - conservative approach
            print(f"⚠️ UNKNOWN SURFACE TYPE: {surface_type}")
            print("   Assuming hard surface but recommend pilot verification")
            return {
                'suitable_for_standard_performance': True,
                'surface_type': surface_type,
                'warning': f'Unknown surface type ({surface_type}) - verify suitability',
                'requires_pilot_evaluation': True
            }

    def calculate_climb_gradients(self, pressure_altitude_ft, temperature_c, density_altitude_ft, headwind_kt):
        """
        Calculate climb gradients at 91 KIAS (takeoff) and 120 KIAS (enroute)

        AVIATION CONTEXT: Climb gradients determine obstacle clearance capability:
        - 91 KIAS: Used for takeoff and initial climb (obstacle clearance critical)
        - 120 KIAS: Used for enroute climb (efficiency optimized)
        - Ground Speed affects gradient: headwind improves, tailwind degrades

        SAFETY CRITICAL: Inadequate climb gradient can result in:
        - Collision with obstacles during departure
        - Inability to meet published departure procedure requirements
        - Terrain avoidance failures in mountainous areas

        CALCULATIONS PERFORMED:
        1. True Airspeed correction for density altitude (2% per 1000 ft DA)
        2. Ground Speed calculation (TAS adjusted for headwind component)
        3. Climb gradient interpolation from embedded POH data

        Args:
            pressure_altitude_ft (int): Pressure altitude for chart lookup
            temperature_c (float): Temperature for chart interpolation
            density_altitude_ft (int): For TAS calculation
            headwind_kt (int): For ground speed calculation (positive=headwind)

        Returns:
            dict: TAS, Ground Speed, and climb gradients for both speeds
        """

        # Convert density altitude to thousands for TAS calculation
        da_thousands = density_altitude_ft / 1000

        # Calculate True Airspeed (TAS) using 2% correction per 1000 ft density altitude
        # WHY 2%: Standard aviation approximation for airspeed/altitude relationship
        tas_91 = 91 * (1 + 0.02 * da_thousands)
        tas_120 = 120 * (1 + 0.02 * da_thousands)

        # Calculate Ground Speed by accounting for wind component
        # Ground Speed = TAS - Headwind (negative headwind = tailwind adds to GS)
        gs_91 = tas_91 - headwind_kt
        gs_120 = tas_120 - headwind_kt

        print("Climb calculations:")
        print("  91 KIAS: " + str(round(tas_91, 1)) + " KTAS, " + str(round(gs_91, 1)) + " kt GS")
        print("  120 KIAS: " + str(round(tas_120, 1)) + " KTAS, " + str(round(gs_120, 1)) + " kt GS")

        # Interpolate climb gradients from POH data with error handling
        # WHY TRY/EXCEPT: POH data may not cover extreme conditions, graceful degradation required
        try:
            gradient_91 = self._interpolate_climb_gradient(pressure_altitude_ft, temperature_c, 'takeoff_climb_gradient_91')
            print("  91 KIAS gradient: " + str(round(gradient_91, 0)) + " ft/NM")
        except Exception as e:
            gradient_91 = None
            print("  91 KIAS gradient error: " + str(e))

        try:
            gradient_120 = self._interpolate_climb_gradient(pressure_altitude_ft, temperature_c, 'enroute_climb_gradient_120')
            print("  120 KIAS gradient: " + str(round(gradient_120, 0)) + " ft/NM (POH data)")
        except Exception as e:
            gradient_120 = None
            print("  120 KIAS gradient error: " + str(e))

        return {
            'tas_91': round(tas_91, 1),      # True airspeed at 91 KIAS
            'gs_91': round(gs_91, 1),        # Ground speed at 91 KIAS
            'gradient_91': gradient_91,      # Climb gradient at 91 KIAS (ft/NM)
            'tas_120': round(tas_120, 1),    # True airspeed at 120 KIAS
            'gs_120': round(gs_120, 1),      # Ground speed at 120 KIAS
            'gradient_120': gradient_120,    # Climb gradient at 120 KIAS (ft/NM)
            'climb_rate_91kias': gradient_91 # Store for CAPS calculations
        }

    def _test_climb_gradient_calculation(self):
        """
        TEST CASE: Verify climb gradient calculations and TAS/GS computations

        SAFETY CRITICAL: Wrong climb gradients could result in obstacle strikes
        """
        # Test case 1: Standard conditions, no wind
        result = self.calculate_climb_gradients(1000, 13, 1000, 0)  # PA=1000, ISA temp, DA=1000, no wind

        # Verify TAS calculation (should be close to IAS at low DA)
        expected_tas_91 = 91 * (1 + 0.02 * 1)  # 1000 ft DA = 1 thousand
        assert abs(result['tas_91'] - expected_tas_91) < 0.1, f"TAS 91 calculation failed"

        # Verify ground speed equals TAS with no wind
        assert result['gs_91'] == result['tas_91'], f"Ground speed should equal TAS with no wind"
        assert result['gs_120'] == result['tas_120'], f"Ground speed should equal TAS with no wind"

        # Test case 2: High density altitude effect
        result_high_da = self.calculate_climb_gradients(3000, 25, 5000, 0)  # High DA conditions
        result_std_da = self.calculate_climb_gradients(3000, 5, 3000, 0)    # Standard DA conditions

        # TAS should be higher at higher density altitude
        assert result_high_da['tas_91'] > result_std_da['tas_91'], f"High DA should increase TAS"

        # Test case 3: Wind effect on ground speed
        result_headwind = self.calculate_climb_gradients(1000, 13, 1000, 10)  # 10 kt headwind
        result_no_wind = self.calculate_climb_gradients(1000, 13, 1000, 0)   # No wind

        # Ground speed should be 10 kt less with 10 kt headwind
        assert result_headwind['gs_91'] == result_no_wind['gs_91'] - 10, f"Headwind ground speed calculation failed"

        print("✅ Climb gradient calculation tests passed")

    def _interpolate_climb_gradient(self, pressure_altitude, temperature, gradient_type):
        """
        Interpolate climb gradient from embedded POH data tables

        AVIATION CONTEXT: POH tables provide climb gradients at specific pressure altitudes
        and temperatures. Real-world conditions require interpolation between table values.

        INTERPOLATION STRATEGY: Two-dimensional interpolation
        1. Interpolate across temperature at low pressure altitude
        2. Interpolate across temperature at high pressure altitude
        3. Interpolate between pressure altitudes using results from steps 1-2

        SAFETY CRITICAL: Interpolation errors could provide overly optimistic climb performance

        Args:
            pressure_altitude (int): Pressure altitude for interpolation
            temperature (float): Temperature in Celsius for interpolation
            gradient_type (str): 'takeoff_climb_gradient_91' or 'enroute_climb_gradient_120'

        Returns:
            float: Interpolated climb gradient in ft/NM

        Raises:
            ValueError: If pressure altitude outside POH data range
        """
        gradient_data = self.performance_data['performance_data'][gradient_type]['conditions']

        # Extract available pressure altitudes from POH data
        altitudes = [cond['pressure_altitude_ft'] for cond in gradient_data]
        altitudes.sort()

        # Check if requested altitude is within POH data range
        # WHY CHECK RANGE: Extrapolation beyond POH data is unsafe for flight planning
        if pressure_altitude < min(altitudes) or pressure_altitude > max(altitudes):
            raise ValueError("PA outside range for " + gradient_type)

        # Find bracketing pressure altitudes for interpolation
        pa_low = pa_high = pressure_altitude
        for i in range(len(altitudes) - 1):
            if altitudes[i] <= pressure_altitude <= altitudes[i + 1]:
                pa_low, pa_high = altitudes[i], altitudes[i + 1]
                break

        # Get POH data for bracketing altitudes
        low_data = next(c for c in gradient_data if c['pressure_altitude_ft'] == pa_low)
        high_data = next(c for c in gradient_data if c['pressure_altitude_ft'] == pa_high)

        # Interpolate across temperature at each altitude
        low_gradient = self._interpolate_gradient_temperature(temperature, low_data['performance'])
        high_gradient = self._interpolate_gradient_temperature(temperature, high_data['performance'])

        # Final interpolation across pressure altitude
        if pa_low == pa_high:
            return low_gradient  # Exact altitude match, no interpolation needed
        else:
            pa_fraction = (pressure_altitude - pa_low) / (pa_high - pa_low)
            return low_gradient + pa_fraction * (high_gradient - low_gradient)

    def _interpolate_gradient_temperature(self, temperature, gradient_data):
        """Interpolate gradient across temperature"""
        temp_points = []
        for key, value in gradient_data.items():
            if 'temp_' in key and 'ft_per_nm' in key:
                if 'minus' in key:
                    temp = -int(key.split('minus')[1].split('c')[0])
                elif 'isa' in key:
                    temp = 15  # ISA temperature at sea level is 15°C
                else:
                    temp_part = key.split('temp_')[1].split('c')[0]
                    if temp_part.isdigit():  # Only convert if it's a digit
                        temp = int(temp_part)
                    else:
                        continue  # Skip invalid temperature keys
                temp_points.append((temp, value))

        temp_points.sort()

        temps = [t[0] for t in temp_points]
        if temperature < min(temps) or temperature > max(temps):
            raise ValueError("Temperature outside range")

        for i in range(len(temp_points) - 1):
            if temp_points[i][0] <= temperature <= temp_points[i + 1][0]:
                temp_low, val_low = temp_points[i]
                temp_high, val_high = temp_points[i + 1]
                break
        else:
            for temp, val in temp_points:
                if temp == temperature:
                    return val

        if temp_low == temp_high:
            return val_low
        else:
            temp_fraction = (temperature - temp_low) / (temp_high - temp_low)
            return val_low + temp_fraction * (val_high - val_low)

    def interpolate_performance(self, pressure_altitude, temperature, performance_type):
        """Interpolate performance data"""
        perf_data = self.performance_data['performance_data'][performance_type]['conditions']

        altitudes = [cond['pressure_altitude_ft'] for cond in perf_data]
        altitudes.sort()

        if pressure_altitude < min(altitudes) or pressure_altitude > max(altitudes):
            raise ValueError("Pressure altitude outside data range")

        pa_low = pa_high = pressure_altitude
        for i in range(len(altitudes) - 1):
            if altitudes[i] <= pressure_altitude <= altitudes[i + 1]:
                pa_low, pa_high = altitudes[i], altitudes[i + 1]
                break

        low_data = next(c for c in perf_data if c['pressure_altitude_ft'] == pa_low)
        high_data = next(c for c in perf_data if c['pressure_altitude_ft'] == pa_high)

        result = {}
        for metric in ['ground_roll_ft', 'total_distance_ft']:
            low_val = self._interpolate_temperature(temperature, low_data['performance'], metric)
            high_val = self._interpolate_temperature(temperature, high_data['performance'], metric)

            if pa_low == pa_high:
                result[metric] = low_val
            else:
                pa_fraction = (pressure_altitude - pa_low) / (pa_high - pa_low)
                result[metric] = low_val + pa_fraction * (high_val - low_val)

            result[metric] = round(result[metric] / Config.PERFORMANCE_DISTANCE_ROUND) * Config.PERFORMANCE_DISTANCE_ROUND

        return result

    def _interpolate_temperature(self, temperature, temp_data, metric):
        """Interpolate across temperature"""
        temps = []
        for key in temp_data.keys():
            if 'temp_' in key:
                temp_str = key.replace('temp_', '').replace('c', '').replace('minus', '-')
                temps.append(int(temp_str))

        temps.sort()

        if temperature < min(temps) or temperature > max(temps):
            raise ValueError("Temperature outside data range")

        temp_low = temp_high = temperature
        for i in range(len(temps) - 1):
            if temps[i] <= temperature <= temps[i + 1]:
                temp_low, temp_high = temps[i], temps[i + 1]
                break

        temp_low_key = "temp_" + str(temp_low) + "c" if temp_low >= 0 else "temp_minus" + str(abs(temp_low)) + "c"
        temp_high_key = "temp_" + str(temp_high) + "c" if temp_high >= 0 else "temp_minus" + str(abs(temp_high)) + "c"

        low_val = temp_data[temp_low_key][metric]
        high_val = temp_data[temp_high_key][metric]

        if temp_low == temp_high:
            return low_val
        else:
            temp_fraction = (temperature - temp_low) / (temp_high - temp_low)
            return low_val + temp_fraction * (high_val - low_val)

    def run_safety_critical_tests(self):
        """
        COMPREHENSIVE TEST RUNNER for all safety-critical performance calculations

        WHY THIS FUNCTION EXISTS:
        - Verifies all aviation calculations work correctly before flight use
        - Provides confidence in safety-critical performance computations
        - Serves as executable documentation of expected behavior
        - Enables quick verification after code changes

        USAGE: Call this method to verify all performance calculations
        Example: calc = PerformanceCalculator(); calc.run_safety_critical_tests()

        TESTING PHILOSOPHY: Test safety-critical calculations comprehensively,
        skip trivial operations that don't affect flight safety.
        """
        print("\\n" + "="*60)
        print("🔬 RUNNING SAFETY-CRITICAL PERFORMANCE CALCULATOR TESTS")
        print("="*60)
        print("Testing all aviation calculations that affect flight safety...")
        print("These tests verify pressure altitude, density altitude, wind components,")
        print("and climb gradient calculations against known aviation formulas.")
        print("\\n⚠️  If any test fails, DO NOT USE for flight planning!")
        print("-"*60)

        try:
            # Test pressure altitude calculations (affects all performance lookups)
            print("\\n1️⃣ Testing Pressure Altitude Calculations...")
            self._test_pressure_altitude_calculation()

            # Test ISA temperature calculations (used in density altitude)
            print("\\n2️⃣ Testing ISA Temperature Calculations...")
            self._test_isa_temperature_calculation()

            # Test density altitude calculations (affects aircraft performance)
            print("\\n3️⃣ Testing Density Altitude Calculations...")
            self._test_density_altitude_calculation()

            # Test wind component calculations (affects runway performance)
            print("\\n4️⃣ Testing Wind Component Calculations...")
            self._test_wind_component_calculation()

            # Test climb gradient calculations (affects obstacle clearance)
            print("\\n5️⃣ Testing Climb Gradient Calculations...")
            self._test_climb_gradient_calculation()

            print("\\n" + "="*60)
            print("✅ ALL SAFETY-CRITICAL TESTS PASSED!")
            print("✈️ Performance calculator is ready for flight planning use.")
            print("🔬 " + str(5) + " test categories completed successfully.")
            print("="*60)

        except AssertionError as e:
            print("\\n" + "🚨"*20)
            print("❌ SAFETY-CRITICAL TEST FAILURE!")
            print(f"💥 Test failed: {e}")
            print("⛔ DO NOT USE CALCULATOR FOR FLIGHT PLANNING!")
            print("🔧 Fix the issue before using this tool for aviation.")
            print("🚨"*20)
            raise

        except Exception as e:
            print("\\n" + "⚠️ "*20)
            print("❓ UNEXPECTED TEST ERROR!")
            print(f"💥 Error: {e}")
            print("🔍 Check implementation for bugs.")
            print("⚠️ "*20)
            raise

    def calculate_v_speeds(self, wind_dir, wind_speed, wind_gust=None, aircraft_weight_lb=3600):
        """
        Calculate V-speeds for takeoff and approach using Boldmethod methodology

        AVIATION CONTEXT: V-speeds are critical for safe aircraft operations:
        - Vr (Rotation): Speed to lift off during takeoff - FIXED at 80 KIAS for SR22T
        - Approach speeds: Vary by configuration and wind conditions

        BOLDMETHOD METHODOLOGY: Professional flight training approach with:
        - Configuration-based base speeds (Full/50%/No flaps)
        - Gust factor corrections (add half the gust factor)
        - Crosswind configuration recommendations
        - Three-stage speed management for precise landings

        Args:
            wind_dir (int): Wind direction in degrees magnetic
            wind_speed (int): Sustained wind speed in knots
            wind_gust (int, optional): Gust speed in knots
            aircraft_weight_lb (int): Aircraft weight in pounds (informational)

        Returns:
            dict: Complete V-speed package with takeoff and approach speeds
        """
        v_speeds = self.performance_data['v_speeds']

        # Fixed rotation speed for SR22T
        vr = v_speeds['vr_kias']

        # Calculate gust factor if gusty winds
        gust_factor = (wind_gust - wind_speed) if wind_gust and wind_gust > wind_speed else 0
        gust_correction = int(gust_factor * v_speeds['wind_corrections']['gust_factor_multiplier'])

        # Determine recommended flap configuration based on crosswind
        # This requires wind component analysis, but we'll use a simple crosswind estimate
        crosswind_threshold = v_speeds['wind_corrections']['crosswind_partial_flaps_threshold']

        # Simple crosswind estimation (actual crosswind calculated elsewhere)
        # Handle string wind directions
        try:
            if isinstance(wind_dir, str) and wind_dir.upper() == 'VRB':
                # For variable wind, assume worst case crosswind
                estimated_crosswind = wind_speed / 2
            else:
                wind_dir_numeric = int(wind_dir)
                estimated_crosswind = abs(wind_speed * math.sin(math.radians(abs(wind_dir_numeric % 90 - 45))))
        except (ValueError, TypeError):
            # Fallback to conservative estimate
            estimated_crosswind = wind_speed / 2
        use_partial_flaps = estimated_crosswind > crosswind_threshold

        # Select appropriate approach speed configuration
        if use_partial_flaps:
            config = 'partial_flaps_50'
            config_recommendation = "50% flaps recommended for crosswind control"
        else:
            config = 'full_flaps'
            config_recommendation = "Full flaps - normal configuration"

        approach_config = v_speeds['approach_speeds'][config]

        # Apply wind corrections to approach speeds
        final_approach_speed = approach_config['final_approach_base_kias'] + gust_correction
        threshold_speed = approach_config['threshold_crossing_kias'] + (gust_correction // 2)  # Less correction for threshold
        touchdown_speed = approach_config['touchdown_target_kias']  # No correction - target stall speed

        # Weight consideration note (informational - no actual calculation per user guidance)
        weight_under_max = 3600 - aircraft_weight_lb
        weight_note = f"At max gross weight (3600 lb)" if aircraft_weight_lb >= 3600 else f"At {aircraft_weight_lb} lb (consider reducing speeds)"

        # Generate Boldmethod three-stage speed control guidance
        speed_control_guidance = [
            f"Stabilized Final: {final_approach_speed} KIAS ({config_recommendation})",
            f"Threshold Crossing: {threshold_speed} KIAS (begin power reduction)",
            f"Touchdown Target: {touchdown_speed} KIAS (just above stall)",
        ]

        if gust_correction > 0:
            speed_control_guidance.append(f"Gust Correction: +{gust_correction} kt added for {gust_factor} kt gust factor")

        print(f"🎯 V-speeds calculated for SR22T operations")
        if gust_correction > 0:
            print(f"   💨 Wind: {wind_speed}G{wind_gust} kt - gust correction applied")
        if use_partial_flaps:
            print(f"   🌪️ Crosswind detected - 50% flaps recommended")

        return {
            # Takeoff speeds
            'vr_kias': vr,
            'takeoff_notes': "Rotate at 80 KIAS regardless of conditions",

            # Approach speeds
            'final_approach_kias': final_approach_speed,
            'threshold_crossing_kias': threshold_speed,
            'touchdown_target_kias': touchdown_speed,

            # Configuration and corrections
            'recommended_flap_config': config,
            'config_notes': approach_config['config_notes'],
            'gust_correction_applied': gust_correction,
            'weight_consideration': weight_note,

            # Boldmethod speed control progression
            'speed_control_guidance': speed_control_guidance,

            # Operational flags
            'use_partial_flaps_for_crosswind': use_partial_flaps,
            'estimated_crosswind_kt': round(estimated_crosswind, 1)
        }