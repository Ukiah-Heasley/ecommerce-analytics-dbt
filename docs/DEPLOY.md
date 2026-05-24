# Deploying the dashboard (GitHub Pages)

The Evidence dashboard can be published as a static site from this repo.
CI builds fresh mock data, runs dbt, then builds and deploys `reports/`.

## One-time repo setup

1. Open **Settings → Pages** in the GitHub repo.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Merge or push the [`deploy-dashboard.yml`](../.github/workflows/deploy-dashboard.yml)
   workflow to `master`.
4. After the first successful run, the site is available at:

   **https://ukiah-heasley.github.io/ecommerce-analytics-dbt/**

   (URL follows `https://<user>.github.io/<repo-name>/`.)

## What the workflow does

On each push to `master` (and on manual **workflow_dispatch**):

1. `python scripts/generate.py --reset --days 7`
2. `python scripts/load_raw.py`
3. `dbt build`
4. `cd reports && npm ci && npm run sources && npm run build`
5. Upload `reports/build/ecommerce-analytics-dbt/` → GitHub Pages

Evidence is configured with `deployment.basePath: /ecommerce-analytics-dbt` so
assets resolve under the project Pages URL (not the domain root).

## Local preview (production base path)

```bash
# From repo root — same pipeline as CI
python scripts/generate.py --reset --days 7
python scripts/load_raw.py
dbt build

cd reports
npm install
npm run sources
npm run build
npm run preview   # serves the built site locally
```

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Pages workflow never appears | Source must be **GitHub Actions**, not “Deploy from branch” |
| Upload artifact “directory not found” | `reports/package.json` `build` script must set `EVIDENCE_BUILD_DIR=./build/ecommerce-analytics-dbt` |
| Blank or broken assets on Pages | `evidence.config.yaml` `deployment.basePath` must match the repo name |
| `sources` fails in CI | Confirm `dbt build` completed and `ecommerce_analytics.duckdb` exists at repo root |
