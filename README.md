# ecommerce-analytics-dbt

End-to-end dbt + DuckDB pipeline modeling an e-commerce warehouse: simulated
source extracts → raw landing → staging → intermediate → marts, with SCD2
snapshots, identity resolution, late-arrival handling, and audit tests.

Built as a hands-on exercise in production-grade analytics engineering on a
laptop.

## Stack

![dbt](https://img.shields.io/badge/dbt-1.11-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)

dbt-core 1.11 · dbt-duckdb 1.10 · DuckDB 1.5 · Python 3.13 · Faker

## What it models

- **Sources:** `users` (auth_db + crm), `products`, `sessions`, `transactions`
- **Snapshots:** SCD2 for users and products
- **Marts:**
  - `dim_users`, `dim_products`, `dim_session_context`, `dim_referrer`, `dim_refund_reason`
  - `fct_sessions`, `fct_transactions`
  - `fct_daily_sessions`, `fct_daily_transactions`
- **Audit:** `audit_late_arrivals` + SLA breach test

## Realistic edge cases baked into the generator

- CDC vs append-only ingestion patterns side by side
- Refunds that mutate the original transaction row (snapshot territory)
- Duplicate + late-arriving session events (event-time lookback windows)
- Cross-source identity overlap on normalized email (identity resolution)
- Periodic price changes (SCD2 point-in-time revenue attribution)

Deterministic seed — same inputs every run.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DBT_PROFILES_DIR=$(pwd)

python scripts/generate.py --reset --days 7   # E — simulate extracts
python scripts/load_raw.py                    # L — land CSVs in raw schema
dbt deps && dbt snapshot && dbt run && dbt test
```

Advance the simulated clock without resetting:

```bash
python scripts/generate.py            # +1 day
python scripts/generate.py --days 3   # +3 days
```

## Layout

```
models/
  staging/        # 1:1 with sources, light typing + renames
  intermediate/   # dedup, identity resolution
  marts/          # dims + facts (grain: event, daily)
  utilities/      # audit models
snapshots/        # SCD2 for users, products
macros/           # default-row SK, revenue status, refund normalization
scripts/
  generate.py     # Faker-based source simulator (deterministic)
  load_raw.py     # CSV → DuckDB raw schema
tests/            # singular tests (SLA breach audit)
```

## Design

Key decisions and rationale in [docs/DESIGN.md](docs/DESIGN.md): E+L/T
separation, snapshot scope, identity resolution, default-row pattern,
bounded replay for late-arriving dims, point-in-time joins.

## License

[MIT](LICENSE)
