# ecommerce-analytics-dbt

An end-to-end dbt + DuckDB pipeline modeling an e-commerce warehouse from simulated source extracts through SCD2 snapshots, identity resolution, late-arrival handling, and an Evidence.dev dashboard — all runnable on a laptop.

Built as a hands-on exercise in production-grade analytics engineering, the project deliberately mirrors patterns you'd encounter with a managed ingestion tool (Fivetran, Debezium) feeding into Snowflake or BigQuery.

## Stack

![dbt](https://img.shields.io/badge/dbt-1.11-orange) ![DuckDB](https://img.shields.io/badge/DuckDB-1.5-yellow) ![Python](https://img.shields.io/badge/Python-3.13-blue) ![Ruff](https://img.shields.io/badge/lint-ruff-261230) ![SQLFluff](https://img.shields.io/badge/lint-sqlfluff-25c2a0)

dbt-core 1.11 · dbt-duckdb 1.10 · DuckDB 1.5 · Python 3.13 · Faker · Evidence.dev

## Where to start

| If you want to… | Go to |
|---|---|
| Understand the layered architecture | [[Architecture]] |
| See every dim and fact in one place | [[Data-Model]] |
| Read the modeling rationale | [[Design-Decisions]] |
| Walk through the realistic edge cases | [[Edge-Cases]] |
| See the dashboard | [[Dashboard]] |
| Set up the dev tooling | [[Developer-Setup]] |

## Quickstart

```bash
git clone https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt
cd ecommerce-analytics-dbt
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DBT_PROFILES_DIR=$(pwd)

python scripts/generate.py --reset --days 7   # E — simulate extracts
python scripts/load_raw.py                    # L — land CSVs in raw schema
dbt deps && dbt build
```

See [[Developer-Setup]] for linting, pre-commit, and dashboard tooling.

## Links

- **Live dashboard:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/)
- **Source code:** [github.com/Ukiah-Heasley/ecommerce-analytics-dbt](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt)
