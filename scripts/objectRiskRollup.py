#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from governance_config import (
    TYPE_WEIGHTS, REPORT_COUNT_WEIGHT, INSTANCE_WEIGHT,
    OBJECT_RISK_BANDS, classify_risk,
)

DEFAULT_DEPS = Path("data/outputs/report_field_dependencies.csv")
DEFAULT_OUT = Path("data/outputs/object_risk_rollup.csv")


def object_from_reference(ref: str) -> str:
    """
    Typical report reference formats:
      Object.Field
      Relationship.Field
      ns__Object__c.Field__c
    For our purposes, treat the object as everything before the last dot.
    """
    ref = (ref or "").strip()
    if "." not in ref:
        return "Unknown"
    return ref.rsplit(".", 1)[0]


def main() -> int:
    p = argparse.ArgumentParser(description="Roll up dependency risk by object using dependency CSV.")
    p.add_argument("--deps", default=str(DEFAULT_DEPS), help="Dependency CSV input path")
    p.add_argument("--out", default=str(DEFAULT_OUT), help="Output CSV path")
    args = p.parse_args()

    deps_path = Path(args.deps)
    out_path = Path(args.out)

    if not deps_path.exists():
        raise FileNotFoundError(f"Missing dependency CSV: {deps_path}")

    # Object aggregations
    obj_reports = defaultdict(set)            # object -> set(report)
    obj_instances = defaultdict(int)          # object -> raw instance count
    obj_weighted_instances = defaultdict(int) # object -> weighted instance count
    obj_fields = defaultdict(set)             # object -> set(field reference)

    with deps_path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ref = row["reference"].strip()
            report = row["report"].strip()
            dep_type = row["dependency_type"].strip()

            obj = object_from_reference(ref)
            obj_reports[obj].add(report)
            obj_instances[obj] += 1
            obj_weighted_instances[obj] += TYPE_WEIGHTS.get(dep_type, 1)
            obj_fields[obj].add(ref)

    rows = []
    for obj in sorted(obj_reports.keys()):
        report_count = len(obj_reports[obj])
        instance_count = obj_instances[obj]
        weighted_instances = obj_weighted_instances[obj]
        field_count = len(obj_fields[obj])

        risk_score = (report_count * REPORT_COUNT_WEIGHT) + (weighted_instances * INSTANCE_WEIGHT)
        risk_band = classify_risk(risk_score, OBJECT_RISK_BANDS)

        rows.append(
            {
                "object": obj,
                "reports_referencing": report_count,
                "fields_referenced": field_count,
                "dependency_instances": instance_count,
                "weighted_instances": weighted_instances,
                "risk_score": risk_score,
                "risk": risk_band,
            }
        )

    # Sort by score desc for a proper scoreboard
    rows.sort(key=lambda x: x["risk_score"], reverse=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "object",
                "reports_referencing",
                "fields_referenced",
                "dependency_instances",
                "weighted_instances",
                "risk_score",
                "risk",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] Objects analysed: {len(rows)}")
    print(f"[OK] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())