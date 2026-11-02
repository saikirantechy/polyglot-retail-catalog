# Polyglot Retail Catalog

**A runnable polyglot-persistence ecommerce catalog for Google Cloud: AlloyDB + MongoDB Atlas + BigQuery + Gemini, with a Flask storefront, an MCP Toolbox configuration and a Google ADK agent.**

[![CI](https://github.com/saikirantechy/polyglot-retail-catalog/actions/workflows/ci.yml/badge.svg)](https://github.com/saikirantechy/polyglot-retail-catalog/actions/workflows/ci.yml)
[![CodeQL](https://github.com/saikirantechy/polyglot-retail-catalog/actions/workflows/codeql.yml/badge.svg)](https://github.com/saikirantechy/polyglot-retail-catalog/actions/workflows/codeql.yml)
[![Deploy to Cloud Run](https://img.shields.io/badge/deploy-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](.github/workflows/deploy-cloudrun.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![AlloyDB](https://img.shields.io/badge/AlloyDB-PostgreSQL-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/alloydb)
[![BigQuery](https://img.shields.io/badge/BigQuery-analytics-669DF6?logo=googlebigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![MCP Toolbox](https://img.shields.io/badge/MCP-Toolbox-6E4AFF)](https://googleapis.github.io/genai-toolbox/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-8E75B2?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Demo mode](https://img.shields.io/badge/demo%20mode-zero%20credentials-0f766e)](#demo-mode)

> **Learning project.** This is an independent implementation inspired by Google's *Build an Intelligent Ecommerce Catalog with Multi-database Persistence* codelab. It does not redistribute the codelab text or upstream sample assets. See [Attribution](#attribution).

---

## Why this repo

Most "polyglot persistence" samples stop at a diagram. This one runs:

- **Zero-setup demo mode** — SQLite mirrors the same domain model, so `pip install` + `python -m app` gives you a working storefront, chat assistant, analytics and API without a cloud account.
- **Real cloud switch** — set AlloyDB, MongoDB Atlas and BigQuery variables and the same services use the real stores. Partial configuration degrades gracefully (`hybrid` mode).
- **One tool layer** — `app/tools.py` powers both the in-app Gemini function-calling assistant and the Google ADK / Agent Engine agent.
- **Production-shaped** — Docker, non-root container, health check, Cloud Run deploy workflow, Workload Identity Federation, CI matrix, CodeQL, Dependabot.

## Feature tour

| Area | What you get |
|---|---|
| Storefront | Server-rendered catalog, category filters, search, price filter, product detail, similarity panel, interaction tracking |
| Assistant | `/api/chat` with Gemini tool calls, product cards, transparent tool trace, deterministic demo fallback |
| Catalog | AlloyDB `products_core_table`, optional pgvector image embeddings, tag-based similarity fallback |
| Attributes | MongoDB `product_details_collection` for flexible per-product attributes |
| Analytics | BigQuery `user_product_interactions` top-product and summary queries |
| Interactions | MongoDB `user_interactions_collection` (or SQLite demo store) |
| Agent | Google ADK `LlmAgent` sharing the exact same tools |
| Data platform | SQL scripts, seed data, MCP Toolbox template, Cloud Run deployment scripts |
| Quality | 26 pytest tests, Ruff lint, GitHub Actions CI, CodeQL, Dependabot |

---

## Architecture

### System flow

```mermaid
flowchart LR
    subgraph Client
        UI["Storefront / Chat UI<br/>Jinja + vanilla JS"]
    end

    subgraph Runtime["Cloud Run"]
        APP["Flask app<br/>API + web + assistant"]
        AGENT["Gemini / ADK agent<br/>function calling"]
        TOOLS["Shared tool layer<br/>app/tools.py"]
    end

    subgraph Data["Polyglot data plane"]
        A[("AlloyDB for PostgreSQL<br/>products, stock, pgvector")]
        M[("MongoDB Atlas<br/>attributes, interactions")]
        B[("BigQuery<br/>analytics")]
        GCS[("Cloud Storage<br/>product images")]
    end

    subgraph Platform
        TB["MCP Toolbox<br/>on Cloud Run"]
        VA["Vertex AI<br/>embeddings + Gemini"]
    end

    UI --> APP
    APP --> TOOLS
    APP --> AGENT
    AGENT --> TOOLS
    TOOLS --> A
    TOOLS --> M
    TOOLS --> B
    A -.-> VA
    GCS --> UI
    TB -. optional unified data tools .-> A
    TB -.-> M
    TB -.-> B
```

### Chat request sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Storefront UI
    participant API as Flask /api/chat
    participant A as Assistant
    participant T as Tool layer
    participant DB as Data stores

    User->>UI: "wireless headphones under $200"
    UI->>API: POST message + history
    API->>A: reply()
    alt Gemini configured
        A->>T: search_products(...)
        T->>DB: AlloyDB / Mongo / BigQuery query
        DB-->>T: Product rows
        T-->>A: JSON tool result
        A-->>API: Answer + collected products + tool trace
    else Demo / fallback
        A->>T: deterministic catalog search
        T->>DB: SQLite demo query
        DB-->>T: Seeded products
        A-->>API: Answer + products + notice
    end
    API-->>UI: reply, products, tool_calls, mode
    UI-->>User: Message + product cards
```

### Deployment topology

```mermaid
flowchart TB
    GH["GitHub Actions<br/>CI / CodeQL / container release"] --> AR["Artifact Registry"]
    AR --> CR["Cloud Run<br/>polyglot-retail-catalog"]
    CR --> SM["Secret Manager<br/>AlloyDB DSN, MongoDB URI"]
    CR --> AL["AlloyDB"]
    CR --> MG["MongoDB Atlas"]
    CR --> BQ["BigQuery"]
    CR --> VX["Vertex AI / Gemini"]
    CR --> MCP["MCP Toolbox on Cloud Run"]
    MCP --> AL
    MCP --> MG
    MCP --> BQ
    WIF["Workload Identity Federation"] -. keyless auth .-> GH
```

### Data ownership

| Store | Owns | Access path |
|---|---|---|
| AlloyDB | Product identity, SKU, price, stock, image embeddings | `PostgresCatalogRepository` / MCP `postgres-sql` |
| MongoDB Atlas | Flexible attributes, interaction events | `MongoRepository` / MCP `mongodb-find` |
| BigQuery | Aggregated interaction analytics | `BigQueryAnalyticsRepository` / MCP `bigquery-sql` |
| Cloud Storage | Product images | URL in `products_core_table.image_url` |
| SQLite | Demo mirror of catalog + interactions | `DemoRepository` |

---

## Demo mode

No cloud account, credentials or Docker required:

```bash
git clone https://github.com/saikirantechy/polyglot-retail-catalog.git
cd polyglot-retail-catalog

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

python -m pip install -r requirements.txt
python -m app
```

Open <http://localhost:8080>.

Demo mode seeds **12 products** and **32 interaction events** into `instance/demo.db`. The assistant uses deterministic intent parsing and tag-based similarity, and the UI shows a `demo` badge. Set `DEMO_MODE=true` to force demo mode even when cloud variables exist.

### Docker

```bash
docker build -t polyglot-retail-catalog .
docker run --rm -p 8080:8080 polyglot-retail-catalog

# Or with Compose (optional local MongoDB profile)
cp .env.example .env
docker compose up --build
docker compose --profile mongo up --build
```

---

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Mode, backends, product count, degraded status |
| `GET` | `/api/products` | Filter by `q`, `category`, `max_price`, `in_stock`, `sort`, `limit`, `offset` |
| `GET` | `/api/products/<uuid-or-sku>` | Product detail |
| `GET` | `/api/products/<uuid-or-sku>/similar` | Vector or tag similarity |
| `GET` | `/api/categories` | Distinct categories |
| `POST` | `/api/interactions` | Record `view`, `click`, `like`, `add_to_cart`, `purchase` |
| `GET` | `/api/products/<uuid-or-sku>/interactions` | Recent interaction events |
| `GET` | `/api/analytics/summary` | Counts, event breakdown, top products |
| `GET` | `/api/analytics/top-products` | Ranked engagement |
| `POST` | `/api/chat` | Assistant reply + product cards + tool trace |
| `GET` | `/` `/product/<sku>` `/chat` | Storefront pages |

```bash
curl "http://localhost:8080/api/products?category=Audio&max_price=200"

curl -X POST http://localhost:8080/api/interactions \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","product_id":"AUD-1001","event_type":"purchase"}'

curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me products similar to AUD-1001"}'
```

---

## Configuration

Copy `.env.example` to `.env`. Nothing is required for demo mode.

| Variable | Default | Effect |
|---|---|---|
| `DEMO_MODE` | `false` | Force SQLite + rule-based assistant |
| `DEMO_DB_PATH` | `instance/demo.db` | Demo database location |
| `SECRET_KEY` | dev value | Flask secret; set in production |
| `PROJECT_ID` / `GOOGLE_CLOUD_PROJECT` | empty | Enables Gemini when set |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex AI location |
| `MODEL` | `gemini-2.5-flash` | Gemini model |
| `ALLOYDB_DSN` or `ALLOYDB_HOST` + credentials | empty | Enables AlloyDB catalog |
| `MONGODB_URI` | empty | Enables MongoDB attributes + interactions |
| `MONGODB_DB` | `ecommerce_db` | MongoDB database |
| `BIGQUERY_PROJECT` | empty | Enables BigQuery analytics |
| `BIGQUERY_DATASET` | `ecommerce_analytics` | BigQuery dataset |
| `BIGQUERY_TABLE` | `user_product_interactions` | BigQuery table |
| `MCP_TOOLBOX_URL` | empty | Reported by health endpoint |

**Modes** are derived automatically: `demo` (no cloud stores), `hybrid` (partial), `cloud` (all three). Each backend falls back independently; a BigQuery outage falls back to the interaction store, and Gemini failures fall back to local search.

---

## Project structure

```text
.
├── app/
│   ├── __init__.py            Flask factory, error handlers
│   ├── __main__.py            python -m app
│   ├── config.py              env-driven settings + mode
│   ├── models.py              Product / Interaction
│   ├── tools.py               shared agent tools (ADK + Gemini)
│   ├── data/                  seeded products + interactions
│   ├── repositories/          SQLite, AlloyDB, MongoDB, BigQuery
│   ├── routes/                web + JSON API blueprints
│   ├── services/              catalog, interactions, analytics, assistants
│   ├── static/                CSS + vanilla JS
│   └── templates/             Jinja storefront, product, chat, error
├── agent/                     Google ADK agent package
├── alloydb/                   schema, verification, extensions, seeds
├── bigquery/                  analytics DDL
├── mongodb/                   collection notes
├── mcp-toolbox/               MCP Toolbox configuration template
├── scripts/                   env setup, Toolbox + Cloud Run deploy
├── tests/                     26 pytest tests (demo mode, no network)
├── .github/                   CI, CodeQL, deploy, release, templates
├── Dockerfile                 non-root, health-checked image
├── docker-compose.yml         app + optional MongoDB
├── requirements*.txt          base / cloud / agent / dev
└── pyproject.toml             Ruff + pytest config
```

---

## Cloud setup

Full detail is in [`docs/deployment.md`](docs/deployment.md). Short version:

1. **AlloyDB** — run `alloydb/01_schema.sql`, then `04_app_extension.sql` and optionally `05_seed_demo_products.sql` in AlloyDB Studio. Add `03_extensions_and_embeddings.sql` for pgvector.
2. **MongoDB Atlas** — create `ecommerce_db`, `product_details_collection`, `user_interactions_collection`; note [`mongodb/README.md`](mongodb/README.md). Store the URI in Secret Manager.
3. **BigQuery** — create `ecommerce_analytics` and run [`bigquery/01_analytics.sql`](bigquery/01_analytics.sql) with your project ID.
4. **MCP Toolbox** — copy `mcp-toolbox/tools.yaml.example` to `tools.yaml`, validate, store in Secret Manager, deploy with `scripts/deploy-toolbox.sh`.
5. **App** — `scripts/deploy-app.sh` builds with Cloud Build and deploys to Cloud Run. Or use the **Deploy to Cloud Run** GitHub workflow with Workload Identity Federation.

### Local cloud run

```bash
python -m pip install -r requirements-cloud.txt
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export ALLOYDB_DSN="postgresql://user:pass@host:5432/postgres"
export MONGODB_URI="mongodb+srv://..."
export BIGQUERY_PROJECT=your-project
python -m app
```

### ADK agent

```bash
python -m pip install -r requirements-agent.txt
adk web        # select the agent/ folder
adk run agent  # terminal
```

See [`agent/README.md`](agent/README.md).

---

## CI/CD workflows

| Workflow | Trigger | What it does |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | push/PR to `main` | Ruff + pytest on Python 3.11/3.12, Docker build |
| [`codeql.yml`](.github/workflows/codeql.yml) | push/PR + weekly | CodeQL Python analysis |
| [`deploy-cloudrun.yml`](.github/workflows/deploy-cloudrun.yml) | manual | Keyless WIF deploy to Cloud Run |
| [`container-release.yml`](.github/workflows/container-release.yml) | `v*.*.*` tags | Publish image to GHCR |
| [Dependabot](.github/dependabot.yml) | weekly | pip, Actions, Docker updates |

### Required repository secrets for deployment

| Secret | Purpose |
|---|---|
| `WIF_PROVIDER` | Workload Identity Provider resource name |
| `WIF_SERVICE_ACCOUNT` | Deploy service account email |

Secret Manager secrets `alloydb-dsn` and `mongodb-uri` are mounted by the deploy job.

### Local quality gates

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest
```

---

## Security notes

- Never commit `.env`, connection strings, service-account keys or `mcp-toolbox/tools.yaml`. `.gitignore` excludes them.
- Use Secret Manager for deployed credentials and least-privilege service accounts.
- The demo storefront has no authentication; do not expose it as a real commerce site without auth, TLS, CSRF protection and rate limiting.
- Restrict MongoDB network access; avoid `0.0.0.0/0` outside a disposable lab.
- Input lengths, event types, sort keys and identifiers are validated server-side; Jinja auto-escaping and `textContent` rendering protect the UI.

## Cost notes

AlloyDB, Cloud Run, BigQuery, Cloud Storage, Vertex AI and Agent Engine can incur charges. Start with scale-to-zero Cloud Run, small AlloyDB instances and BigQuery sandbox limits, then review billing after each lab session.

## Roadmap

- [ ] Image upload to Cloud Storage with signed URLs
- [ ] Real pgvector embedding generation command
- [ ] Mongo → BigQuery scheduled export
- [ ] Multi-turn ADK sessions with memory
- [ ] Playwright storefront smoke tests
- [ ] OpenTelemetry traces for tool calls

## Attribution

- [Google Codelab: Build an Intelligent Ecommerce Catalog with Multi-database Persistence](https://codelabs.developers.google.com/next26/polyglot-cross-cloud-retail)
- [Upstream sample repository](https://github.com/AbiramiSukumaran/polyglot-persist-ecommerce)
- [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/)

The code here is an independent implementation. Product names, seed data and images are illustrative. Keep upstream license and attribution notices when reusing upstream material.

## License

[MIT](LICENSE) © 2026 saikirantechy
