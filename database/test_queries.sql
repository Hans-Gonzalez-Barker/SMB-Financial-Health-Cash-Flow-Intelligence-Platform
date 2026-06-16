-- Test QB Invoices Raw Stage
SELECT 
    id, 
    ingested_at, 
    company_id, 
    payload->>'Id' AS invoice_id,
    (payload->>'TotalAmt')::numeric AS total_amount,
    (payload->>'Balance')::numeric AS remaining_balance
FROM raw_stage.quickbooks_invoices;

-- Test Plaid Transactions Raw Stage
SELECT 
    id, 
    ingested_at, 
    company_id, 
    jsonb_pretty(payload) AS formatted_payload 
FROM raw_stage.plaid_transactions;