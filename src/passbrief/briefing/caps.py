#!/usr/bin/env python3
"""
CAPS (Cirrus Airframe Parachute System) Manager

Provides CAPS deployment information and emergency briefing considerations for Cirrus aircraft.
"""


class CAPSManager:
    """Manages CAPS altitude calculations and emergency briefing generation."""

    @staticmethod
    def get_caps_info(airport_elevation_ft, density_altitude_ft):
        """
        Get CAPS (Cirrus Airframe Parachute System) deployment information
        Returns minimum deployment altitudes and emergency briefing considerations
        """
        # CAPS minimum deployment altitude is 600 ft AGL per Cirrus POH
        # (Practical consideration: 500 ft may be acceptable with obstacles ahead)
        caps_minimum_agl = 600
        caps_minimum_msl = airport_elevation_ft + caps_minimum_agl

        # Best deployment envelope is 1000+ ft AGL for better descent profile
        caps_recommended_agl = 1000
        caps_recommended_msl = airport_elevation_ft + caps_recommended_agl

        # Calculate pattern altitude (typically 1000 ft AGL)
        pattern_altitude = airport_elevation_ft + 1000

        # Density altitude affects CAPS performance
        da_impact = "Standard" if density_altitude_ft <= 5000 else "Reduced performance at high density altitude"

        print(f"🪂 CAPS altitude information calculated for field elevation {airport_elevation_ft} ft")

        return {
            'minimum_agl': caps_minimum_agl,
            'minimum_msl': caps_minimum_msl,
            'recommended_agl': caps_recommended_agl,
            'recommended_msl': caps_recommended_msl,
            'pattern_altitude': pattern_altitude,
            'density_altitude_impact': da_impact,
            'emergency_brief': CAPSManager._generate_emergency_brief(caps_minimum_msl, caps_recommended_msl, pattern_altitude)
        }

    @staticmethod
    def _generate_emergency_brief(min_msl, rec_msl, pattern_alt):
        """Generate CAPS emergency briefing points"""
        brief_points = [
            f"CAPS minimum deployment: {min_msl} ft MSL (600 ft AGL - POH limit)",
            f"CAPS recommended deployment: {rec_msl} ft MSL (1000 ft AGL)",
            f"Pattern altitude CAPS available: {pattern_alt} ft MSL",
            "Emergency procedure: CAPS - PULL - COMMUNICATE - PREPARE",
            "Below 600 ft AGL: Fly the airplane - CAPS deployment not recommended (POH limit)"
        ]
        return brief_points

    @staticmethod
    def get_departure_caps_considerations(airport_elevation_ft, climb_gradient_data):
        """Get CAPS considerations specific to departure phase"""
        caps_minimum_agl = 500
        caps_available_altitude = airport_elevation_ft + caps_minimum_agl

        # Calculate time/distance to CAPS availability based on climb performance
        if climb_gradient_data and 'climb_rate_91kias' in climb_gradient_data:
            climb_rate_fpm = climb_gradient_data['climb_rate_91kias'] * 91 / 60  # Convert from ft/nm to ft/min
            time_to_caps_min = caps_minimum_agl / climb_rate_fpm if climb_rate_fpm > 0 else 0

            # Approximate distance (assuming 91 KIAS climb speed)
            distance_to_caps_nm = (91 / 60) * time_to_caps_min if time_to_caps_min > 0 else 0

            return {
                'time_to_caps_available': round(time_to_caps_min, 1),
                'distance_to_caps_available': round(distance_to_caps_nm, 1),
                'caps_available_altitude': caps_available_altitude,
                'departure_brief': [
                    f"CAPS available at {caps_available_altitude} ft MSL",
                    f"Time to CAPS: ~{round(time_to_caps_min, 1)} minutes after takeoff",
                    f"Distance to CAPS: ~{round(distance_to_caps_nm, 1)} nm from departure",
                    "Initial climb: Fly the airplane - CAPS not available below 600 ft AGL (POH limit)"
                ]
            }
        else:
            return {
                'caps_available_altitude': caps_available_altitude,
                'departure_brief': [
                    f"CAPS available at {caps_available_altitude} ft MSL",
                    "Initial climb: Fly the airplane - CAPS not available below 600 ft AGL (POH limit)"
                ]
            }