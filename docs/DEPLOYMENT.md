# Private Web Deployment

Serenova can be deployed as a private Streamlit web app for controlled
consultant pilot use. Paid production use remains blocked until the release
evidence gates in `RELEASE_EVIDENCE.md` pass.

## Preflight

Run the checks before packaging:

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_references.py
python3 scripts/evaluate_model_outputs.py
python3 scripts/check_deployment_readiness.py
python3 scripts/generate_readiness_report.py
```

`check_deployment_readiness.py` should say private web pilot deployment is
ready. `generate_readiness_report.py` may still say paid production is blocked
until the external evidence exists.

## Required Secrets

Create a private `.env` from `.env.example`. Do not commit it.

Generate the encryption key with:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Required for hosted use:

- `SERENOVA_API_TOKEN`
- `SERENOVA_ADMIN_TOKEN`
- `SERENOVA_ENCRYPTION_KEY`
- `SERENOVA_PSEUDONYM_KEY`
- `SERENOVA_SESSION_RETENTION_DAYS`

Optional:

- `GROQ_API_KEY` for reviewed LLM synthesis.
- `SERENOVA_STORE_CLIENT_NAME=true` only if encrypted storage is active and
  raw-name retention is explicitly approved.

## Docker

Build:

```bash
docker build -t serenova-astro .
```

Run:

```bash
docker run --env-file .env \
  -p 8501:8501 \
  -v serenova_sessions:/app/runtime/sessions \
  -v serenova_feedback:/app/runtime/feedback \
  -v serenova_audit:/app/runtime/audit \
  serenova-astro
```

Open:

```text
http://localhost:8501
```

For phone testing on the same Wi-Fi network, open the host computer's local
network IP with port `8501`.

## Mobile Use

The Streamlit app is responsive and supports phone browsers for light session
entry and result review. For long consultations, tablet or laptop remains the
preferred device because expert JSON panels are dense.

Before sharing a hosted link with the consultant:

1. Confirm HTTPS is enabled by the hosting platform or reverse proxy.
2. Confirm only the consultant can access the app.
3. Confirm session storage is encrypted and backed up.
4. Confirm plaintext local session files are not packaged or uploaded.
5. Generate a readiness report and retain it with the pilot notes.

## Production Boundary

Private deployment readiness is not the same as paid-production approval.
Paid production still requires:

- 25 independently verified reference fixtures.
- Signed expert Jyotish review.
- Consultant pilot approval.
- Privacy review approval.
- Backup and recovery drill evidence.
