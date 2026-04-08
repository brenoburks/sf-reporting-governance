#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from governance_config import TYPE_WEIGHTS

DEFAULT_DEPS = Path("data/outputs/report_field_dependencies.csv")

def parse_args():
    p = argparse.ArgumentParser(
        description="Simulate impact for a given field reference using dependency CSV."
    )
    p.add_argument("--deps", default=str(DEFAULT_DEPS), help="Dependency CSV input path")
    p.add_argument("--field", required=True, help="Field reference to simulate, exact match")
    p.add_argument(
        "--top",
        type=int,
        default=25,
        help="Max number of report rows to print (default 25)",
    )
    return p.parse_args()

def main() -> int:
    args = parse_args()
    deps_path = Path(args.deps)
    target = args.field.strip()

    if not deps_path.exists():
        raise FileNotFoundError(f"Missing dependency CSV: {deps_path}")

    # report -> list of (dep_type, ref)
    matches_by_report = defaultdict(list)
    counts_by_type = defaultdict(int)
    weighted_instances = 0

    with deps_path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ref = row["reference"].strip()
            if ref != target:
                continue

            report = row["report"].strip()
            dep_type = row["dependency_type"].strip()

            matches_by_report[report].append(dep_type)
            counts_by_type[dep_type] += 1
            weighted_instances += TYPE_WEIGHTS.get(dep_type, 1)

    reports = sorted(matches_by_report.keys())
    report_count = len(reports)
    instance_count = sum(counts_by_type.values())

    print("\n==============================")
    print("FIELD IMPACT SIMULATION")
    print("==============================")
    print(f"Field: {target}")
    print(f"Reports affected: {report_count}")
    print(f"Dependency instances: {instance_count}")
    print(f"Weighted instances: {weighted_instances}")
    print("\nBreakdown by dependency type:")
    for t in sorted(counts_by_type.keys()):
        print(f"  - {t}: {counts_by_type[t]} (weight {TYPE_WEIGHTS.get(t, 1)})")

    if report_count == 0:
        print("\nNo matches found. Check spelling / exact reference.")
        return 0

    print("\nAffected reports (showing up to top {0}):".format(args.top))
    shown = 0
    for report in reports:
        shown += 1
        if shown > args.top:
            remaining = report_count - args.top
            print(f"  ... +{remaining} more")
            break
        types = matches_by_report[report]
        # Summarize dep types per report
        summary = ", ".join(sorted(types))
        print(f"  - {report}  [{summary}]")

    print("==============================\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())