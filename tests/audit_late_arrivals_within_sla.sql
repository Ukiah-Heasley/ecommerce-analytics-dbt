{{ config(severity = 'warn') }}

select *
from {{ ref('audit_late_arrivals') }}
