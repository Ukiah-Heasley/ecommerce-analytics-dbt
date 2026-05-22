# Design

## E and L separated from T

`scripts/generate.py` writes CSVs. `scripts/load_raw.py` lands them in a
`raw` schema in DuckDB. dbt runs against `raw`. The alternative —
`meta: external_location` on sources — was rejected because it conflates
loading and transformation; production warehouses are typically fed by a
managed ingestion tool (Fivetran, Debezium, Airbyte) writing into a landing
schema, and the local pipeline mirrors that boundary.

## Snapshots cover CDC sources only

| Source        | Pattern       | Snapshotted |
|---------------|---------------|-------------|
| users         | CDC           | yes         |
| products      | CDC           | yes         |
| transactions  | CDC           | no          |
| sessions      | append-only   | no          |

Transactions are CDC but their mutating attributes (`status`,
`refund_amount`, `refunded_at`) are terminal — a row refunds once. The
latest row carries all history the marts require. Partial refunds or
chargebacks would invalidate this and require a snapshot.

`hard_deletes: new_record` is set so a removed `user_id` records a
deletion-event row rather than appearing current indefinitely.

## Snapshots are not enriched

Snapshots capture staging models verbatim. Derived columns
(`canonical_user_id`) are computed in `int_users`, downstream of the
snapshot. Snapshotting a derivation means any change to the derivation
logic rewrites historical `dbt_valid_from` values.

## Identity resolution by canonical email

Around 5 users in the generated data appear in both `auth_db` and `crm`
with the same normalized email under different `user_id`s. `int_users`
assigns a `canonical_user_id` per `email_normalized`, with `auth_db`
winning ties as the system of record for authentication. Both source rows
are kept; the merge is expressed via `canonical_user_id` and an
`is_merged` flag, preserving source-side joinability.

## Session dedup in intermediate, not staging

Staging is 1:1 with the source by design, so duplicate session rows are
preserved there. `int_sessions_deduped` selects the latest ingest per
`session_id` via `row_number() over (partition by session_id order by
_ingested_at desc)`.

## Default-row pattern for unresolved FKs

Every dim contains a default row keyed by `md5('unknown')`. Facts
`coalesce(...)` to that hash when a dim lookup misses, so unresolved FKs
become joinable rows rather than nulls that break aggregations. The
`default_sk` macro is the single source of truth for the hash expression,
preventing drift between the fact's `coalesce` and the dim's `union all`.

## Bounded resolution replay

`fct_sessions` and `fct_transactions` are incremental on `_ingested_at`.
That alone strands fact rows whose dim FK was still the default SK at
first load: when the late-arriving dim row appears, the fact does not
reprocess.

Each incremental run additionally re-pulls fact rows where the dim SK is
still the default *and* the event time is within
`dim_resolution_replay_days` (30 by default). Outside that window,
unresolved rows are treated as permanently default and removed from the
replay set.

## Point-in-time joins on event time

Facts join dims on `event_at >= valid_from and (event_at < valid_to or
valid_to is null)`. Each event resolves to the dim version current at the
event's timestamp, not at load time. A transaction recorded against a $50
product remains attributed to the $50 version after a subsequent price
change.

## Lookback windows as project vars

`session_lookback_days` and `dim_resolution_replay_days` are defined in
`dbt_project.yml`. The sliding window in `fct_daily_sessions`, the late-
arrival audit, and the SLA breach test all reference
`session_lookback_days`, keeping the window consistent across the
pipeline.

## Audit, warn, do not fail

`audit_late_arrivals` surfaces sessions whose ingest lateness exceeds
`session_lookback_days`. The singular test on top is `severity: warn`.
Late arrivals are an SLA concern, not a correctness defect, and should
not block a build.

## Out of scope

- Multi-currency normalization (no FX table)
- Partial refunds and chargebacks (would require a transactions snapshot)
- Sub-daily or streaming ingestion
