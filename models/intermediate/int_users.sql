{{ config(materialized='view') }}

with users as (
    select * from {{ ref('users_snapshot') }}
),

distinct_email_user as (
    select distinct user_id, email_normalized, _source_system
    from users
    where email_normalized is not null
),

canonical_map as (
    select distinct
        email_normalized,
        first_value(user_id) over (
            partition by email_normalized
            order by
                case when _source_system = 'auth_db' then 0 else 1 end,
                user_id
        ) as canonical_user_id
    from distinct_email_user
)

select
    u.dbt_scd_id                                            as user_sk,
    u.user_id,
    coalesce(c.canonical_user_id, u.user_id)                as canonical_user_id,
    u.user_id != coalesce(c.canonical_user_id, u.user_id)   as is_merged,
    u.email_raw,
    u.email_normalized,
    u.phone,
    u.first_name,
    u.last_name,
    u.status,
    u.created_at,
    u.updated_at,
    u._source_system,
    u._ingested_at,
    u.dbt_valid_from                                        as valid_from,
    u.dbt_valid_to                                          as valid_to,
    u.dbt_valid_to is null                                  as is_current

from users u
left join canonical_map c
    on u.email_normalized = c.email_normalized
