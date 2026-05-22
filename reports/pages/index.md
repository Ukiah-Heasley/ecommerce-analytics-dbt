---
title: Ecommerce — Executive summary
---

The headline numbers across the practice dataset, computed off the marts layer
(`fct_daily_transactions`, `fct_transactions` × `dim_products`).

```sql kpis
  select
    sum(net_revenue)::decimal(12,2)                              as net_revenue,
    sum(gross_revenue)::decimal(12,2)                            as gross_revenue,
    sum(total_refunds)::decimal(12,2)                            as total_refunds,
    sum(transaction_count)                                       as transactions,
    (sum(gross_revenue) / nullif(sum(transaction_count), 0))::decimal(12,2) as aov,
    (sum(total_refunds) / nullif(sum(gross_revenue), 0))         as refund_rate
  from ecommerce.fct_daily_transactions
```

<Grid cols=4>
  <BigValue data={kpis} value=net_revenue title="Net revenue" fmt=usd0 />
  <BigValue data={kpis} value=aov title="Average order value" fmt=usd2 />
  <BigValue data={kpis} value=refund_rate title="Refund rate ($)" fmt=pct1 />
  <BigValue data={kpis} value=transactions title="Transactions" fmt=num0 />
</Grid>

## Revenue trend

```sql revenue_trend
  select
    transaction_day,
    net_revenue,
    gross_revenue,
    total_refunds
  from ecommerce.fct_daily_transactions
  order by transaction_day
```

<LineChart
    data={revenue_trend}
    x=transaction_day
    y=net_revenue
    yFmt=usd0
    title="Net revenue is the daily cashflow after refunds"
    subtitle="Gross revenue minus refunded amount, per day"
    yAxisTitle=" "
    xAxisTitle=" "
    lineColor="#003262"
    lineWidth=2.5
/>

## Order economics

A rising AOV with steady transaction volume means revenue per visit is improving;
a falling AOV with rising volume means we're attracting more, smaller carts.

```sql aov_trend
  select
    transaction_day,
    (gross_revenue / nullif(transaction_count, 0))::decimal(12,2) as aov
  from ecommerce.fct_daily_transactions
  where transaction_count > 0
  order by transaction_day
```

<LineChart
    data={aov_trend}
    x=transaction_day
    y=aov
    yFmt=usd2
    title="Average order value per day"
    subtitle="Gross revenue ÷ transaction count"
    yAxisTitle=" "
    xAxisTitle=" "
    lineColor="#003262"
    lineWidth=2.5
/>

## Refund health

Refunds are a lagging signal — they land days after the original transaction.
The 10% reference line is a placeholder target; replace once the business sets one.

```sql refund_rate_trend
  select
    transaction_day,
    case
      when gross_revenue = 0 then 0
      else total_refunds / gross_revenue
    end as refund_rate_pct
  from ecommerce.fct_daily_transactions
  order by transaction_day
```

<LineChart
    data={refund_rate_trend}
    x=transaction_day
    y=refund_rate_pct
    yFmt=pct1
    title="Refund rate by day"
    subtitle="Refunded $ ÷ gross revenue $, same day basis"
    yAxisTitle=" "
    xAxisTitle=" "
    lineColor="#EE1F60"
    lineWidth=2.5
>
  <ReferenceLine y=0.10 label="Target: 10%" hideValue color=neutral />
</LineChart>

---

See **[Revenue & products](/revenue)** for the products driving the line above.
