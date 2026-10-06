"""TRANSFORM: clean the raw data and add the fields a pricing analyst needs.

Every rule here is a business decision - be ready to explain each one.
"""
import pandas as pd

REQUIRED_COLUMNS = [
    "IDpol", "ClaimNb", "Exposure", "VehPower", "VehAge",
    "DrivAge", "BonusMalus", "VehBrand", "VehGas", "Area", "Density", "Region",
]


def check_schema(df: pd.DataFrame) -> None:
    """Stop the pipeline early if the source data has changed shape."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Raw data is missing columns: {sorted(missing)}")


def data_quality_report(df: pd.DataFrame) -> None:
    """Print how many rows each cleaning rule will affect."""
    checks = {
        "duplicate policy IDs": df["IDpol"].duplicated().sum(),
        "exposure over 1 year": (df["Exposure"] > 1).sum(),
        "more than 4 claims": (df["ClaimNb"] > 4).sum(),
        "vehicle age over 30": (df["VehAge"] > 30).sum(),
        "driver age over 90": (df["DrivAge"] > 90).sum(),
        "zero exposure": (df["Exposure"] <= 0).sum(),
    }
    for issue, count in checks.items():
        print(f"[quality] {issue}: {count:,} rows")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Remove exact duplicate policies.
    df = df.drop_duplicates(subset="IDpol")

    # 2. A policy year cannot be longer than 1 year -> cap exposure at 1.
    df["Exposure"] = df["Exposure"].clip(upper=1.0)

    # 3. A handful of policies show 5-16 claims; treat as data errors / outliers
    #    and cap at 4 so they don't distort average frequency.
    df["ClaimNb"] = df["ClaimNb"].clip(upper=4).astype(int)

    # 4. Unrealistic ages -> cap (vehicle age 100 is almost certainly an error).
    df["VehAge"] = df["VehAge"].clip(upper=30)
    df["DrivAge"] = df["DrivAge"].clip(upper=90)

    # 5. Drop rows with no exposure - they can't tell us anything about risk.
    df = df[df["Exposure"] > 0]
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Group continuous values into bands, the way rating tables do."""
    df = df.copy()
    df["DrivAgeBand"] = pd.cut(
        df["DrivAge"], bins=[17, 25, 35, 50, 65, 90],
        labels=["18-25", "26-35", "36-50", "51-65", "66+"],
    ).astype(str)
    df["VehAgeBand"] = pd.cut(
        df["VehAge"], bins=[-1, 2, 5, 10, 30],
        labels=["0-2", "3-5", "6-10", "11+"],
    ).astype(str)
    df["BonusMalusBand"] = pd.cut(
        df["BonusMalus"], bins=[0, 50, 75, 100, 300],
        labels=["50 (best)", "51-75", "76-100", "100+ (worst)"],
    ).astype(str)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    check_schema(df)
    data_quality_report(df)
    before = len(df)
    df = add_features(clean(df))
    print(f"[transform] {before:,} rows in -> {len(df):,} rows out")
    return df
