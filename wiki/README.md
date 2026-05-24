# Wiki source files

This folder is the **source of truth** for the GitHub Wiki. It is tracked in the
main repo (not gitignored) so wiki content is versioned alongside the code.

## What lives here vs elsewhere

| Content | Location |
|---------|----------|
| Architecture, data model, edge cases, design rationale | `wiki/` → GitHub Wiki |
| Portfolio landing + quickstart | `README.md` |
| GitHub Pages deploy ops (maintainers) | `docs/DEPLOY.md` |
| Dashboard local dev commands | `reports/README.md` |

The live dashboard at [ukiah-heasley.github.io/ecommerce-analytics-dbt](https://ukiah-heasley.github.io/ecommerce-analytics-dbt/) replaces static screenshots — wiki pages link to it directly.

## First-time setup (wiki does not exist yet)

GitHub creates the wiki git remote only after you enable the feature and create
the first page via the web UI.

1. Open **[Settings → General → Features](https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt/settings)** → enable **Wikis**.
2. Go to the repo **Wiki** tab → **Create the first page** (any title/body — this initializes the remote).
3. Publish from this folder (see below).

## Publish updates

From the repo root, after the wiki remote exists:

```bash
git clone https://github.com/Ukiah-Heasley/ecommerce-analytics-dbt.wiki.git /tmp/ecommerce-analytics-dbt.wiki
cp wiki/{Home,_Sidebar,Architecture,Data-Model,Edge-Cases,Dashboard,Design-Decisions,Developer-Setup}.md \
   /tmp/ecommerce-analytics-dbt.wiki/
cd /tmp/ecommerce-analytics-dbt.wiki
git add .
git commit -m "Sync wiki from main repo"
git push
```

Or copy into an existing wiki clone you already have checked out.

## Editing workflow

1. Edit files in `wiki/` on a branch in the main repo (reviewable, versioned).
2. Merge to `master`.
3. Push to the wiki remote (steps above).

Do **not** edit wiki pages only in the GitHub web UI — those changes will be
overwritten on the next sync from `wiki/`.
