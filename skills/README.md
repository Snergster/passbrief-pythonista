# PassBrief Claude Skills

This directory contains Claude Skills that complement the main PassBrief Python tool, providing quick-access functionality without requiring full Pythonista setup.

## Available Skills

### 1. SR22T Runway Brief

**Purpose:** Quick takeoff and landing performance analysis for any runway

**Use Cases:**
- Quick feasibility checks at unfamiliar airports
- Hot day performance verification
- Backcountry strip analysis
- Return flight margin checks after weather changes
- Training scenarios

**Inputs Required:** 7 fields (runway elevation, temp, altimeter, winds, runway heading/length)

**Outputs:**
- Performance calculations (PA, DA, wind components)
- Takeoff/landing distances with runway margins
- Flap configuration recommendations
- Passenger briefing scripts
- GO/NO-GO decisions with reasoning

**Setup Time:** ~30 seconds vs 5+ minutes for full tool

**Status:** ✅ Complete (v1.0.0)

**Directory:** `runway-brief/`

---

## Skills vs Full Python Tool

| Aspect | Full Python Tool | Skills |
|--------|------------------|--------|
| **Setup** | Garmin PDF upload, METAR fetch, airport lookup | Manual input (7 fields) |
| **Time** | 2-5 minutes | 30 seconds |
| **Scope** | Full flight: route, TFRs, weather, waypoints | Single runway only |
| **Automation** | High (fetches everything) | None (you provide data) |
| **Platform** | iOS Pythonista | Any device with Claude |
| **Detail** | Comprehensive multi-page brief | Focused 1-page brief |
| **Use Case** | Pre-flight planning at home/hotel | Quick check at airplane |

**They complement each other - not replacements!**

---

## Installation

### For Claude Desktop/App (when Skills launch)

1. Navigate to skill directory:
   ```bash
   cd skills/runway-brief
   ```

2. Create .zip package:
   ```bash
   zip -r runway-brief.zip .
   ```

3. Upload to Claude → Settings → Skills → Add Skill

4. Select availability:
   - **Personal:** Available across all projects
   - **Project:** Scoped to PassBrief only

### For ChatGPT/Gemini (manual attachment)

1. Create .zip as above
2. Attach file to conversation
3. Reference in prompt: "Using the SR22T Runway Brief skill attached, [your request]"

---

## Skill Development Notes

### Architecture

Each skill follows the structure from `LLM_SKILLS_PRIMER.md`:

```
skill-name/
├── skill.md                    # YAML frontmatter + main workflow
├── README.md                   # Usage guide and examples
├── references/                 # Level 3: Deep-dive content
│   ├── performance-data.py    # POH tables
│   ├── calculation-functions.py  # Formulas with tests
│   └── reference-docs.md      # Methodology explanations
└── examples/                   # Worked examples
    ├── example-scenario-1.md
    └── example-scenario-2.md
```

### Progressive Disclosure

**Level 1 (YAML frontmatter):**
- 100-150 tokens
- Used for Skill discovery and auto-invocation
- Keywords for matching user intent

**Level 2 (skill.md workflows):**
- 2,000-5,000 tokens
- Core methodology and step-by-step instructions
- Loaded when Skill is invoked

**Level 3 (references/):**
- Variable size (can be large)
- Only loaded when explicitly referenced
- Enables complex Skills without token bloat

### Quality Standards (C.L.E.A.R.)

All skills must meet:
- **C**oncise: Main file <10K tokens
- **L**ogical: Clear hierarchy, logical flow
- **E**xplicit: Specific steps, defined terms
- **A**daptive: Handles variations, edge cases
- **R**eflective: Validation gates, quality checks

### MVS Criteria (Minimum Viable Skill)

Only create skills that meet ALL 4:
1. **Recurring:** Used 3+ times (weekly/monthly/quarterly)
2. **Consistent Methodology:** Same HOW, different WHAT
3. **Complex:** Multi-step process requiring structure
4. **High-Value:** Saves 15+ min per use OR high-stakes

---

## Future Skills (Planned)

### 2. TFR & Route Hazard Analysis

**Status:** Draft plan complete (`artifacts/skill-tfr-hazard-analysis.md`)

**Purpose:** Analyze Garmin Pilot briefing data for TFR penetration, convective weather, and route hazards

