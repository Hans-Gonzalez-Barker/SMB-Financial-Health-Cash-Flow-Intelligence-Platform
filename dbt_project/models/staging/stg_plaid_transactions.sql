WITH raw AS (
    SELECT company_id, ingested_at, payload
    FROM {{ source('raw_stage', 'plaid_transactions') }}
),

exploded AS (
    SELECT
        company_id,
        ingested_at,
        jsonb_array_elements(payload -> 'transactions') AS txn
    FROM raw
)

SELECT
    company_id,
    txn ->> 'transaction_id'                    AS transaction_id,
    txn ->> 'account_id'                        AS account_id,
    (txn ->> 'amount')::numeric                 AS amount,
    (txn ->> 'date')::date                      AS transaction_date,
    txn ->> 'name'                              AS vendor_name,
    txn -> 'category' ->> 0                     AS category_primary,
    txn -> 'category' ->> 1                     AS category_secondary,
    txn ->> 'payment_channel'                   AS payment_channel,
    (txn ->> 'pending')::boolean                AS is_pending,
    ingested_at
FROM exploded
