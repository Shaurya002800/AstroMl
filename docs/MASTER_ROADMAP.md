# Serenova Best-in-Class Roadmap

## Definition of "Best"

Serenova should be:

1. Astronomically reproducible.
2. Transparent about every convention and source.
3. Deep enough for an experienced consultant to inspect the evidence.
4. Conservative about uncertain, disputed, or birth-time-sensitive rules.
5. Tested against independent reference calculations.
6. Safe with client data and high-impact topics.
7. Measurably useful to the consultant through structured feedback.

It must not claim scientifically proven prediction accuracy. Astrology outputs
remain interpretive and require human review.

## Release Gates

### V0.5 Classical Depth

- [x] Machine-readable source and rule provenance.
- [x] D2, D3, D4, D12, and D30 working calculation modules.
- [x] Separate Jaimini-style rashi drishti implementation.
- [ ] D16, D24, and D60 after convention selection and cross-engine validation.
- [x] Varga boundary and nearby birth-time sensitivity warnings.
- [x] Expanded yoga conditions, cancellation checks, and strength evidence foundation.
- [x] Planetary strength framework beginning with transparent component scores.
- [ ] Full Shadbala only after formula-source and cross-engine validation.

Gate: every new formula has unit tests, source/convention metadata, and an
explicit validation status.

### V0.6 Independent Validation

- [x] Golden chart fixture format and internal regression baseline.
- [x] Comparison adapter for normalized trusted-software fixtures.
- [ ] At least 25 independently sourced reference charts covering sign boundaries, nodes, retrogrades,
  high latitudes, daylight-saving transitions, and varga boundaries.
- [x] Four internal edge-case regression charts covering baseline, high
  latitude, retrograde motion, and varga boundaries.
- [ ] Independent astrologer formula review.
- [x] Calculation discrepancy report.

Gate: no unexplained core-position discrepancy and documented tolerance for
all derived values.

### V0.7 Interpretation Evaluation

- [x] Rule-level claim provenance in generated reports.
- [x] Absolute-claim, fear-language, medical, legal, and financial safety checks.
- [x] Cross-section consistency and limited unsupported-claim evaluation.
- [x] Consultant usefulness feedback and false-positive tagging.
- [x] Versioned deterministic safety evaluation dataset.
- [x] Versioned deterministic-fallback model-output evaluation dataset.
- [ ] Versioned external-LLM output evaluation dataset after approved representative outputs exist.

Gate: all critical safety checks pass and unsupported-claim rate is measured.

### V0.8 Product Security

- [x] FastAPI service separated from the Streamlit consultant client.
- [x] Consultant/admin role tokens as an interim authorization layer.
- [x] Encrypted sessions, configurable retention, deletion, and export.
- [x] Pseudonymous client IDs and audit logging.
- [x] No raw client records committed to git.

Gate: threat model completed and privacy controls tested.

### V1.0 Operational Readiness

- [x] Consultant handbook and calculation assumptions.
- [x] Encrypted backup and recovery process.
- [x] Release/version tracking in every report.
- [ ] Expert-reviewed rule set and documented known limitations.
- [ ] Pilot sessions with structured feedback before paid production use.

Gate: consultant sign-off, validation report, privacy review, and rollback plan.

Use [EXPERT_REVIEW_PROTOCOL.md](EXPERT_REVIEW_PROTOCOL.md),
[PILOT_PROTOCOL.md](PILOT_PROTOCOL.md), and
[RELEASE_EVIDENCE.md](RELEASE_EVIDENCE.md) to retain the evidence required by
the production-status checks.
