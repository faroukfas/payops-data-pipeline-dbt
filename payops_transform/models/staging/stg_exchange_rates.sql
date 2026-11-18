with source as (
    select * from {{ source('public', 'raw_exchange_rates') }}
),

cleaned as (
    select
        CAST(dt AS DATE) as rate_date,
        UPPER(base) as base_currency,
        UPPER(target_currency) as target_currency,
        CAST(rate AS DECIMAL(18, 6)) as exchange_rate
    from source
)

select * from cleaned