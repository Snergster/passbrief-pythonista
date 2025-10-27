# LLM Skills Primer

**Audience:** AI assistants (Claude, ChatGPT, Gemini, etc.)
**Purpose:** Enable LLMs to build, use, verify, and improve Anthropic Skills in any project
**Format:** Concise operational guide

---

## What Are Skills?

**Skills = Reusable Methodology Bundles**

A Skill is a structured prompt template that captures the **HOW** (methodology) separate from the **WHAT** (substance). Skills reduce prompt overhead by 80% through progressive disclosure.

**File Structure:**
```
my-skill.zip
├── skill.md           # YAML frontmatter + markdown instructions
├── references/        # Optional: Level 3 deep-dive docs
│   └── detailed-guide.md
└── examples/          # Optional: sample outputs
    └── example-1.md
```

**Core Concept: Methodology vs Substance Separation**
- **Methodology (in Skill):** Process, framework, validation steps, structure
- **Substance (user provides):** Data, context, specifics, requirements

**Test:** "Could 10 different people use this Skill for 10 different tasks in the same domain?"
- YES → Good separation (reusable)
- NO → Substance leaked into Skill (too specific)

---

## When to Create a Skill (MVS Criteria)

**Minimum Viable Skill = All 4 criteria must be YES:**

1. **Recurring:** Task happens 3+ times (weekly, monthly, quarterly, etc.)
2. **Consistent Methodology:** The HOW stays the same across uses (only WHAT changes)
3. **Complex:** Multi-step process requiring structure (not single-step trivial)
4. **High-Value:** Saves 15+ min per use OR high-stakes (errors costly)

**Decision Tree:**
```
Q1: Recurring (3+ uses)? → NO = Traditional prompt
Q2: Methodology consistent? → NO = Traditional prompt
Q3: Complex (multi-step)? → NO = Maybe not worth it
Q4: High-value (15+ min saved OR high-stakes)? → NO = Traditional prompt

ALL YES → Create Skill
```

**Examples:**
- ✅ Quarterly financial analysis → YES/YES/YES/YES = **Skill**
- ❌ One-time blog post → NO/YES/YES/NO = **Traditional prompt**
- ✅ Weekly status reports → YES/YES/YES/YES = **Skill**

---

## Skill Patterns (Choose One)

### Pattern 1: Workflow (60% of Skills)

**Use when:** Sequential multi-step process with clear phases

**Structure:**
```markdown
## Overview
[What this does and when to use it]

## Phase 1: [First Phase Name]
### Step 1.1: [Substep]
[Detailed instructions]

### Step 1.2: [Substep]
[Detailed instructions]

## Phase 1 Validation
- [ ] Criterion 1
- [ ] Criterion 2
**IF ANY FAIL:** [Action]
**IF ALL PASS:** Proceed to Phase 2

## Phase 2: [Second Phase Name]
[Continue pattern...]

## Final Quality Checks
[How to verify overall success]
```

**Example:** Financial Analysis, Pitch Deck Builder, Excel Editing

---

### Pattern 2: Principle-Based (30% of Skills)

**Use when:** Decision-making or coaching with guiding principles (not rigid steps)

**Structure:**
```markdown
## Overview
[What this does and when to use it]

## Principle 1: [Principle Name]
[Explanation of principle]

**Application:**
[How to apply this principle]

**Guidance Pattern:** When users describe [situation], suggest: "[coaching advice]"

**Example:**
❌ **Violating this principle:**
[Bad example with explanation]

✅ **Applying this principle:**
[Good example with explanation]

## Principle 2: [Next Principle]
[Continue pattern...]

## Decision Framework
[How to use principles together for complex decisions]
```

**Example:** Agentic Development, Requirements Elicitation, Vendor Evaluation

---

### Pattern 3: Reference Library (10% of Skills)

**Use when:** Educational content with multiple independent topics

**Structure:**
```markdown
## Quick Reference Guide

### Category 1: [Name]
**Topic 1.1:** [Brief description]
→ See references/topic-1-1.md

**Topic 1.2:** [Brief description]
→ See references/topic-1-2.md

### Category 2: [Name]
[Continue pattern...]

## When to Read References
**For learning:** Read sequentially (full education)
**For lookup:** Jump to specific topic (just-in-time reference)
```

**Example:** Prompting Pattern Library (25+ patterns), Code Style Guide

---

## Progressive Disclosure (3-Level Loading)

