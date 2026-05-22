{{ config(
    materialized = 'incremental',
    unique_key = 'transaction_day',
    incremental_strategy = 'delete+insert'
) }}

with txns_to_aggregate as (
    select *
    from {{ ref('fct_transactions') }}
    where
        {{ is_revenue_status() }}
    {% if is_incremental() %}
            and date_trunc('day', event_at)::date in (
                select distinct date_trunc('day', event_at)::date
                from {{ ref('fct_transactions') }}
                where _ingested_at > (
                    select
                        coalesce(
                            max(ingested_at_high_water), timestamp '1900-01-01'
                        )
                    from {{ this }}
                )
            )
        {% endif %}
)

select
    date_trunc('day', event_at)::date as transaction_day,
    count(*) as transaction_count,
    count(
        distinct case
            when
                canonical_user_id != '{{ var("default_unknown") }}'
                then canonical_user_id
        end
    ) as daily_transaction_users,
    sum(amount) as gross_revenue,
    sum(coalesce(refund_amount, 0)) as total_refunds,
    sum(amount) - sum(coalesce(refund_amount, 0)) as net_revenue,
    sum(case when refund_amount is not null then 1 else 0 end) as refund_count,
    max(_ingested_at) as ingested_at_high_water
from txns_to_aggregate
group by 1
