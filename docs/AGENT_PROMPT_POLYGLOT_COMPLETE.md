# Master prompt — Complete and production-upgrade the repository

Use this prompt with GitHub Copilot Agent, Cursor, Claude Code, or another coding agent that has access to the repository.

## MASTER ENGINEERING TASK

### Polyglot Retail Catalog — Complete Implementation, Audit, Fix & Production Upgrade

Repository: https://github.com/saikirantechy/polyglot-retail-catalog

Act as a Principal Cloud Architect, Senior Python Engineer, Full-Stack Developer, Google Cloud Specialist, Database Engineer and AI Agent Engineer.

Your responsibility is to inspect, complete, debug, test and professionally upgrade the EXISTING repository.

Do not create a replacement project. Do not delete working functionality. Preserve the existing architecture, folder structure, Git history and useful implementations.

## 1. Project vision

Build a complete intelligent ecommerce catalog using Google Cloud's polyglot persistence architecture.

Technology stack:

- AlloyDB for PostgreSQL
- pgvector
- Google ML Integration
- Google Cloud Storage
- MongoDB Atlas
- BigQuery
- MCP Toolbox for Databases
- Gemini
- Google Agent Development Kit (ADK)
- Vertex AI Agent Engine
- Python / Flask
- Google Cloud Run
- Docker
- GitHub Actions

Official learning reference:
https://codelabs.developers.google.com/next26/polyglot-cross-cloud-retail

Original sample repository:
https://github.com/AbiramiSukumaran/polyglot-persist-ecommerce

Use these as technical references. Implement the functionality independently, preserve required attribution and license notices, and do not reproduce the complete codelab text or copyrighted sample assets verbatim.

## 2. Phase 1 — Repository audit

Before editing anything:

1. Inspect every existing directory and file.
2. Read README, requirements, configuration, SQL, Python modules, frontend templates, Dockerfiles and GitHub Actions.
3. Identify existing functionality and incomplete implementations.
4. Detect duplicate code, dead files, missing modules and inconsistent imports.
5. Identify broken environment variables and hardcoded credentials.
6. Check dependency compatibility.
7. Inspect all branches and determine which contain useful work. Do not merge or delete branches automatically.
8. Identify the actual application entry point and deployment architecture.

Create:

- docs/PROJECT_AUDIT.md
- docs/IMPLEMENTATION_ROADMAP.md
- docs/ARCHITECTURE.md

Produce a prioritized issue list with severity, affected files and proposed fixes.

Do not stop after producing the audit. Continue implementation.

## 3. Phase 2 — AlloyDB

Implement and verify:

- Product core table
- UUID product identifiers
- SKU uniqueness
- Price and inventory
- SKU indexes
- pgvector extension
- google_ml_integration extension
- 1,408-dimensional image embeddings
- Vertex AI multimodal image embedding generation
- Similarity search
- Product inventory retrieval
- Reliable connection pooling and error handling

Required SQL:

- alloydb/schema.sql
- alloydb/seed.sql
- alloydb/indexes.sql
- alloydb/extensions.sql
- alloydb/embeddings.sql
- alloydb/verification.sql

Use idempotent database migrations where possible.

Prevent duplicate seed records.

Validate that image objects exist before attempting embedding generation.

Never train or generate embeddings from missing or invalid image data.

## 4. Phase 3 — MongoDB Atlas

Implement:

- ecommerce_db
- product_details_collection
- user_interactions_collection

Features:

- Product metadata
- Product specifications
- Product attributes
- User interaction tracking
- Views and click events
- Search and filtering
- Document validation
- Index creation
- Connection pooling

Create import and verification scripts.

Support the official codelab sample datasets without requiring manual document-by-document insertion.

## 5. Phase 4 — BigQuery

Implement:

- ecommerce_analytics dataset
- user_product_interactions table
- Analytics queries
- Product engagement metrics
- Interaction scoring
- Aggregation queries
- Data validation
- ETL workflows

Add reusable SQL under bigquery/.

Use parameterized queries and avoid unsafe SQL construction.

## 6. Phase 5 — MCP Toolbox

Audit the current MCP configuration and fix it.

Implement:

- AlloyDB data source
- MongoDB data source
- BigQuery data source
- Product search tools
- Product detail tools
- Inventory lookup tools
- Similarity search tools
- User interaction tools
- Analytics tools

Requirements:

- Validate tools.yaml against the actual installed Toolbox version.
- Use official versioned installation and container instructions.
- Support local development and Cloud Run deployment.
- Use Secret Manager for sensitive connection configuration.
- Implement health checks.
- Implement meaningful startup and connection diagnostics.

IMPORTANT CURRENT BUG:

MCP Toolbox currently crashes in Google Cloud Shell with:

Segmentation fault

This happens when executing:

- ~/toolbox --version
- ~/toolbox --config tools.yaml --ui
- ~/toolbox --config tools.yaml --ui --enable-api

Investigate binary integrity, architecture compatibility, version compatibility and runtime dependencies.

Do not assume port 5000 is the root cause.

If the local binary is incompatible, implement a verified container-based development and deployment workflow.

Never claim Toolbox is working unless its health endpoint and UI have actually been tested.

## 7. Phase 6 — Gemini and ADK Agent

Build a functional ecommerce AI agent using Google's ADK and Gemini.

Agent capabilities:

1. Natural-language product discovery.
2. Product recommendations.
3. Image-based similarity search.
4. Product attribute filtering.
5. Real-time stock verification.
6. Product detail retrieval.
7. User interaction analysis.
8. Review and feedback analysis when review data exists.
9. BigQuery analytics.
10. Multi-database tool orchestration.

