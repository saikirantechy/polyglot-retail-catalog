# Deployment runbook

Checklist for moving this app from demo mode to Google Cloud. Cloud product flags and model availability change; verify commands against current documentation before execution.

## 0. Demo verification first

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest
python -m app
```

Confirm the catalog, product page, interaction tracking and chat work before adding cloud dependencies.

## 1. Project and APIs

- Select the intended Google Cloud project and enable billing.
- Enable AlloyDB, Cloud Run, Cloud Build, Artifact Registry, Secret Manager, Vertex AI and BigQuery APIs.
- Create the product image bucket.
- Confirm `REGION` (default `us-central1`).

## 2. AlloyDB

1. Provision the cluster and primary instance.
2. In **AlloyDB Studio** run:
   - `alloydb/01_schema.sql`
   - `alloydb/04_app_extension.sql`
   - optional `alloydb/05_seed_demo_products.sql`
   - `alloydb/03_extensions_and_embeddings.sql` for pgvector
3. Verify with `alloydb/02_verify.sql`.
4. Build `ALLOYDB_DSN` and store it in Secret Manager as `alloydb-dsn`.
5. If you use embeddings, grant the AlloyDB service agent the Vertex AI and Cloud Storage roles required by the codelab, then generate embeddings with the upstream SQL.

## 3. MongoDB Atlas

1. Create a cluster and a least-privilege user for `ecommerce_db`.
2. Restrict network access narrowly.
3. Create `product_details_collection` and `user_interactions_collection`; see `mongodb/README.md`.
4. Store the URI in Secret Manager as `mongodb-uri`.

## 4. BigQuery

1. Create dataset `ecommerce_analytics` (US multi-region recommended).
2. Run `bigquery/01_analytics.sql` after replacing `YOUR_PROJECT_ID`.
3. Set `BIGQUERY_PROJECT`, `BIGQUERY_DATASET` and `BIGQUERY_TABLE` for the app.

## 5. MCP Toolbox

```bash
cp mcp-toolbox/tools.yaml.example mcp-toolbox/tools.yaml
# fill environment-based credentials, then validate:
toolbox --config mcp-toolbox/tools.yaml --ui
```

Store the validated configuration in Secret Manager as `tools`, then run `scripts/deploy-toolbox.sh`. Keep `tools.yaml` out of Git.

## 6. Deploy the app

### Scripted

```bash
export PROJECT_ID=your-project
export PROJECT_NUMBER=your-project-number
export REGION=us-central1
bash scripts/deploy-app.sh
```

Required Secret Manager secrets: `alloydb-dsn`, `mongodb-uri`. The script builds with Cloud Build and deploys to Cloud Run.

### GitHub Actions

Configure Workload Identity Federation and add repository secrets `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT`, then run the **Deploy to Cloud Run** workflow. Set `demo_mode=false` for cloud stores or `true` for a credential-free demo deployment.

## 7. ADK agent

```bash
python -m pip install -r requirements-agent.txt
adk web
```

Deploy via the current Vertex AI Agent Engine documentation. Reuse `app/tools.py` so the agent and web app share business logic.

## 8. Validate end-to-end

- `GET /api/health` reports `cloud` (or the expected hybrid) mode and a product count.
- Catalog loads from AlloyDB and attributes from MongoDB.
- Interactions write to MongoDB and appear in analytics.
- BigQuery top-products returns data.
- Similar-product requests use pgvector when embeddings exist.
- Gemini answers cite tools; stopping Vertex access falls back to local search.
- Logs contain no secrets.
