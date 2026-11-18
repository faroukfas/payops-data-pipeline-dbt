{{
    config(
        materialized='table'
    )
}}

with payments as (
    select * from {{ ref('fct_payment_attempts') }}
)

select
    partition_date as transaction_date,
    gateway,
    card_network,
    currency,
    count(payment_id) as total_attempts,
    sum(is_successful) as successful_attempts,
    round(sum(is_successful)::numeric / nullif(count(payment_id), 0) * 100, 2) as success_rate_pct,
    sum(amount_in_usd) as total_volume_usd,
    sum(processor_fee) as total_processor_fees_usd
from payments
group by 1, 2, 3, 4