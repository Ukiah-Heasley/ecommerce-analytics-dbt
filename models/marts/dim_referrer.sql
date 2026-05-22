{{ config(materialized='table') }}

with source as (
    select distinct referrer
    from {{ ref('stg_sessions') }}
    where referrer is not null
)

select
    md5(cast(referrer as varchar)) as referrer_id,
    referrer
from source

union all

select
    {{ default_sk() }} as referrer_id,
    '{{ var("default_unknown") }}' as referrer
