# Operations and security

## Never commit secrets

- `.env`, credential JSON, MongoDB connection strings, database passwords, API keys and access tokens must stay out of Git.
- Use Secret Manager for deployed services.
- Use least-privilege service accounts and database users.
- Rotate any credential that was accidentally committed or shared.

## Network safety

A lab may temporarily use public connectivity to simplify access. Do not use broad `0.0.0.0/0` access in production. Restrict source IPs, prefer private connectivity where supported, and require authentication on Cloud Run services unless public access is an intentional product requirement.

## Cost control

AlloyDB, Cloud Run, BigQuery, Cloud Storage and Agent Engine can incur charges. Review billing after each lab session. Delete only resources you intentionally created and have backed up. Never run project-wide deletion commands as a cleanup shortcut.
