# E-commerce analytics dashboard

[Evidence.dev](https://evidence.dev/) static site over the dbt marts in
`../ecommerce_analytics.duckdb`.

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/)

Full dashboard docs: [Wiki → Dashboard](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki/Dashboard)

## Local development

Build the warehouse from the **repo root** first:

```bash
export DBT_PROFILES_DIR=$(pwd)
python scripts/generate.py --reset --days 7
python scripts/load_raw.py
dbt build
```

Then:

```bash
cd reports
npm install          # first time
npm run sources      # refresh from ../ecommerce_analytics.duckdb
npm run dev          # http://localhost:3000
npm run build        # output → build/ecommerce-analytics-dbt/
npm run preview      # serve the built site locally
```

Style rules: [`STYLE.md`](STYLE.md) · theme: [`evidence.config.yaml`](evidence.config.yaml)

Deploy: [`docs/DEPLOY.md`](../docs/DEPLOY.md)
