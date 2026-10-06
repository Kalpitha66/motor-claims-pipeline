"""EXTRACT: download the raw motor policy data and save it as a CSV.

Data: freMTPL2freq - 677,991 French motor third-party liability policies
(from the CASdatasets R package). It is a standard dataset used to teach
insurance pricing: each row is one policy with its exposure (years on cover)
and number of claims.
"""
from pathlib import Path
import urllib.request

import pandas as pd
import rdata

SOURCE_URL = (
    "https://raw.githubusercontent.com/dutangc/CASdatasets/"
    "master/data/freMTPL2freq.rda"
)
RAW_DIR = Path("data/raw")


def extract() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rda_file = RAW_DIR / "freMTPL2freq.rda"
    csv_file = RAW_DIR / "freMTPL2freq.csv"

    # Only download/convert once - later runs reuse the saved CSV.
    if csv_file.exists():
        print(f"[extract] Using cached file {csv_file}")
        return pd.read_csv(csv_file)

    print("[extract] Downloading raw data...")
    urllib.request.urlretrieve(SOURCE_URL, rda_file)

    print("[extract] Converting R file to CSV (takes ~30 seconds)...")
    df = rdata.read_rda(str(rda_file))["freMTPL2freq"]
    df.to_csv(csv_file, index=False)
    return pd.read_csv(csv_file)
