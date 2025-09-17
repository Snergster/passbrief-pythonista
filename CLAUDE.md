# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an SR22T departure/arrival briefing tool designed for Pythonista iOS. The application provides comprehensive flight performance calculations, weather integration, Garmin Pilot flight briefing parsing, and climb gradient analysis for Cirrus SR22T aircraft operations.

## Development Environment

- **Python Version**: Python 3.12.3 is available
- **Primary Target**: Pythonista iOS environment
- **No Dependency Management**: No requirements.txt, pyproject.toml, or other dependency files present
- **Dependencies**: `requests`, `json`, `math`, `numpy`, `os`, `glob`, `xml.etree.ElementTree`, `datetime`

## Running the Application

### Current Version (Recommended)
```bash
python3 sr22t_briefing_v31.py
```

### Version History
- **v31**: Current - **WORKFLOW EDITION** with complete feature implementation
  - All roadmap features implemented: SID, CAPS, FlavorText, ChatGPT analysis
  - Sequential workflow system with enhanced user experience
  - Complete Garmin Pilot integration replacing ForeFlight
  - Professional briefing format with comprehensive safety checks
  - Advanced route analysis and weather integration (4021+ lines)
- **v30**: Previous - Magnetic heading implementation with wind warnings
- **v29**: Previous - Magnetic heading implementation with WMM2025 integration
- **v27**: Reference - Original complete implementation

## File Versioning System

**For Pythonista iOS compatibility, we use a clear versioning scheme:**

- **Major Changes** (substantial features): Increment number (v30 → v31)
- **Minor Changes** (small fixes/tweaks): Add letters (v31 → v31A, v31B, etc.)

This makes it easy to track which version you're running on your iOS device.

## ⚠️ SAFETY-CRITICAL DATA PROTOCOL

**MANDATORY for all aviation software development:**

1. **Never approximate safety-critical performance data** - Always ask user for real POH/certified data before creating fallbacks
2. **If approximations are unavoidable, make them pessimistic/conservative, never optimistic** - Optimistic performance estimates can kill pilots
3. **Always ask explicitly**: "Do you have the actual POH data for [specific chart/table]?" before proceeding with any approximation
4. **Document all data sources and assumptions explicitly** in code comments and user output
5. **Flag any non-certified data clearly** in all output with warnings like "(approximated)" or "(not POH data)"
6. **Wait for user confirmation** before using any approximated aviation performance data
7. **Remember: Wrong data is worse than no data** in safety-critical aviation calculations

**Aviation Context**: Performance approximations that are too optimistic can result in:
- Obstacle strikes during departure/climb
- Runway overruns on landing
- Inadequate fuel planning
- Loss of aircraft and life

**User Authority**: The user is the pilot and safety authority. Always defer to their aviation knowledge and POH data access.

## Code Architecture (Complete v31 Analysis)

The application follows a modular class-based architecture with 10 main classes:

### Core Components

#### 1. **EMBEDDED_SR22T_PERFORMANCE** (Lines 20-150)
Complete performance tables for SR22T aircraft including:
- **Landing distances** at 3 pressure altitudes × 3 temperatures
- **Takeoff distances** at 3 pressure altitudes × 4 temperatures  
- **Takeoff climb gradients at 91 KIAS** - Critical for departure planning
- **Enroute climb gradients at 120 KIAS** - Used for obstacle clearance

#### 2. **Config** (Lines 156-161)
Application configuration constants:
- `METAR_MAX_AGE_MINUTES = 70`
- `PRESSURE_ALTITUDE_ROUND = 10`
- `DENSITY_ALTITUDE_ROUND = 50`
- `PERFORMANCE_DISTANCE_ROUND = 50`
- `FOREFLIGHT_FILE_MAX_AGE_HOURS = 24`

#### 3. **GarminPilotBriefingManager** (Lines 478-879)
Advanced Garmin Pilot integration with:
- **PDF flight briefing parsing**: Comprehensive flight plan extraction
- **Multi-format support**: Briefings and navigation logs
- **Comprehensive file discovery**: 8+ search paths across iOS/Pythonista
- **Diagnostic mode**: Detailed file system exploration
- **Route extraction**: Departure/arrival identification with waypoints

#### 4. **WeatherManager** (Lines 880-981)
METAR weather integration featuring:
- **NOAA Aviation Weather API** integration
- **Automatic unit conversion**: hPa to inHg pressure conversion
- **Age validation**: Rejects stale METAR data
- **Manual fallback**: Interactive weather input

