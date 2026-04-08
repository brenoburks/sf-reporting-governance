#!/usr/bin/env python3
"""
Shared governance configuration — single source of truth for risk weights and bands.

Tuning these values adjusts scoring across all framework scripts.
"""

# Tunable weights applied per dependency type (governance knobs)
TYPE_WEIGHTS = {
    "column": 1,         # field shown in report output
    "filter_column": 4,  # field used in filtering logic
    "grouping": 3,       # field used in grouping logic
}

# Multipliers used by field-level risk scoring (reportRiskScoring.py)
REPORT_COUNT_WEIGHT = 10   # each distinct report referencing the field
INSTANCE_WEIGHT = 1        # each occurrence (after TYPE_WEIGHTS applied)

# Risk bands at different aggregation levels.
# Thresholds are intentionally different because object-level scores
# aggregate across many fields, producing higher totals.
FIELD_RISK_BANDS = [(120, "Critical"), (70, "High"), (30, "Medium")]
OBJECT_RISK_BANDS = [(300, "Critical"), (150, "High"), (60, "Medium")]
REPORT_RISK_BANDS = [(120, "Critical"), (70, "High"), (30, "Medium")]


def classify_risk(score: int, bands=FIELD_RISK_BANDS) -> str:
    for threshold, label in bands:
        if score >= threshold:
            return label
    return "Low"
