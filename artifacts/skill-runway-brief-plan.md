# SR22T Runway Brief Skill - Complete Plan

## Executive Summary

**Purpose:** Create a standalone Claude Skill that provides quick takeoff and landing performance briefings for Cirrus SR22T operations at any runway, requiring only basic weather and runway data inputs.

**Value Proposition:**
- **Speed:** 30-second briefing vs 5-minute Python workflow
- **Accessibility:** Works on any device with Claude access (not just iOS Pythonista)
- **Scope:** Focused runway-specific analysis (not full flight planning)
- **Complement:** Adds quick-turn capability without replacing comprehensive tool

**Success Criteria:**
1. Produces accurate performance calculations matching Python tool (±50 ft tolerance)
2. Generates consistent outputs for identical inputs across multiple runs
3. Provides actionable GO/NO-GO guidance with specific safety margins
4. Creates natural passenger briefing scripts
5. Requires <10 inputs and <1 minute setup time

---

## Skill Structure Overview

```
runway-brief.zip
├── skill.md                           # Main skill file (YAML + Workflows)
├── references/
│   ├── sr22t-performance-data.py      # Full embedded performance tables
│   ├── calculation-functions.py       # All calculation methods with tests
│   └── v-speeds-reference.md          # V-speed selection logic explained
└── examples/
    ├── example-takeoff-brief.md       # High DA mountain airport
    ├── example-landing-brief.md       # Gusty crosswind scenario
    └── example-both-operations.md     # Complete round-trip analysis
```

---

## Part 1: YAML Frontmatter

```yaml
---
name: SR22T Runway Brief
description: |
  Quick takeoff and landing performance calculator for Cirrus SR22T at any runway.
  Input current weather (winds, temp, altimeter) and runway data (elevation, heading,
  length) to get performance calculations, approach speeds, safety margins, and
  passenger briefing scripts. Uses embedded POH data for accuracy. Perfect for
  unfamiliar airports, hot day verification, or quick feasibility checks without
  full flight planning tools.
version: 1.0.0
author: PassBrief Project
created: 2025-10-20
updated: 2025-10-20
tags: [aviation, cirrus-sr22t, performance, runway-analysis, takeoff, landing, ga-operations]
pattern_type: workflow
platforms: [claude, chatgpt, gemini]
mvs_criteria:
  recurring: true
  consistent_methodology: true
  complex: true
  high_value: true
estimated_time_saved: "15 min per runway analysis"
complexity: medium
use_cases:
  - Quick runway feasibility check at unfamiliar airports
  - Hot day performance verification before departure/return
  - Backcountry strip safety analysis
  - Landing performance check with updated weather
  - Training scenarios and what-if calculations
  - Diversion airport evaluation during flight
aircraft_specific: Cirrus SR22T (adaptable to other models)
safety_critical: true
requires_poh_data: true
---
```

---

## Part 2: Main Skill File Structure

### Overview Section

```markdown
# SR22T Runway Brief Skill

## What This Skill Does

Provides rapid performance analysis for Cirrus SR22T takeoff and landing operations
at any runway worldwide. Using embedded POH performance data and weather inputs,
generates:

- Pressure and density altitude calculations
- Wind component analysis (headwind/crosswind/tailwind)
- Takeoff distance and runway margin
- Landing distance with flap configuration recommendations
- Approach speeds with gust corrections
- Climb performance (feet per nautical mile)
- CAPS deployment altitudes
- Passenger briefing scripts (departure and arrival)
- GO/NO-GO recommendations with safety notes

## When to Use This Skill

**Use this skill when:**
- Evaluating unfamiliar runway capability
- Checking hot/cold day performance changes
- Analyzing return flight feasibility after weather changes
- Planning backcountry operations
- Training what-if scenarios
- Diverting to alternate airport
- Need quick numbers without full flight planning

**Do NOT use this skill for:**
- Complete flight planning (use full PassBrief Python tool)
- Route weather analysis (no TFR/SIGMET evaluation)
- Fuel planning
- Weight & balance calculations
- Cross-country flight planning

## What You Need Before Starting

**Required Inputs (6 items):**
1. Runway elevation (feet MSL) - from airport chart
2. Current temperature (°C) - from ATIS/AWOS/ASOS
3. Current altimeter (inHg) - from ATIS/AWOS/ASOS
4. Wind direction (degrees magnetic) - from ATIS/AWOS/ASOS
5. Wind speed (knots) - from ATIS/AWOS/ASOS
6. Runway heading (degrees magnetic) - from airport chart
7. Runway length (feet) - from airport chart

**Optional Inputs:**
- Wind gusts (knots) - for approach speed calculations
- Operation type (takeoff/landing/both) - defaults to "both"

**Where to get this data:**
- ATIS/AWOS/ASOS recording: Temperature, altimeter, winds
- Airport chart / ForeFlight / Garmin Pilot: Elevation, runway heading/length
- Visual placard at runway: Often shows elevation and runway dimensions
```

---

### Workflow Section (The Core)