**Priority:** High (safety-critical reasoning benefits from consistent methodology)

**Estimated Completion:** TBD

### 3. Passenger Briefing Generator

**Status:** Draft plan complete (`artifacts/skill-passenger-briefing.md`)

**Purpose:** Generate consistent departure and arrival passenger briefing scripts

**Priority:** Medium (nice-to-have, complements SR22T Runway Brief)

**Estimated Completion:** TBD

---

## Testing Skills

### Consistency Test

Run same inputs 5 times, verify outputs identical:

```bash
# Example test for SR22T Runway Brief
python3 test_skill_consistency.py --skill runway-brief \
  --inputs "PA=4000,Temp=25,Winds=calm" \
  --runs 5 \
  --tolerance 50ft
```

### Accuracy Test

Compare Skill outputs to Python tool outputs:

```bash
# Example accuracy test
python3 test_skill_accuracy.py --skill runway-brief \
  --reference sr22t_briefing_v31.py \
  --test-cases 10
```

### Edge Case Test

Verify proper handling of:
- Extreme conditions (very high/low DA)
- Boundary values (exactly 10 kt crosswind)
- Missing data (graceful degradation)
- Invalid inputs (validation and error messages)

---

## Contributing Skills

### Proposal Process

1. Validate MVS criteria (all 4 must be YES)
2. Choose pattern (workflow / principle-based / reference-library)
3. Draft YAML frontmatter + overview
4. Get approval before building full skill

### Development Checklist

- [ ] MVS criteria validated
- [ ] Pattern selected (workflow/principle/reference)
- [ ] YAML frontmatter complete
- [ ] Main workflow written
- [ ] Validation checkpoints added
- [ ] Reference files created (if needed)
- [ ] Examples provided (2-3 scenarios)
- [ ] README with usage guide
- [ ] Tested with 3+ diverse scenarios
- [ ] C.L.E.A.R. quality check passed

### Quality Gates

**Before Release:**
1. Methodology/substance separation verified
2. Token count <10K for main file
3. Consistency test passed (5 runs, identical outputs)
4. Examples demonstrate all major workflows
5. README covers all use cases

---

## Skill Metrics

### SR22T Runway Brief (v1.0.0)

**Size:**
- Total: 2,719 lines
- Main workflow: 507 lines
- Performance data: 419 lines
- Calculation functions: 219 lines (with tests)
- V-speeds reference: 363 lines
- Examples: 789 lines (2 scenarios)
- README: 422 lines

**Complexity:** Medium

**Est. Token Count:**
- Level 1 (YAML): ~120 tokens
- Level 2 (skill.md): ~4,200 tokens
- Level 3 (references): ~3,500 tokens (loaded on demand)

**Time Savings:** ~15 min per runway analysis

**Use Frequency:** Variable (weekly for frequent flyers, monthly for occasional)

---

## Resources

**LLM Skills Primer:** `../LLM_SKILLS_PRIMER.md`
- Complete guide to building, using, and improving Skills
- Pattern selection guidance
- Quality validation checklists

**Skill Plans (Drafts):** `../artifacts/`
- `skill-runway-brief-plan.md` - Complete implementation plan
- `skill-tfr-hazard-analysis.md` - TFR analysis skill draft
- `skill-passenger-briefing.md` - Passenger briefing skill draft

**PassBrief Documentation:** `../CLAUDE.md`
- Full Python tool architecture
- Performance calculation methodology
- Aviation safety protocols

---

## Support

**Questions:**
- Check skill's README.md for usage examples
- Review examples/ directory for similar scenarios
- Consult references/ for calculation details

**Bug Reports:**
- File issue in PassBrief GitHub
- Include: skill name, inputs, expected output, actual output
- Specify which validation check failed

**Feature Requests:**
- Propose new skills via MVS criteria validation
- Submit enhancement ideas for existing skills
- Provide use cases and estimated value

---

## License

MIT License (same as PassBrief project)

Skills may be used, modified, and distributed with attribution to PassBrief Project.

**Aviation Safety Note:** Skills provide data and guidance, but YOU are pilot in command. Always cross-check critical calculations and use conservative personal minimums.

---

**Last Updated:** 2025-10-23
**Skills Count:** 1 complete, 2 planned
**Total Lines:** 2,719 (SR22T Runway Brief v1.0.0)
