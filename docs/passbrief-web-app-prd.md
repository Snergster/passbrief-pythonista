# PassBrief Web Experience PRD

## Document Control
| Item | Value |
| --- | --- |
| Version | v0.1 (Placeholder) |
| Date | YYYY-MM-DD (Placeholder) |
| Author | INSERT NAME |
| Reviewers | Product, Safety, Flight Ops |
| Status | Draft for stakeholder review |

(Assumption: Python-based backend retained; frontend framework to be confirmed.)
(Assumption: Initial release targets Cirrus SR22T operations only.)

## Background and Current State
PassBrief currently delivers an interactive CLI workflow orchestrated by `BriefingGenerator` with embedded SR22T POH data (`performance/data.py`), METAR ingestion (`weather/manager.py`), Garmin Pilot PDF parsing (`garmin/pilot.py`), SID compliance checks (`briefing/sid.py`), CAPS planning (`briefing/caps.py`), and optional GPT-powered analysis gated by API key availability (`briefing/chatgpt.py`). Safety features include METAR freshness enforcement via `Config.METAR_MAX_AGE_MINUTES`, conservative rounding rules, magnetic variation accuracy tiers maintained by `AirportManager`, and manual fallback prompts to keep the pilot as final authority. Packaging into a single file for iOS Pythonista (`scripts/build_for_pythonista.py`) is actively used, and automated tests (`tests/test_sr22t_comprehensive.py`) cover calculators, managers, and workflow logic. Today’s users run PassBrief locally before flight to generate weather, passenger, takeoff, and arrival briefs.

## Goals and Non-Goals
**Goals**
- Deliver a browser-accessible PassBrief experience that preserves CLI accuracy and safety-critical logic (Certain).
- Enable multi-device access (desktop, tablet) with parity for SR22T performance calculations and Garmin/METAR inputs (High confidence).
- Provide operations and safety staff with reviewable digital briefs, including audit trails and annotated calculations (High confidence).
- Maintain Pythonista/iOS single-file build without regression (Certain).

**Non-Goals**
- Support for non-SR22T aircraft or performance data extensions (Certain).
- Real-time ATC or live traffic integrations (Certain).
- Automated flight plan filing or dispatch approvals (Certain).
- Open public beta without authentication guardrails (Speculative: dependent on compliance feedback).

## Target Users
- **Cirrus SR22T Pilot**: IFR-capable pilot generating departure/arrival briefings pre-flight on desktop or tablet.
- **Operations Coordinator**: Staff validating weather/performance inputs for fleet departures, requiring shared visibility.
- **Safety Officer**: Reviewer focused on compliance history, METAR freshness, and deviation tracking.

## User Stories
- As a Cirrus pilot, I can upload Garmin Pilot briefings through the web app to auto-populate my route so I avoid manual transcription.
- As a pilot, I can run performance calculations and review takeoff/landing distances with the same rounding and guardrails as the CLI, ensuring continuity.
- As a pilot, I can trigger AI passenger briefings when an OpenAI API key is configured, mirroring CLI gating.
- As operations staff, I can view a dashboard of generated briefs with timestamps, METAR sources, and status to coordinate departures.
- As a safety officer, I can retrieve historical briefs and confirm METAR age and magnetic variation source before sign-off.
- As a Pythonista power user, I can continue running the CLI workflow unchanged, even after web deployment.

## Functional Requirements
- **Account & Authentication**
  - MVP may operate without accounts; if introduced, support email-based invitations with role tagging (Speculative).
  - Require configurable auth toggle to match hanger security policy.
- **Data Inputs**
  - Upload Garmin Pilot PDFs; reuse existing parsing logic with file size and format validation.
  - Manual entry forms for departure, arrival, alternate airports, passenger count, fuel, and weight/balance details.
  - METAR fetch via NOAA API with freshness display; fallback manual entry if stale or unavailable.
- **Workflow Orchestration**
  - Expose the four CLI workflows (Weather/Route, Passenger Brief, Takeoff Brief, Arrival Brief) as navigable web steps.
  - Preserve sequential guidance and gating logic (e.g., weather must be refreshed before passenger brief is unlocked).
  - Provide real-time validation messages mirroring CLI warnings (e.g., tailwind alerts, METAR stale notifications).
- **Reporting & Exports**
  - Generate downloadable PDF/HTML reports matching CLI output sections, with metadata on data sources and rounding.
  - Produce share links with expiration for operations review (Speculative: dependent on hosting security).
- **AI Integrations**
  - Maintain optional GPT analysis gated by stored API key; never expose key client-side.
  - Log AI prompts/responses for audit with opt-out for privacy-sensitive operations (Speculative).
- **Admin & Monitoring**
  - Basic health dashboard displaying METAR API status, PDF parsing errors, and recent brief counts.
  - Hooks for logging (existing `logging_utils`) with structured JSON output for integration.

