# Test: Can Claude Execute Provided Python Code Consistently?

## Hypothesis
If we provide Claude with:
1. The exact `EMBEDDED_SR22T_PERFORMANCE` dictionary
2. The exact `interpolate_performance()` method code
3. Instructions to execute that code

Will Claude produce **identical outputs** for identical inputs across multiple runs?

## Test Case

### Provided Code (from sr22t_briefing_v31.py)

```python
# Simplified version for testing
EMBEDDED_SR22T_PERFORMANCE = {
    "performance_data": {
        "takeoff_distance": {
            "conditions": [
                {
                    "pressure_altitude_ft": 0,
                    "performance": {
                        "temp_0c": {"ground_roll_ft": 890, "total_distance_ft": 1450},
                        "temp_20c": {"ground_roll_ft": 1040, "total_distance_ft": 1700},
                        "temp_40c": {"ground_roll_ft": 1230, "total_distance_ft": 2000}
                    }
                },
                {
                    "pressure_altitude_ft": 4000,
                    "performance": {
                        "temp_0c": {"ground_roll_ft": 1150, "total_distance_ft": 1900},
                        "temp_20c": {"ground_roll_ft": 1360, "total_distance_ft": 2250},
                        "temp_40c": {"ground_roll_ft": 1640, "total_distance_ft": 2700}
                    }
                }
            ]
        }
    }
}

def interpolate_takeoff_distance(pressure_alt, temp_c):
    """
    Bilinear interpolation for takeoff distance
    """
    data = EMBEDDED_SR22T_PERFORMANCE["performance_data"]["takeoff_distance"]["conditions"]

    # Find bounding pressure altitudes
    pa_values = [d["pressure_altitude_ft"] for d in data]

    # Find surrounding data points
    if pressure_alt <= pa_values[0]:
        pa_low_idx = 0
        pa_high_idx = 0
    elif pressure_alt >= pa_values[-1]:
        pa_low_idx = len(pa_values) - 1
        pa_high_idx = len(pa_values) - 1
    else:
        for i in range(len(pa_values) - 1):
            if pa_values[i] <= pressure_alt <= pa_values[i+1]:
                pa_low_idx = i
                pa_high_idx = i + 1
                break

    # Get temperature keys
    temp_keys = list(data[0]["performance"].keys())

    # Interpolate...
    # (Full implementation would go here)

    # For now, simplified lookup
    result = data[pa_low_idx]["performance"]["temp_20c"]["total_distance_ft"]
    return result

# Test inputs
pressure_altitude = 2000
temperature = 25

result = interpolate_takeoff_distance(pressure_altitude, temperature)
print(f"Takeoff distance: {result} ft")
```

### Test Inputs
- Pressure Altitude: 2000 ft (between 0 and 4000, requires interpolation)
- Temperature: 25°C (between 20°C and 40°C, requires interpolation)

### Expected Behavior
**Consistent Execution:** Same code + same inputs = same output every run

### Question to Test
**Run 1:** What output does Claude produce?
**Run 2:** Does Claude produce identical output?
**Run 3:** Does the code stay identical or does Claude "improve" it?

## Findings (To Be Tested)

### Scenario A: Claude Executes Code As-Is
- ✅ Provides code exactly as written
- ✅ Executes in sandbox
- ✅ Returns consistent output
- ✅ **This would support embedding code in Skills**

### Scenario B: Claude Rewrites Code
- ❌ "Improves" the interpolation algorithm
- ❌ Different implementation each run
- ❌ Outputs vary
- ❌ **This would NOT support embedding code in Skills**

### Scenario C: Claude Uses Code as Reference
- ⚠️ Understands the methodology
- ⚠️ Writes new implementation inspired by provided code
- ⚠️ Consistent methodology, variable implementation
- ⚠️ **Borderline - depends on output variance**

---

## What We Need to Validate

1. **Execution Consistency:** 5 identical inputs → 5 identical outputs?
2. **Code Preservation:** Does Claude execute provided code or rewrite it?
3. **Data Access:** Can Claude reliably access the embedded dictionary?
4. **Error Handling:** What happens with edge cases (out of bounds temps, etc.)?

## Real-World Implications

**If Scenario A (consistent execution):**
- ✅ You CAN embed performance calculations in Skill
- ✅ Skills become much more powerful for your use case
- ✅ Only need Skills, minimal Python wrapper

**If Scenario B (rewrites code):**
- ❌ You CANNOT trust embedded calculations
- ❌ Need Python for all math, Skills for narrative only
- ❌ My original recommendation stands

**If Scenario C (inspired but variable):**
- ⚠️ Need to test variance magnitude
- ⚠️ If <50 ft variance → acceptable
- ⚠️ If >200 ft variance → unacceptable