#### 5. **PerformanceCalculator** (Lines 563-764)
**Core performance engine** with critical calculations:
- `calculate_pressure_altitude()` - Standard pressure altitude
- `calculate_density_altitude()` - Performance-affecting density altitude  
- `calculate_wind_components()` - Headwind/crosswind analysis
- **`calculate_climb_gradients()`** - **KEY FEATURE**: TAS/ground speed and climb gradients for 91/120 KIAS
- `interpolate_performance()` - Takeoff/landing distance interpolation
- Advanced interpolation algorithms for temperature and pressure altitude

#### 6. **AirportManager** (Lines 1150-1303)
Comprehensive airport data management:
- **OurAirports integration**: Automatic airport/runway data fetching
- **CSV parsing**: Real-time airport and runway database queries
- **Runway specifications**: Length, heading, surface information
- **Fallback systems**: Manual input when online data unavailable

#### 7. **BriefingGenerator** (Lines 770-1090)
**Main application orchestrator** with:
- **Multi-modal input workflows**: ForeFlight integration, manual reference, full manual
- **Performance calculation orchestration**: Coordinates all calculations
- **Rich briefing formatting**: Markdown-style output with comprehensive data
- **Interactive UI**: Loop-based interface with multiple briefing capability

### Main Execution Flow (Lines 1096-1122)
```python
def main():
    """Main execution with enhanced ForeFlight integration"""
    briefing_tool = BriefingGenerator()
    
    while True:
        inputs = briefing_tool.get_user_inputs()
        if not inputs:
            break
            
        briefing = briefing_tool.generate_briefing(inputs)
        print(briefing)
        
        if input("Another briefing? (y/n): ").lower() != 'y':
            break
```

## File Structure

```
sr22pythonista/
├── sr22t_briefing_v30.py    # CURRENT - MAGNETIC HEADING EDITION (1490+ lines)
├── sr22t_briefing_v29.py    # Previous - Complete patched version (1305 lines)
├── CLAUDE.md                # Development documentation  
├── .claude/
│   └── settings.local.json  # Claude Code local settings
└── sr22t_briefing_v29.py:Zone.Identifier  # Windows zone identifier
```

## Critical Components Missing from v29

### 1. Performance Calculation Engine
v29 is missing the entire `PerformanceCalculator` class methods:
- `calculate_climb_gradients()` - **Critical for departure briefings**
- `_interpolate_climb_gradient()` - Core interpolation algorithm
- `_interpolate_gradient_temperature()` - Temperature interpolation
- All wind component calculations

### 2. Complete Airport Management
Entire `AirportManager` class missing from v29:
- Automatic airport data fetching (lines 1150-1303)
- Runway database integration
- All manual input fallbacks

### 3. Briefing Generation System
`BriefingGenerator` class completely missing from v29:
- User input workflows
- Performance calculation orchestration  
- Briefing formatting and output
- Interactive UI system

### 4. Main Execution
No `main()` function or `if __name__ == "__main__"` block in v29.

## Key Development Commands

### Testing the Application
```bash
# Run complete version
python3 sr22t_briefing_v27.py

# Test individual components (requires Python imports)
python3 -c "from sr22t_briefing_v27 import PerformanceCalculator; calc = PerformanceCalculator(); print(calc.calculate_density_altitude(5000, 25, 1000))"
```

### Common Development Tasks

#### Adding New Performance Data
- Modify `EMBEDDED_SR22T_PERFORMANCE` dictionary (lines 20-150)
- Update interpolation functions in `PerformanceCalculator` if needed

#### Extending ForeFlight Integration  
- Add new file format parsers in `ForeFlightExportManager`
- Update `supported_formats` list and add corresponding `_parse_*()` method

#### Airport Database Updates
- Modify `AirportManager._fetch_*()` methods for new data sources
- Update CSV parsing logic for database schema changes

## API Integrations

- **NOAA Aviation Weather**: `https://aviationweather.gov/api/data/metar`
- **OurAirports Database**: 
  - `https://davidmegginson.github.io/ourairports-data/airports.csv`
  - `https://davidmegginson.github.io/ourairports-data/runways.csv`

## Critical Aviation Safety Evolution (v29→v30)

**⚠️ MAGNETIC HEADING SYSTEM PERFECTED**

v30 represents the culmination of magnetic heading accuracy improvements:

- **Issue**: OurAirports database provides TRUE headings, but METAR wind data is MAGNETIC
- **Risk**: Incorrect wind component calculations using mixed reference systems  
- **Fix**: Automatic magnetic variation correction applied to runway headings
- **Result**: All headings now consistently use MAGNETIC reference (as required for aviation)

