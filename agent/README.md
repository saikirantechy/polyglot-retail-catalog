# ADK agent

The agent is defined in `agent/agent.py` and reuses the tool functions in
`app/tools.py`, so the same business logic powers:

- the Flask `/api/chat` endpoint (Gemini function calling), and
- the Google ADK / Vertex AI Agent Engine agent.

## Run locally

```bash
python -m pip install -r requirements-agent.txt
adk web
```

Open the ADK web UI and select the `agent` folder. To use a terminal instead:

```bash
adk run agent
```

## Configuration

The tools read environment variables through `app/config.py`:

| Variable | Purpose |
|---|---|
| `GOOGLE_CLOUD_PROJECT` / `PROJECT_ID` | Vertex AI project |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI location (`us-central1` by default) |
| `MODEL` | Gemini model, e.g. `gemini-2.5-flash` |
| `ALLOYDB_DSN` or `ALLOYDB_HOST` | AlloyDB connection |
| `MONGODB_URI` | MongoDB Atlas connection |
| `BIGQUERY_PROJECT` | Enables BigQuery analytics |

Without cloud configuration the tools fall back to the seeded SQLite demo
catalog, which is useful for testing prompts and tool selection offline.

## Deploy to Agent Engine

Follow the current Google Cloud ADK documentation to wrap `root_agent` with
`agent_engines.create(...)`. Keep credentials in Secret Manager and grant the
runtime service account only the roles it needs.
