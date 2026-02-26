#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter

FIELDS_CSV = Path("data/outputs/report_field_risk_scored.csv")
OBJECTS_CSV = Path("data/outputs/object_risk_rollup.csv")
REPORTS_CSV = Path("data/outputs/report_risk_ranked.csv")
OUT_MD = Path("data/outputs/governance_summary.md")


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(val: str, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        return default


def main() -> int:
    fields = read_csv(FIELDS_CSV)
    objects = read_csv(OBJECTS_CSV)
    reports = read_csv(REPORTS_CSV)

    fields_sorted = sorted(fields, key=lambda x: to_int(x.get("risk_score", "0")), reverse=True)
    objects_sorted = sorted(objects, key=lambda x: to_int(x.get("risk_score", "0")), reverse=True)
    reports_sorted = sorted(reports, key=lambda x: to_int(x.get("risk_score", "0")), reverse=True)

    risk_distribution = Counter(f.get("risk", "Unknown") for f in fields)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    with OUT_MD.open("w", encoding="utf-8") as f:

        f.write("# Salesforce Reporting Governance Summary\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- Total fields analysed: **{len(fields)}**\n")
        f.write(f"- Total reports analysed: **{len(reports)}**\n")
        f.write(f"- Total objects analysed: **{len(objects)}**\n")
        highest_risk = fields_sorted[0].get("risk", "N/A") if fields_sorted else "N/A"
        f.write(f"- Highest field risk: **{highest_risk}**\n\n")

        # Highest Risk Field Detail
        if fields_sorted:
            top = fields_sorted[0]
            f.write("## Highest Risk Field Detail\n\n")
            f.write(f"- Field: **{top.get('reference', '')}**\n")
            f.write(f"- Reports referencing: **{top.get('reports_referencing', '')}**\n")
            f.write(
                f"- Risk score: **{top.get('risk_score', '')}** "
                f"({top.get('risk', '')})\n\n"
            )

        # Risk Distribution
        f.write("## Risk Distribution (Fields)\n\n")
        for band in ["Critical", "High", "Medium", "Low"]:
            f.write(f"- {band}: {risk_distribution.get(band, 0)}\n")
        f.write("\n")

        # Top Risk Fields
        f.write("## Top Risk Fields\n\n")
        f.write("| Field | Reports | Score | Risk |\n")
        f.write("|-------|---------|-------|------|\n")
        for row in fields_sorted[:10]:
            f.write(
                f"| {row.get('reference','')} | "
                f"{row.get('reports_referencing','')} | "
                f"{row.get('risk_score','')} | "
                f"{row.get('risk','')} |\n"
            )
        f.write("\n")

        # Top Risk Reports
        f.write("## Top Risk Reports\n\n")
        f.write("| Report | Fields | Score | Risk |\n")
        f.write("|--------|--------|-------|------|\n")
        for row in reports_sorted[:10]:
            f.write(
                f"| {row.get('report','')} | "
                f"{row.get('fields_referenced','')} | "
                f"{row.get('risk_score','')} | "
                f"{row.get('risk','')} |\n"
            )
        f.write("\n")

        # Narrative Report Fragility
        f.write("## Report Fragility Highlights\n\n")
        for row in reports_sorted[:3]:
            f.write(
                f"- **{row.get('report','')}** references {row.get('fields_referenced','0')} "
                f"distinct fields (Score {row.get('risk_score','0')}, {row.get('risk','Unknown')})\n"
            )
        f.write("\n")

        # Top Risk Objects
        f.write("## Top Risk Objects\n\n")
        f.write("| Object | Reports | Score | Risk |\n")
        f.write("|--------|---------|-------|------|\n")
        for row in objects_sorted[:10]:
            f.write(
                f"| {row.get('object','')} | "
                f"{row.get('reports_referencing','')} | "
                f"{row.get('risk_score','')} | "
                f"{row.get('risk','')} |\n"
            )
        f.write("\n")

        # Business Prompts
        f.write("## Business Review Prompts\n\n")
        f.write("- Are any High/Critical fields planned for change?\n")
        f.write("- Which of the top fragile reports support executive dashboards?\n")
        f.write("- Do these reports feed regulatory or financial reporting?\n")
        f.write("- Should mitigation plans exist before modifying underlying fields?\n")

    print(f"[OK] Wrote governance summary: {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())