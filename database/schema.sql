-- Drop the schema and tables if they already exist for a clean slate
DROP SCHEMA IF EXISTS raw_stage CASCADE;

-- Create the dedicated raw staging schema
CREATE SCHEMA raw_stage;

-- Create Plaid transactions raw table
-- We use JSONB to store the raw API responses exactly as they arrive.
CREATE TABLE raw_stage.plaid_transactions (
    id SERIAL PRIMARY KEY,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    company_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL
);

-- Create QuickBooks invoices raw table
CREATE TABLE raw_stage.quickbooks_invoices (
    id SERIAL PRIMARY KEY,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    company_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL
);

-- Create QuickBooks payments raw table
CREATE TABLE raw_stage.quickbooks_payments (
    id SERIAL PRIMARY KEY,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    company_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL
);

-- Index the JSONB structures for performance during later dbt runs
CREATE INDEX idx_plaid_tx_date ON raw_stage.plaid_transactions USING gin (payload);
CREATE INDEX idx_qb_inv_date ON raw_stage.quickbooks_invoices USING gin (payload);