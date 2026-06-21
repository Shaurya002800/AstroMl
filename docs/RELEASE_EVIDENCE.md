# Release Evidence Register

Do not set an approval flag until the corresponding retained artifact exists.

| Status check | Environment flag | Required evidence |
| --- | --- | --- |
| Expert rule review | `SERENOVA_EXPERT_REVIEW_APPROVED` | Signed review using `EXPERT_REVIEW_PROTOCOL.md` |
| Consultant pilot | `SERENOVA_PILOT_APPROVED` | Pilot report using `PILOT_PROTOCOL.md` |
| Privacy review | `SERENOVA_PRIVACY_REVIEW_APPROVED` | Approved threat model and data-handling review |
| Backup drill | `SERENOVA_BACKUP_DRILL_COMPLETED` | Dated backup creation and restore-verification record |

The status API also requires authentication, encryption, no plaintext sessions,
passing fixtures, and at least 25 independently verified reference fixtures.
