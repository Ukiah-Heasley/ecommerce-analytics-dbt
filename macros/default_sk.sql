{#
  Returns the SK hash expression for the default-row pattern. Single
  source of truth for default-row surrogate keys — used by `fct_*`
  COALESCE fallbacks and `dim_*` default-row UNION clauses.

  Usage:
    {{ default_sk() }}                              -- single-column default
    {{ default_sk(var('default_unknown') ~ '|'
                  ~ var('default_unknown')) }}      -- composite key default
#}
{% macro default_sk(value=none) -%}
    md5(cast('{{ value if value is not none else var("default_unknown") }}' as varchar))
{%- endmacro %}
