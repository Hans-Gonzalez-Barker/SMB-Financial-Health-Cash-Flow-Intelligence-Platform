SELECT
    company_id,
    payload ->> 'Id'                                AS invoice_id,
    (payload ->> 'TxnDate')::date                   AS invoice_date,
    (payload ->> 'DueDate')::date                   AS due_date,
    (payload ->> 'TotalAmt')::numeric               AS total_amount,
    (payload ->> 'Balance')::numeric                AS outstanding_balance,
    payload -> 'CustomerRef' ->> 'value'            AS customer_id,
    payload -> 'CustomerRef' ->> 'name'             AS customer_name,
    CASE
        WHEN (payload ->> 'Balance')::numeric = 0 THEN 'paid'
        ELSE 'outstanding'
    END                                             AS payment_status,
    ingested_at
FROM {{ source('raw_stage', 'quickbooks_invoices') }}
