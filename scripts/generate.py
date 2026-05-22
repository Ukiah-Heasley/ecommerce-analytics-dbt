"""
Mock data generator for the v2 sample project.

Simulates two ingestion patterns side by side:
  - CDC tables (users, products, transactions): the file IS the current state.
    Rewritten every run. Refunds mutate existing transaction rows in place,
    advancing `updated_at` — exactly what Fivetran/Debezium would produce.
  - Append-only event log (sessions): rows accumulate forever. Late arrivals
    and duplicates are inserted as new rows; existing rows are never touched.

Usage:
    python generate.py --reset       wipe data/ and generate day 1
    python generate.py               advance one day
    python generate.py --days 5      advance five days from current state
"""

import argparse
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

# ---------------------------------------------------------------------------
# Config — tiny scale, eyeball-able

SIM_START = datetime(2026, 5, 1)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STATE_PATH = DATA_DIR / "STATE.json"
SEED = 42

N_USERS_INITIAL = 100
N_PRODUCTS = 20
N_SESSIONS_PER_DAY = 50
N_TXNS_PER_DAY = 10

CATEGORIES = ["apparel", "electronics", "home", "outdoor", "media"]
PLATFORMS = ["ios", "android", "web"]
DEVICES = ["mobile", "desktop", "tablet"]
COUNTRIES = ["US", "CA", "GB", "DE", "FR", "AU", "JP", "BR"]
REFERRERS = ["google", "direct", "email", "facebook", None]
REFUND_REASONS = [
    "customer_request",
    "duplicate_charge",
    "fraud",
    "item_not_received",
]

# (utm_source, utm_medium, utm_campaign). A None triple represents direct or
# organic traffic; drawn ~30% of the time, rest split across campaigns.
CAMPAIGNS = [
    ("google", "cpc", "spring_sale_2026"),
    ("facebook", "social", "lookalike_q2"),
    ("tiktok", "social", "gen_z_launch"),
    ("newsletter", "email", "weekly_digest"),
    ("partner_blog", "affiliate", "tech_review_apr"),
    (None, None, None),
]
CAMPAIGN_WEIGHTS = [0.18, 0.16, 0.12, 0.14, 0.10, 0.30]

USERS_FILE = DATA_DIR / "raw_users.csv"
PRODUCTS_FILE = DATA_DIR / "raw_products.csv"
SESSIONS_FILE = DATA_DIR / "raw_sessions.csv"
TXNS_FILE = DATA_DIR / "raw_transactions.csv"

USERS_COLS = [
    "user_id",
    "email",
    "phone",
    "first_name",
    "last_name",
    "status",
    "created_at",
    "updated_at",
    "_source_system",
    "_ingested_at",
]
PRODUCTS_COLS = [
    "product_id",
    "name",
    "description",
    "category",
    "price",
    "cost_usd",
    "currency",
    "is_active",
    "created_at",
    "updated_at",
    "_source_system",
    "_ingested_at",
]
SESSIONS_COLS = [
    "session_id",
    "user_id",
    "anonymous_id",
    "started_at",
    "ended_at",
    "duration_seconds",
    "device_type",
    "platform",
    "country",
    "referrer",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "_source_system",
    "_ingested_at",
    "_batch_id",
]
TXNS_COLS = [
    "transaction_id",
    "user_id",
    "session_id",
    "product_id",
    "amount",
    "currency",
    "status",
    "event_at",
    "updated_at",
    "refund_amount",
    "refunded_at",
    "refund_reason",
    "_source_system",
    "_ingested_at",
]


# ---------------------------------------------------------------------------
# IO helpers


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def append_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    new_file = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"current_day": 0}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Value generators


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def day_ts(day: int, fake: Faker) -> datetime:
    """A random timestamp inside the given simulated day."""
    base = SIM_START + timedelta(days=day - 1)
    return base + timedelta(seconds=random.randint(0, 86399))


def messy_phone(fake: Faker) -> str:
    """Return a phone string in one of several real-world formats."""
    digits = fake.numerify("##########")
    fmt = random.choice(["+1-{}-{}-{}", "({}) {}-{}", "{}.{}.{}", "{}{}{}"])
    return fmt.format(digits[:3], digits[3:6], digits[6:])


