{% macro refund_reason_normalized(reason_col, amount_col) %}
    case
        when {{ reason_col }} is not null then {{ reason_col }}
        when {{ amount_col }} is not null then '{{ var("default_unknown") }}'
        else '{{ var("default_not_applicable") }}'
    end
{% endmacro %}
