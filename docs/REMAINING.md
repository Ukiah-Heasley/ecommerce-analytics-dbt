# Remaining work

What's been shipped and what's still on deck after the 2026-05-22 buildout.

## Shipped

- **Generator additions** ([scripts/generate.py](../scripts/generate.py)) — `utm_source / utm_medium / utm_campaign` on `raw_sessions`; `cost_usd` on `raw_products`.
- **Evidence.dev dashboard scaffold** ([reports/](../reports/)) — DuckDB-connected, style-guide theme, four working charts on two pages (revenue / AOV / refund rate / top products).
- **PROPOSALS addendum** — [PROPOSALS/marketing-and-ml-sources.md](../PROPOSALS/marketing-and-ml-sources.md) now documents the precursor work above.

## Remaining — dbt modeling (your exercise)

The new raw columns sit in the raw schema unused. Wire them through:

### UTM fields → `dim_campaign` (new mart)

| File | Change |
|---|---|
| `models/staging/_sources.yml` | Document the three new `raw_sessions` columns |
| `models/staging/stg_sessions.sql` | Pass through `utm_source`, `utm_medium`, `utm_campaign` |
| `models/marts/dim_campaign.sql` (new) | Type-1 dim, hash key on the triple, with a derived `channel_group`. Mirror the `dim_referrer` / `dim_refund_reason` pattern. Include an unknown/direct row. |
| `models/marts/fct_sessions.sql` | Add `campaign_id` FK (join logic mirrors the existing `referrer_id` join). |
| Tests | Uniqueness on `dim_campaign.campaign_id`; not-null on `fct_sessions.campaign_id` after the join. |

Suggested `channel_group` mapping (single `case` expression):

| utm_medium | channel_group |
|---|---|
| `cpc`, `paid_search` | `paid_search` |
| `social` | `social` |
| `email` | `email` |
| `affiliate` | `affiliate` |
| null | `direct` |
| other | `other` |

### `cost_usd` → `dim_products`

| File | Change |
|---|---|
| `models/staging/_sources.yml` | Document the new `raw_products.cost_usd` column |
| `models/staging/stg_products.sql` | Pass through `cost_usd` |
| `models/marts/dim_products.sql` | Pass through `cost_usd`. Optionally add a derived `gross_margin_pct = (price - cost_usd) / price`. |
| Tests | Optional: `cost_usd >= 0`, `cost_usd <= price`. |

## Remaining — dashboard pages to build (your exercise)

Three pages were left off the dashboard for presentation reasons (no TODO stubs in finished views). Build them as new files in [reports/pages/](../reports/pages/):

### `engagement.md` — DAU / WAU / MAU + stickiness

- Distinct `canonical_user_id` (not `user_id`, so identity-merged users count once) from `fct_sessions` over rolling 1 / 7 / 28 day windows
- DAU/MAU stickiness ratio as a single BigValue
- `fct_daily_sessions.daily_logged_in_users` is a head-start for DAU
- DuckDB rolling-window pattern: window function over the daily aggregate with `range between interval '6 days' preceding and current row`
- Don't put DAU and MAU on a dual-axis chart — use small multiples or index both to a common baseline

### `conversion.md` — session → purchase

- Overall conversion rate as a BigValue: `count(distinct session_id) filter (where t.transaction_id is not null) / count(distinct session_id)`
- Bar chart of conversion rate by `dim_referrer.referrer`
- Later, after `dim_campaign` exists: bar chart of conversion rate by `channel_group`
- Join `fct_sessions` to `fct_transactions` on `session_id`; filter txns via the `is_revenue_status()` macro (already in the project)
- Watch for null `session_id` on transactions — exclude those, don't count as non-converting

### `retention.md` — signup cohort retention + revenue retention

- Cohort assignment: `date_trunc('week', min(valid_from))` per `canonical_user_id` from `dim_users` (the *earliest* row, not `is_current = true`)
- Activity table for retention: `fct_sessions`. For revenue: `fct_transactions`
- Weeks-since-signup: `date_diff('week', cohort_week, activity_week)`
- Heatmap: use Evidence's pivoted `<DataTable>` with `<Column contentType=colorscale>` — cleaner read than a true heatmap
- The colorscale `#F1EFE8 → #378ADD` is already defined in [evidence.config.yaml](../reports/evidence.config.yaml) under `colorScales.default`
- Revenue-retention chart: `<LineChart>` with `series=cohort_week`, accent color on the most recent cohort + grey for older ones (highlight one, grey the rest)

## Remaining — once the dbt-modeling exercises land

When `dim_campaign` and `dim_products.cost_usd` are wired, two follow-ups become trivial in the dashboard:

1. **Channel mix on conversion.md** — bar of conversion rate by `dim_campaign.channel_group`.
2. **Margin page on revenue.md** — companion bar to "top products by revenue" showing top products by *gross margin*. These often differ, which is the analytical point.