```markdown
## Workflow: Complete Runway Brief

### Step 0: Determine Operation Type

**Prompt user to select:**

**A. Takeoff Brief Only**
- Use when: Departing this airport, don't need landing info
- Outputs: Takeoff performance, climb gradient, CAPS altitudes, departure passenger brief

**B. Landing Brief Only**
- Use when: Arriving at this airport, already departed elsewhere
- Outputs: Landing performance, approach speeds, arrival passenger brief

**C. Both Operations (Default)**
- Use when: Round-trip analysis or complete runway capability assessment
- Outputs: Full takeoff + landing analysis with comparison

**Action:** Proceed with selected workflows (skip Step 2A or 2B if only one operation selected)

---

### Step 1: Gather and Validate Inputs

**Prompt user for required data:**

```
Please provide the following runway and weather data:

RUNWAY INFORMATION:
- Runway Identifier: [e.g., "09" or "27"]
- Airport Name (optional): [e.g., "KSUN Sun Valley"]
- Runway Elevation: [feet MSL]
- Runway Heading: [degrees magnetic, e.g., 092]
- Runway Length: [feet]

CURRENT WEATHER:
- Temperature: [°C]
- Altimeter: [inHg]
- Wind Direction: [degrees magnetic]
- Wind Speed: [knots]
- Wind Gusts (if any): [knots, or "none"]

OPERATION TYPE:
- [A] Takeoff Only
- [B] Landing Only
- [C] Both (default)
```

**Validation Rules:**

**Runway Data:**
- [ ] Elevation: 0-14,000 ft (if >14,000 ft, warn: "Exceeds typical GA operations")
- [ ] Heading: 0-360° (if invalid, request correction)
- [ ] Length: 1,000-15,000 ft (if <2,000 ft, flag as "short runway - extra caution")

**Weather Data:**
- [ ] Temperature: -40°C to +50°C (if outside range, confirm: "Unusual temperature, please verify")
- [ ] Altimeter: 28.00-31.00 inHg (if outside, warn: "Non-standard altimeter, verify accuracy")
- [ ] Wind direction: 0-360° (if invalid, request correction)
- [ ] Wind speed: 0-60 kt (if >30 kt, flag: "High wind conditions - evaluate risk")
- [ ] Gusts: Must be ≥ sustained wind speed (if gust < sustained, warn inconsistency)

**If any validation fails:**
- State which input failed validation
- Explain why (e.g., "Altimeter 27.50 is below typical range - this would indicate extreme low pressure")
- Request corrected value
- **Do not proceed until all validations pass**

**If all validations pass:**
- Confirm inputs received: "Received: KSUN Rwy 09, Elevation 5,318 ft, Temp 28°C, Altimeter 30.12, Winds 270/12"
- Proceed to Step 1.5

---

### Step 1.5: Calculate Common Performance Data

**Execute the following calculations using provided Python functions** (see `references/calculation-functions.py`):

**Calculation 1: Pressure Altitude**
```python
pressure_altitude = field_elevation + (29.92 - altimeter_setting) * 1000
pressure_altitude_rounded = round(pressure_altitude / 10) * 10  # Round to nearest 10 ft
```

**Calculation 2: ISA Temperature**
```python
isa_temp = 15 - (2 * (pressure_altitude / 1000))
```

**Calculation 3: Density Altitude**
```python
density_altitude = pressure_altitude + (120 * (actual_temp - isa_temp))
density_altitude_rounded = round(density_altitude / 50) * 50  # Round to nearest 50 ft
```

**Calculation 4: Wind Components**
```python
import math
wind_angle = abs(wind_direction - runway_heading)
if wind_angle > 180:
    wind_angle = 360 - wind_angle

headwind_component = wind_speed * math.cos(math.radians(wind_angle))
crosswind_component = wind_speed * math.sin(math.radians(wind_angle))

# Determine if headwind or tailwind
angle_diff = (wind_direction - runway_heading) % 360
if angle_diff > 90 and angle_diff < 270:
    headwind_component = -headwind_component  # It's a tailwind
    wind_type = "tailwind"
else:
    wind_type = "headwind"
```

**Store calculated values:**
- `pressure_altitude` (rounded to nearest 10 ft)
- `density_altitude` (rounded to nearest 50 ft)
- `isa_temp` (for reference)
- `temp_deviation_from_isa` (actual - ISA, show if hot/cold day)
- `headwind_component` (positive = headwind, negative = tailwind)
- `crosswind_component` (absolute value)
- `wind_type` ("headwind" or "tailwind")

**Performance Impact Assessment:**

**Density Altitude Impact:**
- <2,000 ft DA: "Excellent performance"
- 2,000-5,000 ft DA: "Good performance, minor reduction"
- 5,000-8,000 ft DA: "Noticeable performance reduction"
- 8,000-10,000 ft DA: "Significant performance reduction - caution advised"
- >10,000 ft DA: "Severe performance degradation - high risk"

**Wind Impact:**
- Headwind: "Favorable - reduces takeoff/landing distance"
- Tailwind: "Unfavorable - increases takeoff/landing distance significantly"
- Crosswind <10 kt: "Light crosswind - standard technique"
- Crosswind 10-15 kt: "Moderate crosswind - proficient technique required"
- Crosswind >15 kt: "Strong crosswind - consider alternate runway or delay"

**Display summary before proceeding:**
```
CALCULATED PERFORMANCE CONDITIONS:
- Pressure Altitude: [X] ft
- Density Altitude: [Y] ft (ISA +[Z]°C) - [Impact Assessment]
- Headwind: [A] kt ([favorable/unfavorable])
- Crosswind: [B] kt ([light/moderate/strong])
```

---

### Step 2A: Takeoff Brief Workflow (if selected)

**Execute only if operation type includes takeoff**

#### Step 2A.1: Interpolate Takeoff Distance

**Use embedded performance table** (see `references/sr22t-performance-data.py`):

**Lookup logic:**
1. Find bounding pressure altitudes in table (0, 2000, 4000, 6000, 8000, 10000 ft)
2. Find bounding temperatures (0, 10, 20, 30, 40, 50°C)
3. Perform bilinear interpolation between the 4 surrounding data points

**Python code to execute:**
```python
# Reference to embedded data
takeoff_conditions = EMBEDDED_SR22T_PERFORMANCE["performance_data"]["takeoff_distance"]["conditions"]

