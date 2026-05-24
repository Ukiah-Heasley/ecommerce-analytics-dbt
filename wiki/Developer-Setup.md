# Developer Setup

Everything you need to develop on the project locally — dependencies, linting, pre-commit, and dashboard tooling.

For the canonical clone-and-run quickstart, see the repo [README](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt#quickstart).

## Prerequisites

- Python 3.13
- Node 20+ (for the Evidence.dev dashboard)
- macOS or Linux (the helper scripts assume POSIX paths)

## Python environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
export DBT_PROFILES_DIR=$(pwd)
```

## Run the pipeline

```bash
python scripts/generate.py --reset --days 7   # E — simulate extracts
python scripts/load_raw.py                    # L — land CSVs in raw schema
dbt deps && dbt build
```

Advance the simulated clock without resetting:

```bash
python scripts/generate.py            # +1 day
python scripts/generate.py --days 3   # +3 days
python scripts/load_raw.py            # land new CSVs
dbt build                             # refresh staging → snapshots → marts
```

## Pre-commit hooks

Linting is defined in `.pre-commit-config.yaml` — CI runs the same hooks, so there is no config drift.

```bash
pre-commit install
```

This wires `git commit` to run the default-stage hooks: SQLFluff, Ruff, yamllint. The `manual` stage holds dbt-checkpoint (run on demand).

Run on demand:

```bash
pre-commit run --all-files                       # default-stage hooks (hard fail)
pre-commit run --all-files --hook-stage manual   # dbt-checkpoint (warn-only)
```

| Tool | Checks | Stage |
|---|---|---|
| SQLFluff | dbt-templated SQL, DuckDB dialect, dbt Labs' published ruleset | default |
| Ruff | Python lint + format on `scripts/*.py` | default |
| yamllint | YAML style (relaxed) | default |
| dbt-checkpoint | dbt conventions — descriptions, tests, naming | manual |

See [[Design-Decisions]] for why dbt-checkpoint is warn-only rather than a hard fail.

**Gotcha:** SQLFluff/pre-commit fails if another process holds a lock on `ecommerce_analytics.duckdb`.

## Dashboard

Build the warehouse from the repo root first — Evidence reads the DuckDB file produced by dbt:

```bash
cd reports
npm install                 # first time only
npm run sources             # materialize queries from ../ecommerce_analytics.duckdb
npm run dev                 # http://localhost:3000 — live-reload
npm run build               # static site → build/ecommerce-analytics-dbt/
npm run preview             # serve the built site locally
```

Style tokens in `reports/evidence.config.yaml`; conventions in `reports/STYLE.md`.

**Live demo:** [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/) — published on push to `master` via GitHub Actions. See [`docs/DEPLOY.md`](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/blob/master/docs/DEPLOY.md) for one-time Pages setup.

## Where to go next

- [[Home]] — back to the overview
- [[Architecture]] — what you'll be working on once the tooling is set up