## Remaining — promote dashboard SQL into dbt marts

The dashboard pages currently embed analytical SQL (AOV, refund rate, top-products SCD2 join). Promoting these to dbt models gives:

- **Single source of truth** — one definition of "AOV", lineage-tracked, dbt-testable.
- **Trivial page queries** — the markdown shrinks to `select transaction_day, aov from main.fct_daily_transactions order by 1` — no calculations in the dashboard layer.
- **Reuse** — any future BI tool, notebook, or analyst gets the same metric without copying SQL.

Candidates, in priority order:

| Dashboard query (location) | Promote to dbt as | Effort |
|---|---|---|
| `aov_trend` ([index.md](../reports/pages/index.md)) | New columns `aov_usd` on `fct_daily_transactions` | Trivial — add one calculated column |
| `refund_rate_trend` ([index.md](../reports/pages/index.md)) | New column `refund_rate_pct` on `fct_daily_transactions` | Trivial |
| `kpis` ([index.md](../reports/pages/index.md)) (7-day rollup) | New mart `metrics_overview` (one row, current window) | Small |
| `top_products` / `top_products_by_orders` ([revenue.md](../reports/pages/revenue.md)) | New mart `agg_product_performance` — per-product aggregates over the SCD2 point-in-time join, with `gross_revenue`, `order_count`, `refund_count`, and (once `cost_usd` is wired) `gross_margin` | Medium |

After promotion, every Evidence source `.sql` file is a one-line `select * from main.<mart>` passthrough and every page query is `select ... from ecommerce.<mart>` with sorting/filtering only — no calculation.

This is also the "single source of truth" question's real answer: when dashboard SQL is just `select * from a dbt mart`, there's nothing to duplicate. The current architecture is intentionally pre-this — the pages serve as the worked spec for what the dbt marts should look like.

## Remaining — publishing the dashboard

Goal: make this visible from the GitHub repo for portfolio purposes.

**Recommended: GitHub Pages via Actions workflow.**
- Add a workflow `.github/workflows/deploy-dashboard.yml` that on push to `master`:
  1. Sets up Python + Node
  2. Runs `python scripts/generate.py --reset --days 7` + `python scripts/load_raw.py` + `dbt run`
  3. Runs `cd reports && npm ci && npm run sources && npm run build`
  4. Uploads `reports/build/` as a Pages artifact + deploys
- Enable Pages in repo settings → source: GitHub Actions
- Result: dashboard lives at `https://<user>.github.io/ecommerce-analytics-dbt/` on every push

**Also recommended: README screenshots.** A live dashboard URL is great, but the GitHub repo home page should show off a chart immediately. Run the dashboard locally, screenshot one or two of the best charts as PNG, drop into `docs/screenshots/` and embed in [README.md](../README.md) above "Quickstart". First impressions matter.

**Not viable: GitHub Wiki.** Wikis only render markdown — they can't host a SvelteKit/JavaScript app. Don't try this path.

**Alternative: Cloudflare Pages / Netlify.** Both have free tiers, connect to the repo, and deploy on push. Easier setup than the GitHub Actions route — point the service at the repo, set build command `cd reports && npm ci && npm run sources && npm run build`, output `reports/build`. Choose this if you'd rather not maintain CI workflow YAML.

**Alternative: Evidence Cloud.** Evidence's own hosting (free tier). Tightest integration with Evidence (incremental builds, scheduled refresh) but it's a third-party service rather than GitHub-native.

## Remaining — bigger initiatives

- **Full marketing + ML sources proposal** — the four new sources (`raw_ad_spend`, `raw_marketing_touches`, `raw_model_registry`, `raw_predictions`) described in [PROPOSALS/marketing-and-ml-sources.md](../PROPOSALS/marketing-and-ml-sources.md). Unlocks CAC / ROAS / multi-touch attribution / prediction calibration.
- **Optional single-column source additions** — `discount_amount` on transactions (promo effectiveness), `region` on sessions (geographic breakdowns). Both ~5-line generator changes when wanted.

## Suggested order of attack

1. **Wire `cost_usd`** through staging → `dim_products`. Smallest, fastest dbt win. Unlocks a margin chart on `revenue.md`.
2. **Promote dashboard SQL into marts** (`aov`, `refund_rate`, `agg_product_performance`). Pure refactor — same numbers, cleaner architecture, single source of truth.
3. **Set up GitHub Pages deploy.** Once the dashboard is stable, get it published — that's the portfolio-visibility win.
4. **Wire UTM fields** through staging → `dim_campaign` → `fct_sessions`. Bigger lift; unlocks `conversion.md`.
5. **Build the three remaining dashboard pages** (engagement, conversion, retention) using the specs above.
6. **Tackle the full marketing+ML proposal** once the modeling muscle is warm.
