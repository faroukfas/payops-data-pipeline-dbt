{% snapshot snap_payments %}

{{
    config(
        target_database='payops_db',
        target_schema='analytics',
        unique_key='payment_id',
        strategy='check',
        check_cols=['payment_status', 'decline_reason'],
        updated_at='created_at'
    )
}}

select
    payment_id,
    customer_id,
    merchant_id,
    gateway,
    amount,
    currency,
    status as payment_status,
    decline_reason,
    created_at
from {{ source('public', 'raw_payments') }}

{% endsnapshot %}