# Find surrounding pressure altitude points
pa_values = sorted(set(c["pressure_altitude_ft"] for c in takeoff_conditions))
pa_low = max([p for p in pa_values if p <= pressure_altitude], default=pa_values[0])
pa_high = min([p for p in pa_values if p >= pressure_altitude], default=pa_values[-1])

# Find surrounding temperature points (extracted from any condition)
temp_keys = sorted([int(k.replace('temp_', '').replace('c', ''))
                    for k in takeoff_conditions[0]["performance"].keys()])
temp_low = max([t for t in temp_keys if t <= actual_temp], default=temp_keys[0])
temp_high = min([t for t in temp_keys if t >= actual_temp], default=temp_keys[-1])

# Get 4 corner data points
def get_takeoff_data(pa, temp):
    condition = next(c for c in takeoff_conditions if c["pressure_altitude_ft"] == pa)
    temp_key = f"temp_{temp}c"
    return condition["performance"][temp_key]

data_ll = get_takeoff_data(pa_low, temp_low)   # Lower-left
data_lh = get_takeoff_data(pa_low, temp_high)  # Lower-right
data_hl = get_takeoff_data(pa_high, temp_low)  # Upper-left
data_hh = get_takeoff_data(pa_high, temp_high) # Upper-right

# Bilinear interpolation
if pa_low == pa_high:
    # Interpolate only on temperature
    if temp_low == temp_high:
        ground_roll = data_ll["ground_roll_ft"]
        total_distance = data_ll["total_distance_ft"]
    else:
        temp_ratio = (actual_temp - temp_low) / (temp_high - temp_low)
        ground_roll = data_ll["ground_roll_ft"] + temp_ratio * (data_lh["ground_roll_ft"] - data_ll["ground_roll_ft"])
        total_distance = data_ll["total_distance_ft"] + temp_ratio * (data_lh["total_distance_ft"] - data_ll["total_distance_ft"])
elif temp_low == temp_high:
    # Interpolate only on pressure altitude
    pa_ratio = (pressure_altitude - pa_low) / (pa_high - pa_low)
    ground_roll = data_ll["ground_roll_ft"] + pa_ratio * (data_hl["ground_roll_ft"] - data_ll["ground_roll_ft"])
    total_distance = data_ll["total_distance_ft"] + pa_ratio * (data_hl["total_distance_ft"] - data_ll["total_distance_ft"])
else:
    # Full bilinear interpolation
    pa_ratio = (pressure_altitude - pa_low) / (pa_high - pa_low)
    temp_ratio = (actual_temp - temp_low) / (temp_high - temp_low)

    # Interpolate bottom edge
    ground_roll_bottom = data_ll["ground_roll_ft"] + temp_ratio * (data_lh["ground_roll_ft"] - data_ll["ground_roll_ft"])
    total_bottom = data_ll["total_distance_ft"] + temp_ratio * (data_lh["total_distance_ft"] - data_ll["total_distance_ft"])

    # Interpolate top edge
    ground_roll_top = data_hl["ground_roll_ft"] + temp_ratio * (data_hh["ground_roll_ft"] - data_hl["ground_roll_ft"])
    total_top = data_hl["total_distance_ft"] + temp_ratio * (data_hh["total_distance_ft"] - data_hl["total_distance_ft"])

    # Interpolate vertically
    ground_roll = ground_roll_bottom + pa_ratio * (ground_roll_top - ground_roll_bottom)
    total_distance = total_bottom + pa_ratio * (total_top - total_bottom)

# Round to nearest 50 ft
takeoff_ground_roll = round(ground_roll / 50) * 50
takeoff_total_distance = round(total_distance / 50) * 50
```

**Store results:**
- `takeoff_ground_roll_ft`
- `takeoff_total_distance_ft` (includes clearance of 50 ft obstacle)
- `takeoff_runway_margin_ft` = runway_length - takeoff_total_distance

#### Step 2A.2: Calculate Climb Performance

**Use embedded climb gradient table:**

```python
# Climb gradients from POH (feet per nautical mile)
climb_data = EMBEDDED_SR22T_PERFORMANCE["performance_data"]["climb_gradients"]