def messy_email(fake: Faker) -> str:
    """Return an email with realistic inconsistencies (case, whitespace)."""
    e = fake.email()
    if random.random() < 0.2:
        e = e.upper()
    if random.random() < 0.1:
        e = f"  {e} "
    return e


def pick_campaign() -> tuple[str, str, str]:
    """Return (utm_source, utm_medium, utm_campaign); may be all None."""
    return random.choices(CAMPAIGNS, weights=CAMPAIGN_WEIGHTS, k=1)[0]


def utm_cells(triple: tuple) -> dict:
    """Convert a campaign triple to CSV-friendly cells (None → empty string)."""
    src, med, cmp = triple
    return {
        "utm_source": src or "",
        "utm_medium": med or "",
        "utm_campaign": cmp or "",
    }


# ---------------------------------------------------------------------------
# Initial-state generators (day 1)


def gen_initial_users(fake: Faker, day: int) -> list[dict]:
    users = []
    for _ in range(N_USERS_INITIAL):
        email = messy_email(fake)
        phone = messy_phone(fake)
        created = day_ts(day, fake)
        users.append(
            {
                "user_id": f"usr_{fake.uuid4()[:8]}",
                "email": email,
                "phone": phone,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "status": "active",
                "created_at": iso(created),
                "updated_at": iso(created),
                "_source_system": "auth_db",
                "_ingested_at": iso(created),
            }
        )

    # Identity-resolution test: ~5% of users have a duplicate row in crm
    # with same normalized email/phone but a different user_id.
    overlap_count = max(1, int(N_USERS_INITIAL * 0.05))
    for u in random.sample(users, overlap_count):
        users.append(
            {
                **u,
                "user_id": f"usr_{fake.uuid4()[:8]}",
                "email": u["email"].lower().strip(),
                "_source_system": "crm",
            }
        )
    return users


def gen_initial_products(fake: Faker, day: int) -> list[dict]:
    products = []
    for _ in range(N_PRODUCTS):
        created = day_ts(day, fake)
        price = round(random.uniform(5, 250), 2)
        # Cost is set once at creation; price drifts in gen_daily_products, but
        # cost stays flat so margin compresses/expands over the SCD2 history.
        cost = round(price * random.uniform(0.35, 0.65), 2)
        products.append(
            {
                "product_id": f"prd_{fake.uuid4()[:8]}",
                "name": fake.catch_phrase(),
                "description": fake.sentence(nb_words=8),
                "category": random.choice(CATEGORIES),
                "price": price,
                "cost_usd": cost,
                "currency": random.choices(
                    ["USD", "EUR"], weights=[0.85, 0.15]
                )[0],
                "is_active": True,
                "created_at": iso(created),
                "updated_at": iso(created),
                "_source_system": "product_db",
                "_ingested_at": iso(created),
            }
        )
    return products


# ---------------------------------------------------------------------------
# Daily change generators