### v30 Magnetic Heading System Features:
- **Three-Tier Accuracy System**: pygeomag (best) → manual input (good) → regional approximation (acceptable)
- **User-Friendly Prompts**: Direct magnetic heading input with intelligent regional defaults
- **Wind-Based Accuracy Warnings**: Automatic warnings for 20+ kt winds or 10+ kt crosswinds
- **Smart Default Generation**: Regional approximation provides sensible defaults for quick ops
- **Practical Implementation**: Optimized for real-world flight operations vs theoretical perfection
- **Enhanced Safety**: Clear warnings when accuracy matters most (high wind conditions)

### v30 User Experience Improvements:
1. **Simplified Interface**: Direct "Runway XX magnetic heading [default]°: " prompts
2. **Smart Defaults**: Regional approximation provides quick defaults for low-wind operations  
3. **Conditional Warnings**: Accuracy alerts only when wind conditions require precision
4. **Operational Focus**: Designed for practical flight planning workflow efficiency

### Before/After Example:
```
Before: Runway 09 heading 090° (true) + Wind 120°@15kt (magnetic) = WRONG calculation
After:  Runway 09 heading 102° (magnetic) + Wind 120°@15kt (magnetic) = CORRECT calculation
```

## v30 Development Notes

- **Current Production Version**: v30 includes all features plus perfected magnetic heading system
- **Comprehensive Documentation**: Updated docstring with complete feature overview and roadmap
- **Practical Implementation**: User-friendly magnetic heading interface balances accuracy with efficiency
- **iOS-optimized**: File system paths and UI designed for Pythonista
- **Offline-capable**: Comprehensive manual input fallbacks
- **Data-driven**: Performance calculations based on embedded tables
- **Aviation safety**: Three-tier magnetic heading accuracy system with wind-based warnings
- **User-friendly**: Extensive diagnostic output and error handling
- **Aviation-focused**: Real-world flight planning workflow integration

## Planned Features (Roadmap)

1. **SID Departure Check**: Automated Standard Instrument Departure procedure validation
2. **CAPS Altitudes**: Integration of Cirrus Airframe Parachute System altitudes into takeoff briefings
3. **Flavor Text**: Enhanced takeoff briefing with descriptive operational guidance
4. **ChatGPT Integration**: AI-powered ForeFlight flight plan analysis and advisory system

---

# COLLABORATION GUIDE

## Quick Ops Card (copy-paste ready)

```
[Mode] challenge → recommend → implement
[Env] OS: Windows/Ubuntu | Python: 3.12 | Internet: on by default
[Project] Root: ~/project | Layout: src/, tests/, scripts/, data/, artifacts/
[Tools] uv (or pip+venv), ruff, pytest, pyright (or mypy)
[Defaults] JSON config; local-first; no servers; deterministic CLI
[Formatting] Python uses spaces (PEP 8). Tabs acceptable elsewhere.
[Logging] APP_LOG = full | critical | silent  (default: critical)
[Outputs] Code + tests + README updates + sample run; save to ./artifacts
[Stop/Go] "go/send it/ship it/green light" = implement; "hold/pause/abort" = stop
[Timebox] Research ≤ 10 min; 3 failed attempts → ask with options
[Security] Never paste secrets; use .env + redaction in logs
```

## Confidence & Plan Header (prepend to any non-trivial answer)

```
Confidence: High/Medium/Low
Assumptions: [1–3 bullets]
Risks/Unknowns: [1–3 bullets]
Plan: [1–3 steps; files to touch; commands to run]
Artifacts: [files to create/update in ./artifacts or project tree]
```

**Rule:** if confidence ≥ 80% and tradeoffs are minor, provide one recommendation. Otherwise provide **2–3 options** with a one-line tradeoff each and mark your preferred option.

## Definition of Done (assistant self-check)

- [ ] Code compiles/runs locally; commands documented in README usage section
- [ ] Tests included and passing: happy path + primary error path
- [ ] Test commands shown (e.g., `pytest -q`) and output (or expected output) provided
- [ ] Logging toggle verified (APP_LOG values); noisy logs avoided in "silent" mode
- [ ] README updated: install, run, test, config, troubleshooting
- [ ] Sample data and example invocation provided
- [ ] No secrets checked into code or printed in chat
- [ ] Artifacts saved to `./artifacts` with clear filenames
- [ ] Changes scoped to agreed refactor authority (see below)

## Execution Playbook

