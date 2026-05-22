"""
load_raw.py

Loads CSVs from data/ into the `raw` schema of ecommerce_analytics.duckdb so dbt
sources have real tables to query. Run before `dbt run`.

This is the L in ELT — the boundary where data lands in the warehouse,
before dbt does any transformation. Keeping it separate from dbt mirrors
how Fivetran / Airbyte / Debezium would feed a real Snowflake setup.

Bronze convention: rows land byte-for-byte faithful to source. All
cleaning, normalization, and dedup happens in staging.

Usage:
    python scripts/load_raw.py
"""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DUCKDB_PATH = PROJECT_ROOT / "ecommerce_analytics.duckdb"
DATA_DIR = PROJECT_ROOT / "data"
RAW_SCHEMA = "raw"

SOURCES = {
    "raw_users": "raw_users.csv",
    "raw_products": "raw_products.csv",
    "raw_sessions": "raw_sessions.csv",
    "raw_transactions": "raw_transactions.csv",
}


def connect() -> duckdb.DuckDBPyConnection:
    """Open (or create) the project DuckDB database."""
    return duckdb.connect(str(DUCKDB_PATH))


def ensure_schema(con: duckdb.DuckDBPyConnection, schema: str) -> None:
    """Create the schema if it doesn't already exist."""
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")


def load_csv(con: duckdb.DuckDBPyConnection, table: str, csv_path: Path) -> int:
    """
    Load `csv_path` into `raw.<table>`, returning row count.

    Both CDC tables and the append-only sessions log use CREATE OR REPLACE:
    the CSV is the full current state of the upstream system. A real
    warehouse with Fivetran would do incremental MERGE; that complexity
    belongs in dbt's incremental models, not here.

    `nullstr=''` makes empty CSV cells land as SQL NULL rather than empty
    strings — important for joins on nullable columns like user_id.
    """
    full_name = f"{RAW_SCHEMA}.{table}"
    con.execute(
        f"CREATE OR REPLACE TABLE {full_name} AS "
        f"SELECT * FROM read_csv_auto(?, header=true, nullstr='')",
        [str(csv_path)],
    )
    row = con.execute(f"SELECT count(*) FROM {full_name}").fetchone()
    assert row is not None
    return row[0]


def main() -> None:
    if not DATA_DIR.exists() or not any(DATA_DIR.glob("*.csv")):
        raise SystemExit(
            "No CSVs in data/. Run `python generate.py --reset` first."
        )

    con = connect()
    ensure_schema(con, RAW_SCHEMA)

    for table, fname in SOURCES.items():
        rows = load_csv(con, table, DATA_DIR / fname)
        print(f"  raw.{table:<20} {rows:>6} rows")

    con.close()


if __name__ == "__main__":
    main()