# Interpolate for current density altitude
# Table has: pressure_altitude → climb_gradient_91kias, climb_gradient_120kias

# Find surrounding DA points
da_values = sorted(set(c["density_altitude_ft"] for c in climb_data))
da_low = max([d for d in da_values if d <= density_altitude], default=da_values[0])
da_high = min([d for d in da_values if d >= density_altitude], default=da_values[-1])

if da_low == da_high:
    climb_91kias = next(c["gradient_91kias_ft_per_nm"] for c in climb_data if c["density_altitude_ft"] == da_low)
    climb_120kias = next(c["gradient_120kias_ft_per_nm"] for c in climb_data if c["density_altitude_ft"] == da_low)
else:
    data_low = next(c for c in climb_data if c["density_altitude_ft"] == da_low)
    data_high = next(c for c in climb_data if c["density_altitude_ft"] == da_high)

    da_ratio = (density_altitude - da_low) / (da_high - da_low)
    climb_91kias = data_low["gradient_91kias_ft_per_nm"] + da_ratio * (data_high["gradient_91kias_ft_per_nm"] - data_low["gradient_91kias_ft_per_nm"])
    climb_120kias = data_low["gradient_120kias_ft_per_nm"] + da_ratio * (data_high["gradient_120kias_ft_per_nm"] - data_low["gradient_120kias_ft_per_nm"])

# Round to nearest 5 ft/nm
climb_gradient_91kias = round(climb_91kias / 5) * 5
climb_gradient_120kias = round(climb_120kias / 5) * 5
```

**Store results:**
- `climb_gradient_91kias_ft_per_nm`
- `climb_gradient_120kias_ft_per_nm`

#### Step 2A.3: Calculate CAPS Altitudes

```python
# CAPS minimum deployment altitude (600 ft AGL per Cirrus)
caps_minimum_agl = 600
caps_minimum_msl = runway_elevation + caps_minimum_agl

# CAPS recommended deployment altitude (2000 ft AGL for optimal deployment)
caps_recommended_agl = 2000
caps_recommended_msl = runway_elevation + caps_recommended_agl

# Pattern altitude (typically 1000 ft AGL)
pattern_altitude_agl = 1000
pattern_altitude_msl = runway_elevation + pattern_altitude_agl
```

**Store results:**
- `caps_minimum_msl`
- `caps_recommended_msl`
- `pattern_altitude_msl`

#### Step 2A.4: Generate Departure Passenger Brief

**Use Passenger Briefing Skill methodology** (Skill #2 from earlier):

**Required elements:**
1. Flight context (departing from this airport)
2. Weather expectations (based on density altitude and winds)
3. CAPS mention
4. Passenger preparation

**Script template:**

```python
# Determine weather tone
if density_altitude < 5000:
    weather_tone = "excellent conditions for takeoff"
    passenger_prep = "Sit back and enjoy the climb out"
elif density_altitude < 8000:
    weather_tone = "good conditions, though you'll notice a longer takeoff roll at this elevation"
    passenger_prep = "Keep your seatbelt snug as we climb to cruise altitude"
else:
    weather_tone = "high elevation and warm temperatures, so we'll have an extended takeoff roll and climb—completely normal for these conditions"
    passenger_prep = "Keep your seatbelt snug, and we'll have a gradual climb to our cruising altitude"

# Wind mention
if abs(headwind_component) > 10:
    if wind_type == "headwind":
        wind_mention = f"with a nice {int(abs(headwind_component))}-knot headwind helping us out"
    else:
        wind_mention = f"with a {int(abs(headwind_component))}-knot tailwind to account for"
elif crosswind_component > 10:
    wind_mention = f"with a bit of a crosswind today"
else:
    wind_mention = ""

# Generate script
departure_passenger_brief = f"""Here's what to expect for our takeoff from {airport_name if airport_name else 'this airport'}: We have {weather_tone}{', ' + wind_mention if wind_mention else ''}. This Cirrus is equipped with the CAPS whole-plane parachute system for an extra layer of safety. {passenger_prep}, and let me know if you have any questions."""
```

#### Step 2A.5: Format Takeoff Brief Output

**Generate comprehensive takeoff brief:**

```markdown
# SR22T TAKEOFF BRIEF - {Airport} Runway {Runway ID}

## PERFORMANCE SUMMARY
**Pressure Altitude:** {pressure_altitude} ft ({field_elevation} ft elevation {+/- pressure correction} ft altimeter correction)
**Density Altitude:** {density_altitude} ft (ISA {+/-}X°C - {impact assessment})

**Wind Analysis:**
- {Headwind/Tailwind}: {component} kt ({favorable/unfavorable})
- Crosswind: {component} kt ({light/moderate/strong})

## TAKEOFF PERFORMANCE
**Ground Roll:** {takeoff_ground_roll} ft
**Total Distance to 50ft:** {takeoff_total_distance} ft

