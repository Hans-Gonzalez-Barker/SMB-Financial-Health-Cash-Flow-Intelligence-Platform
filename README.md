# SMB Financial Health & Cash Flow Intelligence Platform

An end-to-end data pipeline and predictive analytics platform that ingests SMB financial transactions, transforms raw data using `dbt`, runs cash flow forecasting and anomaly detection, and serves predictions via an API to a Streamlit dashboard.

## Architecture & Folder Structure

```text
smb-financial-intelligence/
├── .github/workflows/    # GitHub Actions automation
├── api/                  # FastAPI codebase
├── dbt_project/          # dbt-core transformation models
├── frontend/             # Streamlit user interface
├── ingestion/            # Python scripts for Plaid/QuickBooks APIs
├── ml_models/            # Machine learning training & serialization
├── .gitignore            # Excludes credentials and virtual environments
└── README.md             # Project documentation
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

