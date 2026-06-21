# Threat Model

## Sensitive Data

- Birth date and exact time
- Birth location
- Client name or reference
- Consultation interpretation and feedback

## Main Risks

- Session files committed to source control
- Unencrypted local storage
- Shared API tokens
- Logs containing birth details
- Feedback notes containing identifying information
- Accidental exposure through backups or screenshots

## Implemented Controls

- Session and audit files are gitignored.
- Raw names are omitted by default.
- Stable pseudonyms require a separate secret.
- Session encryption uses Fernet authenticated encryption.
- Plaintext session storage is denied by default.
- API report/feedback and administrative endpoints use separate configured tokens.
- Token comparison is constant-time.
- Session export and deletion validate filenames against path traversal.
- Audit records omit birth data.
- Feedback free text is omitted by default.
- Retention cleanup is configurable.
- A migration utility encrypts legacy plaintext sessions; source deletion is explicit.

## Remaining Controls Before Production

- Move from shared role tokens to managed user identities and short-lived tokens.
- Store encryption keys in an operating-system or cloud secret manager.
- Add encrypted backups and tested recovery.
- Add rate limiting and network access controls.
- Complete privacy/legal review.
