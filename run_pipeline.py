"""Run the whole pipeline: extract -> transform -> load -> KPI reports.

Usage:  python run_pipeline.py
"""
from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.load import load, run_kpi_queries


def main() -> None:
    raw = extract()
    clean = transform(raw)
    load(clean)
    run_kpi_queries()
    print("Done. KPI tables are in the outputs/ folder.")


if __name__ == "__main__":
    main()