def gen_daily_sessions(
    fake: Faker, day: int, users: list[dict], existing_sessions: list[dict]
) -> list[dict]:
    """New sessions for this day, plus duplicates and late arrivals."""
    new_rows = []
    ingested_today = SIM_START + timedelta(days=day - 1, hours=23)

    for _ in range(N_SESSIONS_PER_DAY):
        is_anon = random.random() < 0.15
        user = None if is_anon else random.choice(users)
        started = day_ts(day, fake)
        duration = random.randint(30, 3600)
        ended = started + timedelta(seconds=duration)
        new_rows.append(
            {
                "session_id": f"ses_{fake.uuid4()[:8]}",
                "user_id": "" if is_anon else user["user_id"],
                "anonymous_id": f"anon_{fake.uuid4()[:8]}",
                "started_at": iso(started),
                "ended_at": iso(ended) if random.random() > 0.05 else "",
                "duration_seconds": duration,
                "device_type": random.choices(DEVICES, weights=[0.5, 0.4, 0.1])[
                    0
                ],
                "platform": random.choice(PLATFORMS),
                "country": random.choice(COUNTRIES),
                "referrer": random.choice(REFERRERS) or "",
                **utm_cells(pick_campaign()),
                "_source_system": "event_tracker",
                "_ingested_at": iso(ingested_today),
                "_batch_id": f"batch_{ingested_today.strftime('%Y%m%d')}",
            }
        )

    # Edge case: ~2 duplicate sessions ingested again later in the day
    for dup in random.sample(new_rows, min(2, len(new_rows))):
        new_rows.append(
            {
                **dup,
                "_ingested_at": iso(ingested_today + timedelta(minutes=5)),
            }
        )

    # Edge case: ~2 late-arriving sessions whose started_at is 2 days behind
    if day >= 3:
        for _ in range(2):
            user = random.choice(users)
            started = day_ts(day - 2, fake)
            duration = random.randint(30, 3600)
            new_rows.append(
                {
                    "session_id": f"ses_{fake.uuid4()[:8]}",
                    "user_id": user["user_id"],
                    "anonymous_id": f"anon_{fake.uuid4()[:8]}",
                    "started_at": iso(started),
                    "ended_at": iso(started + timedelta(seconds=duration)),
                    "duration_seconds": duration,
                    "device_type": random.choice(DEVICES),
                    "platform": random.choice(PLATFORMS),
                    "country": random.choice(COUNTRIES),
                    "referrer": random.choice(REFERRERS) or "",
                    **utm_cells(pick_campaign()),
                    "_source_system": "event_tracker",
                    "_ingested_at": iso(ingested_today),
                    "_batch_id": f"batch_{ingested_today.strftime('%Y%m%d')}",
                }
            )

    return new_rows


def gen_daily_transactions(
    fake: Faker,
    day: int,
    users: list[dict],
    products: list[dict],
    sessions_today: list[dict],
    existing_txns: list[dict],
) -> list[dict]:
    """Returns the full updated transactions list (CDC-style overwrite)."""
    ingested_today = SIM_START + timedelta(days=day - 1, hours=23)
    txns = list(existing_txns)

    # New transactions for today
    eligible_sessions = [s for s in sessions_today if s["user_id"]]
    for _ in range(N_TXNS_PER_DAY):
        product = random.choice(products)
        if eligible_sessions and random.random() > 0.05:
            session = random.choice(eligible_sessions)
            user_id = session["user_id"]
            session_id = session["session_id"]
            event_at = datetime.fromisoformat(
                session["started_at"]
            ) + timedelta(seconds=random.randint(60, 1500))
        else:
            user_id = random.choice(users)["user_id"]
            session_id = ""
            event_at = day_ts(day, fake)

        txns.append(
            {
                "transaction_id": f"txn_{fake.uuid4()[:8]}",
                "user_id": user_id,
                "session_id": session_id,
                "product_id": product["product_id"],
                "amount": product["price"],
                "currency": product["currency"],
                "status": "completed",
                "event_at": iso(event_at),
                "updated_at": iso(event_at),
                "refund_amount": "",
                "refunded_at": "",
                "refund_reason": "",
                "_source_system": "payments",
                "_ingested_at": iso(ingested_today),
            }
        )

    # Edge case: from day 2 onward, refund 1–2 past transactions.
    # CDC semantics — mutate the existing row in place; advance updated_at.
    if day >= 2:
        refundable = [
            t
            for t in txns
            if t["status"] == "completed"
            and (ingested_today - datetime.fromisoformat(t["event_at"])).days
            >= 1
        ]
        for t in random.sample(
            refundable, min(random.randint(1, 2), len(refundable))
        ):
            full = random.random() > 0.3
            amount = float(t["amount"])
            refund_amount = (
                amount if full else round(amount * random.uniform(0.2, 0.8), 2)
            )
            t["status"] = "refunded" if full else "partially_refunded"
            t["refund_amount"] = refund_amount
            t["refunded_at"] = iso(
                ingested_today - timedelta(hours=random.randint(1, 12))
            )
            t["refund_reason"] = random.choice(REFUND_REASONS)
            t["updated_at"] = t["refunded_at"]
            t["_ingested_at"] = iso(ingested_today)

    return txns


