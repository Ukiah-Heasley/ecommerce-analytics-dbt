{{ config(materialized='view') }}

select
    session_id,
    started_at,
    _ingested_at,
    _source_system,
    _batch_id,
    date_diff('day', started_at::date, _ingested_at::date) as lateness_days
from {{ ref('stg_sessions') }}
where
    date_diff('day', started_at::date, _ingested_at::date)
    > {{ var('session_lookback_days') }}