**Optimization for token efficiency:**

**Level 1: Description (100-150 tokens)**
- YAML frontmatter metadata
- Used for Skill discovery and auto-invocation
- **Never accessed during execution** (Claude uses for matching only)

**Level 2: Instructions (1,000-5,000 tokens)**
- Core methodology, workflow steps, validation gates
- Loaded when Skill is invoked
- **Majority of Skill content lives here**

**Level 3: Resources (variable, often 0)**
- Deep reference material, extensive examples, appendices
- **Only loaded if explicitly referenced** from Level 2
- Enables complex Skills without token bloat

**Why it matters:** Without progressive disclosure, composing 8 Skills would exceed context windows. With it, only relevant portions load.

---

## Building a Skill (Step-by-Step)

### Step 1: Validate MVS Criteria
Run through 4 questions. If any NO, stop and use traditional prompt instead.

### Step 2: Choose Pattern
- Sequential steps with phases? → **Workflow**
- Guiding principles for decisions? → **Principle-Based**
- Educational reference content? → **Reference Library**

### Step 3: Create YAML Frontmatter

```yaml
---
name: [Descriptive Skill Name]
description: |
  [1-2 sentences: What this Skill does and when to use it.
  Focus on user intent keywords for auto-invocation.]
version: 1.0.0
author: [Your name or team]
created: [YYYY-MM-DD]
tags: [domain, task-type, use-case]
pattern_type: workflow  # or principle-based or reference-library
platforms: [claude, chatgpt, gemini]
mvs_criteria:
  recurring: true
  consistent_methodology: true
  complex: true
  high_value: true
estimated_time_saved: "[X] min per use"
complexity: medium  # low, medium, high
use_cases:
  - [Specific use case 1]
  - [Specific use case 2]
  - [Specific use case 3]
---
```

**Description Tips (for Claude auto-invocation):**
- Include keywords users would naturally say
- Focus on WHAT user wants, not HOW Skill works
- Examples:
  - ✅ "Framework for analyzing quarterly financial data with revenue trends, cost analysis, profitability metrics"
  - ❌ "A 3-phase workflow with validation gates for financial analysis"

### Step 4: Write Methodology (Level 2)

Follow chosen pattern structure. Key principles:

**DO:**
- Be specific about process (not vague like "analyze carefully")
- Include validation checkpoints
- Provide ❌/✅ contrast examples
- Use consistent formatting (headings hierarchy)
- Add "IF condition THEN action" logic for adaptability

**DON'T:**
- Include user's specific data (that's substance)
- Make it domain-specific unless that's the intent
- Assume user knowledge (define terminology)
- Skip quality checks/validation gates

### Step 5: Add Examples (Optional but Recommended)

Show 2-3 filled examples of Skill in action:
- Example name
- Context user provided
- Expected output format
- How Skill was applied

### Step 6: Add References (Level 3, if needed)

For complex Skills, create separate reference files:
- Detailed explanations
- Advanced techniques
- Troubleshooting guides
- Domain-specific deep dives

Reference from Level 2 like: `→ See references/advanced-techniques.md`

### Step 7: Create .zip File

```
skill-name.zip
├── skill.md
├── references/ (if applicable)
│   └── *.md
└── examples/ (if applicable)
    └── *.md
```

### Step 8: Test with 3+ Scenarios

Use Skill with 3 different tasks in same domain:
- Simple scenario
- Medium complexity scenario
- Complex scenario

Verify:
- Skill methodology applies correctly
- No substance leaking from examples
- Validation gates work
- Output quality consistent

---

## Using a Skill

### In Claude (Automatic Invocation)

**Setup:**
1. Upload Skill .zip to Settings → Capabilities
2. Choose Skill type:
   - **Personal:** Available to you across all projects
   - **Project:** Only in specific project
   - **Plugin:** Shareable with others

**Usage:**
- Just describe your task naturally
- Claude auto-invokes if description matches
- You don't tag or explicitly call Skills
- Up to 8 Skills can compose automatically

**Example:**
```
User: "Create a Q3 financial analysis for the board meeting"
→ Claude auto-loads "Financial Analysis" Skill
→ Follows Skill methodology
→ Asks user for substance (Q3 data, focus areas)
```

### In ChatGPT/Gemini (Manual Attachment)

**Setup:**
1. Attach Skill .zip file to conversation (like any file upload)

