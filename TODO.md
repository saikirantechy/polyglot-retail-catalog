# TODO

Status snapshot: 2026-11-02

## Done

- [x] Flask application factory, settings and graceful demo/cloud mode switching
- [x] SQLite demo repository with 12 products and 32 seeded interactions
- [x] AlloyDB catalog repository with optional columns and pgvector search
- [x] MongoDB interaction + flexible-attribute repository
- [x] BigQuery analytics repository with fallback to interaction store
- [x] Shared agent tool layer (`app/tools.py`) used by Gemini and ADK
- [x] Gemini function-calling assistant with rule-based fallback
- [x] Google ADK agent package (`agent/`)
- [x] Storefront UI: catalog, search, filters, product detail, similarity, chat
- [x] JSON API: products, categories, interactions, analytics, chat, health
- [x] MCP Toolbox configuration template
- [x] AlloyDB schema, extension and seed SQL
- [x] Dockerfile, Compose, non-root user, health check
- [x] 26 pytest tests and Ruff lint passing
- [x] CI, CodeQL, Cloud Run deploy, GHCR release workflows
- [x] Dependabot, issue forms, PR template
- [x] Professional README with badges and Mermaid diagrams
- [x] Repository published: https://github.com/saikirantechy/polyglot-retail-catalog

## Next (cloud validation)

- [ ] Create Workload Identity Federation provider and deploy service account
- [ ] Add `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT` repository secrets
- [ ] Provision AlloyDB, run `alloydb/01_schema.sql` + `04_app_extension.sql` + seed
- [ ] Create MongoDB Atlas collections and store `mongodb-uri` in Secret Manager
- [ ] Create BigQuery dataset/table and set `BIGQUERY_PROJECT`
- [ ] Store `alloydb-dsn` in Secret Manager
- [ ] Validate `mcp-toolbox/tools.yaml` and deploy Toolbox
- [ ] Deploy the app to Cloud Run and verify `/api/health` shows `cloud` mode
- [ ] Run `adk web` and verify tool calls against live data
- [ ] Generate real image embeddings and verify pgvector similarity

## Deferred roadmap

- [ ] Image upload to Cloud Storage with signed URLs
- [ ] CLI command to generate pgvector embeddings with Vertex AI
- [ ] MongoDB to BigQuery scheduled export
- [ ] Multi-turn ADK sessions with persistent memory
- [ ] Playwright storefront smoke tests
- [ ] OpenTelemetry traces for tool calls

## Notes

- Demo mode requires no cloud credentials: `python -m app`.
- Keep `.env`, `mcp-toolbox/tools.yaml` and connection strings out of Git.
- Update this file as items are completed; keep the README roadmap in sync.
