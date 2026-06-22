# SMB Financial Health & Cash Flow Intelligence Platform - Project Context Document for Claude Sessions

## Project Overview

This project is an end-to-end data engineering and predictive analytics platform. It ingests raw financial data from small businesses via the Plaid and QuickBooks APIs, transforms that unstructured JSON data into clean analytical tables, runs machine learning models to predict cash flow and detect anomalies, and serves these insights to a frontend dashboard.

The Business Value: 82% of small businesses fail due to cash flow issues. This tool moves beyond standard accounting by using ML to provide forward-looking risk signals, anomaly alerts, and receivables aging predictions based on existing transactional data.

## Technical Architecture 

* We are employing a modern ELT (Extract-Load-Transform) architecture using open-source and free-tier cloud solutions.

* Ingestion: Python requests, GitHub Actions (for scheduling), Plaid API (Sandbox), QuickBooks API (OAuth Sandbox).

* Storage (Operational & Analytical): PostgreSQL (Neon cloud — free tier, serverless Postgres).

* Transformation: dbt-core 1.11.11 + dbt-postgres 1.10.1 (Local/CLI, Python 3.12).

* Machine Learning: Local Python (scikit-learn, prophet), models exported as .pkl.

* Serving API: FastAPI hosted on Render or Koyeb.

* Frontend: Streamlit Community Cloud.


## Data Strategy & Schema Design

```text
We are strictly following the ELT pattern.

The raw_stage schema: Data is ingested exactly as it arrives from the APIs and dumped into PostgreSQL JSONB columns.

plaid_transactions: Uses the "Envelope Pattern." Contains 1 row with a massive JSON payload. Transactions must be unpacked using Postgres jsonb_array_elements().

quickbooks_invoices & quickbooks_payments: Uses the "Resource Stream Pattern." Contains 1 row per entity.

The analytics schema: This is where dbt will take the raw JSONB data, parse it, clean it, and build structured, relational tables (e.g., monthly_burn_rate, cash_flow_forecast).
```

## Repository Structure

```text
The project operates as a monorepo:

/SMB-Financial-Health-Platform
├── .github/workflows/    # CI/CD and automated ingestion schedules
├── api/                  # FastAPI application
├── database/             # schema.sql and verification_queries.sql
├── dbt_project/          # dbt models, schemas, and tests
├── frontend/             # Streamlit application
├── ingestion/            # ingest.py and token helper scripts
├── ml_models/            # Jupyter notebooks and .pkl model files
├── .env                  # Secret keys (Git-ignored)
├── .gitignore            # Hides venv/, .env, __pycache__, etc.
└── requirements.txt      # Python dependencies
```


## Current Progress & Roadmap

* [x] Phase 1: Local Environment & Data Ingestion (COMPLETE)

- PostgreSQL installed and smb_finance database created.

- /database/schema.sql executed to create the raw_stage tables with JSONB columns.

- Plaid and QuickBooks API keys acquired and stored in local .env.

- /ingestion/ingest.py script written to successfully extract Sandbox data and load it into local Postgres.

- Initial queries verified (Data successfully unpacked using ->> and jsonb_array_elements).

- Project committed to GitHub with a secure .gitignore.

* [x] Phase 2: Cloud Storage Migration (COMPLETE)

- Provisioned a free Neon PostgreSQL database (serverless, AWS us-east-1).

- Replicated raw_stage schema (plaid_transactions, quickbooks_invoices, quickbooks_payments) in the cloud via Neon SQL editor.

- Updated get_db_connection() in ingest.py to check for DATABASE_URL first (cloud path with sslmode=require), falling back to individual DB_* vars for local development.

- DATABASE_URL added to .env. Pipeline verified end-to-end against Neon.

* [x] Phase 3: Data Transformation (dbt) (COMPLETE)

- Installed dbt-core 1.11.11 and dbt-postgres 1.10.1 into Python 3.12 venv (dbt incompatible with Python 3.14).

- Initialized dbt project at /dbt_project/. Configured ~/.dbt/profiles.yml to connect to Neon (analytics schema, sslmode=require).

- Declared raw_stage tables as dbt sources in models/staging/sources.yml.

- Built 3 staging models (views): stg_plaid_transactions (jsonb_array_elements unpack), stg_quickbooks_invoices, stg_quickbooks_payments.

- Built 2 mart models (tables): monthly_burn_rate, receivables_aging with aging bucket logic.

- Added built-in dbt tests: unique + not_null on transaction_id, not_null on amount, unique + not_null on invoice_id.

* [ ] Phase 4: Automation (GitHub Actions) (UP NEXT)

- Automate ingest.py and dbt run using a cron schedule.

* [ ] Phase 5: Machine Learning (Local Training)

- Query clean dbt tables to train Prophet (cash flow) and Isolation Forest (anomalies).

- Serialize models to .pkl.

* [ ] Phase 6: The Serving Layer (FastAPI)

- Build endpoints to serve predictions and database metrics.

* [ ] Phase 7: The Frontend Dashboard (Streamlit)

- Connect Streamlit to FastAPI and deploy via Community Cloud.

## Environment & Dependencies

```text
Core Requirements (requirements.txt):

psycopg2-binary>=2.9.0
requests>=2.31.0
python-dotenv>=1.0.0
```

## Future additions: fastapi, uvicorn, streamlit, prophet, scikit-learn

```text
Environment Variables Template (.env):

DATABASE_URL=                  # Neon connection string (cloud — takes priority)

DB_HOST=                       # Local fallback
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

PLAID_CLIENT_ID=
PLAID_SECRET=
PLAID_ACCESS_TOKEN=
PLAID_ENV=sandbox

QB_CLIENT_ID=
QB_CLIENT_SECRET=
QB_REALM_ID=
QB_REFRESH_TOKEN=
```