## Non-Functional Requirements
- **Safety & Reliability**: Preserve deterministic calculations; double-run critical calculations before presenting; flag any discrepancy.
- **Regulatory Compliance**: Surface disclaimers from README; log data sources for each brief to support FAA oversight.
- **Security**: Encrypt briefs at rest; TLS in transit; API keys stored server-side with secrets manager (Speculative: cloud provider dependent).
- **Performance**: Page load under 2s on LTE; METAR fetch under 5s with cached fallback; concurrency target 50 pilots/hour.
- **Availability**: Target 99.5% uptime for hosted service; offline fallback allows pilot to download minimal data for local CLI execution.
- **Usability**: Responsive design optimized for 11-inch tablet landscape and 13-inch laptop; keyboard-only navigation supported.

## System Overview
Proposed architecture layers the existing PassBrief modules behind a web API while preserving CLI entry points.

```
[Browser SPA] ⇄ HTTPS ⇄ [Web Backend (FastAPI or Flask) (Speculative)] ⇄ Existing PassBrief Modules
                                      ↓
                     [Task Queue for async METAR fetch & PDF parsing (Speculative)]
                                      ↓
                [Persistent Store: Postgres/SQLite + S3-equivalent for PDFs (Speculative)]
```

- Backend imports `BriefingGenerator` helpers but exposes functions via service adapters; CLI continues calling the same classes.
- METAR fetch runs async with timeout mirroring `WeatherManager` logic; manual fallback prompts surfaced via UI modals.
- Garmin PDF uploads stored temporarily, parsed via existing `GarminPilotBriefingManager`, and redacted after report generation.
- Performance and SID/CAPS calculations run server-side using existing modules, with results serialized to the frontend.
- Pythonista build pipeline remains untouched by gating web-specific code behind feature flags or separate module entry points.

## Release Plan
| Phase | Scope | Acceptance Criteria |
| --- | --- | --- |
| MVP Parity | Web workflows for Weather/Passenger/Takeoff/Arrival; Garmin upload; METAR fetch; PDF export; no accounts | Pilot completes full brief with identical numerical outputs vs CLI (± rounding rules); Pythonista build passes tests |
| Enhanced UX | Dashboard, historical briefs, annotations, AI prompt logging, responsive refinements | Ops coordinator reviews two distinct briefs without CLI; UI passes tablet usability review |
| Advanced Analytics | Trend analysis, safety alerts, admin dashboard, multi-user roles | Safety officer retrieves 30-day incident view; alert thresholds configurable without code |

## Success Metrics and Validation
- 95% of generated briefs match CLI calculations within existing tolerances during dual-run validation.
- 80% of targeted pilots adopt the web workflow within 60 days while CLI usage remains stable.
- Zero safety incidents attributable to calculation errors post-launch.
- METAR freshness violations <2% of briefs; alerts acknowledged within 10 minutes.
- Quarterly audit confirms compliance logs include data sources and AI usage notes.
- Validation plan: regression tests on calculators/managers, automated diff of CLI vs API outputs, pilot usability walkthroughs, safety officer sign-off gates before phased rollout.

## Risks and Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Safety-critical miscalculation | Catastrophic flight risk | Reuse existing calculator modules; dual-run outputs; human-in-the-loop review before release |
| METAR/API latency | Delayed briefs | Implement caching and fallback manual entry; display stale time banners |
| Magnetic variation drift | Heading inaccuracies | Continue three-tier magnetic handling; schedule annual data refresh |
| AI hallucinations | Passenger misinformation | Keep AI optional and clearly labelled; require manual confirmation before sharing |
| Web auth gaps | Unauthorized access | Ship without accounts only for controlled intranet; plan role-based access before external hosting |
| Pythonista regression | Loss of mobile workflow | Maintain separate entry point; run build script in CI for every change |

## Dependencies and Open Questions
- Hosting platform decision (e.g., Azure, AWS, on-prem) (Speculative).
- Choice of SPA framework (React vs Vue) and alignment with in-house expertise (Speculative).
- Secrets management approach for API keys and GPT tokens.
- FAA/flight department compliance review cycle for new digital workflows.
- Storage policy for archived briefs and retention timeline.
- Requirement for SSO or integration with existing pilot portals.

## Next Steps
- Establish architecture spike to wrap `BriefingGenerator` methods with API endpoints and confirm parity.
- Draft UI wireframes for each workflow step using CLI output as baseline.
- Align with compliance on data retention, audit logging, and hosting guardrails.
- Configure automated regression harness to compare CLI vs API outputs on sample flight scenarios.

**Learning Strategy**
1. Review existing tests (`tests/test_sr22t_comprehensive.py`) to understand safety assertions before coding.
2. Prototype a minimal FastAPI adapter locally to explore serialization of current briefing outputs (Speculative exploratory task).
3. Shadow safety officer expectations by summarizing METAR freshness and magnetic variation handling in documentation addendum.
