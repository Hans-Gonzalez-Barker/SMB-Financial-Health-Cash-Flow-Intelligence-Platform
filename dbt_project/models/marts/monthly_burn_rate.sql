SELECT
    company_id,
    DATE_TRUNC('month', transaction_date)       AS month,
    COUNT(*)                                    AS transaction_count,
    SUM(amount)                                 AS total_spend,
    AVG(amount)                                 AS avg_transaction_size,
    MAX(amount)                                 AS largest_expense
FROM {{ ref('stg_plaid_transactions') }}
WHERE amount > 0
  AND is_pending = false
GROUP BY company_id, DATE_TRUNC('month', transaction_date)
ORDER BY month DESC
