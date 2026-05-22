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
    from device_types d
    cross join platforms p
)

select
    md5(cast(device_type || '|' || platform as varchar)) as session_context_id,
    device_type,
    platform
from combos
