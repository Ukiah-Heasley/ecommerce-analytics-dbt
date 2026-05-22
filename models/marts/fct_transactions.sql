{{
  config(
    materialized = 'incremental',
    unique_key = 'transaction_id',
    incremental_strategy = 'delete+insert',
  )
}}

with
{% if is_incremental() %}
    pending_resolution as (
        select transaction_id
        from {{ this }}
        where
            (user_sk = {{ default_sk() }} or product_sk = {{ default_sk() }})
            and event_at
            >= current_date
            - interval '{{ var("dim_resolution_replay_days") }} days'
    ),
{% endif %}
txns_to_load as (
    select
        transaction_id,
        user_id,
        product_id,
        session_id,
        amount,
        currency,
        status,
        event_at,
        updated_at,
        refund_amount,
        refunded_at,
        refund_reason_normalized,
        _source_system,
        _ingested_at
    from {{ ref('stg_transactions') }}
    {% if is_incremental() %}
        where
            _ingested_at
            >= coalesce(
                (select max(_ingested_at) from {{ this }}), '1900-01-01'
            )
            or transaction_id in (select transaction_id from pending_resolution)
    {% endif %}
)

select
    t.transaction_id,
    t.user_id,
    t.product_id,
    t.session_id,
    coalesce(u.user_sk, {{ default_sk() }}) as user_sk,
    coalesce(u.canonical_user_id, '{{ var("default_unknown") }}')
        as canonical_user_id,
    coalesce(p.product_sk, {{ default_sk() }}) as product_sk,
    coalesce(rr.refund_reason_id, {{ default_sk() }}) as refund_reason_id,
    t.amount,
    t.currency,
    t.status,
    t.event_at,
    t.updated_at,
    t.refund_amount,
    t.refunded_at,
    t._source_system,
    t._ingested_at

from txns_to_load as t

left join {{ ref('dim_users') }} as u
    on
        t.user_id = u.user_id
        and t.event_at >= u.valid_from
        and (t.event_at < u.valid_to or u.valid_to is null)

left join {{ ref('dim_products') }} as p
    on
        t.product_id = p.product_id
        and t.event_at >= p.valid_from
        and (t.event_at < p.valid_to or p.valid_to is null)

left join {{ ref('dim_refund_reason') }} as rr
    on t.refund_reason_normalized = rr.refund_reason
