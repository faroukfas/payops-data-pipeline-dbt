-- This test fails if any successful transaction has an amount less than or equal to 0
select
    payment_id,
    amount,
    payment_status
from {{ ref('fct_payment_attempts') }}
where payment_status = 'success'
  and amount <= 0