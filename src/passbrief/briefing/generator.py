#!/usr/bin/env python3
"""
Briefing Generator - Main Application Orchestrator

This is the primary class that coordinates all briefing generation activities.
It provides a workflow-based interface for comprehensive flight preparation.
"""

import logging
import logging
import math
from datetime import datetime
from typing import Optional

# Import all required modules
from ..config import Config
from ..performance import PerformanceCalculator
from ..weather import WeatherManager
from ..airports import AirportManager
from ..garmin import GarminPilotBriefingManager
from ..io import ConsoleIO, IOInterface
from .sid import SIDManager
from .caps import CAPSManager
from .flavortext import FlavorTextManager
from .chatgpt import ChatGPTAnalysisManager


class BriefingGenerator:
    def __init__(self, io: Optional[IOInterface] = None):
        self.io = io or ConsoleIO()
        self.logger = logging.getLogger(__name__)
        self.calculator = PerformanceCalculator()
        self.garmin_manager = GarminPilotBriefingManager(io=self.io)
        self.weather_manager = WeatherManager(io=self.io)
        self.sid_manager = SIDManager()
        self.caps_manager = CAPSManager()
        self.flavor_text_manager = FlavorTextManager()
        self.chatgpt_manager = ChatGPTAnalysisManager()
        
        # Store results between workflow steps
        self.current_briefing_data = None
        self.weather_analysis_results = None
        self.passenger_brief_results = None

    # ------------------------------------------------------------------
    # IO helpers
    # ------------------------------------------------------------------
    def _prompt(self, message: str, default: str = "") -> str:
        return self.io.prompt(message, default)

    def _confirm(self, message: str, default: bool = False) -> bool:
        return self.io.confirm(message, default)

    def _info(self, message: str = "") -> None:
        self.io.info(message)

    def _warn(self, message: str) -> None:
        self.io.warning(message)

    def _error(self, message: str) -> None:
        self.io.error(message)
        
    @staticmethod
    def _normalize_runway_input(runway_input):
        """Normalize runway input to standard two-digit format (e.g., '3' -> '03')"""
        if not runway_input:
            return runway_input
        
        # Remove common prefixes and clean up
        runway = runway_input.upper().replace('RW', '').replace('RUNWAY', '').strip()
        
        # Handle single digit runways by adding leading zero
        if runway.isdigit() and len(runway) == 1:
            return '0' + runway
        
        # Handle two-digit runways with suffix (e.g., '3L' -> '03L')
        if len(runway) == 2 and runway[0].isdigit() and runway[1].isalpha():
            return '0' + runway
        
        return runway
        
    def get_user_inputs(self):
        """Workflow-based briefing system for comprehensive flight preparation"""
        self._info("\n" + "=" * 70)
        self._info("SR22T FLIGHT BRIEFING TOOL v31.0 - WORKFLOW EDITION")
        self._info("Garmin Pilot Integration + Sequential Briefing System")
        self._info("=" * 70)
        
        # Check for Garmin Pilot briefings
        recent_briefings = self.garmin_manager.check_for_briefings()
        
        if recent_briefings:
            self._info(f"\n🎉 Found {len(recent_briefings)} Garmin Pilot briefing(s):")
            for i, briefing in enumerate(recent_briefings):
                file_timestamp = datetime.fromtimestamp(briefing['file_modified'])
                file_age = datetime.now() - file_timestamp
                
                if file_age.days > 0:
                    age_str = f"{file_age.days}d ago"
                elif file_age.total_seconds() > 3600:
                    age_str = f"{int(file_age.total_seconds() / 3600)}h ago"
                else:
                    age_str = f"{int(file_age.total_seconds() / 60)}m ago"
                
                date_str = file_timestamp.strftime("%m/%d %H:%M")
                
                self._info(f"  {i+1}. {briefing['departure']} → {briefing['arrival']}")
                self._info(f"     📅 {date_str} ({age_str}) | 📄 {briefing['type']} | 📁 {briefing['filename']}")

            self._info(
                f"\nSelect Garmin Pilot briefing (1-{len(recent_briefings)}) or continue without: "
            )
            choice = self._prompt(
                f"Choice (1-{len(recent_briefings)}, ENTER to skip)", ""
            ).strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(recent_briefings):
                selected_briefing = recent_briefings[int(choice)-1]
                
                # Handle cases where PDF parsing couldn't extract airport codes
                if (selected_briefing['departure'] == 'UNKNOWN' or 
                    selected_briefing['arrival'] == 'UNKNOWN'):
                    self._info("\n🛠️ PDF parsing was incomplete for this briefing.")
                    self._info(
                        f"   Current: {selected_briefing['departure']} → {selected_briefing['arrival']}"
                    )
                    self._info("   Please provide the missing information:")
                    
                    if selected_briefing['departure'] == 'UNKNOWN':
                        dep = self._prompt("   🛫 Departure airport").strip().upper()
                        if dep:
                            selected_briefing['departure'] = dep
                    
                    if selected_briefing['arrival'] == 'UNKNOWN':
                        arr = self._prompt("   🛬 Arrival airport").strip().upper()
                        if arr:
                            selected_briefing['arrival'] = arr
                    
                    # Optionally ask for route if both airports are now known
                    if (selected_briefing['departure'] != 'UNKNOWN' and 
                        selected_briefing['arrival'] != 'UNKNOWN' and
                        selected_briefing.get('route') == 'UNKNOWN'):
                        route = self._prompt(
                            f"   🗺️ Route (optional, e.g., {selected_briefing['departure']} WAYPOINT1 WAYPOINT2 {selected_briefing['arrival']})",
                            "",
                        ).strip().upper()
                        if route:
                            selected_briefing['route'] = route
                
                self.current_briefing_data = selected_briefing
                self._info(
                    f"✅ Loaded briefing: {selected_briefing['departure']} → {selected_briefing['arrival']}"
                )
        else:
            self._info("\n📝 No Garmin Pilot briefings found")
        
        return self._show_workflow_menu()
    
    def _show_workflow_menu(self):
        """Display workflow options and handle user selection"""
        self._info("\n" + "-" * 70)
        
        if self.current_briefing_data:
            route = f"{self.current_briefing_data['departure']} → {self.current_briefing_data['arrival']}"
            self._info(f"Flight: {route} (Garmin Pilot briefing loaded ✓)")
        else:
            self._info("Flight: Manual input mode (no Garmin Pilot briefing)")
            
        self._info("\nWORKLOW MODE:")
        status_weather = "✅" if self.weather_analysis_results else "⏸️"
        status_passenger = "✅" if self.passenger_brief_results else ("⏸️" if self.weather_analysis_results else "⏹️")
        status_takeoff = "⏸️"
        status_arrival = "⏸️"
        
        self._info(f"  {status_weather} 1. Weather/Route Analysis    (T-15min before passengers)")
        self._info(f"  {status_passenger} 2. Passenger Briefing        (When passengers arrive)")  
        self._info(f"  {status_takeoff} 3. Takeoff Briefing          (Runup area/after clearance)")
        self._info(f"  {status_arrival} 4. Arrival Briefing          (Approaching destination)")
        
        self._info("\nQUICK ACCESS:")
        self._info("  A. Weather Analysis Only")
        self._info("  B. Passenger Brief Only")
        self._info("  C. Takeoff Brief Only")
        self._info("  D. Arrival Brief Only")
        self._info("  E. Full Sequential Workflow")
        self._info("  Q. Quit")
        
        while True:
            choice = self._prompt("Select briefing type (1-4, A-E, Q)").strip().upper()

            if choice == '1':
                return self._weather_analysis_workflow()
            if choice == '2':
                return self._passenger_briefing_workflow()
            if choice == '3':
                return self._takeoff_briefing_workflow()
            if choice == '4':
                return self._arrival_briefing_workflow()
            if choice == 'A':
                return self._weather_analysis_workflow()
            if choice == 'B':
                return self._passenger_briefing_workflow()
            if choice == 'C':
                return self._takeoff_briefing_workflow()
            if choice == 'D':
                return self._arrival_briefing_workflow()
            if choice == 'E':
                return self._full_sequential_workflow()
            if choice == 'Q' or choice == '':
                return None

            self._warn("Invalid choice. Please try again.")
    
    def _weather_analysis_workflow(self):
        """Weather and route analysis using Garmin Pilot data (T-15min before passengers)"""
        self._info("\n" + "="*50)
        self._info("🌤️  WEATHER & ROUTE ANALYSIS")
        self._info("="*50)
        
        if not self.current_briefing_data:
            self._warn("⚠️ No Garmin Pilot briefing loaded")
            self._info("This analysis requires Garmin Pilot briefing data for comprehensive weather analysis")
            self._prompt("Press ENTER to return to menu...")
            return self._show_workflow_menu()
        
        self._info("🔍 Analyzing Garmin Pilot briefing data...")
        
        try:
            # Use current airport data workflow but with minimal input for weather analysis
            departure = self.current_briefing_data['departure']
            arrival = self.current_briefing_data['arrival']
            
            self._info(f"📊 Analyzing weather data for {departure} → {arrival}...")
            
            # Display weather information from the briefing
            self._info("\n" + "="*50)
            self._info("🌤️  WEATHER & ROUTE ANALYSIS RESULTS")
            self._info("="*50)
            
            # Show basic flight information
            self._info(f"✈️  **FLIGHT PLAN**")
            self._info(f"   Route: {departure} → {arrival}")
            if self.current_briefing_data.get('route', 'UNKNOWN') != 'UNKNOWN':
                self._info(f"   Waypoints: {self.current_briefing_data['route']}")
            
            # Show weather summary from PDF extraction
            weather_summary = self.current_briefing_data.get('weather_summary', {})
            if weather_summary:
                self._info(f"\n🌦️  **WEATHER HAZARDS DETECTED**")
                self._info(f"   {weather_summary.get('summary', 'No weather information available')}")
                
                if weather_summary.get('sigmets_found', 0) > 0:
                    self._info(f"   ⚠️  {weather_summary['sigmets_found']} SIGMET(s) - Significant weather conditions")
                if weather_summary.get('airmets_found', 0) > 0:
                    self._info(f"   ⚠️  {weather_summary['airmets_found']} AIRMET(s) - Hazardous weather for light aircraft")
                if weather_summary.get('notams_found', 0) > 0:
                    self._info(f"   ℹ️  {weather_summary['notams_found']} NOTAM(s) - Airport/airspace notices")
                if weather_summary.get('tfrs_found', 0) > 0:
                    self._info(f"   🚫 {weather_summary['tfrs_found']} TFR(s) - Temporary flight restrictions")
                
                if weather_summary.get('weather_notes'):
                    self._info(f"   🌤️  Conditions: {', '.join(weather_summary['weather_notes'])}")
            
            # Optional ChatGPT enhancement if available
            if self.chatgpt_manager.available:
                self._info(f"\n🤖 **ENHANCED AI ANALYSIS** (Optional)")
                self._info(f"   ChatGPT is available for detailed weather analysis...")
                enhance = self._prompt("   Generate AI weather analysis? (y/n) [n]: ").strip().lower()
                
                if enhance == 'y':
                    self._info("   🔄 Generating AI analysis...")
                    # Get weather data (this will be minimal for weather analysis)
                    weather_data = {'temp_c': 15, 'altimeter': 30.00, 'wind_dir': 270, 'wind_speed': 10}
                    airport_data = {'icao': departure, 'name': departure}
                    results = {'density_altitude': 3000, 'wind_components': {'headwind': 5, 'crosswind': 3}}
                    
                    analysis = self.chatgpt_manager.generate_briefing_analysis(
                        self.current_briefing_data, 'departure', airport_data, weather_data, results
                    )
                    
                    if analysis:
                        self._info("\n🤖 **AI ANALYSIS RESULTS**")
                        self._info(analysis)
                    else:
                        self._warn("   ⚠️ AI analysis failed")
            
            self._info(f"\n✅ Weather analysis complete!")
            self.weather_analysis_results = f"Weather analysis completed for {departure} → {arrival}"
                
        except Exception as e:
            self._info(f"⚠️ Error during weather analysis: {e}")
            
        self._prompt("\nPress ENTER to continue...")
        return self._show_workflow_menu()
    
    def _passenger_briefing_workflow(self):
        """Generate passenger-friendly briefing script"""
        self._info("\n" + "="*50)
        self._info("👥 PASSENGER BRIEFING")
        self._info("="*50)
        
        if not self.weather_analysis_results:
            self._warn("⚠️ Weather analysis not completed")
            self._info("Passenger briefing works best after completing weather analysis")
            proceed = self._prompt("Continue anyway? (y/N): ").strip().lower()
            if proceed != 'y':
                return self._show_workflow_menu()
        
        self._info("🗣️ Generating passenger briefing script...")
        
        try:
            if self.chatgpt_manager.available:
                analysis = self._generate_passenger_briefing_script()
                if analysis:
                    self.passenger_brief_results = analysis
                    self._info("\n" + "="*50)
                    self._info("👥 PASSENGER BRIEFING SCRIPT")
                    self._info("="*50)
                    self._info(analysis)
                    self._info("\n✅ Passenger briefing complete!")
                else:
                    self._warn("⚠️ Passenger briefing generation failed")
            else:
                self._warn("⚠️ ChatGPT not available for passenger briefing")
                
        except Exception as e:
            self._info(f"⚠️ Error generating passenger briefing: {e}")
            
        self._prompt("\nPress ENTER to continue...")
        return self._show_workflow_menu()
    
    def _takeoff_briefing_workflow(self):
        """Takeoff briefing with performance calculations using Garmin Pilot data if available"""
        self._info("\n" + "="*50)
        self._info("🛫 TAKEOFF BRIEFING")
        self._info("="*50)
        
        if self.current_briefing_data:
            departure = self.current_briefing_data['departure']
            self._info(f"🛫 Departure briefing for {departure} (from Garmin Pilot briefing)")
            
            runway_input = self._prompt(f"Runway at {departure}: ").strip()
            if not runway_input:
                return self._show_workflow_menu()
            runway = self._normalize_runway_input(runway_input)
            
            # SID prompt with empty default
            # Simple SID handling - manual input only
            using_sid = self._prompt(f"Using a SID departure? (y/n) [n]: ").lower().strip()
            sid_climb_rate = None
            sid_name = None
            sid_initial_altitude = None
            
            if using_sid == 'y':
                sid_name = self._prompt(f"SID name (for reference only): ").upper().strip() or "SID"
                sid_climb_input = self._prompt(f"Required climb gradient (ft/nm): ").strip()
                try:
                    sid_climb_rate = float(sid_climb_input)
                    if sid_climb_rate < 100 or sid_climb_rate > 1000:
                        self._info(f"⚠️ Unusual climb gradient: {sid_climb_rate} ft/nm")
                except (ValueError, TypeError):
                    self._info(f"⚠️ Invalid climb gradient, using standard 200 ft/nm")
                    sid_climb_rate = 200.0
                
                # Get SID initial altitude
                sid_altitude_input = self._prompt(f"SID initial altitude (ft MSL): ").strip()
                try:
                    sid_initial_altitude = int(sid_altitude_input)
                    if sid_initial_altitude < 1000 or sid_initial_altitude > 18000:
                        self._info(f"⚠️ Unusual initial altitude: {sid_initial_altitude} ft MSL")
                except (ValueError, TypeError):
                    self._info(f"⚠️ Invalid altitude entered")
                    sid_initial_altitude = None
            
            return {
                'icao': departure,
                'operation': 'departure', 
                'runway': runway,
                'sid_name': sid_name,
                'sid_climb_rate': sid_climb_rate,
                'sid_initial_altitude': sid_initial_altitude,
                'briefing_data': self.current_briefing_data,
                'source': 'Garmin Pilot'
            }
        else:
            self._warn("⚠️ No Garmin Pilot briefing loaded - using manual input")
            return self._manual_departure_workflow()
    
    def _arrival_briefing_workflow(self):
        """Arrival briefing with performance calculations using Garmin Pilot data if available"""
        self._info("\n" + "="*50)
        self._info("🛬 ARRIVAL BRIEFING")
        self._info("="*50)
        
        if self.current_briefing_data:
            arrival = self.current_briefing_data['arrival']
            self._info(f"🛬 Arrival briefing for {arrival} (from Garmin Pilot briefing)")
            
            runway_input = self._prompt(f"Runway at {arrival}: ").strip()
            if not runway_input:
                return self._show_workflow_menu()
            runway = self._normalize_runway_input(runway_input)
            
            return {
                'icao': arrival,
                'operation': 'arrival', 
                'runway': runway,
                'briefing_data': self.current_briefing_data,
                'source': 'Garmin Pilot'
            }
        else:
            self._warn("⚠️ No Garmin Pilot briefing loaded - using manual input")
            return self._manual_arrival_workflow()
    
    def _full_sequential_workflow(self):
        """Run all three briefings in sequence"""
        self._info("\n🔄 Starting full sequential workflow...")
        
        # 1. Weather Analysis
        result = self._weather_analysis_workflow()
        if not result:
            return None
            
        # 2. Passenger Briefing 
        result = self._passenger_briefing_workflow()
        if not result:
            return None
            
        # 3. Takeoff Briefing
        return self._takeoff_briefing_workflow()
    
    def _generate_passenger_briefing_script(self):
        """Generate passenger-friendly briefing using weather analysis results"""
        if not self.current_briefing_data:
            return "No flight data available for passenger briefing"
        
        route = f"{self.current_briefing_data['departure']} → {self.current_briefing_data['arrival']}"
        
        # Create passenger-focused prompt
        prompt = f"""You are a professional pilot creating a passenger briefing for a general aviation flight. Convert technical weather analysis into passenger-friendly explanations.

FLIGHT INFORMATION:
- Route: {route}
- Aircraft: Cirrus SR22T (4-seat single engine)

WEATHER ANALYSIS RESULTS:
{self.weather_analysis_results if self.weather_analysis_results else 'Weather analysis not available'}

BASIC ROUTE INFORMATION:
{self.current_briefing_data.get('route_summary', 'Route details from Garmin Pilot briefing')}

CREATE A PASSENGER BRIEFING SCRIPT THAT:

1. **Welcome & Flight Overview**:
   - Warm greeting and flight time/route introduction
   - Aircraft type and safety features (mention CAPS if relevant)

2. **Weather Translation**:
   - Convert "TFRs" → "temporary flight restrictions" → "we'll be flying around some restricted airspace"
   - Convert "Convective SIGMETs" → "thunderstorm areas" → "we may see some weather to avoid"
   - Convert "Mountain obscuration" → "clouds around the mountain peaks"
   - Convert "Turbulence PIREPs" → "some bumps reported by other pilots"
   - Convert technical wind data → "smooth/bumpy conditions expected"

3. **What Passengers Will Experience**:
   - Expected ride quality (smooth, light chop, bumpy)
   - Altitude changes and why ("climbing to get above the weather")
   - Route deviations and why ("going around some weather")
   - Approximate timing for each phase

4. **Comfort & Expectations**:
   - When to expect the smoothest/bumpiest parts
   - Normal sounds and sensations
   - What to do if they feel uncomfortable

5. **Positive Reassurance**:
   - Emphasize safety planning and weather avoidance
   - Professional weather analysis and routing
   - Multiple backup plans

TONE: Confident, professional, reassuring. Explain technical concepts in simple terms. Focus on safety planning rather than hazards.

FORMAT: Conversational script that can be read aloud, approximately 2-3 minutes when spoken."""

        return self.chatgpt_manager._call_openai_api(prompt)
    
    def _normalize_sid_name(self, sid_input):
        """Normalize SID name input to standard format"""
        if not sid_input:
            return None
        
        # Handle common formats: TRALR6, TRALR SIX, TRALR 6, etc.
        sid_input = sid_input.replace(' ', '').replace('-', '').upper()
        
        # Convert spelled-out numbers to digits
        number_map = {
            'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5',
            'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'TEN': '10'
        }
        
        for word, digit in number_map.items():
            if sid_input.endswith(word):
                sid_input = sid_input.replace(word, digit)
                break
        
        return sid_input
    
    def _get_sid_climb_requirement(self, icao, sid_name):
        """Get SID climb gradient requirement with retry logic"""
        if not sid_name:
            return None
        
        self._info(f"   📡 Looking up SID {sid_name} climb requirements for {icao}...")
        
        # Try FAA data lookup with 2 retries
        for attempt in range(2):
            try:
                if attempt == 0:
                    self._info(f"   🔍 Fetching SID data from FAA CIFP...")
                else:
                    self._info(f"   🔄 Retrying SID lookup (attempt {attempt + 1}/2)...")
                
                # Attempt to get SID data from FAA source
                climb_requirement = self._fetch_faa_sid_data(icao, sid_name)
                if climb_requirement:
                    # Handle both old string format and new dictionary format
                    if isinstance(climb_requirement, dict):
                        # New enhanced format with detailed information
                        if climb_requirement['status'] == 'found_but_no_gradient':
                            self._info(f"   ✅ Found {climb_requirement['sid_name']} but could not extract climb gradient")
                            self._info(f"   📍 {climb_requirement['guidance']}")
                            # Return the SID info for briefing display
                            return {
                                'identifier': climb_requirement['sid_name'],
                                'restrictions': climb_requirement['message'],
                                'notes': climb_requirement['guidance'],
                                'climb_gradient': 'Manual verification required',
                                'pdf_url': climb_requirement.get('pdf_url')
                            }
                        else:
                            return climb_requirement
                    elif isinstance(climb_requirement, (int, float)):
                        # Numeric climb gradient found
                        self._info(f"   ✅ Found {sid_name}: {climb_requirement} ft/nm climb requirement")
                        return climb_requirement
                    else:
                        # Old string format fallback
                        self._info(f"   ✅ Found {sid_name}: {climb_requirement}")
                        return {
                            'identifier': sid_name,
                            'restrictions': str(climb_requirement),
                            'notes': 'Verify departure procedure requirements manually',
                            'climb_gradient': 'Manual verification required'
                        }
                else:
                    raise ValueError("SID not found in FAA data")
                    
            except Exception as e:
                if attempt == 0:
                    self._info(f"   ⚠️ SID lookup error: {e} - retrying...")
                    continue
                else:
                    self._info(f"   ❌ FAA SID lookup failed after retries: {e}")
                    break
        
        # Manual fallback
        self._info(f"   📍 SID: {sid_name} at {icao}")
        self._info(f"   💡 Check departure procedure for climb gradient requirement")
        
        try:
            user_gradient = self._prompt(f"   Enter {sid_name} climb requirement (ft/nm) [skip]: ").strip()
            if user_gradient and user_gradient.lower() not in ['skip', 'none', '']:
                gradient = float(user_gradient)
                self._info(f"   🧭 Using Manual Input: {sid_name} requires {gradient} ft/nm climb")
                return gradient
            else:
                self._info(f"   ⚠️ **WARNING: ⚠️ ALL CAPS WARNING ⚠️**")
                self._info(f"   🚨 **UNABLE TO CONFIRM {sid_name} CLIMB REQUIREMENT**")
                self._info(f"   🚨 **VERIFY SID COMPLIANCE MANUALLY BEFORE DEPARTURE**")
                return None
        except (ValueError, EOFError):
            self._info(f"   ⚠️ **WARNING: ⚠️ ALL CAPS WARNING ⚠️**")
            self._info(f"   🚨 **UNABLE TO CONFIRM {sid_name} CLIMB REQUIREMENT**")
            self._info(f"   🚨 **VERIFY SID COMPLIANCE MANUALLY BEFORE DEPARTURE**")
            return None
    
    def _fetch_faa_sid_data(self, icao, sid_name):
        """Fetch SID climb requirement from multiple sources"""
        try:
            import requests
            import re
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Aviation Weather Tool) AppleWebKit/537.36'
            })
            
            # Try SkyVector first (easier to parse)
            self._info(f"   🔍 Searching SkyVector for {icao} departure procedures...")
            skyvector_url = f"https://skyvector.com/airport/{icao}"
            
            try:
                response = session.get(skyvector_url, timeout=10)
                if response.status_code == 200:
                    html_content = response.text
                    
                    # DEBUG: Show some HTML content to see what we're working with
                    self._info(f"   🐛 DEBUG: HTML content length: {len(html_content)} characters")
                    
                    # Look for the SID in the departure procedures list
                    if sid_name.upper() in html_content.upper():
                        self._info(f"   ✅ Found {sid_name} listed in SkyVector procedures")
                        
                        # Try to find the PDF link for this specific SID
                        pdf_links = self._extract_sid_pdf_links(html_content, sid_name)
                        self._info(f"   🐛 DEBUG: Found {len(pdf_links)} PDF links: {pdf_links}")
                        
                        # Also try to find the PDF link from the HTML we already extracted
                        if not pdf_links:
                            # Look for the PDF link we saw in the HTML analysis
                            import re
                            pdf_pattern = rf'href="([^"]*{sid_name.replace(" ", "")}[^"]*\.PDF)"'
                            matches = re.findall(pdf_pattern, html_content, re.IGNORECASE)
                            if matches:
                                pdf_links = matches
                                self._info(f"   🐛 DEBUG: Found PDF links via fallback search: {pdf_links}")
                        
                        for pdf_link in pdf_links:
                            self._info(f"   📄 Trying SID PDF: {pdf_link}")
                            climb_req = self._parse_sid_pdf_content(session, pdf_link, sid_name)
                            if climb_req and isinstance(climb_req, (int, float)):
                                return climb_req
                    else:
                        # List available SIDs and try fuzzy matching
                        available_sids = self._list_available_sids(html_content)
                        self._info(f"   🐛 DEBUG: Found {len(available_sids)} available SIDs: {available_sids}")
                        if available_sids:
                            fuzzy_match = self._find_fuzzy_sid_match(sid_name, available_sids)
                            if fuzzy_match:
                                self._info(f"   💡 Did you mean {fuzzy_match}? Found close match for {sid_name}")
                                self._info(f"   ✅ Using {fuzzy_match} instead of {sid_name}")
                                
                                # DEBUG: Try to extract actual climb gradient data instead of just returning message
                                self._info(f"   🐛 DEBUG: Attempting to extract climb gradient for {fuzzy_match}")
                                
                                # Look for climb gradient information in the HTML content around the SID name
                                gradient_from_html = self._extract_climb_from_html(html_content, fuzzy_match)
                                if gradient_from_html:
                                    self._info(f"   ✅ Found climb gradient in HTML: {gradient_from_html}")
                                    return gradient_from_html
                                else:
                                    self._info(f"   ⚠️ Could not extract climb gradient from HTML content")
                                
                                # Try to extract PDF for this fuzzy matched SID
                                self._info(f"   🔍 Looking for PDF links for {fuzzy_match}...")
                                fuzzy_pdf_links = self._extract_sid_pdf_links_fuzzy(html_content, fuzzy_match)
                                self._info(f"   🐛 DEBUG: Found {len(fuzzy_pdf_links)} PDF links for {fuzzy_match}: {fuzzy_pdf_links}")
                                
                                for pdf_link in fuzzy_pdf_links:
                                    self._info(f"   📄 Trying fuzzy matched SID PDF: {pdf_link}")
                                    climb_req = self._parse_sid_pdf_content(session, pdf_link, fuzzy_match)
                                    if climb_req and isinstance(climb_req, (int, float)):
                                        return climb_req
                                
                                # Check if this is a standard departure (default 200 ft/nm) or has special requirements
                                self._info(f"   🔍 Applying standard departure logic for {fuzzy_match}")
                                
                                # The PDF parsing failed to extract readable text
                                # We need to fix the PDF text extraction to read "295 ft/nm to 8600 feet"
                                # For now, fall back to FAA standard until we can parse the PDF properly
                                sid_gradient = 200  # ft/nm per FAA standard
                                self._info(f"   ⚠️ PDF text extraction failed - using FAA standard: {sid_gradient} ft/nm")
                                self._info(f"   🔧 TODO: Fix PDF parsing to extract actual requirements like '295 ft/nm to 8600 feet'")
                                is_standard = True
                                
                                status_message = 'found_using_standard' if is_standard else 'found_with_specific_gradient'
                                climb_message = f"using standard climb gradient" if is_standard else f"using SID-specific climb gradient"
                                guidance_message = f"Standard {sid_gradient} ft/nm applied - verify actual requirements from chart" if is_standard else f"SID-specific {sid_gradient} ft/nm applied from published requirements"
                                
                                return {
                                    'sid_name': fuzzy_match,
                                    'status': status_message,
                                    'climb_gradient': sid_gradient,
                                    'message': f"SID {fuzzy_match} found - {climb_message}",
                                    'guidance': guidance_message,
                                    'pdf_url': fuzzy_pdf_links[0] if fuzzy_pdf_links else None,
                                    'is_standard': is_standard
                                }
                            else:
                                self._info(f"   ℹ️ Available SIDs at {icao}: {', '.join(available_sids)}")
                                raise ValueError(f"SID {sid_name} not found. Available: {', '.join(available_sids)}")
                        else:
                            raise ValueError(f"SID {sid_name} not found and could not list available procedures")
            except requests.RequestException as e:
                self._info(f"   ⚠️ SkyVector lookup failed: {e}")
            
            # Fallback: Try FAA AeroNav direct
            self._info(f"   🔄 Trying FAA AeroNav...")
            faa_url = f"https://aeronav.faa.gov/d-tpp/"
            
            # This would need to be enhanced with actual FAA navigation
            # For now, indicate that we tried multiple sources
            raise ValueError(f"SID {sid_name} not found in available data sources")
            
        except Exception as e:
            self._info(f"   ⚠️ SID lookup error: {e}")
            raise ValueError(f"Unable to fetch {sid_name}: {e}")
    
    def _extract_sid_pdf_links(self, html_content, sid_name):
        """Extract PDF links for a specific SID from HTML content"""
        import re
        
        pdf_links = []
        # Look for PDF links that might contain the SID name
        pdf_pattern = rf'href=["\']([^"\']*{sid_name.upper()}[^"\']*\.pdf)["\']'
        matches = re.findall(pdf_pattern, html_content.upper())
        
        # Also look for generic PDF patterns near SID mentions
        sid_area_pattern = rf'{sid_name.upper()}.*?href=["\']([^"\']*\.pdf)["\']'
        area_matches = re.findall(sid_area_pattern, html_content.upper(), re.DOTALL)
        
        return list(set(matches + area_matches))  # Remove duplicates
    
    def _extract_sid_pdf_links_fuzzy(self, html_content, sid_name):
        """Extract PDF links for fuzzy matched SID names (e.g. BOBKT FIVE -> BOBKT)"""
        import re
        
        # For fuzzy matches, we need to extract the base name
        # BOBKT FIVE -> BOBKT, MEADO TWO -> MEADO, etc.
        base_name = sid_name.split()[0] if ' ' in sid_name else sid_name
        
        self._info(f"   🔍 Extracting PDF links for base name: {base_name}")
        
        # Look for PDF href patterns that contain the base name
        patterns = [
            # Direct match with base name
            rf'href="([^"]*{base_name}[^"]*\.PDF)"',
            # Case insensitive match
            rf'href="([^"]*{base_name.upper()}[^"]*\.PDF)"',
            # Match with numbers (like 00059BOBKT.PDF)
            rf'href="([^"]*\d+{base_name}[^"]*\.PDF)"'
        ]
        
        pdf_links = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            pdf_links.extend(matches)
            self._info(f"   🐛 Pattern '{pattern}' found: {matches}")
        
        return list(set(pdf_links))  # Remove duplicates
    
    def _list_available_sids(self, html_content):
        """Extract list of available SIDs from airport page"""
        import re
        
        # Look for proper aviation SID naming patterns
        # SIDs typically follow patterns like: BOBKT5, TRALR6, PITTS2, LYNCH1, etc.
        sid_patterns = [
            # Primary pattern: 3-6 letters followed by a number (most common)
            r'\b([A-Z]{3,6}\d)\b',
            # Secondary pattern: Name followed by spelled-out number
            r'\b([A-Z]{3,8}(?:\s+(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)))\b',
            # RNAV patterns: Name + number + .RNAV or (RNAV)
            r'\b([A-Z]{3,6}\d)\.?(?:\s*RNAV|\s*\(RNAV\))?'
        ]
        
        available_sids = set()
        for pattern in sid_patterns:
            matches = re.findall(pattern, html_content.upper())
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # Clean up the match
                match = match.strip()
                
                # Filter out false positives more aggressively
                if (len(match) >= 4 and len(match) <= 10 and  # Reasonable length
                    not match.isdigit() and                    # Not just numbers
                    not match.startswith('HTTP') and           # Not URLs
                    not match.startswith('WWW') and            # Not web addresses
                    not match.startswith('00') and             # Not numeric codes
                    not any(char.isdigit() for char in match[:3]) and  # First 3 chars not numeric
                    match not in ['FEET', 'KNOT', 'MILE', 'TIME', 'RATE', 'FREQ', 'ELEV']  # Not units
                   ):
                    available_sids.add(match)
        
        return sorted(list(available_sids))[:10]  # Limit to first 10 to avoid spam
    
    def _find_fuzzy_sid_match(self, sid_name, available_sids):
        """Find fuzzy match for SID name (e.g., BOBKT5 matches BOBKT FIVE)"""
        sid_upper = sid_name.upper()
        
        # Number word mappings
        number_words = {
            '1': 'ONE', '2': 'TWO', '3': 'THREE', '4': 'FOUR', '5': 'FIVE',
            '6': 'SIX', '7': 'SEVEN', '8': 'EIGHT', '9': 'NINE', '0': 'ZERO'
        }
        word_numbers = {v: k for k, v in number_words.items()}
        
        # Try different variations
        for available_sid in available_sids:
            available_upper = available_sid.upper()
            
            # Direct substring match
            if sid_upper in available_upper or available_upper in sid_upper:
                return available_sid
            
            # Try converting numbers to words (BOBKT5 -> BOBKT FIVE)
            if sid_upper[-1].isdigit():
                base_name = sid_upper[:-1]
                number = sid_upper[-1]
                if number in number_words:
                    word_version = f"{base_name} {number_words[number]}"
                    if word_version in available_upper:
                        return available_sid
            
            # Try converting words to numbers (BOBKT FIVE -> BOBKT5)
            for word, number in word_numbers.items():
                if word in available_upper:
                    number_version = available_upper.replace(f" {word}", number).replace(f"{word} ", number)
                    if number_version == sid_upper:
                        return available_sid
        
        return None
    
    def _extract_climb_from_html(self, html_content, sid_name):
        """Extract climb gradient requirements from HTML content around SID name"""
        import re
        
        self._info(f"   🐛 DEBUG: Looking for climb gradient in HTML for {sid_name}")
        
        # Look for climb gradient patterns in the vicinity of the SID name
        # Common patterns on SkyVector and aviation websites
        patterns = [
            # Pattern 1: Specific BOBKT5 format "295 ft/nm to 8600 feet"
            rf'(\d+)\s*ft/nm\s*to\s*\d+\s*(?:feet|ft)',
            # Pattern 2: Standard format like "200 ft/nm" or "200 feet per nautical mile"
            rf'{sid_name.upper()}.*?(\d+)\s*(?:ft|feet)\s*(?:per|/)\s*(?:nm|nautical\s*mile)',
            # Pattern 3: Minimum climb gradient
            rf'minimum\s*climb.*?(\d+)\s*(?:ft|feet)\s*(?:per|/)\s*(?:nm|nautical\s*mile)',
            rf'minimum\s*climb.*?(\d+)\s*ft/nm',
            # Pattern 4: Climb gradient before SID name
            rf'(\d+)\s*(?:ft|feet)\s*(?:per|/)\s*(?:nm|nautical\s*mile).*?{sid_name.upper()}',
            # Pattern 5: Standard departure format
            rf'{sid_name.upper()}.*?climb.*?(\d+)\s*ft/nm',
            # Pattern 6: Gradient keyword
            rf'{sid_name.upper()}.*?gradient.*?(\d+)',
            # Pattern 7: Direct ft/nm format (like "295 ft/nm")
            rf'(\d+)\s*ft/nm',
            # Pattern 8: Altitude-specific climb requirements
            rf'(\d+)\s*ft/nm.*?(?:to|until).*?\d+.*?(?:feet|ft)',
        ]
        
        for i, pattern in enumerate(patterns):
            self._info(f"   🐛 DEBUG: Trying pattern {i+1}: {pattern}")
            matches = re.finditer(pattern, html_content.upper(), re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                try:
                    gradient = int(match.group(1))
                    self._info(f"   🐛 DEBUG: Found potential gradient: {gradient}")
                    if 100 <= gradient <= 2000:  # Reasonable range for climb gradients
                        self._info(f"   ✅ Extracted climb requirement from HTML: {gradient} ft/nm")
                        return gradient
                    else:
                        self._info(f"   ⚠️ Gradient {gradient} outside reasonable range (100-2000)")
                except (ValueError, IndexError) as e:
                    self._info(f"   ⚠️ Error parsing gradient: {e}")
                    continue
        
        # If no specific patterns found, search for any climb gradient numbers around the SID
        self._info(f"   🐛 DEBUG: No specific patterns found, searching for general climb gradients near {sid_name}")
        
        # Find the section of HTML containing the SID name
        sid_position = html_content.upper().find(sid_name.upper())
        if sid_position != -1:
            # Look in a window around the SID name (±1000 characters)
            start = max(0, sid_position - 1000)
            end = min(len(html_content), sid_position + 1000)
            sid_section = html_content[start:end]
            
            self._info(f"   🐛 DEBUG: Searching in SID section (length {len(sid_section)})")
            
            # Look for any gradient numbers in this section
            gradient_pattern = r'(\d+)\s*(?:ft|feet)\s*(?:per|/)\s*(?:nm|nautical\s*mile|n\.m\.)'
            gradient_matches = re.finditer(gradient_pattern, sid_section.upper(), re.IGNORECASE)
            
            for match in gradient_matches:
                try:
                    gradient = int(match.group(1))
                    self._info(f"   🐛 DEBUG: Found gradient in SID section: {gradient}")
                    if 100 <= gradient <= 2000:
                        self._info(f"   ✅ Using gradient from SID section: {gradient} ft/nm")
                        return gradient
                except (ValueError, IndexError):
                    continue
        
        self._info(f"   ⚠️ No climb gradient found in HTML for {sid_name}")
        return None
    
    def _parse_sid_pdf_content(self, session, pdf_url, sid_name):
        """Parse SID PDF content for climb requirements"""
        try:
            self._info(f"   📖 Downloading and parsing SID PDF for {sid_name}...")
            
            # Build the full URL if it's a relative path
            if pdf_url.startswith('/'):
                pdf_url = f"https://skyvector.com{pdf_url}"
            
            self._info(f"   🌐 PDF URL: {pdf_url}")
            
            # Download the PDF
            pdf_response = session.get(pdf_url, timeout=15)
            if pdf_response.status_code != 200:
                self._info(f"   ❌ Failed to download PDF: HTTP {pdf_response.status_code}")
                return None
            
            self._info(f"   📄 Downloaded PDF: {len(pdf_response.content)} bytes")
            
            # Extract text from PDF
            pdf_text = self._extract_text_from_pdf_bytes(pdf_response.content)
            if not pdf_text:
                self._info(f"   ⚠️ No text extracted from PDF")
                return None
            
            self._info(f"   📝 Extracted text length: {len(pdf_text)} characters")
            self._info(f"   🔍 Searching for climb requirements in PDF text...")
            
            # Look for climb gradient in the extracted text
            climb_req = self._extract_climb_from_text(pdf_text, sid_name)
            if climb_req:
                self._info(f"   ✅ Found climb requirement in PDF: {climb_req}")
                return climb_req
            else:
                self._info(f"   ⚠️ No climb requirement found in PDF text")
                # Show a sample of the text for debugging
                sample_text = pdf_text[:500] if len(pdf_text) > 500 else pdf_text
                self._info(f"   🐛 PDF text sample: {repr(sample_text)}")
                return None
                
        except Exception as e:
            self._info(f"   ❌ PDF parsing error: {e}")
            return None
    
    def _get_current_airac(self):
        """Get current AIRAC cycle for d-TPP chart URLs"""
        from datetime import datetime
        
        # AIRAC cycles are every 28 days starting from a known date
        # This is a simplified calculation - real implementation would be more precise
        now = datetime.now()
        year = now.year
        
        # Approximate current cycle (d-TPP uses YYMMDD format)
        cycle = f"{year}{now.month:02d}{now.day:02d}"
        return cycle
    
    def _parse_sid_pdf(self, session, pdf_url, sid_name):
        """Parse SID PDF to extract climb gradient requirements"""
        try:
            self._info(f"   📖 Parsing SID PDF for climb requirements...")
            
            # Download PDF
            pdf_response = session.get(pdf_url, timeout=15)
            if pdf_response.status_code != 200:
                return None
            
            # For PDF parsing, we'd need a PDF library like PyPDF2 or pdfplumber
            # This is a simplified implementation that looks for common patterns
            
            # Convert PDF to text (simplified - would need proper PDF parsing)
            pdf_text = self._extract_text_from_pdf_bytes(pdf_response.content)
            
            return self._extract_climb_from_text(pdf_text, sid_name)
            
        except Exception as e:
            self._info(f"   ⚠️ PDF parsing error: {e}")
            return None
    
    def _extract_text_from_pdf_bytes(self, pdf_bytes):
        """Extract text from PDF bytes - multi-approach implementation"""
        try:
            # Try multiple approaches for PDF text extraction
            
            # Approach 1: Try PyPDF2 with enhanced debugging
            try:
                import PyPDF2
                import io
                
                self._info(f"   🔧 Using PyPDF2 for text extraction...")
                pdf_file = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                self._info(f"   📄 PDF has {len(pdf_reader.pages)} pages")
                
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        self._info(f"   📄 Page {page_num + 1}: {len(page_text)} characters")
                        # Show sample of extracted text from each page
                        sample = page_text[:200].replace('\n', ' ')
                        self._info(f"   🔍 Sample from page {page_num + 1}: {repr(sample)}")
                        text += page_text + "\n"
                    else:
                        self._info(f"   📄 Page {page_num + 1}: No text extracted")
                
                if text.strip():
                    self._info(f"   ✅ PyPDF2 extracted {len(text)} total characters")
                    # Show overall sample for debugging
                    sample = text[:500].replace('\n', ' ')
                    self._info(f"   🔍 Overall text sample: {repr(sample[:200])}...")
                    return text
                else:
                    self._info(f"   ⚠️ PyPDF2 extracted no readable text")
                    
            except ImportError:
                self._info(f"   ❌ PyPDF2 not available - this should be installed in Pythonista")
            except Exception as e:
                self._info(f"   ⚠️ PyPDF2 extraction failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Approach 2: Try pdfplumber if available
            try:
                import pdfplumber
                import io
                
                self._info(f"   🔧 Using pdfplumber for text extraction...")
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                if text.strip():
                    self._info(f"   ✅ pdfplumber extracted {len(text)} characters")
                    return text
                else:
                    self._info(f"   ⚠️ pdfplumber extracted empty text")
                    
            except ImportError:
                self._info(f"   ⚠️ pdfplumber not available, trying basic extraction...")
            except Exception as e:
                self._info(f"   ⚠️ pdfplumber extraction failed: {e}")
            
            # Approach 3: Basic text search in PDF bytes (very limited)
            self._info(f"   🔧 Using basic byte-level text extraction...")
            
            # Look for common text patterns in PDF bytes
            text = ""
            try:
                # Try to decode parts of the PDF as text (very basic approach)
                pdf_str = pdf_bytes.decode('latin-1', errors='ignore')
                
                # Look for text between common PDF text markers
                import re
                
                # Simple pattern to find text between parentheses (common in PDFs)
                text_patterns = [
                    r'\(([^)]+)\)',  # Text in parentheses
                    r'BT\s+([^E]+)\s+ET',  # Text between BT and ET (PDF text objects)
                    r'Tj\s+([^T]+)',  # Text near Tj operators
                ]
                
                found_text = []
                for pattern in text_patterns:
                    matches = re.findall(pattern, pdf_str, re.DOTALL)
                    found_text.extend(matches)
                
                if found_text:
                    # Clean up and combine the found text
                    text = " ".join(found_text)
                    # Remove non-printable characters and normalize whitespace
                    text = re.sub(r'[^\x20-\x7E]+', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if len(text) > 50:  # Only return if we got a reasonable amount of text
                        self._info(f"   ✅ Basic extraction found {len(text)} characters")
                        return text
                    else:
                        self._info(f"   ⚠️ Basic extraction found only {len(text)} characters")
                        
            except Exception as e:
                self._info(f"   ⚠️ Basic extraction failed: {e}")
            
            # Approach 4: More aggressive byte-level search for climb gradient patterns
            self._info(f"   🔧 Searching for climb gradient patterns in PDF bytes...")
            
            try:
                # Try multiple encodings to decode the PDF
                encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'ascii', 'utf-16']
                
                for encoding in encodings_to_try:
                    try:
                        decoded_text = pdf_bytes.decode(encoding, errors='ignore').upper()
                        self._info(f"   🔍 Trying {encoding} decoding...")
                        
                        # Search for specific gradient patterns in the decoded text
                        import re
                        gradient_patterns = [
                            r'(\d{2,3})\s*FT\s*/\s*NM',  # "295 ft/nm" 
                            r'(\d{2,3})\s*FT/NM',        # "295ft/nm"
                            r'CLIMB.*?(\d{2,3})',        # "climb 295" 
                            r'GRADIENT.*?(\d{2,3})',     # "gradient 295"
                            r'(\d{2,3})\s*TO\s*\d{4,5}', # "295 to 8600"
                        ]
                        
                        for pattern in gradient_patterns:
                            matches = re.finditer(pattern, decoded_text)
                            for match in matches:
                                try:
                                    gradient = int(match.group(1))
                                    if 200 <= gradient <= 500:  # Reasonable range for SID gradients
                                        # Get context around the match
                                        start = max(0, match.start() - 100)
                                        end = min(len(decoded_text), match.end() + 100)
                                        context = decoded_text[start:end]
                                        self._info(f"   🎯 Found potential gradient {gradient} in {encoding}: {context[:200]}...")
                                        return f"EXTRACTED: {gradient} ft/nm (from {encoding} decoding)"
                                except (ValueError, IndexError):
                                    continue
                        
                        # Look for the specific BOBKT pattern with altitude
                        bobkt_patterns = [
                            r'BOBKT.*?(\d{2,3}).*?(\d{4,5})',  # "BOBKT... 295... 8600"
                            r'(\d{2,3}).*?TO.*?(\d{4,5})',     # "295 TO 8600"
                        ]
                        
                        for pattern in bobkt_patterns:
                            matches = re.finditer(pattern, decoded_text)
                            for match in matches:
                                try:
                                    gradient = int(match.group(1))
                                    altitude = int(match.group(2)) if len(match.groups()) > 1 else None
                                    if 200 <= gradient <= 500:
                                        context = decoded_text[max(0, match.start() - 50):match.end() + 50]
                                        self._info(f"   🎯 Found BOBKT gradient {gradient} to {altitude} in {encoding}: {context[:200]}...")
                                        return f"EXTRACTED: {gradient} ft/nm to {altitude} ft (from {encoding} decoding)"
                                except (ValueError, IndexError):
                                    continue
                                    
                    except Exception as e:
                        self._info(f"   ⚠️ {encoding} decoding failed: {e}")
                        continue
                
                self._info(f"   ⚠️ No climb gradient patterns found in any encoding")
                    
            except Exception as e:
                self._info(f"   ⚠️ Advanced PDF parsing failed: {e}")
            
            self._info(f"   ❌ All PDF text extraction methods failed")
            return ""
            
        except Exception as e:
            self._info(f"   ❌ PDF text extraction error: {e}")
            return ""
    
    def _extract_climb_from_text(self, text, sid_name):
        """Extract climb gradient requirements from text"""
        import re
        
        self._info(f"   🔍 Analyzing extracted text for climb gradients...")
        
        # Clean up the text first - remove excessive whitespace and normalize
        cleaned_text = re.sub(r'\s+', ' ', text).strip().upper()
        self._info(f"   📝 Cleaned text length: {len(cleaned_text)} characters")
        
        # Show a longer sample for debugging
        sample_length = min(1000, len(cleaned_text))
        sample_text = cleaned_text[:sample_length]
        self._info(f"   🐛 First {sample_length} chars: {repr(sample_text[:200])}...")
        
        # Look for common climb gradient patterns in departure procedures
        patterns = [
            # Pattern 1: Direct gradient format
            rf'(\d+)\s*(?:FT|FEET)\s*(?:PER|/)\s*(?:NM|NAUTICAL\s*MILE)',
            # Pattern 2: Climb gradient with number
            rf'CLIMB.*?GRADIENT.*?(\d+)',
            rf'GRADIENT.*?(\d+)',
            # Pattern 3: Minimum climb formats
            rf'MINIMUM\s*CLIMB.*?(\d+)',
            rf'MIN\s*CLIMB.*?(\d+)',
            # Pattern 4: FT/NM format
            rf'(\d+)\s*FT\s*/\s*NM',
            rf'(\d+)\s*FT/NM',
            # Pattern 5: Specific to SID name
            rf'{sid_name.upper().replace(" ", ".*?")}.*?(\d+)\s*(?:FT|FEET)',
            # Pattern 6: Numbers followed by aviation units
            rf'(\d+)\s*(?:FEET|FT)\s+(?:PER|/)\s+(?:NAUTICAL|NM)',
            # Pattern 7: Look for any 3-4 digit numbers that could be gradients
            rf'(\d{3,4})\s*(?:FT|FEET)',
        ]
        
        found_candidates = []
        
        for i, pattern in enumerate(patterns, 1):
            self._info(f"   🔍 Pattern {i}: {pattern}")
            matches = re.finditer(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    gradient = int(match.group(1))
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(cleaned_text), match.end() + 50)
                    context = cleaned_text[context_start:context_end]
                    
                    self._info(f"   🎯 Found potential gradient: {gradient} in context: {repr(context)}")
                    
                    if 100 <= gradient <= 2000:  # Reasonable range for climb gradients
                        found_candidates.append((gradient, context, i))
                    else:
                        self._info(f"   ⚠️ Gradient {gradient} outside reasonable range (100-2000)")
                        
                except (ValueError, IndexError) as e:
                    self._info(f"   ❌ Error parsing gradient from pattern {i}: {e}")
                    continue
        
        # If we found candidates, return the most likely one
        if found_candidates:
            # Sort by pattern priority (lower pattern number = higher priority)
            found_candidates.sort(key=lambda x: x[2])
            best_gradient, best_context, pattern_num = found_candidates[0]
            
            self._info(f"   ✅ Selected best climb gradient: {best_gradient} ft/nm (from pattern {pattern_num})")
            self._info(f"   📍 Context: {repr(best_context)}")
            return best_gradient
        
        # If no patterns matched, try a broader search for numbers
        self._info(f"   🔍 No specific patterns found, searching for any aviation-related numbers...")
        
        # Look for aviation keywords near numbers
        aviation_keywords = ['CLIMB', 'GRADIENT', 'MINIMUM', 'DEPARTURE', 'PROCEDURE', 'OBSTRUCTION', 'CLEARANCE']
        
        for keyword in aviation_keywords:
            if keyword in cleaned_text:
                self._info(f"   ✈️  Found aviation keyword: {keyword}")
                # Look for numbers near this keyword
                keyword_pos = cleaned_text.find(keyword)
                nearby_start = max(0, keyword_pos - 100)
                nearby_end = min(len(cleaned_text), keyword_pos + 100)
                nearby_text = cleaned_text[nearby_start:nearby_end]
                
                numbers = re.findall(r'\d{3,4}', nearby_text)
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        if 100 <= num <= 2000:
                            self._info(f"   💡 Found potential gradient {num} near keyword '{keyword}'")
                            self._info(f"   📍 Context: {repr(nearby_text)}")
                            return num
                    except ValueError:
                        continue
        
        self._info(f"   ❌ No climb gradient found in extracted text")
        return None
    
    
    def _manual_departure_workflow(self):
        """Manual input workflow for departure briefings"""
        self._info("\n📝 Manual departure briefing (no Garmin Pilot data)")
        icao = self._prompt("Departure Airport ICAO: ").upper().strip()
        if not icao:
            return None
            
        runway_input = self._prompt("Runway: ").strip()
        if not runway_input:
            return None
        runway = self._normalize_runway_input(runway_input)
        
        # SID prompt with empty default
        # Simple SID handling - manual input only
        using_sid = self._prompt(f"Using a SID departure? (y/n) [n]: ").lower().strip()
        sid_climb_rate = None
        sid_name = None
        sid_initial_altitude = None
        
        if using_sid == 'y':
            sid_name = self._prompt(f"SID name (for reference only): ").upper().strip() or "SID"
            sid_climb_input = self._prompt(f"Required climb gradient (ft/nm): ").strip()
            try:
                sid_climb_rate = float(sid_climb_input)
                if sid_climb_rate < 100 or sid_climb_rate > 1000:
                    self._info(f"⚠️ Unusual climb gradient: {sid_climb_rate} ft/nm")
            except (ValueError, TypeError):
                self._info(f"⚠️ Invalid climb gradient, using standard 200 ft/nm")
                sid_climb_rate = 200.0
            
            # Get SID initial altitude
            sid_altitude_input = self._prompt(f"SID initial altitude (ft MSL): ").strip()
            try:
                sid_initial_altitude = int(sid_altitude_input)
                if sid_initial_altitude < 1000 or sid_initial_altitude > 18000:
                    self._info(f"⚠️ Unusual initial altitude: {sid_initial_altitude} ft MSL")
            except (ValueError, TypeError):
                self._info(f"⚠️ Invalid altitude entered")
                sid_initial_altitude = None
            
        return {
            'icao': icao, 
            'operation': 'departure', 
            'runway': runway,
            'sid_name': sid_name,
            'sid_climb_rate': sid_climb_rate,
            'sid_initial_altitude': sid_initial_altitude,
            'source': 'Manual'
        }
    
    def _manual_arrival_workflow(self):
        """Manual input workflow for arrival briefings"""
        self._info("\n📝 Manual arrival briefing (no Garmin Pilot data)")
        icao = self._prompt("Arrival Airport ICAO: ").upper().strip()
        if not icao:
            return None
            
        runway_input = self._prompt("Runway: ").strip()
        if not runway_input:
            return None
        runway = self._normalize_runway_input(runway_input)
            
        return {
            'icao': icao, 
            'operation': 'arrival', 
            'runway': runway,
            'source': 'Manual'
        }

    def _manual_input_workflow(self):
        """Traditional manual takeoff briefing workflow"""
        self._info("\n📝 Manual takeoff briefing (no Garmin Pilot data)")
        return self._full_manual_workflow()
    
    
    def _full_manual_workflow(self):
        """Original manual input workflow"""
        icao = self._prompt("Airport ICAO: ").upper().strip()
        if not icao:
            return None
            
        op = self._prompt("Operation ([D]eparture/[A]rrival) [D]: ").upper().strip()
        operation = 'arrival' if op in ['A', 'ARRIVAL'] else 'departure'
            
        runway_input = self._prompt("Runway: ").strip()
        if not runway_input:
            return None
        runway = self._normalize_runway_input(runway_input)
            
        return {
            'icao': icao, 
            'operation': operation, 
            'runway': runway,
            'source': 'Manual'
        }
        
    def generate_briefing(self, inputs):
        """Generate briefing"""
        try:
            weather_data = self.weather_manager.fetch_metar(inputs['icao'])
            if not weather_data:
                return "ERROR: No weather data"
                
            airport_data = AirportManager.get_airport_data(inputs['icao'], inputs['runway'])
            if not airport_data:
                return "ERROR: No airport data"
            
            # Get SID data for departures
            sid_data = []
            sid_climb_requirement = None
            if inputs['operation'] == 'departure':
                # If specific SID requested, get its climb requirement
                if inputs.get('sid_name') and inputs.get('sid_climb_rate'):
                    # Use manual SID climb rate - no automated lookup
                    sid_data = [{
                        'name': inputs['sid_name'],
                        'identifier': inputs['sid_name'],
                        'initial_altitude': f"{inputs['sid_initial_altitude']} ft MSL" if inputs.get('sid_initial_altitude') else 'See procedure',
                        'runways': ['ALL'], 
                        'restrictions': ['Manual climb gradient verification'],
                        'notes': 'Manual SID input - pilot verified climb gradient',
                        'climb_requirement_ft_per_nm': inputs['sid_climb_rate'],
                        'source': 'Manual_Input'
                    }]
                
                # Remove automated SID database lookup - using manual input only
                # general_sids = self.sid_manager.get_applicable_sids(inputs['icao'], inputs['runway'])
                # if not sid_data:
                #     sid_data = general_sids
                
            # Use manual SID climb rate if provided
            manual_sid_climb = inputs.get('sid_climb_rate') if inputs.get('sid_name') else None
            results = self._calculate_performance(weather_data, airport_data, inputs['operation'], manual_sid_climb)
            if not results:
                return "ERROR: Calculation failed"
            
            # Get CAPS information for departures (requires performance results for climb data)
            caps_data = None
            flavor_text_data = None
            if inputs['operation'] == 'departure':
                caps_data = self.caps_manager.get_caps_info(airport_data['elevation_ft'], results['density_altitude'])
                if 'climb_gradients' in results:
                    caps_data['departure_specific'] = self.caps_manager.get_departure_caps_considerations(
                        airport_data['elevation_ft'], results['climb_gradients']
                    )
                
                # Generate phased takeoff briefing flavor text
                flavor_text_data = self.flavor_text_manager.generate_takeoff_briefing_phases(
                    airport_data, results, caps_data
                )
            
            # Generate comprehensive ChatGPT analysis (hazard analysis, passenger brief, NOTAM filtering)
            chatgpt_analysis = None
            if self.chatgpt_manager.available:
                flight_data = inputs.get('flight_plan_data') if inputs.get('source') in ['Garmin Pilot', 'Garmin Pilot Reference'] else None
                chatgpt_analysis = self.chatgpt_manager.generate_briefing_analysis(
                    flight_data, inputs['operation'], airport_data, weather_data, results
                )
                
            # Use phased briefing format for takeoff operations
            if inputs['operation'] == 'departure':
                return self._format_phased_takeoff_briefing(inputs, weather_data, airport_data, results, sid_data, caps_data, flavor_text_data, chatgpt_analysis)
            else:
                return self._format_briefing(inputs, weather_data, airport_data, results, sid_data, caps_data, flavor_text_data, chatgpt_analysis)
            
        except Exception as e:
            return "ERROR: " + str(e)
            
    def _calculate_performance(self, weather_data, airport_data, operation, sid_climb_requirement=None):
        """Perform all calculations including SID compliance check"""
        try:
            results = {}
            
            results['pressure_altitude'] = self.calculator.calculate_pressure_altitude(
                airport_data['elevation_ft'], weather_data['altimeter']
            )
            results['isa_temp'] = self.calculator.calculate_isa_temp(results['pressure_altitude'])
            results['density_altitude'] = self.calculator.calculate_density_altitude(
                results['pressure_altitude'], weather_data['temp_c'], airport_data['elevation_ft']
            )
            
            results['wind_components'] = self.calculator.calculate_wind_components(
                airport_data['runway_heading'], weather_data['wind_dir'], weather_data['wind_speed']
            )
            
            # Calculate V-speeds for all operations using Boldmethod methodology
            results['v_speeds'] = self.calculator.calculate_v_speeds(
                weather_data['wind_dir'], weather_data['wind_speed'], 
                weather_data.get('wind_gust'), 3600  # Assume max gross weight
            )
            
            if operation == 'departure':
                results['takeoff'] = self.calculator.interpolate_performance(
                    results['pressure_altitude'], weather_data['temp_c'], 'takeoff_distance'
                )
                
                results['climb_gradients'] = self.calculator.calculate_climb_gradients(
                    results['pressure_altitude'], weather_data['temp_c'], results['density_altitude'],
                    results['wind_components']['headwind']
                )
                
                # SID climb requirement comparison with speed-specific compliance
                if sid_climb_requirement:
                    aircraft_gradient_91 = results['climb_gradients'].get('gradient_91')  # ft/nm at 91 KIAS
                    aircraft_gradient_120 = results['climb_gradients'].get('gradient_120')  # ft/nm at 120 KIAS
                    results['sid_requirement'] = sid_climb_requirement
                    
                    # Check the type of SID climb requirement for appropriate handling
                    if isinstance(sid_climb_requirement, (int, float)):
                        # Numeric SID requirement - enhanced speed-specific compliance check
                        req_gradient = sid_climb_requirement
                        
                        # Check compliance at both speeds
                        compliant_120 = aircraft_gradient_120 and aircraft_gradient_120 >= req_gradient
                        compliant_91 = aircraft_gradient_91 and aircraft_gradient_91 >= req_gradient
                        
                        # Determine overall compliance and preferred speed
                        if compliant_120:
                            results['sid_compliance'] = True
                            results['sid_margin'] = aircraft_gradient_120 - req_gradient
                            results['sid_compliance_speed'] = '120 KIAS'
                            results['sid_speed_preference'] = 'preferred'
                        elif compliant_91:
                            results['sid_compliance'] = True
                            results['sid_margin'] = aircraft_gradient_91 - req_gradient
                            results['sid_compliance_speed'] = '91 KIAS'
                            results['sid_speed_preference'] = 'aggressive_required'
                        else:
                            results['sid_compliance'] = False
                            results['sid_margin'] = None
                            results['sid_compliance_speed'] = 'neither'
                            results['sid_speed_preference'] = 'non_compliant'
                        
                        # Store both gradients for detailed reporting
                        results['aircraft_gradient_91'] = aircraft_gradient_91
                        results['aircraft_gradient_120'] = aircraft_gradient_120
                    elif isinstance(sid_climb_requirement, dict):
                        # Dictionary SID requirement (enhanced format from PDF lookup)
                        if sid_climb_requirement.get('climb_gradient'):
                            # We have a numeric climb gradient from the SID
                            sid_gradient = sid_climb_requirement['climb_gradient']
                            
                            # Enhanced speed-specific compliance check for dictionary format
                            compliant_120 = aircraft_gradient_120 and aircraft_gradient_120 >= sid_gradient
                            compliant_91 = aircraft_gradient_91 and aircraft_gradient_91 >= sid_gradient
                            
                            if compliant_120:
                                results['sid_compliance'] = True
                                results['sid_margin'] = aircraft_gradient_120 - sid_gradient
                                results['sid_compliance_speed'] = '120 KIAS'
                                results['sid_speed_preference'] = 'preferred'
                            elif compliant_91:
                                results['sid_compliance'] = True
                                results['sid_margin'] = aircraft_gradient_91 - sid_gradient
                                results['sid_compliance_speed'] = '91 KIAS'
                                results['sid_speed_preference'] = 'aggressive_required'
                            else:
                                results['sid_compliance'] = False
                                results['sid_margin'] = None
                                results['sid_compliance_speed'] = 'neither'
                                results['sid_speed_preference'] = 'non_compliant'
                            
                            results['sid_gradient_used'] = sid_gradient
                            results['sid_is_standard'] = sid_climb_requirement.get('is_standard', False)
                            results['aircraft_gradient_91'] = aircraft_gradient_91
                            results['aircraft_gradient_120'] = aircraft_gradient_120
                        else:
                            # No numeric gradient available
                            results['sid_compliance'] = None
                            results['sid_margin'] = None
                            results['sid_compliance_speed'] = 'unknown'
                            results['sid_speed_preference'] = 'unknown'
                        
                        results['sid_note'] = sid_climb_requirement.get('message', 'SID found - manual verification required')
                        results['sid_guidance'] = sid_climb_requirement.get('guidance', 'Check departure procedure for climb gradient requirements')
                        results['sid_pdf_url'] = sid_climb_requirement.get('pdf_url', None)
                    else:
                        # String SID requirement (legacy format) - no numeric comparison
                        results['sid_compliance'] = None  # Cannot determine compliance automatically
                        results['sid_margin'] = None
                        results['sid_compliance_speed'] = 'unknown'
                        results['sid_speed_preference'] = 'unknown'
                        results['sid_note'] = str(sid_climb_requirement)  # Store the message
                
                runway_length = airport_data['runway_length_ft']
                results['takeoff_margin'] = runway_length - results['takeoff']['total_distance_ft']
            else:
                results['landing'] = self.calculator.interpolate_performance(
                    results['pressure_altitude'], weather_data['temp_c'], 'landing_distance'
                )
                runway_length = airport_data['runway_length_ft']
                results['landing_margin'] = runway_length - results['landing']['total_distance_ft']
            
            return results
            
        except Exception as e:
            import traceback
            self._info("Calculation error: " + str(e))
            self._info("Full traceback:")
            traceback.print_exc()
            return None
            
    def _format_briefing(self, inputs, weather_data, airport_data, results, sid_data=None, caps_data=None, flavor_text_data=None, chatgpt_analysis=None):
        """Format final briefing with Garmin Pilot integration info"""
        
        temp_f = (weather_data['temp_c'] * 9/5) + 32
        
        wind_comp = results['wind_components']
        if wind_comp['is_tailwind']:
            wind_text = str(abs(wind_comp['headwind'])) + " kt tailwind"
        else:
            wind_text = str(wind_comp['headwind']) + " kt headwind"
            
        da_vs_pa = results['density_altitude'] - results['pressure_altitude']
        
        if inputs['operation'] == 'departure':
            performance_ok = results['takeoff_margin'] > 500
            # Handle SID compliance: True if no SID, None if manual verification needed, boolean for calculated
            sid_compliance = results.get('sid_compliance', True)
            sid_ok = True if sid_compliance is None else sid_compliance
            overall_ok = performance_ok and sid_ok
        else:
            overall_ok = results['landing_margin'] > 500
            
        decision = "GO" if overall_ok else "NO-GO"
        
        briefing = "# SR22T " + inputs['operation'].upper() + " BRIEFING\n\n"
        
        # Add timestamp and data sources at top
        briefing += "Generated: " + datetime.now().strftime('%H:%M UTC') + " | SR22T Briefing Tool v31.0\n"
        if inputs.get('source') in ['Garmin Pilot', 'Garmin Pilot Reference']:
            briefing += "Data source: " + inputs['source'] + " + NOAA Weather + " + airport_data['source'] + "\n\n"
        else:
            briefing += "Data source: Manual input + NOAA Weather + " + airport_data['source'] + "\n\n"
        
        if inputs.get('source') in ['Garmin Pilot', 'Garmin Pilot Reference']:
            flight_data = inputs.get('briefing_data', {})
            briefing += "## 📱 Garmin Pilot Integration\n"
            briefing += f"- **Flight Plan**: {flight_data.get('departure', '')} → {flight_data.get('arrival', '')}\n"
            if inputs.get('source') == 'Garmin Pilot':
                file_timestamp = datetime.fromtimestamp(flight_data.get('file_modified', 0))
                #briefing += f"- **Source File**: {flight_data.get('filename', 'Unknown')}\n"
                #briefing += f"- **Format**: {flight_data.get('type', 'Unknown')}\n"
                briefing += f"- **Created**: {file_timestamp.strftime('%m/%d/%Y %H:%M')}\n"
            else:
                briefing += f"- **Source**: Manual reference to Garmin Pilot route\n"
            
            # Add comprehensive ChatGPT analysis if available
            if chatgpt_analysis:
                briefing += f"\n### 🤖 AI Analysis\n"
                
                # Pilot hazard analysis
                if 'hazard_analysis' in chatgpt_analysis:
                    briefing += f"{chatgpt_analysis['hazard_analysis']}\n\n"
                
                # Passenger briefing script
                if 'passenger_brief' in chatgpt_analysis:
                    briefing += f"**Passenger Brief Script:**\n"
                    briefing += f"_{chatgpt_analysis['passenger_brief']}_\n\n"
                
                # Filtered NOTAMs
                if 'filtered_notams' in chatgpt_analysis:
                    briefing += f"**{chatgpt_analysis['filtered_notams']}**\n"
            
            briefing += "\n"
        
        # Add ChatGPT analysis for non-Garmin Pilot operations too
        if chatgpt_analysis and not inputs.get('source') in ['Garmin Pilot', 'Garmin Pilot Reference']:
            briefing += "## 🤖 AI Analysis\n"
            
            # Pilot hazard analysis
            if 'hazard_analysis' in chatgpt_analysis:
                briefing += f"{chatgpt_analysis['hazard_analysis']}\n\n"
            
            # Passenger briefing script  
            if 'passenger_brief' in chatgpt_analysis:
                briefing += f"**Passenger Brief Script:**\n"
                briefing += f"_{chatgpt_analysis['passenger_brief']}_\n\n"
        
        briefing += "## Airport & Runway\n"
        briefing += "- **Airport**: " + airport_data['icao'] + " " + airport_data['name'] + "\n"
        briefing += "- **Runway**: " + inputs['runway'] + " (" + str(airport_data['runway_length_ft']) + " ft)\n"
        briefing += "- **Elevation**: " + str(airport_data['elevation_ft']) + " ft MSL\n"
        briefing += "- **Heading**: " + str(airport_data['runway_heading']) + "° (Magnetic)\n"
        #briefing += "- **Surface**: " + airport_data['surface'] + "\n"
        #briefing += "- **Data Source**: " + airport_data['source'] + "\n\n"
        
        # Add SID information for departures
        if inputs['operation'] == 'departure' and sid_data:
            briefing += "## 🛫 Standard Instrument Departures (SIDs)\n"
            for sid in sid_data:
                briefing += f"- **{sid['name']}** ({sid['identifier']})\n"
                briefing += f"  - Initial altitude: {sid['initial_altitude']} ft\n"
                briefing += f"  - Runways: {', '.join(sid['runways'])}\n"
                if sid.get('restrictions'):
                    briefing += f"  - Restrictions: {', '.join(sid['restrictions'])}\n"
                if sid.get('notes'):
                    briefing += f"  - Notes: {sid['notes']}\n"
                briefing += "\n"
        elif inputs['operation'] == 'departure':
            briefing += "## 🛫 Standard Instrument Departures (SIDs)\n"
            briefing += "- No SIDs available or no SID database for this airport\n"
            briefing += "- Expect vectors or contact ATC for departure instructions\n\n"
        
        # Add CAPS basic information for departures (emergency briefing moved after Decision point)
        if inputs['operation'] == 'departure' and caps_data:
            briefing += "## 🪂 CAPS (Cirrus Airframe Parachute System)\n"
            briefing += f"- **Minimum deployment**: {caps_data['minimum_msl']} ft MSL ({caps_data['minimum_agl']} ft AGL)\n"
            briefing += f"- **Recommended deployment**: {caps_data['recommended_msl']} ft MSL ({caps_data['recommended_agl']} ft AGL)\n"
            briefing += f"- **Pattern altitude**: {caps_data['pattern_altitude']} ft MSL (CAPS available)\n"
            briefing += f"- **Density altitude impact**: {caps_data['density_altitude_impact']}\n"
            
            if 'departure_specific' in caps_data:
                dep_data = caps_data['departure_specific']
                briefing += f"- **Departure considerations**:\n"
                for point in dep_data['departure_brief']:
                    briefing += f"  - {point}\n"
            briefing += "\n"
        
        # Add enhanced takeoff briefing flavor text for departures
        if inputs['operation'] == 'departure' and flavor_text_data:
            briefing += self.flavor_text_manager.format_takeoff_briefing_text(flavor_text_data)
        
        briefing += "## Weather\n"
        briefing += "- **Temperature**: " + str(weather_data['temp_c']) + "°C (" + str(int(temp_f)) + "°F)\n"
        briefing += "- **Altimeter**: " + str(weather_data['altimeter']) + " inHg\n"
        briefing += "- **Pressure altitude**: " + str(results['pressure_altitude']) + " ft\n"
        briefing += "- **Density altitude**: " + str(results['density_altitude']) + " ft (" + str(da_vs_pa) + " vs PA)\n"
        briefing += "- **Wind**: " + str(weather_data['wind_dir']) + "°/" + str(weather_data['wind_speed']) + " kt\n"
        briefing += "  - " + wind_text + ", " + str(wind_comp['crosswind']) + " kt " + wind_comp['crosswind_direction'] + " crosswind\n"
        
        # Add Landing Ground Roll Calculation for arrival operations right after weather
        if inputs['operation'] == 'arrival':
            briefing += "\n**Landing Ground Roll Calculation:**\n"
            briefing += "- Pressure altitude: " + str(results['pressure_altitude']) + " ft\n"
            briefing += "- Temperature: " + str(weather_data['temp_c']) + "°C\n"
            briefing += "- Interpolated from POH performance tables\n"
            briefing += "- Result: " + str(int(results['landing']['ground_roll_ft'])) + " ft ground roll\n"
        
        if wind_comp['is_tailwind'] and abs(wind_comp['headwind']) > 5:
            briefing += "  - ⚠️ **TAILWIND WARNING**: " + str(abs(wind_comp['headwind'])) + " kt tailwind component\n"
        
        briefing += "\n"
        
        if inputs['operation'] == 'departure':
            briefing += "## Performance (3600 lb, 50% flaps)\n"
            briefing += "**Takeoff Performance**\n"
            briefing += "- Ground roll: " + str(int(results['takeoff']['ground_roll_ft'])) + " ft\n"
            briefing += "- Over 50 ft obstacle: " + str(int(results['takeoff']['total_distance_ft'])) + " ft\n"
            briefing += "- Runway available: " + str(airport_data['runway_length_ft']) + " ft\n"
            briefing += "- **Margin**: " + str(int(results['takeoff_margin'])) + " ft\n\n"
            
            if 'climb_gradients' in results:
                climb_data = results['climb_gradients']
                briefing += "**Climb Performance**\n"
                
                briefing += "- 91 KIAS: " + str(climb_data['tas_91']) + " KTAS, " + str(climb_data['gs_91']) + " kt GS\n"
                if climb_data['gradient_91']:
                    briefing += "  - Aircraft gradient capability: " + str(int(climb_data['gradient_91'])) + " ft/NM\n"
                else:
                    briefing += "  - Gradient data: Not available\n"
                    
                briefing += "- 120 KIAS: " + str(climb_data['tas_120']) + " KTAS, " + str(climb_data['gs_120']) + " kt GS\n"
                if climb_data['gradient_120']:
                    briefing += "  - Aircraft gradient capability: " + str(int(climb_data['gradient_120'])) + " ft/NM\n"
                else:
                    briefing += "  - Gradient data: Not available\n"
                briefing += "\n"
                
                # Add enhanced SID requirements section with speed-specific compliance
                if results.get('sid_requirement'):
                    sid_name = inputs.get('sid_name', 'SID')
                    sid_req = results['sid_requirement']
                    sid_compliance = results.get('sid_compliance')
                    sid_margin = results.get('sid_margin', 0)
                    sid_speed_preference = results.get('sid_speed_preference', 'unknown')
                    compliance_speed = results.get('sid_compliance_speed', 'unknown')
                    aircraft_91 = results.get('aircraft_gradient_91', 0)
                    aircraft_120 = results.get('aircraft_gradient_120', 0)
                    
                    briefing += "**SID Climb Requirements**\n"
                    
                    # Add initial altitude if available
                    if inputs.get('sid_initial_altitude'):
                        briefing += f"- **{sid_name} Initial Altitude**: {inputs['sid_initial_altitude']} ft MSL\n"
                    
                    # Handle different types of SID requirements
                    if isinstance(sid_req, (int, float)):
                        # Numeric SID requirement with enhanced speed-specific messaging
                        req_gradient = int(sid_req)
                        
                        if sid_compliance:
                            if sid_speed_preference == 'preferred':
                                briefing += f"- **{sid_name} Requirement**: {req_gradient} ft/NM (✅ COMPLIANT at 120 KIAS)\n"
                                briefing += f"- **Compliance**: PREFERRED SPEED - Use 120 KIAS for comfortable margin\n"
                                if aircraft_120:
                                    margin_120 = aircraft_120 - req_gradient
                                    briefing += f"- **120 KIAS Margin**: {int(margin_120)} ft/NM above requirement\n"
                            elif sid_speed_preference == 'aggressive_required':
                                briefing += f"- **{sid_name} Requirement**: {req_gradient} ft/NM (✅ COMPLIANT at 91 KIAS ONLY)\n"
                                briefing += f"- **⚠️ AGGRESSIVE CLIMB REQUIRED**: Must use 91 KIAS to meet SID requirement\n"
                                briefing += f"- **⚠️ CAUTION**: Steep climb angle - maintain airspeed discipline\n"
                                if aircraft_91:
                                    margin_91 = aircraft_91 - req_gradient
                                    briefing += f"- **91 KIAS Margin**: {int(margin_91)} ft/NM above requirement (tight margin)\n"
                                if aircraft_120:
                                    deficit_120 = req_gradient - aircraft_120
                                    briefing += f"- **120 KIAS Deficit**: {int(deficit_120)} ft/NM below requirement (insufficient)\n"
                        else:
                            briefing += f"- **{sid_name} Requirement**: {req_gradient} ft/NM (❌ NON-COMPLIANT)\n"
                            briefing += f"- **⚠️ SID CANNOT BE FLOWN**: Aircraft performance insufficient at any speed\n"
                            if aircraft_120:
                                deficit_120 = req_gradient - aircraft_120
                                briefing += f"- **120 KIAS Deficit**: {int(deficit_120)} ft/NM below requirement\n"
                            if aircraft_91:
                                deficit_91 = req_gradient - aircraft_91
                                briefing += f"- **91 KIAS Deficit**: {int(deficit_91)} ft/NM below requirement\n"
                    elif isinstance(sid_req, dict):
                        # Dictionary SID requirement (enhanced format with speed-specific compliance)
                        if sid_req.get('climb_gradient'):
                            # We have a numeric gradient requirement
                            gradient = sid_req['climb_gradient']
                            is_standard = sid_req.get('is_standard', False)
                            gradient_source = " (FAA Standard)" if is_standard else " (Specific to SID)"
                            
                            # Add initial altitude if available
                            if inputs.get('sid_initial_altitude'):
                                briefing += f"- **{sid_name} Initial Altitude**: {inputs['sid_initial_altitude']} ft MSL\n"
                            
                            briefing += f"- **{sid_name} Requirement**: {gradient} ft/NM{gradient_source}\n"
                            
                            # Enhanced speed-specific compliance status
                            if sid_compliance:
                                if sid_speed_preference == 'preferred':
                                    briefing += f"- **Compliance**: ✅ COMPLIANT at 120 KIAS (PREFERRED SPEED)\n"
                                    if aircraft_120:
                                        margin_120 = aircraft_120 - gradient
                                        briefing += f"- **120 KIAS Margin**: {int(margin_120)} ft/NM above requirement\n"
                                elif sid_speed_preference == 'aggressive_required':
                                    briefing += f"- **Compliance**: ✅ COMPLIANT at 91 KIAS ONLY\n"
                                    briefing += f"- **⚠️ AGGRESSIVE CLIMB REQUIRED**: Must use 91 KIAS to meet SID requirement\n"
                                    if aircraft_91:
                                        margin_91 = aircraft_91 - gradient
                                        briefing += f"- **91 KIAS Margin**: {int(margin_91)} ft/NM above requirement\n"
                            else:
                                briefing += f"- **Compliance**: ❌ NON-COMPLIANT at any speed\n"
                                if aircraft_120:
                                    deficit_120 = gradient - aircraft_120
                                    briefing += f"- **120 KIAS Deficit**: {int(deficit_120)} ft/NM below requirement\n"
                                if aircraft_91:
                                    deficit_91 = gradient - aircraft_91
                                    briefing += f"- **91 KIAS Deficit**: {int(deficit_91)} ft/NM below requirement\n"
                            
                            if is_standard:
                                briefing += f"- **Note**: Standard climb gradient applied - verify actual SID requirements\n"
                        else:
                            # No numeric gradient available
                            briefing += f"- **{sid_name}**: {sid_req.get('message', 'Found')}\n"
                            briefing += f"- **Status**: {sid_req.get('guidance', 'Manual verification required')}\n"
                            briefing += f"- **⚠️ Manual Check Required**: Verify climb gradient requirement from chart\n"
                        
                        # Add PDF link if available
                        if sid_req.get('pdf_url'):
                            pdf_url = sid_req['pdf_url']
                            if pdf_url.startswith('/'):
                                pdf_url = f"https://skyvector.com{pdf_url}"
                            briefing += f"- **Chart**: {pdf_url}\n"
                    else:
                        # String SID requirement (legacy format)
                        briefing += f"- **{sid_name}**: {str(sid_req)}\n"
                        briefing += f"- **Status**: Manual verification required\n"
                        briefing += f"- **⚠️ Action Required**: Verify climb gradient and speed requirements from chart\n"
                    briefing += "\n"
            
            # Add V-speeds for takeoff
            if 'v_speeds' in results:
                v_data = results['v_speeds']
                briefing += "**V-speeds (Takeoff)**\n"
                briefing += f"- **Vr (Rotate)**: {v_data['vr_kias']} KIAS\n"
                briefing += f"- {v_data['takeoff_notes']}\n\n"
        else:
            briefing += "## Performance (3600 lb, 100% flaps)\n"
            briefing += "**Landing Performance**\n"
            briefing += "- Ground roll: " + str(int(results['landing']['ground_roll_ft'])) + " ft\n"
            briefing += "- Total distance: " + str(int(results['landing']['total_distance_ft'])) + " ft\n"
            briefing += "- Runway available: " + str(airport_data['runway_length_ft']) + " ft\n"
            briefing += "- **Margin**: " + str(int(results['landing_margin'])) + " ft\n\n"
            
            # Add go-around climb performance for arrivals
            # Use the same calculator methods used for departures since climb performance is identical
            go_around_results = self.calculator.calculate_climb_gradients(
                results['pressure_altitude'], weather_data['temp_c'], results['density_altitude'],
                results['wind_components']['headwind']
            )
            if go_around_results:
                briefing += "**Go-Around Climb Performance**\n"
                briefing += f"- **120 KIAS**: {go_around_results['tas_120']} KTAS, {go_around_results['gs_120']} kt GS\n"
                if go_around_results['gradient_120']:
                    briefing += f"  - Available gradient: {int(go_around_results['gradient_120'])} ft/NM\n"
                else:
                    briefing += f"  - Gradient data: Not available\n"
                briefing += f"- **Note**: Performance for missed approach or go-around maneuver\n"
                briefing += f"- **⚠️ Balked Landing**: Not covered by tool - requires pilot evaluation\n\n"
        
        briefing += "## Decision: **" + decision + "**\n"
        if decision == "NO-GO":
            reasons = []
            if inputs['operation'] == 'departure':
                if results['takeoff_margin'] <= 500:
                    reasons.append("Insufficient runway margin")
                # Only add SID non-compliance if we have a definitive False result (not None)
                sid_compliance = results.get('sid_compliance', True)
                if sid_compliance is False:  # Explicitly False, not None
                    sid_name = inputs.get('sid_name', 'SID')
                    reasons.append(f"Cannot meet {sid_name} climb requirement")
            else:
                if results['landing_margin'] <= 500:
                    reasons.append("Insufficient runway margin")
            
            briefing += "❌ " + ", ".join(reasons) + "\n"
        else:
            briefing += "✅ All margins adequate for safe operation\n"
        
        # Add V-speeds section after decision for landing operations
        if inputs['operation'] == 'arrival' and 'v_speeds' in results:
            v_data = results['v_speeds']
            briefing += "\n**V-speeds (Approach & Landing) - Boldmethod Three-Stage**\n"
            briefing += f"- **Final Approach**: {v_data['final_approach_kias']} KIAS ({v_data['config_notes']})\n"
            briefing += f"- **Threshold Crossing**: {v_data['threshold_crossing_kias']} KIAS (begin power reduction)\n"
            briefing += f"- **Touchdown Target**: {v_data['touchdown_target_kias']} KIAS (just above stall)\n"
            
            if v_data['gust_correction_applied'] > 0:
                briefing += f"- **Gust Correction**: +{v_data['gust_correction_applied']} kt added to base speeds\n"
            
            if v_data['use_partial_flaps_for_crosswind']:
                briefing += f"- **⚠️ Crosswind Config**: 50% flaps recommended (est. {v_data['estimated_crosswind_kt']} kt crosswind)\n"
            
            briefing += f"- **Speed Control**: Progressive deceleration during approach phase\n"
            briefing += f"- **Weight**: {v_data['weight_consideration']}\n\n"
        
        # Add CAPS emergency briefing for departures after decision point
        if inputs['operation'] == 'departure' and caps_data and decision == "GO":
            briefing += "\n## 🚨 Takeoff Emergency Brief\n"
            for point in caps_data['emergency_brief']:
                briefing += f"- {point}\n"
            briefing += "\n"
        
        # Add Calculation Details for takeoff operations only (landing already included above)
        if inputs['operation'] == 'departure':
            briefing += "\n## Calculation Details\n"
            briefing += "**Takeoff Ground Roll Calculation:**\n"
            briefing += "- Pressure altitude: " + str(results['pressure_altitude']) + " ft\n"
            briefing += "- Temperature: " + str(weather_data['temp_c']) + "°C\n"
            briefing += "- Interpolated from POH performance tables\n"
            briefing += "- Result: " + str(int(results['takeoff']['ground_roll_ft'])) + " ft ground roll\n"
            
        briefing += "\n---\n"
        
        return briefing

    def _format_phased_takeoff_briefing(self, inputs, weather_data, airport_data, results, sid_data=None, caps_data=None, flavor_text_data=None, chatgpt_analysis=None):
        """Format takeoff briefing in three practical phases for cockpit workflow"""
        
        temp_f = (weather_data['temp_c'] * 9/5) + 32
        wind_comp = results['wind_components']
        
        # Determine wind description for Phase 3 
        if wind_comp['is_tailwind']:
            wind_text = f"{abs(wind_comp['headwind'])} kt tailwind"
        else:
            wind_text = f"{wind_comp['headwind']} kt headwind"
        
        decision = "GO" if results.get('takeoff_margin', 0) > 500 and results.get('sid_compliance', True) != False else "NO-GO"
        
        briefing = ""
        
        # =============================================================================
        # PHASE 1: POST-IFR CLEARANCE (Numbers entered in Garmin)
        # =============================================================================
        briefing += "#################### 📋 PHASE 1: POST-IFR CLEARANCE\n"
        #briefing += "*Read after IFR clearance received and numbers entered in Garmin*\n\n"
        
        # Garmin Pilot section
        if inputs.get('briefing_data'):
            flight_data = inputs['briefing_data']
            briefing += "**📱 Garmin Pilot Flight**\n"
            briefing += f"- **Route**: {flight_data.get('departure', '')} → {flight_data.get('arrival', '')}\n"
            if flight_data.get('route_waypoints'):
                waypoints = " → ".join([wp['name'] for wp in flight_data['route_waypoints'][:4]])
                if len(flight_data['route_waypoints']) > 4:
                    waypoints += " → ..."
                briefing += f"- **Waypoints**: {waypoints}\n"
            briefing += "\n"
        
        # Airport & Runway section
        briefing += "**🛫 Airport & Runway**\n"
        briefing += f"- **Airport**: {airport_data['icao']} {airport_data['name']}\n"
        briefing += f"- **Runway**: {inputs['runway']} ({airport_data['runway_length_ft']} ft)\n"
        briefing += f"- **Runway Heading**: {airport_data['runway_heading']}° magnetic\n"
        #briefing += f"- **Surface**: {airport_data['surface']}\n\n"
        
        # SID section (enhanced with compliance)
        if results.get('sid_requirement'):
            sid_name = inputs.get('sid_name', 'SID')
            sid_req = results['sid_requirement']
            sid_compliance = results.get('sid_compliance')
            sid_speed_preference = results.get('sid_speed_preference', 'unknown')
            
            briefing += "**🛫 SID Departure**\n"
            if inputs.get('sid_initial_altitude'):
                briefing += f"- **{sid_name} Initial Altitude**: {inputs['sid_initial_altitude']} ft MSL\n"
            
            if isinstance(sid_req, (int, float)):
                req_gradient = int(sid_req)
                if sid_compliance:
                    if sid_speed_preference == 'preferred':
                        briefing += f"- **{sid_name}**: {req_gradient} ft/NM (✅ COMPLIANT at 120 KIAS)\n"
                    elif sid_speed_preference == 'aggressive_required':
                        briefing += f"- **{sid_name}**: {req_gradient} ft/NM (⚠️ REQUIRES 91 KIAS)\n"
                        briefing += f"- **CAUTION**: Aggressive climb required for SID compliance\n"
                else:
                    briefing += f"- **{sid_name}**: {req_gradient} ft/NM (❌ NON-COMPLIANT)\n"
            briefing += "\n"
        else:
            briefing += "**🛫 SID Departure**\n"
            briefing += "- No SID planned\n\n"
        
        # Climb Performance & Requirements
        if 'climb_gradients' in results:
            climb_data = results['climb_gradients']
            briefing += "**📈 Climb Performance**\n"
            briefing += f"- **91 KIAS**: {climb_data['tas_91']} KTAS, {climb_data['gs_91']} kt GS"
            if climb_data['gradient_91']:
                briefing += f", {int(climb_data['gradient_91'])} ft/NM\n"
            else:
                briefing += ", gradient N/A\n"
            briefing += f"- **120 KIAS**: {climb_data['tas_120']} KTAS, {climb_data['gs_120']} kt GS"
            if climb_data['gradient_120']:
                briefing += f", {int(climb_data['gradient_120'])} ft/NM\n"
            else:
                briefing += ", gradient N/A\n"
            briefing += "\n"
        
        # Decision section
        briefing += f"**✅ DECISION: {decision}**\n"
        if decision == "NO-GO":
            reasons = []
            if results.get('takeoff_margin', 0) <= 500:
                reasons.append("Insufficient runway margin")
            sid_compliance = results.get('sid_compliance', True)
            if sid_compliance is False:
                sid_name = inputs.get('sid_name', 'SID')
                reasons.append(f"Cannot meet {sid_name} climb requirement")
            briefing += f"- **Reasons**: {', '.join(reasons)}\n"
        else:
            briefing += f"- **Takeoff Margin**: {int(results['takeoff_margin'])} ft\n"
            if results.get('sid_compliance') == True:
                briefing += f"- **SID Compliance**: ✅ Confirmed\n"
        briefing += "\n"
        
        # =============================================================================
        # PHASE 2: RUNUP AREA
        # =============================================================================
        briefing += "#################### 🔧 PHASE 2: RUNUP AREA\n"
        #briefing += "*Read during runup checklist*\n\n"
        
        # Takeoff Emergency Briefing
        if caps_data and decision == "GO":
            briefing += "**🚨 Takeoff Emergency Brief**\n"
            briefing += f"- **CAPS minimum deployment**: {caps_data['minimum_msl']} ft MSL ({caps_data['minimum_agl']} ft AGL - POH limit)\n"
            
            # Calculate recommended deployment altitude (1000 ft AGL)
            airport_elevation = airport_data['elevation_ft']
            caps_recommended_msl = airport_elevation + 1000
            caps_pattern_msl = airport_elevation + 1000  # Pattern altitude typically 1000 ft AGL
            
            briefing += f"- **CAPS recommended deployment**: {caps_recommended_msl} ft MSL (1000 ft AGL)\n"
            briefing += f"- **Pattern altitude CAPS available**: {caps_pattern_msl} ft MSL\n"
            briefing += "- **Emergency procedure**: CAPS - PULL - COMMUNICATE - PREPARE\n"
            briefing += "- **Below 600 ft AGL**: Fly the airplane - CAPS deployment not recommended (POH limit)\n"
            briefing += "\n"
        
        # Performance section
        briefing += "**📊 Takeoff Performance (3600 lb, 50% flaps)**\n"
        briefing += f"- **Ground Roll**: {int(results['takeoff']['ground_roll_ft'])} ft\n"
        briefing += f"- **Over 50 ft**: {int(results['takeoff']['total_distance_ft'])} ft\n"
        briefing += f"- **Runway Available**: {airport_data['runway_length_ft']} ft\n"
        briefing += f"- **Margin**: {int(results['takeoff_margin'])} ft\n\n"
        
        # V-speeds
        if 'v_speeds' in results:
            v_data = results['v_speeds']
            briefing += "**🎯 V-speeds (Takeoff)**\n"
            briefing += f"- **Vr (Rotate)**: {v_data['vr_kias']} KIAS\n"
            briefing += f"- {v_data['takeoff_notes']}\n\n"
        
        # =============================================================================
        # PHASE 3: HOLDING SHORT
        # =============================================================================
        briefing += "#################### ✈️ PHASE 3: HOLDING SHORT\n"
        #briefing += "*Read while holding short before takeoff clearance*\n\n"
        
        # Confirm runway
        #briefing += "**🛫 Runway Confirmation**\n"
        briefing += f"- **Runway**: {inputs['runway']} (confirm visually)\n"
        briefing += f"- **Heading**: {airport_data['runway_heading']}° magnetic\n"
        
        # Wind summary
        #briefing += "**💨 Wind Summary**\n"
        briefing += f"- **Wind**: {wind_text}\n"
        briefing += f"- **Crosswind**: {wind_comp['crosswind']} kt {wind_comp['crosswind_direction']}\n"
        if wind_comp['is_tailwind'] and abs(wind_comp['headwind']) > 5:
            briefing += f"- **⚠️ TAILWIND WARNING**: {abs(wind_comp['headwind'])} kt tailwind component\n"
        briefing += "\n"
        
        # Expected ground roll
        #briefing += "**📏 Expected Performance**\n"
        briefing += f"- **Expected Ground Roll**: {int(results['takeoff']['ground_roll_ft'])} ft\n\n"
        
        # Emergency brief reminder
        if caps_data and decision == "GO":
            briefing += "**🚨 Emergency Brief Reminder**\n"
            # Just show the key points from Phase 1 emergency brief
            p1 = flavor_text_data['phase1'] if flavor_text_data else None
            if p1:
                briefing += f"- **At {p1['decision_point']} ft**: {p1['action']} if before 60 KIAS\n"
            else:
                # Fallback if no flavor text
                briefing += f"- **Below rotation**: Abort, maximum braking, runway available\n"
            briefing += f"- **After rotation**: CAPS available at {caps_data['minimum_msl']} ft MSL\n"
        
        return briefing

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution with enhanced Garmin Pilot integration and automatic runway data"""
    self._info("🛩️ SR22T Briefing Tool v31.0 - WORKFLOW EDITION")
    self._info("✨ Sequential Workflow + Weather Analysis + Garmin Pilot Integration")
    self._info("Running on Pythonista iOS")
    
    briefing_tool = BriefingGenerator()
    
    while True:
        inputs = briefing_tool.get_user_inputs()
        if not inputs:
            break
            
        self._info("\n🔄 Generating briefing...")
        briefing = briefing_tool.generate_briefing(inputs)
        
        self._info("\n" + "="*60)
        self._info(briefing)
        self._info("="*60)
        
        if self._prompt("\n🔄 Another briefing? (y/n): ").lower() != 'y':
            break
            
    self._info("\n✈️ Flight safe!")

if __name__ == "__main__":
    main()
