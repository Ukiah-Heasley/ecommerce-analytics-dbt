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
        amount::DECIMAL(10, 2)                       as amount,
        currency,
        status,
        event_at::TIMESTAMP                          as event_at,
        updated_at::TIMESTAMP                        as updated_at,
        refund_amount::DECIMAL(10, 2)                                    as refund_amount,
        refunded_at::TIMESTAMP                                           as refunded_at,
        refund_reason,
        {{ refund_reason_normalized('refund_reason', 'refund_amount') }} as refund_reason_normalized,
        _source_system,
        _ingested_at::TIMESTAMP                      as _ingested_at
    from source
)

select * from renamed
