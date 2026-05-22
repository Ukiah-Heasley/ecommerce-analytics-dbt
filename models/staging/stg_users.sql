{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'raw_users') }}
),

renamed as (
    select
        user_id,
        email as email_raw,
        first_name,
        last_name,
        status,
        created_at::timestamp as created_at,
        updated_at::timestamp as updated_at,
        _source_system,
        _ingested_at::timestamp as _ingested_at,
        nullif(trim(lower(email)), '') as email_normalized,
        nullif(trim(phone), '') as phone
    from source
)

select * from renamed