**Usage:**
```
Using the [Skill Name] attached, [your specific task].

Context:
- [Substance you're providing]
- [Specific requirements]
- [Constraints]
```

**Example:**
```
Using the Financial Analysis Skill attached, analyze Q3 2025
performance for board presentation.

Context:
- Revenue: $1.2M (Q2: $1.04M)
- Churn: 3% (Q2: 4%)
- Target audience: Board of Directors
- Focus: Growth trajectory and retention trends
```

---

## Verifying Skill Quality

### C.L.E.A.R. Principles Checklist

**Concise:**
- [ ] Main file <10,000 tokens
- [ ] No unnecessary verbosity
- [ ] Instructions clear and direct

**Logical:**
- [ ] Clear hierarchical structure (headings flow logically)
- [ ] Sections in logical order
- [ ] Prerequisites before advanced steps

**Explicit:**
- [ ] Specific instructions (not vague)
- [ ] Terminology defined
- [ ] Success criteria clear
- [ ] Examples provided

**Adaptive:**
- [ ] Handles variations (conditional logic)
- [ ] Graceful degradation if data incomplete
- [ ] Works across different scenarios in domain

**Reflective:**
- [ ] Validation checkpoints throughout
- [ ] Quality gates (IF/THEN decision points)
- [ ] Output verification steps
- [ ] Self-checking mechanisms

### Methodology/Substance Separation Test

**Test each section:**
1. Could this apply to ANY task in this domain?
   - YES → Good (methodology)
   - NO → Bad (substance leaked in)

2. Does this require user to provide specifics?
   - YES → Good (substance stays with user)
   - NO → Check if you're being too prescriptive

