# SMB Financial Health & Cash Flow Intelligence Platform

An end-to-end data pipeline and predictive analytics platform that ingests SMB financial transactions, transforms raw data using `dbt`, runs cash flow forecasting and anomaly detection, and serves predictions via an API to a Streamlit dashboard.

## Architecture & Folder Structure

```text
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

## Tech Stack
```text
- Ingestion: Python (Plaid Sandbox, QuickBooks Developer Sandbox)

- Storage: PostgreSQL (Neon / Supabase)

- Transformation: dbt-core

- ML Layer: Python (scikit-learn, Prophet, Isolation Forest)

- API Layer: FastAPI

- Frontend: Streamlit

- CI/CD: GitHub Actions
```

## More info
```text
read CLAUDE.md file for more context on the project + progress
```