**Runway Analysis:**
- Available: {runway_length} ft
- Required: {takeoff_total_distance} ft
- **Margin: {runway_margin} ft ({percentage}% - {EXCELLENT/GOOD/ADEQUATE/MARGINAL/INSUFFICIENT})**

## CLIMB PERFORMANCE
**At 91 KIAS (Initial Climb - Best Angle):**
- Climb Gradient: {climb_91kias} ft/NM
- Estimated Rate: ~{calculated based on groundspeed} fpm

**At 120 KIAS (Enroute Climb - Best Rate):**
- Climb Gradient: {climb_120kias} ft/NM
- Estimated Rate: ~{calculated} fpm

## CAPS ALTITUDES
**Field Elevation:** {runway_elevation} ft MSL
**CAPS Minimum:** {caps_minimum_msl} ft MSL ({caps_minimum_agl} ft AGL) - Emergency deployment only, limited effectiveness
**CAPS Recommended:** {caps_recommended_msl} ft MSL ({caps_recommended_agl} ft AGL) - Optimal deployment window
**Pattern Altitude:** {pattern_altitude_msl} ft MSL ({pattern_altitude_agl} ft AGL) - CAPS fully effective above this altitude

## EMERGENCY BRIEF - Phased Approach

**Phase 1 - Ground Roll (0 to rotation):**
If engine failure occurs before rotation: **ABORT TAKEOFF** - Close throttle, apply brakes, stop on remaining runway.

**Phase 2 - Rotation to {caps_minimum_msl} ft MSL:**
If engine failure: Land straight ahead or within 30° of runway heading. Insufficient altitude for CAPS deployment.

**Phase 3 - {caps_minimum_msl} ft to {caps_recommended_msl} ft MSL:**
If engine failure: **IMMEDIATE CAPS DEPLOYMENT** - Pull red handle without hesitation. Limited time for successful deployment.

**Phase 4 - Above {caps_recommended_msl} ft MSL:**
If engine failure: Troubleshoot per POH checklist. CAPS available if unable to resolve. Time permits decision-making.

## DEPARTURE PASSENGER BRIEF

{departure_passenger_brief}

## SAFETY NOTES
{List of cautions and advisories based on conditions}

**GO/NO-GO: {✅ GO / ⚠️ GO WITH CAUTION / ❌ NO-GO}**
{Specific reasoning}
```

**Margin Assessment Categories:**
- **EXCELLENT:** >150% (margin > 1.5× required distance)
- **GOOD:** 125-150% (margin 1.25-1.5× required)
- **ADEQUATE:** 110-125% (margin 1.1-1.25× required)
- **MARGINAL:** 100-110% (margin 1.0-1.1× required) - Weather/technique dependent
- **INSUFFICIENT:** <100% (required > available) - **NO-GO**

---

### Step 2B: Landing Brief Workflow (if selected)

**Execute only if operation type includes landing**

#### Step 2B.1: Determine Flap Configuration

**Use wind conditions to select flap setting:**

```python
# Extract gust factor if provided
if wind_gusts and wind_gusts > wind_speed:
    gust_factor = wind_gusts - wind_speed
else:
    gust_factor = 0

# Flap configuration logic (from v_speeds data)
if crosswind_component >= 15:
    flap_config = "no_flaps"
    config_reason = f"Strong crosswind ({int(crosswind_component)} kt) warrants no flap configuration for better control"
elif crosswind_component >= 10 or gust_factor >= 10:
    flap_config = "partial_flaps_50"
    config_reason = f"Moderate crosswind ({int(crosswind_component)} kt) or gusty conditions warrant 50% flaps"
else:
    flap_config = "full_flaps"
    config_reason = "Normal landing configuration"

# Get base approach speeds from embedded data
v_speeds = EMBEDDED_SR22T_PERFORMANCE["v_speeds"]["approach_speeds"][flap_config]
base_final_approach = v_speeds["final_approach_base_kias"]
threshold_crossing = v_speeds["threshold_crossing_kias"]
touchdown_target = v_speeds["touchdown_target_kias"]
config_notes = v_speeds["config_notes"]
```

#### Step 2B.2: Calculate Approach Speeds with Corrections

```python
# Gust correction (add half the gust factor to approach speed)
if gust_factor > 0:
    gust_correction = round(gust_factor * 0.5, 1)
else:
    gust_correction = 0

# Final approach speed
final_approach_speed = base_final_approach + gust_correction

# Store results
approach_speeds = {
    "configuration": flap_config,
    "configuration_reason": config_reason,
    "final_approach_kias": round(final_approach_speed),
    "threshold_crossing_kias": threshold_crossing,
    "touchdown_target_kias": touchdown_target,
    "gust_correction_applied": gust_correction,
    "config_notes": config_notes
}
```

**Flap Configuration Mapping:**
- `full_flaps`: "Full Flaps (100%)"
- `partial_flaps_50`: "Flaps 50% (Flaps 1)"
- `no_flaps`: "No Flaps"

#### Step 2B.3: Interpolate Landing Distance

**Use same interpolation logic as takeoff, but with landing table:**

```python
# Reference landing distance table
landing_conditions = EMBEDDED_SR22T_PERFORMANCE["performance_data"]["landing_distance"]["conditions"]

