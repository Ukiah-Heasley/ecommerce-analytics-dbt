# Edge Cases

The data generator (`scripts/generate.py`) deliberately produces the messy realities a real ingestion pipeline has to absorb. Each pattern below shows up consistently across runs (deterministic seed=42), so the corresponding model logic gets exercised every build.

## Duplicate session events

**What the generator does:** ~14 sessions per 7-day window are emitted twice — same `session_id`, different `_ingested_at`.

**How the pipeline handles it:** Staging is 1:1 with the source by design, so duplicates are preserved there. `int_sessions_deduped` selects the latest ingest per session_id:

```sql
select * from (
  select
    *,
    row_number() over (
      partition by session_id
      order by _ingested_at desc
    ) as rn
  from {{ ref('stg_sessions') }}
) where rn = 1
```

The dedup happens in **intermediate, not staging**, so the staging layer remains a faithful mirror of the source — debuggable, auditable, and free of opinionated logic.

**Inspect:**
```sql
select session_id, count(*) as ingest_count
from raw.raw_sessions
group by session_id having count(*) > 1;
```

## Late-arriving session events

**What the generator does:** From day 3 onward, ~10 sessions per week have `started_at` set 2 days before their `_ingested_at`.

**How the pipeline handles it:**
- `fct_daily_sessions` uses an event-time lookback window of `session_lookback_days` (3 by default) so late arrivals re-aggregate into the correct historical day.
- `audit_late_arrivals` surfaces any session whose ingest lateness exceeds the lookback window.
- The singular SLA test on top of the audit is `severity: warn` — late arrivals are an SLA concern, not a correctness defect, and shouldn't block a build.

**Inspect:**
```sql
select session_id, started_at, _ingested_at,
       date_diff('day', started_at, _ingested_at) as lateness_days
from raw.raw_sessions
where date_diff('day', started_at, _ingested_at) > 0
order by lateness_days desc;
```

## Refunds that mutate the original row

**What the generator does:** ~14% of transactions are refunded. The refund mutates the *original* transaction row — `status`, `refund_amount`, `refunded_at`, and `updated_at` change in place — exactly what a CDC tool like Fivetran or Debezium would emit.

**How the pipeline handles it:** Transactions are technically CDC, but the mutating attributes are **terminal** — a transaction refunds once. The latest row carries all the history `fct_transactions` needs, so no snapshot is required. Partial refunds or chargebacks would change this analysis; see [[Design-Decisions]] for the explicit out-of-scope note.

**Inspect:**
```sql
select status, count(*), round(sum(amount_usd), 2) as gross,
       round(sum(coalesce(refund_amount, 0)), 2) as refunded
from raw.raw_transactions group by status;
```

## Cross-source identity overlap

**What the generator does:** ~5 users per run appear in **both** `auth_db` and `crm` with the **same normalized email** under different `user_id`s — the classic identity-resolution problem that surfaces whenever two source systems independently mint primary keys.

**How the pipeline handles it:** `int_users` assigns a `canonical_user_id` per `email_normalized`, with `auth_db` winning ties as the system of record for authentication. Both source rows are kept; the merge is expressed via `canonical_user_id` and an `is_merged` flag. Source-side joinability is preserved while downstream marts get a single user grain.

**Inspect:**
```sql
select email_normalized, count(distinct user_id) as source_user_count
from raw.raw_users
group by email_normalized having count(distinct user_id) > 1;
```

## Periodic price changes (SCD2 territory)

**What the generator does:** Roughly 1 product per ~3 days gets a price bump. The row mutates in place in `raw_products`; `updated_at` advances.

**How the pipeline handles it:** `snapshots/products` captures the SCD2 history. `fct_transactions` joins `dim_products` on event time:

```sql
and ft.event_at >= dp.valid_from
and (ft.event_at < dp.valid_to or dp.valid_to is null)
```

A transaction made against the $50 version stays attributed to the $50 version forever. Without this, every price change retroactively rewrites your historical revenue numbers — a silent and devastating reporting bug.

**Inspect:**
```sql
select product_id, price_usd, dbt_valid_from, dbt_valid_to
from snapshots_products_snapshot
where product_id in (
  select product_id
  from snapshots_products_snapshot
  group by product_id having count(*) > 1
) order by product_id, dbt_valid_from;
```

## Where to go next

- [[Architecture]] — why the snapshot / dedup / replay layers exist where they do
- [[Data-Model]] — the dims and facts these patterns flow through