def gen_daily_users(
    fake: Faker, day: int, existing_users: list[dict]
) -> list[dict]:
    """Returns the full updated users list (CDC-style overwrite)."""
    users = list(existing_users)
    ingested_today = SIM_START + timedelta(days=day - 1, hours=23)

    # A few new signups per day
    for _ in range(random.randint(2, 5)):
        created = day_ts(day, fake)
        users.append(
            {
                "user_id": f"usr_{fake.uuid4()[:8]}",
                "email": messy_email(fake),
                "phone": messy_phone(fake),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "status": "active",
                "created_at": iso(created),
                "updated_at": iso(created),
                "_source_system": "auth_db",
                "_ingested_at": iso(ingested_today),
            }
        )

    # CDC update: bump status on one existing user (active → suspended, rare)
    if random.random() < 0.3 and users:
        u = random.choice(users)
        if u["status"] == "active":
            u["status"] = "suspended"
            u["updated_at"] = iso(ingested_today)
            u["_ingested_at"] = iso(ingested_today)

    return users


def gen_daily_products(
    fake: Faker, day: int, existing_products: list[dict]
) -> list[dict]:
    """Returns the full updated products list. Price changes on ~10% of days."""
    products = list(existing_products)
    ingested_today = SIM_START + timedelta(days=day - 1, hours=23)

    if day > 1 and random.random() < 0.4 and products:
        p = random.choice(products)
        old_price = float(p["price"])
        p["price"] = round(old_price * random.uniform(0.85, 1.15), 2)
        p["updated_at"] = iso(ingested_today)
        p["_ingested_at"] = iso(ingested_today)

    return products


# ---------------------------------------------------------------------------
# Orchestration


def advance_one_day(fake: Faker, day: int) -> None:
    if day == 1:
        users = gen_initial_users(fake, day)
        products = gen_initial_products(fake, day)
        sessions_today = gen_daily_sessions(fake, day, users, [])
        txns = gen_daily_transactions(
            fake, day, users, products, sessions_today, []
        )
        write_csv(USERS_FILE, USERS_COLS, users)
        write_csv(PRODUCTS_FILE, PRODUCTS_COLS, products)
        write_csv(SESSIONS_FILE, SESSIONS_COLS, sessions_today)
        write_csv(TXNS_FILE, TXNS_COLS, txns)
        return

    users = gen_daily_users(fake, day, read_csv(USERS_FILE))
    products = gen_daily_products(fake, day, read_csv(PRODUCTS_FILE))
    sessions_today = gen_daily_sessions(
        fake, day, users, read_csv(SESSIONS_FILE)
    )
    txns = gen_daily_transactions(
        fake, day, users, products, sessions_today, read_csv(TXNS_FILE)
    )
    write_csv(USERS_FILE, USERS_COLS, users)
    write_csv(PRODUCTS_FILE, PRODUCTS_COLS, products)
    append_csv(SESSIONS_FILE, SESSIONS_COLS, sessions_today)
    write_csv(TXNS_FILE, TXNS_COLS, txns)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe data/ and start over at day 1.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="How many days to advance (default 1).",
    )
    args = parser.parse_args()

    if args.reset:
        for p in [
            USERS_FILE,
            PRODUCTS_FILE,
            SESSIONS_FILE,
            TXNS_FILE,
            STATE_PATH,
        ]:
            p.unlink(missing_ok=True)

    DATA_DIR.mkdir(exist_ok=True)
    state = load_state()
    start_day = state["current_day"] + 1
    end_day = start_day + args.days - 1

    Faker.seed(SEED + state["current_day"])
    random.seed(SEED + state["current_day"])
    fake = Faker()

    for day in range(start_day, end_day + 1):
        advance_one_day(fake, day)
        state["current_day"] = day
        save_state(state)
        sim_date = (SIM_START + timedelta(days=day - 1)).date()
        n_users = sum(1 for _ in read_csv(USERS_FILE))
        n_products = sum(1 for _ in read_csv(PRODUCTS_FILE))
        n_sessions = sum(1 for _ in read_csv(SESSIONS_FILE))
        n_txns = sum(1 for _ in read_csv(TXNS_FILE))
        print(
            f"  day {day} ({sim_date})  → users={n_users}  "
            f"products={n_products}  sessions={n_sessions}  txns={n_txns}"
        )


if __name__ == "__main__":
    main()