# Same bilinear interpolation process as takeoff (Step 2A.1)
# Using pressure_altitude and actual_temp to interpolate

# ... (identical interpolation code, but using landing_conditions instead of takeoff_conditions)

# Round to nearest 50 ft
landing_ground_roll = round(ground_roll / 50) * 50
landing_total_distance = round(total_distance / 50) * 50

# Calculate runway margin
landing_runway_margin = runway_length - landing_total_distance
```

#### Step 2B.4: Generate Arrival Passenger Brief

**Use Arrival Passenger Brief from Skill #2:**

```python
# Determine conditions mention
if crosswind_component > 10 or gust_factor > 10:
    conditions_mention = f"with {'gusty ' if gust_factor > 10 else ''}{'crosswinds' if crosswind_component > 10 else 'winds'}, so you might notice the nose pointed slightly into the wind on final—that's completely normal"
elif density_altitude > 8000:
    conditions_mention = f"at a high-elevation airport, so you might notice a slightly longer approach—completely normal for these conditions"
else:
    conditions_mention = "with smooth conditions expected"

# Generate arrival script
arrival_passenger_brief = f"""We should be landing at {airport_name if airport_name else 'our destination'} in about twelve minutes. Temperature on the ground is {int(actual_temp)} degrees {conditions_mention}. I'll need to focus on the approach and landing, so I'll go quiet for a few minutes—make sure your seatbelt is snug and any loose items are secured."""
```

#### Step 2B.5: Format Landing Brief Output

```markdown
# SR22T LANDING BRIEF - {Airport} Runway {Runway ID}

## PERFORMANCE SUMMARY
**Pressure Altitude:** {pressure_altitude} ft
**Density Altitude:** {density_altitude} ft (ISA {+/-}X°C - {impact})

**Wind Analysis:**
- {Headwind/Tailwind}: {component} kt ({favorable/unfavorable})
- Crosswind: {component} kt ({light/moderate/strong})
{if gusts: - **Gusts:** +{gust_factor} kt variance}

## APPROACH CONFIGURATION
**Recommended:** {Flap configuration display name}
- **Reason:** {configuration_reason}
- Final Approach Speed: {final_approach_speed} KIAS ({base_speed} base {+ gust_correction if applicable})
- Threshold Crossing: {threshold_crossing} KIAS
- Touchdown Target: {touchdown_target} KIAS

{if alternate configs exist:}
**Alternate Configurations:**
- {list other viable configs with speeds}

## LANDING PERFORMANCE
**Ground Roll:** {landing_ground_roll} ft
**Total Distance (over 50ft obstacle):** {landing_total_distance} ft

**Runway Analysis:**
- Available: {runway_length} ft
- Required: {landing_total_distance} ft
- **Margin: {landing_margin} ft ({percentage}% - {assessment})**

## WIND CONSIDERATIONS
{if gusts > 10kt:}
⚠️ **Gusty Winds:** {wind_speed}G{wind_gusts} requires:
- Extra airspeed carried to flare (+{gust_correction} kt added above)
- Firm approach technique (expect sink in gust lulls)
- Use rudder for centerline, aileron into crosswind
- Be ready for go-around if unstabilized below 500 AGL

{if crosswind > 10kt:}
⚠️ **Crosswind Technique:**
- Crab into wind on approach, align with rudder in flare
- Expect drift after touchdown, use rudder/nosewheel steering
- Aileron into wind after touchdown to prevent upwind wing lift

{if headwind > 10kt:}
✅ **Headwind Component:** {headwind} kt reduces landing distance ~{percentage estimate}%

{if tailwind component:}
⚠️ **TAILWIND CAUTION:** {tailwind} kt increases landing distance significantly
- Consider using alternate runway if available
- Ensure adequate margin before committing to land

## GO-AROUND CONSIDERATIONS
**Density Altitude Impact:** {if DA > 8000: "High DA reduces climb performance—ensure go-around feasible before committing to land" else: "Normal go-around performance expected"}

**Runway Environment:** {if runway < 3000: "Short runway—limited options after touchdown. Commit to landing or go around early." else: "Adequate runway for safe go-around decision."}

## ARRIVAL PASSENGER BRIEF

{arrival_passenger_brief}

## SAFETY NOTES
{conditions-specific notes}

**GO/NO-GO: {decision}**
{reasoning}
```

---

### Step 3: Combined Analysis (if both operations selected)

**If user selected "Both Operations," generate comparison:**

```markdown
# SR22T COMPLETE RUNWAY ANALYSIS - {Airport} Runway {Runway ID}

{Include both takeoff and landing briefs from Steps 2A.5 and 2B.5}

## COMPARATIVE ANALYSIS

**Runway Margins:**
- Takeoff Margin: {takeoff_margin} ft ({takeoff_percentage}%)
- Landing Margin: {landing_margin} ft ({landing_percentage}%)
- **Most Restrictive:** {Takeoff/Landing} operation

**Performance Considerations:**
{if takeoff margin < landing margin:}
- Takeoff is more limiting than landing
- Reason: {density altitude/tailwind/runway length analysis}
- Recommendation: {specific guidance}

