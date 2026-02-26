#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

DEFAULT_INPUT = Path("data/outputs/report_field_dependencies.csv")
DEFAULT_OUTPUT = Path("data/outputs/report_field_risk_scored.csv")

# Tunable weights (governance knobs)
TYPE_WEIGHTS = {
    "column": 1,         # field shown in report output
    "filter_column": 4,  # field used in filtering logic
    "grouping": 3,       # field used in grouping logic
}

# Tunable multipliers
REPORT_COUNT_WEIGHT = 10   # each distinct report referencing the field
INSTANCE_WEIGHT = 1        # each occurrence (after TYPE_WEIGHTS applied)

def classify_risk(score: int) -> str:
    # Starter bands (tune later once you have real org data)
    if score >= 120:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 30:
        return "Medium"
    return "Low"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_csv", default=str(DEFAULT_INPUT))
    parser.add_argument("--out", dest="output_csv", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing dependency CSV: {input_path}")

    # Aggregations
    field_to_reports = defaultdict(set)
    field_instance_count = defaultdict(int)
    field_weighted_instances = defaultdict(int)

    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = row["reference"].strip()
            report = row["report"].strip()
            dep_type = row["dependency_type"].strip()

            field_to_reports[ref].add(report)
            field_instance_count[ref] += 1

            w = TYPE_WEIGHTS.get(dep_type, 1)  # default weight 1 for unknown types
            field_weighted_instances[ref] += w

    rows = []
    for ref in sorted(field_to_reports.keys()):
        report_count = len(field_to_reports[ref])
        instance_count = field_instance_count[ref]
        weighted_instances = field_weighted_instances[ref]

        risk_score = (report_count * REPORT_COUNT_WEIGHT) + (weighted_instances * INSTANCE_WEIGHT)
        risk_band = classify_risk(risk_score)

        rows.append(
            {
                "reference": ref,
                "reports_referencing": report_count,
                "dependency_instances": instance_count,
                "weighted_instances": weighted_instances,
                "risk_score": risk_score,
                "risk": risk_band,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "reference",
                "reports_referencing",
                "dependency_instances",
                "weighted_instances",
                "risk_score",
                "risk",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Fields analysed: {len(rows)}")
    print(f"[OK] Wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())