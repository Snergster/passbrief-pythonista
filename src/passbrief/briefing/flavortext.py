#!/usr/bin/env python3
"""
Flavor Text Manager for Enhanced Takeoff Briefings

Provides professional phased takeoff briefing generation based on aviation industry standards.
"""


class FlavorTextManager:
    """Generates enhanced takeoff briefings with specific altitude gates and emergency procedures."""

    @staticmethod
    def generate_takeoff_briefing_phases(airport_data, results, caps_data):
        """
        Generate phased takeoff briefing with specific altitude gates and emergency procedures
        Based on professional aviation briefing standards
        """
        field_elevation = airport_data['elevation_ft']
        runway_length = airport_data['runway_length_ft']
        takeoff_distance = results['takeoff']['total_distance_ft']
        takeoff_margin = results['takeoff_margin']

        # Phase 1: Abort decision point (typically 50-70% of takeoff roll)
        abort_decision_distance = int(takeoff_distance * 0.6)  # 60% of calculated takeoff distance

        # Stopping distance assessment
        if takeoff_margin > 1000:
            stopping_assessment = "excellent"
        elif takeoff_margin > 500:
            stopping_assessment = "adequate"
        else:
            stopping_assessment = "marginal"

        # Phase altitude calculations
        phase2_ceiling = field_elevation + 600  # 600 ft AGL
        phase3_ceiling = field_elevation + 2000  # 2000 ft AGL
        phase4_start = phase3_ceiling

        # CAPS availability from CAPS data
        caps_minimum = caps_data['minimum_msl'] if caps_data else field_elevation + 500

        phases = {
            'phase1': {
                'title': f'Phase 1 - Before Rotation (0 to ~{abort_decision_distance} feet)',
                'altitude_range': f'0 to ~{abort_decision_distance} feet down runway',
                'action': 'abort the takeoff',
                'details': f'bring the aircraft to a stop on the remaining runway',
                'assessment': f'We have {stopping_assessment} stopping distance available',
                'decision_point': abort_decision_distance,
                'remaining_runway': runway_length - abort_decision_distance
            },
            'phase2': {
                'title': f'Phase 2 - After Rotation (beyond ~{abort_decision_distance} feet to {phase2_ceiling} feet MSL)',
                'altitude_range': f'rotation to {phase2_ceiling} feet MSL (600 feet AGL)',
                'action': 'committed to takeoff',
                'details': 'execute a 30-degree turn to the right or left to find the best available landing area',
                'commitment_point': abort_decision_distance,
                'ceiling_msl': phase2_ceiling,
                'ceiling_agl': 600
            },
            'phase3': {
                'title': f'Phase 3 - Intermediate Altitude ({phase2_ceiling} to {phase3_ceiling} feet MSL)',
                'altitude_range': f'{phase2_ceiling} feet MSL to {phase3_ceiling} feet MSL (600-2000 feet AGL)',
                'action': 'immediate CAPS deployment',
                'details': 'Pull the red handle without hesitation',
                'floor_msl': phase2_ceiling,
                'ceiling_msl': phase3_ceiling,
                'floor_agl': 600,
                'ceiling_agl': 2000
            },
            'phase4': {
                'title': f'Phase 4 - Above {phase4_start} feet MSL (2000+ feet AGL)',
                'altitude_range': f'Above {phase4_start} feet MSL (2000+ feet AGL)',
                'action': 'time for troubleshooting procedures',
                'details': 'before considering CAPS deployment',
                'floor_msl': phase4_start,
                'floor_agl': 2000
            }
        }

        return phases

    @staticmethod
    def format_takeoff_briefing_text(phases):
        """Format the phased takeoff briefing into readable text"""
        briefing_text = "## 🛫 Takeoff Emergency Briefing (Phased Approach)\\n\\n"

        # Phase 1
        p1 = phases['phase1']
        briefing_text += f"**{p1['title']}:** If we experience any emergency before reaching approximately **{p1['decision_point']} feet** down the runway, we will **{p1['action']}** and {p1['details']}. We have {p1['assessment']}.\\n\\n"

        # Phase 2
        p2 = phases['phase2']
        briefing_text += f"**{p2['title']}:** Once we've used more than **{p2['commitment_point']} feet of runway**, we are **{p2['action']}**. If the engine fails between rotation and **{p2['ceiling_msl']} feet MSL ({p2['ceiling_agl']} feet AGL)**, we will {p2['details']}.\\n\\n"

        # Phase 3
        p3 = phases['phase3']
        briefing_text += f"**{p3['title']}:** If the engine fails between **{p3['floor_msl']} feet MSL and {p3['ceiling_msl']} feet MSL ({p3['floor_agl']}-{p3['ceiling_agl']} feet AGL)**, this is an **{p3['action']}**. {p3['details']}.\\n\\n"

        # Phase 4
        p4 = phases['phase4']
        briefing_text += f"**{p4['title']}:** Above **{p4['floor_msl']} feet MSL**, we have {p4['action']} {p4['details']}.\\n\\n"

        return briefing_text