**Common Leaks:**
- ❌ Hardcoded dates, names, numbers
- ❌ Specific company/project details
- ❌ User's personal preferences baked in
- ❌ Examples too specific (can't generalize)

**Fixes:**
- ✅ Use placeholders: [Date], [Project Name], [Metric]
- ✅ Make examples generic but clear
- ✅ Let user provide all specifics in context

### Token Count Check

**Main file (skill.md):**
- Minimum: 500 tokens (too short = not enough structure)
- Optimal: 2,000-5,000 tokens (sweet spot)
- Maximum: 10,000 tokens (too long = should split to Level 3)

**With references:**
- Total can be much larger (Level 3 only loads on demand)

**Check:** Use token counter or estimate:
- ~4 characters = 1 token
- 1,000 words ≈ 750 tokens

### Test Coverage

**Run Skill through 3+ diverse scenarios:**

**Scenario 1: Simple (baseline)**
- Minimal complexity
- All data provided
- Straightforward application

**Scenario 2: Medium (typical)**
- Moderate complexity
- Some missing data (test graceful degradation)
- Conditional logic triggered

**Scenario 3: Complex (stress test)**
- High complexity
- Multiple conditions
- Edge cases
- Tests full Skill capability

**What to verify:**
- Output quality consistent across all 3
- Methodology applies correctly
- Validation gates work
- No hallucinated substance
- User understands what to provide

---

## Improving an Existing Skill

### Diagnosis: Identify Issues

**Common Problems:**

1. **Too Vague (Output inconsistent)**
   - Symptom: Different results each time
   - Cause: Instructions not specific enough
   - Fix: Add explicit steps, examples, validation gates

2. **Too Specific (Not reusable)**
   - Symptom: Only works for one narrow use case
   - Cause: Substance leaked into methodology
   - Fix: Extract substance, generalize instructions

3. **Too Complex (Confusing)**
   - Symptom: Users don't understand what to provide
   - Cause: Too many steps, poor organization
   - Fix: Simplify, add overview, break into phases

4. **Missing Validation (Quality issues)**
   - Symptom: Output has errors, incomplete work
   - Cause: No quality gates or checkpoints
   - Fix: Add validation steps at each phase

5. **Wrong Pattern (Awkward to use)**
   - Symptom: Feels forced, doesn't match task nature
   - Cause: Workflow used for principles, or vice versa
   - Fix: Switch to correct pattern

### Improvement Process

**Step 1: Collect Feedback**
- Use Skill 5+ times
- Note: What worked? What didn't?
- Ask users: Confusing parts? Missing info?

**Step 2: Analyze Patterns**
- Review failed uses: Why did they fail?
- Review successful uses: What made them work?
- Look for common issues

**Step 3: Prioritize Fixes**

**High Priority (Fix immediately):**
- Incorrect methodology (wrong steps)
- Missing critical validation
- Substance leakage (not reusable)

**Medium Priority (Fix next version):**
- Vague instructions (add specificity)
- Missing examples
- Poor organization

**Low Priority (Nice to have):**
- Additional edge cases
- More references
- Optimization for tokens

**Step 4: Make Targeted Changes**

**Add Specificity:**
```markdown
❌ Before: "Analyze the data carefully"
✅ After:
1. Calculate mean, median, mode
2. Identify outliers (>2 std dev)
3. Check for trends (linear regression)
```

**Add Validation:**
```markdown
## Phase 1 Validation
- [ ] All required data present
- [ ] Data format correct (dates as YYYY-MM-DD)
- [ ] No missing values in key columns

**IF ANY FAIL:** Request missing data from user
**IF ALL PASS:** Proceed to Phase 2
```

**Add Examples:**
```markdown
**Example: Applying Step 2.3**

❌ **Incorrect approach:**
"Revenue is $1M" (no context, no comparison)

✅ **Correct approach:**
"Q3 revenue: $1.2M (+15% vs Q2: $1.04M, +8% vs Q3 2024: $1.11M)"
[Explanation: Provides absolute value, period-over-period, year-over-year]
```

**Generalize Substance:**
```markdown
❌ Before: "Focus on tech sector stocks in portfolio"
✅ After: "Focus on [sector] [asset type] in portfolio"
[User provides: sector = "tech", asset type = "stocks"]
```

**Step 5: Test Improvements**
- Use improved Skill with same 3 scenarios
- Compare output quality: Before vs After
- Verify issues resolved, no new issues introduced

**Step 6: Version Control**

Update YAML frontmatter:
```yaml
version: 1.1.0  # Was 1.0.0
updated: 2025-10-17
changelog: |
  v1.1.0 (2025-10-17):
  - Added Phase 2 validation gates
  - Generalized sector-specific language
  - Added 3 new examples
  - Improved specificity in Step 3.2
```

Keep old version as backup for 30 days.

---

## Common Mistakes to Avoid

### Mistake 1: Explaining What Sections Are

**Don't do this:**
```markdown
## Output Format
This section describes how to format your output.

The output should include:
1. A summary section at the top
2. Detailed analysis below
```

**Do this instead:**
```markdown
## Output Format

**Summary** (3-5 bullet points)
- Key finding 1
- Key finding 2

**Detailed Analysis**
### Revenue Trends
[Analysis here]

### Cost Structure
[Analysis here]
```

**Why:** Show structure, don't describe it. User sees the format directly.

---

### Mistake 2: Vague Process Instructions

**Don't do this:**
```markdown
Analyze the data thoughtfully and provide insights.
```

**Do this instead:**
```markdown
1. Calculate key metrics:
   - Mean, median, standard deviation
   - Period-over-period % change
   - Trend direction (linear regression slope)

2. Identify patterns:
   - Cyclical trends (seasonality)
   - Anomalies (>2σ from mean)
   - Inflection points (trend reversals)

3. Synthesize insights:
   - What's driving changes? (hypothesis)
   - What's the magnitude? (quantify)
   - What's the trajectory? (project forward)
```

**Why:** Specific steps = consistent output. Vague = randomness.

---

### Mistake 3: Mixing Methodology with Substance

**Don't do this:**
```markdown
Compare Q3 2024 revenue ($950K) to Q3 2025 revenue and calculate growth rate.
```

**Do this instead:**
```markdown
Compare [baseline period] revenue to [current period] revenue:
- Absolute change: $[current] - $[baseline]
- % change: ([current] - [baseline]) / [baseline] × 100

User provides:
- Baseline period and revenue
- Current period and revenue
```

**Why:** First version only works for one specific comparison. Second works for any comparison.

---

### Mistake 4: No Validation Gates

**Don't do this:**
```markdown
## Phase 1: Data Gathering
Collect all relevant data.

## Phase 2: Analysis
Analyze the data.
```

**Do this instead:**
```markdown
## Phase 1: Data Gathering
Collect:
- Revenue data (monthly, last 12 months)
- Cost data (variable + fixed)
- Customer metrics (acquisition, churn)

## Phase 1 Validation
- [ ] All 12 months present (no gaps)
- [ ] Revenue + costs reconcile to P&L
- [ ] Customer metrics match CRM export

**IF ANY FAIL:** Pause, request missing data
**IF ALL PASS:** Proceed to Phase 2

## Phase 2: Analysis
[Continue...]
```

**Why:** Validation prevents garbage-in-garbage-out. Catches issues early.

---

### Mistake 5: Wrong Pattern for Task

**Workflow used incorrectly:**
```markdown
## Step 1: Decide if refactoring is needed
Look at the code and decide.

## Step 2: Choose refactoring approach
Pick the best one.
```

**This should be Principle-Based:**
```markdown
## Principle 1: Refactor for Readability First
Code is read 10x more than written.

**Application:**
- When: Code works but is confusing
- How: Rename variables, extract functions, add comments
- Test: Can junior dev understand in <5 min?

**Guidance Pattern:** When users ask "Should I refactor?",
suggest: "Run the 5-minute comprehension test first"

**Example:**
❌ Premature refactoring: "Let me optimize this loop"
✅ Readability first: "Let me extract this 50-line function into named subfunctions"
```

**Why:** Rigid steps don't fit decision-making tasks. Principles provide flexible guidance.

---

## Platform-Specific Notes

### Claude
- **Auto-invocation:** Description field is matching criteria (use user intent keywords)
- **Composability:** Up to 8 Skills can work together automatically
- **Types:** Personal (user-wide), Project (scoped), Plugin (shareable)

### ChatGPT
- **Manual attachment:** User uploads .zip, explicitly references in prompt
- **Canvas integration:** Great for Workflow Skills producing documents
- **Routing system:** Combine with GPT-5 routing for complex tasks

### Gemini
- **Multimodal advantage:** Skills can reference images, diagrams
- **Workspace integration:** @Docs, @Sheets, @Drive + Skills = powerful
- **Code execution:** Skills can trigger Python for validation/calculation

---

## Quick Reference Card

### When to Create Skill
- Recurring (3+) ✅
- Consistent methodology ✅
- Complex (multi-step) ✅
- High-value (15+ min saved OR high-stakes) ✅

### Choose Pattern
- **Workflow:** Sequential steps → Financial Analysis
- **Principle-Based:** Coaching/decisions → Agentic Development
- **Reference:** Educational content → Prompting Patterns

### C.L.E.A.R. Quality Check
- **C**oncise: <10K tokens main file
- **L**ogical: Clear hierarchy, logical flow
- **E**xplicit: Specific steps, defined terms
- **A**daptive: Handles variations, conditionals
- **R**eflective: Validation gates, quality checks

### Methodology vs Substance
- **Methodology (Skill):** HOW to do the work
- **Substance (User):** WHAT specific work to do
- **Test:** "Works for 10 different tasks in same domain?"

### Progressive Disclosure
- **Level 1 (Description):** 100-150 tokens, metadata
- **Level 2 (Instructions):** 2,000-5,000 tokens, core methodology
- **Level 3 (Resources):** Variable, deep-dive references (load on demand)

---

## For LLMs: How to Help Users with Skills

### When User Asks for Skill Creation

1. **Validate MVS criteria first** (ask 4 questions)
2. **If NO to any:** Suggest traditional prompt instead
3. **If ALL YES:** Proceed with Skill creation
4. **Choose pattern together** (ask about task nature)
5. **Build incrementally:**
   - Start with YAML + Overview
   - Add core methodology
   - Add validation gates
   - Add examples
   - Review and refine
6. **Test with 3 scenarios** before finalizing

### When User Provides Existing Skill

1. **Read and understand** full structure
2. **Identify pattern** (Workflow/Principle/Reference)
3. **Check C.L.E.A.R. principles**
4. **Test methodology/substance separation**
5. **Use as intended:** Follow instructions precisely
6. **Suggest improvements** if quality issues found

### When User's Task Might Need Skill

**Detect signals:**
- User says "I do this often/regularly"
- Clear methodology emerges in conversation
- Multi-step process with validation needs
- High-value or high-stakes work

**Suggest:**
"This looks like a recurring workflow. Would you like to create a Skill so you don't have to explain the methodology each time?"

**Guide through creation if yes.**

---

**End of Primer**

**Key Takeaway for LLMs:** Skills are methodology templates that separate HOW (reusable process) from WHAT (user-specific substance). When helping users, focus on capturing generalizable methodology while ensuring substance stays with the user.

**Version:** 1.0 (2025-10-17)
