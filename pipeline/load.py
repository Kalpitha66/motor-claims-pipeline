"""LOAD: write the clean data into a SQLite database, then run KPI queries.

SQLite is a database stored in a single file - no server to install.
"""
from pathlib import Path
import sqlite3

import pandas as pd

DB_PATH = Path("data/motor.db")
SQL_FILE = Path("sql/kpi_queries.sql")
OUTPUT_DIR = Path("outputs")


def load(df: pd.DataFrame) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("policies", conn, if_exists="replace", index=False)
        # Indexes make GROUP BY / WHERE on these columns faster.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_age ON policies (DrivAgeBand)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_area ON policies (Area)")
    print(f"[load] {len(df):,} rows written to {DB_PATH}")


def run_kpi_queries() -> None:
    """Run each query in kpi_queries.sql and save the result as a CSV
    (these CSVs can be opened directly in Power BI or Excel)."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    text = SQL_FILE.read_text()
    # Each query in the file starts with a line like: -- name: frequency_by_age
    # ([1:] skips the explanatory comments at the top of the file)
    blocks = text.split("-- name:")[1:]
    with sqlite3.connect(DB_PATH) as conn:
        for block in blocks:
            name, query = block.split("\n", 1)
            result = pd.read_sql_query(query, conn)
            out = OUTPUT_DIR / f"{name.strip()}.csv"
            result.to_csv(out, index=False)
            print(f"[kpi] {out}")
