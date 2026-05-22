{{ config(materialized='table') }}

with source as (
    select distinct refund_reason
    from {{ ref('stg_transactions') }}
    where refund_reason is not null
)

select
    md5(cast(refund_reason as varchar)) as refund_reason_id,
    refund_reason
from source

union all

select
    {{ default_sk(var("default_not_applicable")) }} as refund_reason_id,
    '{{ var("default_not_applicable") }}' as refund_reason

union all

select
    {{ default_sk() }} as refund_reason_id,
    '{{ var("default_unknown") }}' as refund_reason
