"""Tests check that each cleaning rule does what it says.

They use a tiny made-up table, so they run in about a second and need no
download. GitHub Actions runs them automatically on every push (CI).
"""
import pandas as pd
import pytest

from pipeline.transform import check_schema, clean, add_features, transform


def sample_data() -> pd.DataFrame:
    return pd.DataFrame({
        "IDpol":      [1, 2, 3, 3, 4],
        "ClaimNb":    [0, 1, 11, 11, 0],
        "Exposure":   [0.5, 1.8, 1.0, 1.0, 0.0],
        "VehPower":   [5, 6, 7, 7, 8],
        "VehAge":     [1, 100, 4, 4, 12],
        "DrivAge":    [19, 40, 99, 99, 60],
        "BonusMalus": [50, 80, 120, 120, 50],
        "VehBrand":   ["B1", "B2", "B3", "B3", "B1"],
        "VehGas":     ["Regular", "Diesel", "Diesel", "Diesel", "Regular"],
        "Area":       ["A", "B", "C", "C", "D"],
        "Density":    [50, 500, 5000, 5000, 1000],
        "Region":     ["R1", "R2", "R3", "R3", "R4"],
    })


def test_duplicates_removed():
    assert clean(sample_data())["IDpol"].is_unique


def test_exposure_capped_at_one_year():
    assert clean(sample_data())["Exposure"].max() <= 1.0


def test_zero_exposure_rows_dropped():
    assert (clean(sample_data())["Exposure"] > 0).all()


def test_claims_capped_at_four():
    assert clean(sample_data())["ClaimNb"].max() == 4


def test_unrealistic_ages_capped():
    df = clean(sample_data())
    assert df["VehAge"].max() <= 30
    assert df["DrivAge"].max() <= 90


def test_age_bands_created():
    df = add_features(clean(sample_data()))
    assert set(df["DrivAgeBand"]) <= {"18-25", "26-35", "36-50", "51-65", "66+"}
    assert "nan" not in set(df["DrivAgeBand"])


def test_missing_column_stops_pipeline():
    with pytest.raises(ValueError):
        check_schema(sample_data().drop(columns=["Exposure"]))


def test_full_transform_row_count():
    # 5 rows -> 1 duplicate removed -> 1 zero-exposure removed = 3 rows
    assert len(transform(sample_data())) == 3