### 1) Challenge → Recommend → Implement
- Start by sanity-checking requirements, constraints, and edge cases.
- If the plan is sound and you have a "go," implement without re-debate.

### 2) Multiple options policy
- If confidence < 80% or there are material tradeoffs, provide 2–3 options:
  - **Option A (preferred):** short why
  - **Option B:** short why
  - **Option C:** short why
- Then proceed with the chosen option once you see an explicit **go** word.

### 3) Refactoring authority (scope and safety)
- **Default scope:** files you authored plus adjacent modules required to complete the task.
- **May refactor** small utilities for coherence if you also write tests that lock current behavior.
- **Outside scope** or large design changes require explicit approval.
- Always include tests with refactors and note any user-visible changes.

### 4) Tests: assistant writes and (where tools allow) runs them
- The assistant **owns** writing tests for any non-trivial change.
- If execution tools are available, run tests and include the output.
- If not, provide exact commands and expected outputs; request the user to run if needed.
- Prefer `pytest` with a `tests/` tree; include at least one failure-mode test.

### 5) Logging level mechanics
Use an environment variable to control verbosity, with three clear levels:

```python
# logging_setup.py
import os, logging

LEVELS = {
    "full": logging.DEBUG,
    "critical": logging.WARNING,
    "silent": logging.ERROR,
}

def setup_logging():
    level = os.getenv("APP_LOG", "critical").lower()
    logging.basicConfig(
        level=LEVELS.get(level, logging.WARNING),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
```

Usage examples:
```
APP_LOG=full python -m yourapp.cli …
APP_LOG=critical python -m yourapp.cli …   # default
APP_LOG=silent python -m yourapp.cli …
```

### 6) Tabs vs PEP 8
- **Python:** use **spaces** for indentation per PEP 8 to avoid formatter/tooling conflicts.
- **Other languages/files:** tabs are acceptable if the project uses them. Be consistent.

### 7) Silent cleanup rules
Small, non-behavior-changing fixes are allowed without ceremony **only if** tests exist or are added to prove behavior is unchanged:
- Typo fixes, dead imports, minor rename with no API change, docstring improvements.
- Any risk of behavior change converts this to a refactor that must ship with tests and be called out explicitly.

### 8) Error handling and when to ask
- If blocked after 3 concrete attempts or by missing context, stop and propose the smallest set of questions with options you can proceed with immediately.
- Timebox research to 10 minutes unless told otherwise.

### 9) Artifacts & paths
- Write generated outputs to `./artifacts` by default.
- Reference absolute or project-root-relative paths in replies; include checksums for large outputs when helpful.

### 10) Internet access and sources
- Default **on**. If allowed, prefer official docs and primary sources; cite exact versions.
- Approved domains can be whitelisted per project if needed.

### 11) Security & secrets
- Never paste tokens, keys, or PII into chat.
- Use `.env` locally; demonstrate with `python-dotenv` if appropriate.
- Redact sensitive strings in logs and outputs.

## Stop/Go lexicon (case-insensitive)

- **Go words:** `go`, `send it`, `ship it`, `green light`
- **Stop words:** `hold`, `pause`, `abort`, `rethink`

**Rule:** On a **go**, the assistant implements without reopening debate. One-line blocker is allowed if the plan is unsafe or impossible.

---

# USER BACKGROUND & PREFERENCES

## Technical Background
- **Internet Infrastructure**: 25+ years (ISP operations, Cisco router development, network simulation)
- **Python Status**: 5-year gap, last used Python2 - needs gradual Python3 re-introduction
- **Systems**: 15+ years Ubuntu, Git comfortable, command line proficient
- **Aviation**: GA pilot, Cirrus SR22T partial owner - engineering background aids avionics comprehension

## Communication Preferences
- **Level**: Mid-to-high concepts, drill down on demand
- **Style**: Professional peer, challenge ideas, suggest alternatives
- **Documentation**: Inline comments explaining WHY, function I/O, architectural reasoning
- **Analogies**: Use networking/infrastructure or aviation analogies when helpful

## Learning Style
- **Primary Method**: Working examples with comprehensive documentation, then experiment
- **Anti-Pattern**: Don't explain hammer origins when you say "use a hammer"
- **Progression**: Incremental development (steps 2-41 mentality), comfortable with prep work
- **Knowledge Gaps**: Python3 modern practices, web development (not interested)

## Project Approach
- **Focus**: Personal productivity and aviation quality-of-life tools
- **Architecture**: Local-first solutions, not web-based
- **Maintenance**: Will automate anything that becomes annoying
- **Collaboration**: When work claimed complete, it should actually be complete