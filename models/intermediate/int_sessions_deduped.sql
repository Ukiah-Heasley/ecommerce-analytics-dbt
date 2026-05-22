{{ config(materialized='view') }}

with sessions as (
    select
        session_id,
        user_id,
        anonymous_id,
        started_at,
        ended_at,
        duration_seconds,
        device_type,
        platform,
        country,
        referrer,
        _source_system,
        _ingested_at,
        _batch_id,
        row_number() over (
            partition by session_id
            order by _ingested_at desc
        ) as row_num
    from {{ ref('stg_sessions') }}
)

select
    session_id,
    user_id,
    anonymous_id,
    started_at,
    ended_at,
    duration_seconds,
    device_type,
    platform,
    country,
    referrer,
    _source_system,
    _ingested_at,
    _batch_id
from sessions
where row_num = 1
