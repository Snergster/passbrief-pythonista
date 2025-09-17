#!/usr/bin/env python3
"""
ChatGPT Flight Plan Analysis Manager

Provides AI-powered flight plan analysis including hazard analysis, passenger briefings,
and NOTAM filtering using OpenAI's GPT models.
"""

import os


class ChatGPTAnalysisManager:
    """Manages AI-powered flight plan analysis and briefing generation."""

    def __init__(self):
        self.api_key = self._load_api_key()
        self.available = self.api_key is not None

    def _load_api_key(self):
        """
        Load OpenAI API key from local file
        Looks for 'openai_api_key.txt' in project root with plain text API key
        """
        try:
            key_file_path = os.path.join(os.path.dirname(__file__), 'openai_api_key.txt')
            if os.path.exists(key_file_path):
                with open(key_file_path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key.startswith('sk-'):  # Basic OpenAI API key format validation
                        print("🤖 ChatGPT analysis available - API key loaded")
                        return api_key
                    else:
                        print("⚠️ Invalid OpenAI API key format in openai_api_key.txt")
                        return None
            else:
                # Silently skip if no key file - this is expected and normal
                return None
        except Exception as e:
            print(f"⚠️ Error loading OpenAI API key: {e}")
            return None

    def generate_briefing_analysis(self, flight_plan_data, operation, airport_data, weather_data, results):
        """
        Generate comprehensive briefing analysis including:
        1. Pilot hazard analysis
        2. Passenger briefing script
        3. Smart NOTAM filtering (when available)
        """
        if not self.available:
            return None

        try:
            analysis_results = {}

            # Generate pilot hazard analysis
            hazard_analysis = self._generate_pilot_hazard_analysis(
                flight_plan_data, operation, airport_data, weather_data, results
            )
            if hazard_analysis:
                analysis_results['hazard_analysis'] = hazard_analysis

            # Generate passenger briefing script
            passenger_brief = self._generate_passenger_briefing(
                flight_plan_data, operation, airport_data, weather_data, results
            )
            if passenger_brief:
                analysis_results['passenger_brief'] = passenger_brief

            # Filter NOTAMs if available in briefing data
            if flight_plan_data and 'notams' in flight_plan_data:
                filtered_notams = self._filter_relevant_notams(
                    flight_plan_data['notams'], operation, airport_data
                )
                if filtered_notams:
                    analysis_results['filtered_notams'] = filtered_notams

            return analysis_results if analysis_results else None

        except Exception as e:
            print(f"⚠️ ChatGPT analysis error: {e}")
            return None

    def _generate_pilot_hazard_analysis(self, flight_plan_data, operation, airport_data, weather_data, results):
        """Generate pilot-focused hazard analysis based on Garmin Pilot briefing data"""
        if not flight_plan_data:
            # Fallback to simple analysis if no briefing data
            return self._generate_simple_hazard_analysis(operation, airport_data, weather_data, results)

        # Extract comprehensive Garmin Pilot data for analysis
        route_analysis = self._extract_garmin_pilot_route_data(flight_plan_data)
        weather_analysis = self._extract_garmin_pilot_weather_data(flight_plan_data)

        prompt = """You are an aviation safety specialist analyzing a comprehensive Garmin Pilot flight briefing with embedded route and weather data. Provide a detailed pilot hazard analysis.

FLIGHT PLAN DATA:
{route_analysis}

COMPREHENSIVE WEATHER DATA:
{weather_analysis}

CURRENT CONDITIONS:
- Airport: {icao} ({name})
- Runway: {runway_heading}° magnetic
- Current Weather: {temp_c}°C, {altimeter} inHg, Wind {wind_dir}°/{wind_speed}kt
- Density Altitude: {density_altitude} ft
- Wind Components: {headwind}kt headwind, {crosswind}kt crosswind

PROVIDE COMPREHENSIVE ROUTE-SPECIFIC ANALYSIS:

1. **TFR PENETRATION ANALYSIS**:
   - For each TFR, determine if the planned route goes THROUGH the TFR boundaries (violation) or passes NEAR it (situational awareness)
   - Consider planned altitude vs TFR altitude restrictions (surface to X feet) - route may be CLEAR if above TFR ceiling
   - Assume ±2nm flight path corridor for GPS navigation accuracy when determining penetration
   - Distance classifications: >5nm = "CLEAR OF TFR", 1-5nm = "NEAR TFR", <1nm = "VERY CLOSE TO TFR", intersects = "PENETRATES TFR"
   - State clearly with distance: "PENETRATES TFR at FL180 (TFR: SFC-FL200)" or "CLEAR OF TFR by 6.2nm" or "NEAR TFR - closest approach 2.8nm"
   - Use departure airport time zone for all timing unless clearly marked otherwise

2. **Convective Weather Penetration**:
   - Analyze convective SIGMETs and thunderstorm movement vectors
   - Determine if route PENETRATES convective areas or passes safely clear
   - Calculate EXACT timing when/where flight intersects weather (Zulu + Local time)
   - Include altitude tops, movement direction, and recommended deviations

3. **Mountain Weather Hazards**:
   - Evaluate G-AIRMETs for mountain obscuration, turbulence, and icing
   - Assess if planned altitude provides adequate terrain clearance in poor visibility
   - Include minimum safe altitudes and alternate routing if obscured

4. **PIREP Integration**:
   - Cross-reference actual pilot reports with planned route and altitudes
   - Highlight specific ride conditions, icing, and turbulence reports along the path
   - Include PIREP altitudes vs planned cruise altitude

5. **Winds Aloft Strategy**:
   - Analyze multi-level winds aloft vs planned cruise altitude
   - Calculate optimal altitude for efficiency and weather avoidance
   - Quantify fuel burn impact and time savings/penalties

6. **Critical Decision Points**:
   - Identify specific waypoints/times where weather decisions must be made
   - Provide "no-go" conditions and alternate airport requirements
   - Include timing in both Zulu and local time zones

7. **Performance Impact**:
   - Calculate specific wind vector effects on fuel burn and flight time
   - Assess climb/descent performance in mountain terrain
   - Evaluate alternate airport accessibility

8. **Hazard Timeline**:
   - Create chronological timeline with BOTH Zulu and Local times
   - List each hazard encounter with: Time (Z + Local), Location, Required Action
   - Format: "1430Z (0730 Local): Approach TFR boundary - CLEAR by 6.2nm" or "1445Z (0745 Local): Route PENETRATES TFR at 12,000ft (TFR: SFC-10,000ft) - CLEAR"

CRITICAL REQUIREMENTS:
- Always specify PENETRATES vs CLEAR vs NEAR for all hazards
- Provide all times in both Zulu AND local time
- Give precise distances for "near" encounters
- Consider altitude restrictions for all hazard analysis
- Focus on GO/NO-GO decision criteria with specific thresholds

Format as structured analysis with specific waypoints, altitudes, times, and quantified impacts.""".format(
            route_analysis=route_analysis,
            weather_analysis=weather_analysis,
            icao=airport_data['icao'],
            name=airport_data['name'],
            runway_heading=airport_data.get('runway_heading', 'Unknown'),
            temp_c=weather_data['temp_c'],
            altimeter=weather_data['altimeter'],
            wind_dir=weather_data['wind_dir'],
            wind_speed=weather_data['wind_speed'],
            density_altitude=results['density_altitude'],
            headwind=results['wind_components']['headwind'],
            crosswind=results['wind_components']['crosswind']
        )

        return self._call_openai_api(prompt)

    def _generate_simple_hazard_analysis(self, operation, airport_data, weather_data, results):
        """Fallback analysis when no briefing data available"""
        scope_description = "entire flight including enroute weather" if operation == 'departure' else "arrival conditions only"

        conditions_summary = (
            f"Current Conditions:\n"
            f"- Airport: {airport_data['icao']} ({airport_data['name']})\n"
            f"- Runway: {airport_data.get('runway_heading', 'Unknown')}° magnetic\n"
            f"- Weather: {weather_data['temp_c']}°C, {weather_data['altimeter']} inHg, Wind {weather_data['wind_dir']}°/{weather_data['wind_speed']}kt\n"
            f"- Density Altitude: {results['density_altitude']} ft\n"
            f"- Wind Components: {results['wind_components']['headwind']}kt headwind, {results['wind_components']['crosswind']}kt crosswind"
        )

        prompt = """You are an aviation safety specialist. Analyze the following flight conditions and provide a concise pilot hazard analysis focused on actionable safety information for {scope_description}.

{conditions_summary}

Provide a focused paragraph (3-4 sentences) covering:
1. Immediate safety concerns for this specific operation
2. Weather-related hazards that could affect flight safety
3. Any performance or operational considerations based on current conditions
4. Specific recommendations or cautions for the pilot

Format as a single paragraph starting with "Hazard Analysis:" and focus on practical, actionable safety information. If no significant hazards are identified, state that clearly.""".format(
            scope_description=scope_description,
            conditions_summary=conditions_summary
        )

        return self._call_openai_api(prompt)

    def _extract_garmin_pilot_route_data(self, flight_plan_data):
        """Extract and format route data from Garmin Pilot briefing"""
        route_summary = []

        # Basic route info
        if 'departure' in flight_plan_data and 'arrival' in flight_plan_data:
            route_summary.append(f"Route: {flight_plan_data['departure']} to {flight_plan_data['arrival']}")

        # Distance and time
        if 'distance' in flight_plan_data:
            route_summary.append(f"Distance: {flight_plan_data['distance']} nm")
        if 'flight_time' in flight_plan_data:
            route_summary.append(f"Flight Time: {flight_plan_data['flight_time']}")

        # Waypoints with timing and altitudes
        if 'waypoints' in flight_plan_data:
            route_summary.append("\\nWAYPOINT ANALYSIS:")
            for wp in flight_plan_data['waypoints'][:8]:  # Limit to first 8 waypoints
                wp_info = f"- {wp.get('name', 'Unknown')}"
                if 'altitude' in wp:
                    wp_info += f" at {wp['altitude']}ft"
                if 'time' in wp:
                    wp_info += f" ({wp['time']})"
                if 'wind_data' in wp:
                    wp_info += f" - Wind: {wp['wind_data']}"
                route_summary.append(wp_info)

        # Planned altitudes
        if 'planned_altitude' in flight_plan_data:
            route_summary.append(f"\\nPlanned Cruise: {flight_plan_data['planned_altitude']}ft")

        # Fuel planning
        if 'fuel_data' in flight_plan_data:
            route_summary.append(f"Fuel Planning: {flight_plan_data['fuel_data']}")

        return "\\n".join(route_summary) if route_summary else "Route data not available in flight plan"

    def _extract_garmin_pilot_weather_data(self, flight_plan_data):
        """Extract and format weather data from Garmin Pilot briefing"""
        weather_summary = []

        # Winds aloft analysis
        if 'winds_aloft' in flight_plan_data:
            weather_summary.append("WINDS ALOFT:")
            for altitude, wind_data in flight_plan_data['winds_aloft'].items():
                weather_summary.append(f"- {altitude}: {wind_data}")

        # Weather layers and hazards
        if 'weather_layers' in flight_plan_data:
            weather_summary.append("\\nWEATHER LAYERS:")
            for layer in flight_plan_data['weather_layers']:
                weather_summary.append(f"- {layer}")

        # AIRMETs and SIGMETs
        if 'airmets' in flight_plan_data:
            weather_summary.append("\\nAIRMETs:")
            for airmet in flight_plan_data['airmets']:
                weather_summary.append(f"- {airmet}")

        if 'sigmets' in flight_plan_data:
            weather_summary.append("\\nSIGMETs:")
            for sigmet in flight_plan_data['sigmets']:
                weather_summary.append(f"- {sigmet}")

        # Convective weather
        if 'convective_weather' in flight_plan_data:
            weather_summary.append(f"\\nCONVECTIVE WEATHER: {flight_plan_data['convective_weather']}")

        # Icing conditions
        if 'icing' in flight_plan_data:
            weather_summary.append(f"\\nICING CONDITIONS: {flight_plan_data['icing']}")

        # Turbulence
        if 'turbulence' in flight_plan_data:
            weather_summary.append(f"\\nTURBULENCE: {flight_plan_data['turbulence']}")

        # TFRs
        if 'tfrs' in flight_plan_data:
            weather_summary.append("\\nTFRs (Temporary Flight Restrictions):")
            for tfr in flight_plan_data['tfrs']:
                weather_summary.append(f"- {tfr}")

        # Garmin-specific convective SIGMETs (higher priority than regular SIGMETs)
        if 'convective_sigmets' in flight_plan_data:
            weather_summary.append("\\nCONVECTIVE SIGMETs (CRITICAL):")
            for sigmet in flight_plan_data['convective_sigmets']:
                weather_summary.append(f"- {sigmet}")

        # PIREPs - real pilot reports
        if 'pireps' in flight_plan_data:
            weather_summary.append("\\nPILOT REPORTS (PIREPs):")
            for pirep in flight_plan_data['pireps']:
                weather_summary.append(f"- {pirep}")

        # Hazard timing analysis - when flight encounters each hazard
        if 'hazard_timing' in flight_plan_data:
            weather_summary.append("\\nWEATHER HAZARD TIMING:")
            for timing in flight_plan_data['hazard_timing']:
                weather_summary.append(f"- {timing}")

        # Current METAR conditions
        if 'metars' in flight_plan_data:
            weather_summary.append("\\nCURRENT CONDITIONS (METARs):")
            for airport, metar in flight_plan_data['metars'].items():
                weather_summary.append(f"- {airport}: {metar}")

        # Terminal forecasts
        if 'tafs' in flight_plan_data:
            weather_summary.append("\\nAIRPORT FORECASTS (TAFs):")
            for airport, taf in flight_plan_data['tafs'].items():
                weather_summary.append(f"- {airport}: {taf}")

        return "\\n".join(weather_summary) if weather_summary else "Weather data not available in flight plan"

    def test_garmin_pilot_data_extraction(self):
        """Test Garmin Pilot data extraction methods with sample data"""
        print("\\n🧪 Testing Garmin Pilot data extraction methods...")

        # Sample Garmin Pilot data structure
        sample_flight_plan = {
            'departure': 'KSLC',
            'arrival': 'KBIL',
            'distance': '337',
            'flight_time': '1h 18m',
            'planned_altitude': '18000',
            'waypoints': [
                {'name': 'KSLC', 'altitude': '4226', 'time': '16:45Z'},
                {'name': 'NARCS', 'altitude': '18000', 'time': '17:15Z', 'wind_data': '290/25kt'},
                {'name': 'KBIL', 'altitude': '3672', 'time': '18:03Z'}
            ],
            'winds_aloft': {
                '12000': '280/20kt',
                '18000': '290/25kt',
                '24000': '300/35kt'
            },
            'turbulence': 'Light chop expected above FL200',
            'convective_weather': 'Isolated thunderstorms south of route',
            'airmets': ['AIRMET Sierra for IFR conditions'],
            'sigmets': ['SIGMET for severe turbulence FL280-FL420']
        }

        # Test route data extraction
        route_data = self._extract_garmin_pilot_route_data(sample_flight_plan)
        assert 'KSLC to KBIL' in route_data, "Route extraction failed"
        assert '337 nm' in route_data, "Distance extraction failed"
        assert '1h 18m' in route_data, "Flight time extraction failed"
        assert 'NARCS' in route_data, "Waypoint extraction failed"
        print("✅ Route data extraction working correctly")

        # Test weather data extraction
        weather_data = self._extract_garmin_pilot_weather_data(sample_flight_plan)
        assert 'WINDS ALOFT' in weather_data, "Winds aloft extraction failed"
        assert '290/25kt' in weather_data, "Wind data extraction failed"
        assert 'Light chop' in weather_data, "Turbulence extraction failed"
        assert 'AIRMET Sierra' in weather_data, "AIRMET extraction failed"
        print("✅ Weather data extraction working correctly")

        # Test passenger weather summary
        passenger_summary = self._extract_passenger_weather_summary(sample_flight_plan)
        assert 'light chop' in passenger_summary.lower(), "Passenger weather summary failed"
        print("✅ Passenger weather summary working correctly")

        print("🎉 All Garmin Pilot data extraction tests passed!")

    def _generate_passenger_briefing(self, flight_plan_data, operation, airport_data, weather_data, results):
        """Generate passenger briefing script based on Garmin Pilot briefing data"""
        if operation == 'departure':
            return self._generate_departure_passenger_brief(flight_plan_data, airport_data, weather_data, results)
        else:
            return self._generate_arrival_passenger_brief(flight_plan_data, airport_data, weather_data, results)

    def _generate_departure_passenger_brief(self, flight_plan_data, airport_data, weather_data, results):
        """Generate departure passenger briefing with Garmin Pilot route analysis"""
        # Extract flight details from briefing data
        if flight_plan_data:
            departure = flight_plan_data.get('departure', airport_data['icao'])
            arrival = flight_plan_data.get('arrival', 'our destination')
            route_desc = f"from {departure} to {arrival}"

            # Get flight time from briefing data if available
            flight_time = flight_plan_data.get('flight_time', 'approximately XX minutes')

            # Get weather expectations from route data
            weather_summary = self._extract_passenger_weather_summary(flight_plan_data)
        else:
            route_desc = f"departing {airport_data['icao']}"
            flight_time = "approximately XX minutes"
            weather_summary = "smooth conditions expected"

        prompt = """Create a friendly, conversational passenger briefing script for departure. The pilot will read this to passengers before takeoff.

FLIGHT DETAILS:
- Route: {route_desc}
- Flight Time: {flight_time}
- Current Weather: {temp_c}°C, Wind {wind_dir}°/{wind_speed}kt
- Aircraft: Cirrus SR22T with CAPS parachute system
- Route Weather Expectations: {weather_summary}

Create a 3-4 sentence casual script covering:
1. Flight time and destination with enthusiasm
2. Realistic weather expectations based on route analysis (smooth/light chop/moderate chop, any weather to expect enroute)
3. Brief mention of CAPS safety system for reassurance
4. Any specific passenger preparation (rough air, longer flight time, scenic views, etc.)

Start with "Here's what to expect for our flight:" and keep it conversational, informative, and reassuring. Use specific details from the route analysis to make it feel personalized to this flight.""".format(
            route_desc=route_desc,
            flight_time=flight_time,
            temp_c=weather_data['temp_c'],
            wind_dir=weather_data['wind_dir'],
            wind_speed=weather_data['wind_speed'],
            weather_summary=weather_summary
        )

        return self._call_openai_api(prompt)

    def _generate_arrival_passenger_brief(self, flight_plan_data, airport_data, weather_data, results):
        """Generate arrival passenger briefing with current conditions"""
        prompt = """Create a brief, professional passenger script for arrival phase at {icao}.

CURRENT CONDITIONS:
- Approaching: {icao} ({name})
- Weather: {temp_c}°C, Wind {wind_dir}°/{wind_speed}kt
- Wind Components: {headwind}kt headwind, {crosswind}kt crosswind

Create a 2-3 sentence script covering:
1. Estimated time to landing (typically 10-15 minutes for arrival brief)
2. Current conditions at destination (temperature, any bumps expected on approach)
3. Sterile cockpit explanation (pilot needs to focus on approach/landing)
4. Seatbelt and securing items reminder

Start with "We should be landing at {name} in about 12 minutes..." and keep it brief, professional but friendly, and reassuring.""".format(
            icao=airport_data['icao'],
            name=airport_data['name'],
            temp_c=weather_data['temp_c'],
            wind_dir=weather_data['wind_dir'],
            wind_speed=weather_data['wind_speed'],
            headwind=results['wind_components']['headwind'],
            crosswind=results['wind_components']['crosswind']
        )

        return self._call_openai_api(prompt)

    def _extract_passenger_weather_summary(self, flight_plan_data):
        """Extract passenger-friendly weather summary from briefing data"""
        summary_parts = []

        # Check for turbulence
        if 'turbulence' in flight_plan_data:
            if 'moderate' in flight_plan_data['turbulence'].lower():
                summary_parts.append("some bumps expected")
            elif 'light' in flight_plan_data['turbulence'].lower():
                summary_parts.append("light chop possible")

        # Check for convective weather
        if 'convective_weather' in flight_plan_data:
            if flight_plan_data['convective_weather']:
                summary_parts.append("routing around weather")

        # Check winds aloft for smooth flight
        if 'winds_aloft' in flight_plan_data:
            # Analyze if strong winds might cause turbulence
            strong_winds = any('40' in str(wind) or '50' in str(wind) for wind in flight_plan_data['winds_aloft'].values())
            if strong_winds:
                summary_parts.append("some turbulence from strong winds aloft")

        # Default to smooth if no issues identified
        if not summary_parts:
            summary_parts.append("smooth conditions expected")

        return ", ".join(summary_parts)

    def _filter_relevant_notams(self, notams_data, operation, airport_data):
        """Filter NOTAMs to show only relevant information"""
        if not notams_data:
            return None

        # TODO: Extract time of operation for relevance filtering
        current_time = "daytime departure"  # This should be calculated from actual flight time

        prompt = """Filter the following NOTAMs to show only information relevant to a {operation} operation at {icao}.

Operation Details:
- Type: {operation}
- Airport: {icao}
- Time: {current_time}
- Runway: Runway {runway_heading}°

NOTAMs to filter:
{notams_data}

Remove NOTAMs that are NOT relevant such as:
- Distant obstacles (5+ miles away)
- Taxiway closures for taxiways not being used
- Tower/facility closures when they're currently open
- Equipment outages that don't affect this specific operation

Keep NOTAMs that ARE relevant such as:
- Runway conditions or closures
- Approach/departure restrictions
- Airspace changes affecting arrival/departure
- Equipment outages affecting this specific operation

Format the response as "Relevant NOTAMs:" followed by bullet points of only the important items. If no relevant NOTAMs, respond with "No significant NOTAMs for this operation."

Keep it concise and focused on what the pilot actually needs to know.""".format(
            operation=operation,
            icao=airport_data['icao'],
            current_time=current_time,
            runway_heading=airport_data.get('runway_heading', 'Unknown'),
            notams_data=notams_data
        )

        return self._call_openai_api(prompt)

    def _call_openai_api(self, prompt):
        """
        Call OpenAI API with the analysis prompt
        Returns analysis text or None if failed
        """
        try:
            import requests
            import json

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'gpt-3.5-turbo',  # Using cost-effective model for flight plan analysis
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an aviation weather and flight planning specialist. Provide concise, practical analysis focused on flight safety.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 800,  # Increased for detailed route analysis
                'temperature': 0.2  # Lower temperature for more consistent, factual responses
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
            else:
                print(f"⚠️ OpenAI API error: HTTP {response.status_code}")
                return None

        except ImportError:
            print("⚠️ Missing required libraries for ChatGPT analysis (requests)")
            return None
        except Exception as e:
            print(f"⚠️ ChatGPT API call failed: {e}")
            return None