{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'raw_sessions') }}
),

renamed as (
    select
        session_id,
        user_id,
        anonymous_id,
        started_at::TIMESTAMP as started_at,
        ended_at::TIMESTAMP as ended_at,
        duration_seconds::INTEGER as duration_seconds,
        device_type,
        platform,
        country,
        referrer,
        _source_system,
        _ingested_at::TIMESTAMP as _ingested_at,
        _batch_id
    from source
)

select * from renamed
