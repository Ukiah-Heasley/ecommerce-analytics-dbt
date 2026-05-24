---
title: Revenue & products
---

Which products drive the headline revenue number? The SCD2 point-in-time join
on `dim_products` ensures we use the product *name* that was active when the
transaction occurred — not whatever the name happens to be today.

```sql top_products
  select
    p.name                            as product,
    p.category                        as category,
    sum(t.amount)::decimal(12,2)      as gross_revenue,
    count(*)                          as orders
  from ecommerce.fct_transactions t
  join ecommerce.dim_products p
    on t.product_id = p.product_id
   and t.event_at >= p.valid_from
   and t.event_at <  coalesce(p.valid_to, timestamp '2999-12-31')
  where t.status in ('completed', 'partially_refunded')
  group by 1, 2
  order by gross_revenue desc
  limit 10
```

<BarChart
    data={top_products}
    swapXY=true
    x=product
    y=gross_revenue
    yFmt=usd0
    sort=false
    title="Top 10 products by gross revenue"
    subtitle="Completed and partially refunded orders; fully refunded excluded."
    yAxisTitle=" "
    xAxisTitle=" "
    seriesColors={["#003262"]}
/>

## The same list, by order count

When the top-by-revenue list differs from top-by-orders, you're seeing
price-mix at work — a small number of high-ticket sales lifting the revenue
ranking past products that sell more units.

```sql top_products_by_orders
  select
    p.name                       as product,
    count(*)                     as orders
  from ecommerce.fct_transactions t
  join ecommerce.dim_products p
    on t.product_id = p.product_id
   and t.event_at >= p.valid_from
   and t.event_at <  coalesce(p.valid_to, timestamp '2999-12-31')
  where t.status in ('completed', 'partially_refunded')
  group by 1
  order by orders desc
  limit 10
```

<BarChart
    data={top_products_by_orders}
    swapXY=true
    x=product
    y=orders
    sort=false
    title="Top 10 products by order count"
    subtitle="Completed and partially refunded orders; fully refunded excluded."
    yAxisTitle=" "
    xAxisTitle=" "
    seriesColors={["#46535E"]}
/>
