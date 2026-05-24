# Design Decisions

Cross-cutting choices that don't fit cleanly into [[Architecture]] or [[Data-Model]] but matter for understanding *why* the project looks the way it does.

> The architectural decisions (E/L/T split, snapshot scope, identity resolution, default rows, replay window) are documented on their respective pages. This page covers the *operational* and *tooling* decisions.

## Audit, warn, do not fail

`audit_late_arrivals` surfaces sessions whose ingest lateness exceeds `session_lookback_days`. The singular test on top is `severity: warn`.

Late arrivals are an **SLA concern**, not a correctness defect. The pipeline produced correct numbers given the data it had at the moment it ran; the issue is upstream punctuality. Hard-failing on that would mean a single misbehaving source system can block every downstream build at 3am, which is the wrong incentive. Surface, don't suppress; warn, don't fail.

The same philosophy applies to dbt-checkpoint conventions (see below): mechanical defects fail loudly; quality-of-life issues warn.

## Quality tooling: warn-by-default for project conventions

Three tools, two failure modes:

| Tool | Checks | Failure mode |
|---|---|---|
| SQLFluff | dbt-templated SQL, DuckDB dialect | **Hard fail** in CI |
| Ruff | Python lint + format (`scripts/*.py`) | **Hard fail** in CI |
| dbt-checkpoint | dbt conventions (descriptions, tests, naming) | **Warn-only** in CI |

The split is intentional. SQL syntax and Python lint failures are mechanical and unambiguous — there's a right answer, and CI should enforce it. dbt-checkpoint failures (missing descriptions, missing tests, model-naming conventions) are reported as warnings because the project is still being built out, and these checks should *guide* work without *blocking* the build.

CI and local dev share a single config: `.pre-commit-config.yaml`. CI runs `pre-commit run --all-files` for default-stage hooks and the manual stage with `continue-on-error: true`.

The pre-commit config places dbt-checkpoint hooks on the `manual` stage so they don't run on every `git commit`. Invoke them explicitly:

```bash
pre-commit run --all-files --hook-stage manual
```

Once the model layer stabilizes, flip dbt-checkpoint to a hard fail and remove the warn-only escape hatch.

## SQLFluff config follows dbt Labs' published ruleset

The `.sqlfluff` config follows dbt Labs' published ruleset verbatim:

- `templater = dbt`
- 80-column lines
- lowercase identifiers
- trailing commas
- group-by by number
- explicit aliasing

Plus `dialect = duckdb` for local runs.

Two directories are excluded:

- `macros/` — per dbt's published guidance, heavy Jinja confuses the parser
- `snapshots/` — the snapshot config block isn't valid SQL on its own

If a macro starts producing strange lint errors, check whether the parser is choking on Jinja before assuming the SQL is wrong.

## Out of scope

These are *deliberately* not modeled. Each would be a meaningful expansion in its own right:

- **Multi-currency normalization** — no FX table. All amounts are in USD.
- **Partial refunds and chargebacks** — would invalidate the "refunds are terminal" assumption that lets `fct_transactions` skip snapshotting (see [[Edge-Cases]]).
- **Sub-daily or streaming ingestion** — the lookback windows and incremental cadence assume daily batch.

## Where to go next

- [[Architecture]] — the layered design these decisions hang off
- [[Developer-Setup]] — concrete commands for the tooling discussed above
