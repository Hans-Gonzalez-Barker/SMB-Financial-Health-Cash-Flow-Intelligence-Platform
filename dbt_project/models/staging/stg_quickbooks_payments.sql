SELECT
    company_id,
    payload ->> 'Id'                                AS payment_id,
    (payload ->> 'TxnDate')::date                   AS payment_date,
    (payload ->> 'TotalAmt')::numeric               AS payment_amount,
    payload -> 'CustomerRef' ->> 'value'            AS customer_id,
    payload -> 'Line' -> 0
              -> 'LinkedTxn' -> 0
              ->> 'TxnId'                           AS linked_invoice_id,
    ingested_at
FROM {{ source('raw_stage', 'quickbooks_payments') }}
