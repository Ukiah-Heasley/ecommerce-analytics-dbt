{{ config(materialized='table') }}

with snapshot as (
    select
        dbt_scd_id as product_sk,
        product_id,
        name,
        description,
        category,
        price,
        currency,
        is_active,
        _source_system,
        created_at,
        updated_at,
        dbt_valid_from as valid_from,
        dbt_valid_to as valid_to,
        dbt_valid_to is null as is_current
    from {{ ref('products_snapshot') }}
)

select * from snapshot

union all

select
    {{ default_sk() }} as product_sk,
    '{{ var("default_unknown") }}' as product_id,
    '{{ var("default_unknown") }}' as name,
    null as description,
    '{{ var("default_unknown") }}' as category,
    cast(0 as decimal(10, 2)) as price,
    null as currency,
    false as is_active,
    '{{ var("default_unknown") }}' as _source_system,
    timestamp '1900-01-01 00:00:00' as created_at,
    timestamp '1900-01-01 00:00:00' as updated_at,
    timestamp '1900-01-01 00:00:00' as valid_from,
    null as valid_to,
    true as is_current
