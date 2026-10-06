# Motor Claims Frequency Pipeline

A small, tested data pipeline that turns 678k raw motor insurance policies into
claim-frequency KPI tables, the first building block of motor pricing.

![tests](https://github.com/YOUR-USERNAME/motor-claims-pipeline/actions/workflows/ci.yml/badge.svg)

## Why I built it

I work in insurance operations, where I see every day how policy, case and
supplier data feed decisions. I wanted to show the same thinking at the pricing
end: take raw policy data, check its quality, clean it with documented business
rules, and produce reliable KPIs that a pricing or underwriting team could use.

## What it does

```
extract.py   ->   transform.py        ->   load.py           ->   outputs/*.csv
download raw      quality checks,          SQLite database,      KPI tables for
policy data       cleaning rules,          indexed; SQL KPI      Power BI / Excel
                  rating bands             queries
```

- **Python (pandas)** for extraction and transformation
- **SQL (SQLite)** for storage and KPI queries (`sql/kpi_queries.sql`)
- **pytest** unit tests for every cleaning rule (`tests/`)
- **GitHub Actions CI** runs the tests automatically on every push

## Data

`freMTPL2freq` from the CASdatasets R package: 677,991 French motor
third-party liability policies with exposure (years on cover), claim counts
and rating factors (driver age, vehicle age, bonus-malus, area, region).

## Data quality decisions

| Issue found | Rows | Decision | Reason |
|---|---|---|---|
| Exposure over 1 year | 1,224 | Cap at 1.0 | A policy year cannot exceed one year |
| More than 4 claims on one policy | 8 | Cap at 4 | Likely errors; would distort averages |
| Vehicle age over 30 | 1,116 | Cap at 30 | Values like 100 are not realistic |
| Driver age over 90 | 401 | Cap at 90 | Very small, unreliable group |
| Duplicate policy IDs / zero exposure | 0 | Remove if present | Checked on every run |

## Results

Portfolio claim frequency: **0.074 claims per exposure year** (26,405 claims over 358,343 years).

| Driver age | Claim frequency |
|---|---|
| 18-25 | 0.148 |
| 26-35 | 0.075 |
| 36-50 | 0.073 |
| 51-65 | 0.068 |
| 66+ | 0.059 |

| Bonus-malus | Claim frequency |
|---|---|
| 50 (best) | 0.051 |
| 51-75 | 0.092 |
| 76-100 | 0.129 |
| 100+ (worst) | 0.352 |

Area (A = rural to F = dense urban): frequency rises from 0.054 in A to about 0.096 in E/F.

## What I found

Claim frequency is highest for 18–25 year olds (14.8 per 100 policy-years). It roughly halves for 26–35 and 36–50, which are close enough (7.5 vs 7.3) to group into one rating band. It falls further for 51–65 (6.8) and 66+ (5.9).

Vehicle age: Frequency rises slightly from new cars (7.3) to a peak at 6–10 years (8.1), then drops for cars over 11 years (6.8). A likely explanation is mileage: older cars are often second cars or used for shorter trips, so they spend less time on the road and have fewer chances to cause third-party accidents. The dataset has no mileage field, so this would need testing. Vehicle age may also overlap with driver age, which a GLM could separate out.

## How to run

```bash
pip install -r requirements.txt
python run_pipeline.py     # ~30 seconds first time (downloads data)
pytest -v                  # runs the tests
```



