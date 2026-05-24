# E-commerce analytics dashboard

[Evidence.dev](https://evidence.dev/) static site over the dbt marts in
`../ecommerce_analytics.duckdb`. Part of the
[ecommerce-analytics-dbt](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt)
portfolio project.

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/)
(after [GitHub Pages is enabled](../docs/DEPLOY.md))

## Prerequisites

Build the warehouse from the **repo root** first — Evidence reads the DuckDB
file produced by dbt:

```bash
export DBT_PROFILES_DIR=$(pwd)
python scripts/generate.py --reset --days 7
python scripts/load_raw.py
dbt build
```

## Local development

```bash
cd reports
npm install          # first time
npm run sources      # refresh parquet from ../ecommerce_analytics.duckdb
npm run dev          # http://localhost:3000
```

## Production build

```bash
npm run build        # output → build/ecommerce-analytics-dbt/
npm run preview      # serve the built site locally
```

The build uses `deployment.basePath: /ecommerce-analytics-dbt` in
[`evidence.config.yaml`](evidence.config.yaml) for GitHub Pages. See
[`docs/DEPLOY.md`](../docs/DEPLOY.md) for the CI deploy workflow.

## Style

Chart and layout rules: [`STYLE.md`](STYLE.md)

## Pages

| Page | File | Content |
|------|------|---------|
| Executive summary | [`pages/index.md`](pages/index.md) | KPIs, revenue trend, AOV, refund rate |
| Revenue & products | [`pages/revenue.md`](pages/revenue.md) | Top products by revenue and order count |

Main project docs: [`../README.md`](../README.md) ·
[`../docs/DESIGN.md`](../docs/DESIGN.md) ·
[`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
