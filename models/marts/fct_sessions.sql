{{
  config(
    materialized = 'incremental',
    unique_key = 'session_id',
    incremental_strategy = 'delete+insert',
  )
}}

with
{% if is_incremental() %}
    pending_resolution as (
        select session_id
        from {{ this }}
        where
            user_sk = {{ default_sk() }}
            and started_at
            >= current_date
            - interval '{{ var("dim_resolution_replay_days") }} days'
    ),
{% endif %}
sessions_to_load as (
    select *
    from {{ ref('int_sessions_deduped') }}
    {% if is_incremental() %}
        where
            _ingested_at
            >= coalesce(
                (select max(_ingested_at) from {{ this }}), '1900-01-01'
            )
            or session_id in (select session_id from pending_resolution)
    {% endif %}
)

select
    s.session_id,
    s.user_id,
    s.anonymous_id,
    coalesce(u.user_sk, {{ default_sk() }}) as user_sk,
    coalesce(u.canonical_user_id, '{{ var("default_unknown") }}')
        as canonical_user_id,
    coalesce(
        sc.session_context_id,
        {{ default_sk(var("default_unknown") ~ '|' ~ var("default_unknown")) }}
    )
        as session_context_id,
    coalesce(r.referrer_id, {{ default_sk() }}) as referrer_id,
    s.started_at,
    s.ended_at,
    s.duration_seconds,
    s.country,
    s._source_system,
    s._ingested_at,
    s._batch_id

from sessions_to_load as s

left join {{ ref('dim_users') }} as u
    on
        s.user_id = u.user_id
        and s.started_at >= u.valid_from
        and (s.started_at < u.valid_to or u.valid_to is null)

left join {{ ref('dim_session_context') }} as sc
    on
        coalesce(s.device_type, '{{ var("default_unknown") }}') = sc.device_type
        and coalesce(s.platform, '{{ var("default_unknown") }}') = sc.platform

left join {{ ref('dim_referrer') }} as r
    on coalesce(s.referrer, '{{ var("default_unknown") }}') = r.referrer
