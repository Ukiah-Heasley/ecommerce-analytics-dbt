{{ config(materialized='table') }}

with device_types as (
    select distinct device_type
    from {{ ref('stg_sessions') }}
    where device_type is not null
    union
    select '{{ var("default_unknown") }}'
),

platforms as (
    select distinct platform
    from {{ ref('stg_sessions') }}
    where platform is not null
    union
    select '{{ var("default_unknown") }}'
),

combos as (
    select
        d.device_type,
        p.platform
    from device_types as d
    cross join platforms as p
)

select
    device_type,
    platform,
    md5(cast(device_type || '|' || platform as varchar)) as session_context_id
from combos
