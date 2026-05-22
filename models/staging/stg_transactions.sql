{{ config(materialized='view') }}

with source as (
    select *
    from {{ source('raw', 'raw_transactions') }}
),

renamed as (
    select
        transaction_id,
        user_id,
        session_id,
        product_id,
        amount::decimal(10, 2) as amount,
        currency,
        status,
        event_at::timestamp as event_at,
        updated_at::timestamp as updated_at,
        refund_amount::decimal(10, 2) as refund_amount,
        refunded_at::timestamp as refunded_at,
        refund_reason,
        {{ refund_reason_normalized('refund_reason', 'refund_amount') }}
            as refund_reason_normalized,
        _source_system,
        _ingested_at::timestamp as _ingested_at
    from source
)

select * from renamed
