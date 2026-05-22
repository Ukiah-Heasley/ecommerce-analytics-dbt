{#
  Returns a SQL predicate that's true for transaction statuses that
  contribute to revenue. Whitelist (not blacklist) so a new unknown
  status can't silently inflate revenue metrics — add it here
  explicitly when introduced.

  Usage:
    where {{ is_revenue_status() }}
    where {{ is_revenue_status('t.status') }}
#}
{% macro is_revenue_status(column='status') -%}
    {{ column }} in ('completed', 'refunded', 'partially_refunded')
{%- endmacro %}
