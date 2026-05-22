select
    transaction_id,
    user_id,
    product_id,
    session_id,
    amount,
    currency,
    status,
    event_at,
    refund_amount,
    refunded_at
from main.fct_transactions
