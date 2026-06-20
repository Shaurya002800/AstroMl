# Astrology Model Plan

## Goal

Build a private, consultant-facing astrology assistant that helps during live sessions. It should produce deep, structured, auditable Jyotish analysis while leaving final judgment with the human consultant.

The strongest architecture is not a black-box ML predictor. For astrology, the safer and more powerful design is:

1. Deterministic astronomical calculations.
2. A transparent classical-rule engine.
3. A curated knowledge base with source notes and caveats.
4. Retrieval and synthesis for explanation.
5. A guarded LLM layer that cannot invent facts outside the computed report.
6. Human review and session notes from the consultant.

## Why Not Pure ML

There is no reliable labeled dataset proving that a chart maps cleanly to life outcomes. A pure ML model would likely learn noise, produce overconfident claims, and become impossible to audit.

The model should instead predict in the astrology-specific sense: it should identify tendencies, periods, strengths, risk areas, and questions for deeper consultation according to the chosen Jyotish framework.

## V1 Scope

- Birth detail intake: name, date, exact/approximate time, place, latitude, longitude, timezone.
- D1 rashi chart with Lahiri sidereal positions.
- Nakshatra and pada for ascendant and planets.
- Planetary dignity with caveats.
- D9 Navamsa, D10 Dasamsa, D7 Saptamsa.
- Vimshottari mahadasha and antardasha.
- Sarvashtakavarga with validation total.
- Selected yogas with source notes and cancellation caveats.
- Consultant brief: overview, dasha focus, notable strengths, attention flags, career pointers, suggested session questions.
- LLM interpretation that only uses structured data.

## V2 Scope

- [x] Add Pratyantar dasha.
- [x] Add retrograde/combustion checks for all relevant planets.
- [x] Add Parashari graha drishti.
- [x] Add whole-sign house lordship placement.
- [ ] Add sign-based rashi drishti as a separate mode.
- [x] Add ownership-based functional tendencies and Yogakaraka flags.
- [x] Add dispositor chains, cycles, and final-dispositor detection.
- Add D2, D3, D4, D12, D16, D24, D30, D60 only after formula validation.
- [x] Add query-date transit positions and natal-house contacts.
- [ ] Add transit ingress/egress date windows and station windows.
- Add source references per rule in machine-readable JSON/YAML.
- Add golden-chart test fixtures verified against trusted astrology software.

## V3 Scope

### V0.4 Timing and Synthesis

- [x] Continuous slow-planet sign ingress/egress windows.
- [x] Nearest station windows for Mercury through Saturn.
- [x] Evidence synthesis separating structural support from current activation.
- [x] Initial career, relationships, finance, education, and wellbeing reviews.

### V0.5 Classical Depth

- [ ] Expand yoga rules and implement cancellation/strength conditions.
- [ ] Add D2, D3, D4, D12, D16, D24, D30, and D60 after formula validation.
- [ ] Add Shadbala and more complete planetary-strength analysis.
- [ ] Add birth-time rectification workflow and sensitivity reports.

### V0.6 Validation and Sources

- [ ] Machine-readable source registry per rule and convention.
- [ ] Golden-chart fixtures compared with trusted Jyotish software.
- [ ] Independent expert review of formulas and interpretation rules.
- [ ] Hallucination, absolute-claim, source-coverage, and regression evaluation.

### V0.7 Product and Learning Loop

- [ ] Retrieval-augmented explanation from curated classical/traditional notes.
- [ ] Consultant session observations and follow-up notes.
- [ ] Feedback scoring for useful/not-useful interpretations.
- [ ] Authenticated API separate from the website.
- [ ] Encryption, retention controls, audit logs, and client-data deletion.

## Safety Rules

- Never state that an event will certainly happen.
- Never present medical, legal, or financial advice as astrology-derived certainty.
- Always surface calculation assumptions: ayanamsa, house system, timezone, exactness of birth time.
- Preserve caveats from every rule.
- When a rule is simplified, label it as simplified.
- If birth time is approximate, warn that ascendant, houses, divisional charts, and dasha timing can shift.

## Product Shape For Sessions

The consultant should see:

- One-page summary first.
- Raw calculation panel second.
- Deeper interpretive sections third.
- Session questions and caveats always visible.
- Exportable session record after the call.

The client should not see raw AI output without consultant review.