The agent must use MCP Toolbox tools instead of duplicating database access logic.

Implement:

- Agent definition
- Instructions
- Tool registration
- Session management
- Error handling
- Logging
- Conversation context
- Structured response schemas

Do not fabricate product availability, reviews, inventory or analytics.

The agent must distinguish unavailable data from zero-valued data.

## 8. Phase 7 — Flask storefront

Complete the existing application.

Required pages:

- Home
- Product Catalog
- Product Details
- ETL & Analytics
- AI Agent

Required features:

- Responsive design
- Search
- Category filtering
- Product cards
- Product image loading
- Product details
- Inventory indicators
- User interaction tracking
- Analytics dashboard
- AI shopping assistant

Use the existing UI architecture where possible.

Improve:

- Visual hierarchy
- Navigation
- Loading states
- Empty states
- Error messages
- Accessibility
- Mobile responsiveness

Avoid unnecessary redesigns that break existing functionality.

## 9. Phase 8 — Cloud deployment

Implement complete deployment support:

- Dockerfile
- .dockerignore
- Cloud Run deployment configuration
- MCP Toolbox deployment
- Secret Manager integration
- Service account permissions
- Health checks
- Environment configuration
- Logging and monitoring

Support:

- Local development
- Docker development
- Google Cloud deployment

Do not hardcode project IDs, passwords, regions, connection strings or service URLs.

## 10. Phase 9 — Security

Implement:

- .env.example
- Comprehensive .gitignore
- Secret Manager integration
- Least-privilege IAM
- Secure MongoDB access
- Secure AlloyDB connectivity
- Input validation
- Error handling without leaking credentials

Scan the complete Git working tree and tracked history for accidentally committed secrets.

Do not print secret values in logs.

Do not use 0.0.0.0/0 as a production security recommendation.

Never commit service-account JSON keys, private keys, database passwords or tokens.

## 11. Phase 10 — Testing

Create automated tests for:

- Database connections
- Database schemas
- Product CRUD
- SKU uniqueness
- Inventory lookup
- Vector search
- MongoDB retrieval
- BigQuery queries
- MCP tools
- ADK agent tools
- Flask routes
- API responses
- Environment configuration

Add:

- pytest
- Unit tests
- Integration tests
- Mock services for tests that cannot access cloud resources
- GitHub Actions CI

Tests must not require paid cloud resources to run basic unit-test suites.

## 12. Documentation

Create a professional documentation structure:

```text
docs/
  PROJECT_AUDIT.md
  ARCHITECTURE.md
  IMPLEMENTATION_ROADMAP.md
  LOCAL_SETUP.md
  GOOGLE_CLOUD_SETUP.md
  ALLOYDB_SETUP.md
  MONGODB_SETUP.md
  BIGQUERY_SETUP.md
  MCP_TOOLBOX_SETUP.md
  AI_AGENT_SETUP.md
  CLOUD_RUN_DEPLOYMENT.md
  TROUBLESHOOTING.md
  SECURITY.md
```

Update the root README with:

- Project overview
- Architecture diagram
- Technology stack
- Features
- Prerequisites
- Installation
- Configuration
- Local development
- Testing
- Deployment
- Screenshots placeholders
- Troubleshooting
- Credits and references

## 13. Engineering execution rules

Follow this order:

1. Audit the current repository.
2. Fix critical startup and dependency issues.
3. Complete database schemas and migrations.
4. Complete MCP Toolbox.
5. Complete the ADK agent.
6. Complete Flask application integration.
7. Complete deployment.
8. Add tests.
9. Update documentation.
10. Run final validation.

For every implementation:

- Inspect existing files before editing.
- Reuse existing modules where appropriate.
- Make small, logically grouped changes.
- Avoid unnecessary rewrites.
- Run tests after meaningful changes.
- Fix regressions immediately.
- Do not introduce fake implementations or placeholder success responses.
- Do not claim cloud deployment succeeded without verifying it.
- Do not delete useful existing features.

If credentials or external cloud resources are unavailable, implement the code, mocks, configuration templates and documented setup steps. Clearly mark what remains dependent on external access.

## 14. Final deliverables

The finished repository must have:

- Complete runnable application
- Working database integrations
- MCP Toolbox configuration
- Functional Gemini / ADK agent
- Responsive Flask storefront
- Docker configuration
- Cloud Run deployment support
- Secure environment templates
- Automated tests
- GitHub Actions CI
- Complete documentation
- Architecture diagram
- Troubleshooting guide

At the end, generate:

docs/FINAL_IMPLEMENTATION_REPORT.md

Include:

- What was already working
- What was fixed
- New files
- Modified files
- Tests executed
- Test results
- Outstanding blockers
- Cloud resources requiring manual setup
- Exact local startup commands
- Exact deployment commands

Start by inspecting the repository. Then execute the roadmap and implement the actual fixes. Do not merely generate a plan or a list of suggestions.

## How I recommend executing it

Use your existing repository's root folder and open the coding agent in that workspace.

Repository to work on:

https://github.com/saikirantechy/polyglot-retail-catalog

Important: Ask the agent to audit first, then fix in stages. Do not ask it to rewrite everything in one pass.

One especially important point: the repository currently advertises a zero-credential demo mode. The coding agent should verify that this is genuinely functional and does not silently substitute mock data for real database results.

Suggested project outcome: a fully documented, reproducible Google Cloud polyglot ecommerce application that can be demonstrated as a Vexlo engineering project, not just a copy of a codelab.
