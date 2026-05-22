{{
  config(
    materialized = 'incremental',
    unique_key = 'session_day',
    incremental_strategy = 'delete+insert',
  )
}}

select
    date_trunc('day', started_at)::date as session_day,
    count(*) as session_count,
    count(distinct nullif(canonical_user_id, '{{ var("default_unknown") }}'))
        as daily_logged_in_users,
    count(distinct coalesce(
        nullif(canonical_user_id, '{{ var("default_unknown") }}'),
        anonymous_id
    )) as daily_visitors,
    count(distinct case when user_id is null then anonymous_id end)
        as daily_anonymous_devices,
    avg(duration_seconds) as avg_session_duration_seconds

from {{ ref('fct_sessions') }}

{% if is_incremental() %}
    where
        started_at
        >= (
            select
                max(session_day)
                - interval '{{ var("session_lookback_days") }} days'
            from {{ this }}
        )
{% endif %}

group by 1
