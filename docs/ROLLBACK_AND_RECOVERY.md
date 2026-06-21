# Rollback and Recovery

## Release Rollback

1. Keep the previous tested application revision available.
2. Stop the current Streamlit/API processes.
3. Restore the previous revision without modifying session archives.
4. Run unit tests and reference validation.
5. Start the API on localhost and verify health/auth.
6. Start the consultant client and generate a non-client sample report.

## Session Backup

Only encrypted `.json.enc` sessions are included. The backup command refuses
to proceed if plaintext session files exist.

```bash
export SERENOVA_BACKUP_DIR="/secure/backup/location"
python3 scripts/backup_sessions.py
```

Each archive contains a SHA-256 manifest and is verified immediately.

## Key Recovery

The Fernet encryption key is required to decrypt sessions. Losing the key makes
the sessions unrecoverable. Store it in a secret manager and keep a separately
protected recovery copy. Never commit it to the repository or include it in the
same archive as the encrypted sessions.