{if landing margin < takeoff margin:}
- Landing is more limiting than takeoff
- Reason: {wind conditions/approach configuration/etc}
- Recommendation: {specific guidance}

**Round-Trip Viability:**
{if both margins are adequate:}
✅ Both operations have adequate margins for safe operations

{if either is marginal:}
⚠️ {Operation} has marginal performance - monitor conditions before committing

{if conditions changing:}
📊 **Weather Trend Consideration:**
If conditions change (temperature/winds), re-evaluate using this Skill with updated data before return flight.

**OVERALL GO/NO-GO: {decision}**
{Combined reasoning from both operations}
```

---

## Validation Checklist

**Before delivering any brief, verify:**

**Calculation Accuracy:**
- [ ] All interpolations used correct bounding data points
- [ ] All roundings applied per specification (10 ft for PA, 50 ft for DA/distances)
- [ ] Wind components calculated correctly (headwind vs tailwind identified properly)
- [ ] Margin calculations: available - required = margin (positive = safe, negative = insufficient)

**Output Completeness:**
- [ ] All required sections present (Performance Summary, Performance Data, Safety Notes, GO/NO-GO)
- [ ] Passenger brief included (appropriate for operation type)
- [ ] Specific numbers provided (no placeholders like "X ft" remaining)
- [ ] Assessment categories applied correctly (EXCELLENT/GOOD/etc based on margin percentages)

**Safety Logic:**
- [ ] GO/NO-GO decision matches margin assessment
- [ ] If margin <10% or negative → **NO-GO** with clear explanation
- [ ] If margin 10-25% → **GO WITH CAUTION** with specific conditions to monitor
- [ ] If margin >25% → **GO** (may include advisories for high DA, winds, etc.)
- [ ] Safety notes include all relevant cautions (high DA, crosswinds, gusts, tailwinds, short runway)

**Consistency:**
- [ ] Temperature used consistently (°C throughout, not mixing with °F)
- [ ] Altitudes consistent (MSL vs AGL clearly labeled)
- [ ] Speeds in KIAS (not TAS or groundspeed unless explicitly calculated and labeled)

---

## Examples for Level 3 (examples/ folder)

### Example 1: High Density Altitude Takeoff

**File:** `examples/example-high-da-takeoff.md`

**Scenario:**
- Airport: KEGE (Eagle County, CO)
- Runway: 07, 9,000 ft elevation
- Temperature: 32°C (hot summer day)
- Altimeter: 30.15
- Winds: 090/8 (aligned with runway)
- Runway length: 8,000 ft

**Expected Challenges:**
- Very high density altitude (~12,500 ft)
- Reduced climb performance
- Extended takeoff roll

**Output should demonstrate:**
- Proper high-DA warnings
- GO/NO-GO logic with marginal conditions
- CAPS altitude calculations at high elevation
- Passenger brief adjusted for high-DA operations

---

### Example 2: Gusty Crosswind Landing

**File:** `examples/example-crosswind-landing.md`

**Scenario:**
- Airport: KSUN (Sun Valley, ID)
- Runway: 31, 5,318 ft elevation
- Temperature: 18°C (cool day)
- Altimeter: 29.92
- Winds: 270/15 gusting 25
- Runway length: 7,550 ft

**Expected Challenges:**
- Strong gusty crosswind
- Flap configuration decision (50% vs no flaps)
- Gust correction calculations
- Crosswind technique required

**Output should demonstrate:**
- Proper flap selection logic
- Gust correction applied to approach speed
- Detailed wind technique guidance
- Passenger brief addressing turbulence/wind

---

### Example 3: Complete Round-Trip Analysis

**File:** `examples/example-round-trip.md`

**Scenario:**
- Morning departure: Cool temps, good performance
- Afternoon return: Hot temps, degraded performance
- Show how margins change with temperature

**Output should demonstrate:**
- Both takeoff and landing briefs
- Comparative analysis section
- Temperature sensitivity discussion
- Decision guidance for return timing

---

## Part 3: Reference Files

### File 1: `references/sr22t-performance-data.py`

**Contents:**
- Complete `EMBEDDED_SR22T_PERFORMANCE` dictionary from sr22t_briefing_v31.py
- All takeoff distance tables (lines 85-300 from your code)
- All landing distance tables
- Climb gradient tables
- V-speeds with approach configurations

**Format:**
```python
EMBEDDED_SR22T_PERFORMANCE = {
    "metadata": {
        "aircraft_model": "Cirrus SR22T",
        "weight_lb": 3600,
        "data_source": "Cirrus SR22T POH",
        "data_version": "2023 POH Revision",
        "notes": "Performance data at max gross weight. Reduce distances by ~10% per 100 lb under max gross."
    },

    "v_speeds": {
        # Full v_speeds section from your code
    },

    "performance_data": {
        "takeoff_distance": {
            # Full takeoff table
        },

        "landing_distance": {
            # Full landing table
        },

        "climb_gradients": {
            # Climb gradient data at various density altitudes
        }
    }
}
```

---

### File 2: `references/calculation-functions.py`

**Contents:**
All calculation functions with inline tests:

```python
import math

