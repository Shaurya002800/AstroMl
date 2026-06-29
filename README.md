# Serenova Astrology Session Tool

Internal astrology consultation assistant for generating structured Vedic chart data and a guarded session interpretation.

This is not the public website. The intended user is the consultant during a live session.

## Current Architecture

1. Birth details are entered in Streamlit.
2. Swiss Ephemeris computes sidereal planetary positions using Lahiri ayanamsa.
3. Deterministic modules calculate chart features: D1, D9, D10, D7, Vimshottari dasha through Pratyantar, dignity, motion, combustion, whole-sign house lordships, functional roles, dispositors, Parashari aspects, query-date transits and timing windows, Ashtakavarga, selected yogas, and bounded domain reviews.
4. `astrology_model.py` converts computed facts into a consultation brief with caveats, confidence notes, and suggested follow-up questions.
5. `presentation.py` turns the same facts into a conclusion-first report in English, Hindi, or Hinglish for non-expert readers.
6. The guarded LLM layer remains optional for reviewed consultant synthesis; the default user-facing report is deterministic.

The Streamlit screen shows a production-readiness panel with the current engine
status, independent-fixture progress, blocked release gates, and the next
evidence needed before paid production use.

The birth-place picker covers all 28 Indian states and 8 union territories
with 158 major cities and towns, including Bijnor district's urban local-body
towns. City-centre coordinates are approximate; use the manual location option
for villages, overseas births, or more precise coordinates.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
streamlit run src/app.py
```

Set `GROQ_API_KEY` in your environment before generating LLM interpretations.

For the authenticated internal API:

```bash
export SERENOVA_API_TOKEN="replace-with-a-secret"
export SERENOVA_ADMIN_TOKEN="replace-with-a-different-secret"
uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Generate and configure a Fernet key before saving sessions:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
export SERENOVA_ENCRYPTION_KEY="generated-key"
```

Raw client names are not stored by default. Set
`SERENOVA_STORE_CLIENT_NAME=true` only when encrypted storage is active. Set
`SERENOVA_PSEUDONYM_KEY` for stable pseudonymous references and
`SERENOVA_SESSION_RETENTION_DAYS` for automatic local retention cleanup.
`SERENOVA_SESSION_DIR` can point session storage at a dedicated encrypted
volume or an isolated test directory.

Plaintext session storage is denied by default. It can be enabled only for
deliberate local development with `SERENOVA_ALLOW_PLAINTEXT_SESSIONS=true`.

Legacy plaintext sessions can be encrypted after configuring the key:

```bash
python3 scripts/migrate_legacy_sessions.py
python3 scripts/migrate_legacy_sessions.py --delete-plaintext
```

The first command preserves plaintext sources for review. The second removes
each plaintext file only after its encrypted replacement is written.

Production status remains false until the independent fixture target is met and
review evidence is approved through `SERENOVA_EXPERT_REVIEW_APPROVED`,
`SERENOVA_PILOT_APPROVED`, `SERENOVA_PRIVACY_REVIEW_APPROVED`, and
`SERENOVA_BACKUP_DRILL_COMPLETED`. Set these only after the corresponding
signed review or drill artifact exists.

## Deploy For Private Pilot

The app includes Streamlit server config, a Dockerfile, a safe `.env.example`,
and a deployment readiness check. See [Private Web Deployment](docs/DEPLOYMENT.md).

```bash
python3 scripts/check_deployment_readiness.py
docker build -t serenova-astro .
docker run --env-file .env -p 8501:8501 serenova-astro
```

Private web pilot deployment can be technically ready before paid-production
approval. The production-readiness panel and readiness report remain the source
of truth for external validation, expert review, privacy approval, and backup
evidence.

## Design Principle

The AI should not invent astrology. The trusted source of astrological facts is the deterministic calculation and rule engine. The LLM is only a translator and session-writing assistant.

Astrology should be presented as interpretive guidance, not guaranteed prediction. The tool must avoid absolute claims, medical/legal/financial certainty, and fear-based language.

## Current Conventions

- Lahiri ayanamsa.
- Whole-sign houses for lordships, yogas, and Parashari aspects.
- Mean lunar node for Rahu; Ketu is derived at 180 degrees.
- Node aspects are excluded because Jyotish traditions differ.
- Combustion thresholds are explicit working conventions and are returned with the computed result.
- Functional roles are ownership-based tendencies, not unconditional benefic/malefic verdicts.
- Transits are mapped from natal Ascendant and Moon and must be combined with natal and dasha evidence.
- Domain support and activation scores summarize evidence; they are not outcome probabilities.
- Every major rule family exposes source, convention, and validation-status metadata.
- Generated interpretations are rejected if deterministic safety checks detect absolute, fear-based, medical, or financial directives.
- A deterministic interpretation fallback remains available if the external LLM fails or is rejected.
- Ambiguous and nonexistent daylight-saving clock times require an explicit conversion policy.
- The main result hides scores and technical chart mechanics by default, shows practical conclusions first, and keeps expert evidence in a collapsed panel.
- English, Hindi, and Hinglish outputs are generated from the same structured facts and preserve the same priority order.

## Development Checks

```bash
python3 -m unittest discover -s tests
python3 src/report.py
python3 scripts/validate_references.py
python3 scripts/evaluate_model_outputs.py
python3 scripts/summarize_feedback.py
python3 scripts/generate_readiness_report.py
python3 scripts/check_deployment_readiness.py
```
