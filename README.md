# ecommerce-analytics-dbt

![CI](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/actions/workflows/ci.yml/badge.svg)

An end-to-end dbt + DuckDB pipeline modeling an e-commerce warehouse from simulated
source extracts through SCD2 snapshots, identity resolution, late-arrival handling,
and an Evidence.dev dashboard — all runnable on a laptop.

Built as a hands-on exercise in production-grade analytics engineering, the project
deliberately mirrors patterns you'd encounter with a managed ingestion tool
(Fivetran, Debezium) feeding into Snowflake or BigQuery.

![dbt](https://img.shields.io/badge/dbt-1.11-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Ruff](https://img.shields.io/badge/lint-ruff-261230)
![SQLFluff](https://img.shields.io/badge/lint-sqlfluff-25c2a0)

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/) ·
**Docs:** [Wiki](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki)

## What this demonstrates

- **E/L/T boundary** — Python simulate + load into `raw`; dbt owns transform only
- **SCD2 snapshots** — users and products; CDC scope discipline (transactions excluded)
- **Identity resolution** — cross-source `canonical_user_id` with auth_db precedence
- **Late arrivals** — sliding lookback, audit mart, warn-only SLA test
- **Incremental replay** — bounded dim-resolution window for unresolved FKs
- **Default-row pattern** — joinable unknowns instead of null-poisoned aggregates
- **Evidence dashboard** — 2 live pages + extension exercises; CI deploys to GitHub Pages

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

Advance the simulated clock: `python scripts/generate.py` → `load_raw.py` → `dbt build`.

For linting, pre-commit, Node, and dashboard dev: [Developer Setup (wiki)](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki/Developer-Setup).

## What it models

- **Sources:** `users` (auth_db + crm), `products`, `sessions`, `transactions`
- **Snapshots:** SCD2 for users and products (`users_snapshot`, `products_snapshot`)
- **Marts:** dims + facts at event and daily grain
- **Audit:** late-arrival SLA surface + warn-only test

Edge cases baked into the generator: CDC vs append-only ingestion, refund mutations,
duplicate/late session events, cross-source identity overlap, periodic price changes.

## Documentation

| Topic | Location |
|-------|----------|
| Architecture, data model, edge cases, design rationale | [Wiki](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki) |
| Local dev, linting, pre-commit | [Developer Setup (wiki)](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki/Developer-Setup) |
| Dashboard pages and styling | [Dashboard (wiki)](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki/Dashboard) |
| Repo docs index, deploy, wiki sync | [`docs/README.md`](docs/README.md) |

Wiki source files live in [`wiki/`](wiki/) — tracked in this repo, published to GitHub Wiki.

## Roadmap

- Enforce dbt-checkpoint conventions as a CI hard fail (currently warn-only; see [Design Decisions](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki/Design-Decisions))

## License

[MIT](LICENSE)
