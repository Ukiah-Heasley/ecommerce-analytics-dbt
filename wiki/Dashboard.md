# Dashboard

The Evidence.dev dashboard ([reports/](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/tree/master/reports)) reads directly from the local DuckDB file and renders as a static HTML site.

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/)

Two pages are live; engagement, conversion, and retention pages are left as practice exercises.

## Executive summary

[Open live →](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/)

The headline numbers across the practice dataset, computed off the marts layer.

| Chart | What it shows | Source |
|---|---|---|
| **Net revenue** (BigValue) | Daily cashflow after refunds | `fct_daily_transactions` |
| **Average order value** (BigValue) | Gross revenue ÷ transaction count | `fct_daily_transactions` |
| **Refund rate ($)** (BigValue) | Refunded amount ÷ gross revenue | `fct_daily_transactions` |
| **Transactions** (BigValue) | Total count in window | `fct_daily_transactions` |
| **Revenue trend** (line) | Net revenue per day | `fct_daily_transactions` |
| **Average order value per day** (line) | AOV trend | `fct_daily_transactions` |

## Revenue & Products

[Open live →](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/revenue)

Top-line revenue plus product-level performance, joining the transaction facts to the SCD2 product dim on event time so historical attribution is correct across price changes (see [[Edge-Cases]]).

| Chart | What it shows | Source |
|---|---|---|
| **Top products by revenue** (bar) | Highest-grossing products, point-in-time-priced | `fct_transactions` × `dim_products` SCD2 join |
| **Top products by order count** (bar) | Highest-volume products | `fct_transactions` × `dim_products` |
| **Refund rate trend** (line) | Refunds as % of gross over time | `fct_daily_transactions` |

## Styling

Theme tokens live in `reports/evidence.config.yaml`; conventions documented in `reports/STYLE.md`. Colorscale `#F1EFE8 → #378ADD` is project-default for sequential heatmaps.

## Running it yourself

```bash
cd reports
npm install                 # first time only
npm run sources             # materialize queries from ../ecommerce_analytics.duckdb
npm run dev                 # http://localhost:3000 — live-reload
npm run build               # static site → build/ecommerce-analytics-dbt/
```

Published to GitHub Pages on push to `master`. See [`docs/DEPLOY.md`](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/blob/master/docs/DEPLOY.md) for setup.

## Where to go next

- [[Architecture]] — how data flows from raw CSVs to these charts
- [[Developer-Setup]] — local dashboard dev commands