def calculate_pressure_altitude(field_elevation_ft, altimeter_inhg):
    """
    Calculate pressure altitude using standard aviation formula.

    Args:
        field_elevation_ft: Airport elevation above sea level
        altimeter_inhg: Current altimeter setting from METAR/ATIS

    Returns:
        Pressure altitude in feet (rounded to nearest 10 ft)
    """
    pa = field_elevation_ft + (29.92 - altimeter_inhg) * 1000
    return round(pa / 10) * 10

def test_pressure_altitude():
    """Test cases for pressure altitude calculation"""
    assert calculate_pressure_altitude(0, 29.92) == 0, "Standard day at sea level should be 0"
    assert calculate_pressure_altitude(5000, 30.12) == 4800, "High pressure test failed"
    assert calculate_pressure_altitude(5000, 29.72) == 5200, "Low pressure test failed"
    print("✅ Pressure altitude tests passed")

# ... (include all other calculation functions with tests)
```

---

### File 3: `references/v-speeds-reference.md`

**Contents:**
Explanation of V-speed selection logic, flap configurations, and wind corrections:

```markdown
# SR22T V-Speeds and Configuration Reference

## Approach Speed Selection Logic

### Flap Configurations

**Full Flaps (100%):**
- Use when: Crosswind <10 kt, no significant gusts
- Advantages: Shortest landing distance, best forward visibility
- Final Approach: 82.5 KIAS base
- Threshold: 79 KIAS
- Touchdown Target: 67 KIAS

**50% Flaps (Flaps 1):**
- Use when: Crosswind 10-15 kt OR gusts ≥10 kt
- Advantages: Better crosswind control, less float in gusts
- Final Approach: 87.5 KIAS base
- Threshold: 84 KIAS
- Touchdown Target: 72 KIAS

**No Flaps:**
- Use when: Crosswind >15 kt OR emergency
- Advantages: Maximum control authority, go-around performance
- Final Approach: 92.5 KIAS base
- Threshold: 89 KIAS
- Touchdown Target: 77 KIAS

### Gust Corrections

Add HALF the gust factor to final approach speed:
- Winds 15G25 → Gust factor = 10 kt → Add 5 kt
- Winds 12G18 → Gust factor = 6 kt → Add 3 kt

Do NOT add gust correction to threshold or touchdown speeds.

### Weight Corrections

Performance data is at max gross weight (3,600 lb).
- Reduce approach speed by 1 kt per 100 lb under max gross
- Example: At 3,400 lb → Reduce speeds by 2 kt
```

---

## Part 4: Testing & Validation Plan

### Pre-Release Testing

**Test 1: Calculation Consistency**
- Run same inputs 5 times
- Verify outputs identical (±0 ft variance on rounded values)
- Inputs: PA 4000 ft, Temp 25°C, calm winds
- Expected: Identical takeoff/landing distances across all 5 runs

**Test 2: Interpolation Accuracy**
- Compare Skill outputs to Python tool outputs
- Test cases: 10 different combinations of PA and temperature
- Acceptance: ±50 ft variance (within POH tolerance)

**Test 3: Edge Case Handling**
- Extreme high DA (>12,000 ft)
- Extreme temperatures (-20°C, +45°C)
- Strong tailwinds (>15 kt)
- Very short runways (<2,000 ft)
- Verify appropriate warnings and NO-GO decisions

**Test 4: GO/NO-GO Logic**
- Insufficient margin (required > available) → Must be NO-GO
- Marginal margin (5-10%) → Must be GO WITH CAUTION
- Adequate margin (>25%) → Should be GO

**Test 5: Passenger Brief Quality**
- Read aloud test (30 seconds or less for departure, 20 seconds for arrival)
- CAPS mention present in every departure brief
- Sterile cockpit explanation in every arrival brief
- Tone appropriate to conditions

---

## Part 5: Success Metrics

**Quantitative:**
- Calculation accuracy: <50 ft variance vs Python tool
- Consistency: 0% variance across identical inputs
- Speed: <60 seconds from input to complete brief
- Completeness: 100% of required sections present

**Qualitative:**
- GO/NO-GO decisions align with conservative safety margins
- Passenger briefs sound natural when read aloud
- Safety warnings appropriate and actionable
- Professional aviation terminology used correctly

---

## Part 6: Future Enhancements (Out of Scope for v1.0)

**Potential additions:**
- Multi-aircraft support (SR22, SR20, other models)
- Weight & balance integration
- Short-field technique recommendations
- Contaminated runway adjustments (wet, snow, ice)
- Custom performance data upload
- Metric unit support (meters, kg, °C → keeps same)

---

## Conclusion

This Skill provides a focused, fast, accurate tool for runway-specific performance analysis, complementing the comprehensive PassBrief Python system. By embedding all necessary POH data and calculation logic, it enables pilots to make informed GO/NO-GO decisions in under 60 seconds using only basic weather and runway information available at any airport worldwide.

**Development Priority:** HIGH
**Estimated Development Time:** 8-12 hours (includes testing and examples)
**Expected Value:** Fills critical gap for quick-turn and unfamiliar airport operations
