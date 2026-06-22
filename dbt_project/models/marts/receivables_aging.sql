SELECT
    company_id,
    invoice_id,
    customer_name,
    invoice_date,
    due_date,
    total_amount,
    outstanding_balance,
    CURRENT_DATE - due_date                     AS days_overdue,
    CASE
        WHEN CURRENT_DATE - due_date <= 0   THEN 'current'
        WHEN CURRENT_DATE - due_date <= 30  THEN '1-30 days'
        WHEN CURRENT_DATE - due_date <= 60  THEN '31-60 days'
        ELSE                                     '60+ days'
    END                                         AS aging_bucket
FROM {{ ref('stg_quickbooks_invoices') }}
WHERE payment_status = 'outstanding'
ORDER BY days_overdue DESC
