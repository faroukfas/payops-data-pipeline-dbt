{{
    config(
        materialized='incremental',
        unique_key='payment_id',
        on_schema_change='sync_all_columns'
    )
}}

with payments as (
    select * from {{ ref('stg_payments') }}
),

exchange_rates as (
    select * from {{ ref('stg_exchange_rates') }}
),

enriched as (
    select
        p.payment_id,
        p.customer_id,
        p.merchant_id,
        p.gateway,
        p.card_network,
        p.issuing_country,
        p.amount,
        p.currency,
        p.processor_fee,
        p.payment_status,
        p.decline_reason,
        p.created_at,
        p.partition_date,
        coalesce(p.amount * er.exchange_rate, p.amount) as amount_in_usd,
        case 
            when p.payment_status = 'success' then 1 
            else 0 
        end as is_successful
    from payments p
    left join exchange_rates er
        on p.partition_date = er.rate_date
        and p.currency = er.base_currency
        and er.target_currency = 'USD'
        
    -- This block only runs on incremental (subsequent) runs, filtering for new records
    {% if is_incremental() %}
    where p.created_at > (select max(created_at) from {{ this }})
    {% endif %}
)

select * from enriched