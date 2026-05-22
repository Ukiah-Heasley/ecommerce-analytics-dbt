{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'raw_products') }}
),

renamed as (
    select
        product_id,
        name,
        description,
        category,
        price::DECIMAL(10, 2)   as price,
        currency,
        is_active::BOOLEAN      as is_active,
        created_at::TIMESTAMP   as created_at,
        updated_at::TIMESTAMP   as updated_at,
        _source_system,
        _ingested_at::TIMESTAMP as _ingested_at
    from source
)

select * from renamed
