# ecommerce-analytics-dbt

![CI](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/actions/workflows/ci.yml/badge.svg)

End-to-end dbt + DuckDB pipeline: simulated source extracts → raw landing → staging →
intermediate → marts, with SCD2 snapshots, identity resolution, late-arrival handling,
and an Evidence.dev dashboard — all runnable on a laptop.

![dbt](https://img.shields.io/badge/dbt-1.11-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/) ·
**Docs:** [Wiki](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/wiki)

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DBT_PROFILES_DIR=$(pwd)

python scripts/generate.py --reset --days 7   # E — simulate extracts
python scripts/load_raw.py                    # L — land CSVs in raw schema
dbt deps && dbt build
```

Advance the simulated clock: `python scripts/generate.py` → `load_raw.py` → `dbt build`.

## What it models

- **Sources:** `users` (auth_db + crm), `products`, `sessions`, `transactions`
- **Snapshots:** SCD2 for users and products
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
| GitHub Pages deploy (maintainers) | [`docs/DEPLOY.md`](docs/DEPLOY.md) |

Wiki source files live in [`wiki/`](wiki/) — tracked in this repo, published to GitHub Wiki.

## License

[MIT](LICENSE)
