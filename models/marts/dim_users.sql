{{ config(materialized='table') }}

select
    user_sk,
    user_id,
    canonical_user_id,
    is_merged,
    email_raw,
    email_normalized,
    phone,
    first_name,
    last_name,
    status,
    _source_system,
    created_at,
    updated_at,
    valid_from,
    valid_to,
    is_current
from {{ ref('int_users') }}

union all

select
    {{ default_sk() }}                                   as user_sk,
    '{{ var("default_unknown") }}'                       as user_id,
    '{{ var("default_unknown") }}'                       as canonical_user_id,
    false                                                as is_merged,
    null                                                 as email_raw,
    null                                                 as email_normalized,
    null                                                 as phone,
    null                                                 as first_name,
    null                                                 as last_name,
    '{{ var("default_unknown") }}'                       as status,
    '{{ var("default_unknown") }}'                       as _source_system,
    timestamp '1900-01-01 00:00:00'                      as created_at,
    timestamp '1900-01-01 00:00:00'                      as updated_at,
    timestamp '1900-01-01 00:00:00'                      as valid_from,
    null                                                 as valid_to,
    true                                                 as is_current
