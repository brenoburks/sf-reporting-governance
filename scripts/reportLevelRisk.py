#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from governance_config import TYPE_WEIGHTS, REPORT_RISK_BANDS, classify_risk

DEFAULT_DEPS = Path("data/outputs/report_field_dependencies.csv")
DEFAULT_OUT = Path("data/outputs/report_risk_ranked.csv")

REPORT_INSTANCE_WEIGHT = 2
FIELD_DIVERSITY_WEIGHT = 8


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate report-level risk ranking.")
    parser.add_argument("--deps", default=str(DEFAULT_DEPS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    deps_path = Path(args.deps)
    out_path = Path(args.out)

    if not deps_path.exists():
        raise FileNotFoundError(f"Missing dependency CSV: {deps_path}")

    report_fields = defaultdict(set)
    report_instances = defaultdict(int)
    report_weighted_instances = defaultdict(int)

    with deps_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report = row["report"].strip()
            ref = row["reference"].strip()
            dep_type = row["dependency_type"].strip()

            report_fields[report].add(ref)
            report_instances[report] += 1
            report_weighted_instances[report] += TYPE_WEIGHTS.get(dep_type, 1)

    rows = []

    for report in sorted(report_fields.keys()):
        field_count = len(report_fields[report])
        instance_count = report_instances[report]
        weighted_instances = report_weighted_instances[report]

        risk_score = (
            (weighted_instances * REPORT_INSTANCE_WEIGHT)
            + (field_count * FIELD_DIVERSITY_WEIGHT)
        )

        risk_band = classify_risk(risk_score, REPORT_RISK_BANDS)

        rows.append(
            {
                "report": report,
                "fields_referenced": field_count,
                "dependency_instances": instance_count,
                "weighted_instances": weighted_instances,
                "risk_score": risk_score,
                "risk": risk_band,
            }
        )

    # Sort highest risk first
    rows.sort(key=lambda x: x["risk_score"], reverse=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "report",
                "fields_referenced",
                "dependency_instances",
                "weighted_instances",
                "risk_score",
                "risk",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Reports analysed: {len(rows)}")
    print(f"[OK] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())