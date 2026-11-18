with source as (
    select * from {{ source('public', 'raw_payments') }}
),

cleaned as (
    select
        CAST(payment_id AS VARCHAR) as payment_id,
        CAST(customer_id AS VARCHAR) as customer_id,
        CAST(merchant_id AS VARCHAR) as merchant_id,
        LOWER(gateway) as gateway,
        CAST(amount AS DECIMAL(18, 2)) as amount,
        LOWER(currency) as currency,
        CAST(processor_fee AS DECIMAL(18, 2)) as processor_fee,
        LOWER(status) as payment_status,
        LOWER(decline_reason) as decline_reason,
        LOWER(card_network) as card_network,
        UPPER(issuing_country) as issuing_country,
        CAST(created_at AS TIMESTAMP) as created_at,
        CAST(dt AS DATE) as partition_date
    from source
)

select * from cleaned