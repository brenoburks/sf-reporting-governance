#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
import xml.etree.ElementTree as ET


DEFAULT_REPORTS_ROOT = Path("force-app/main/default/reports")
DEFAULT_OUT = Path("data/outputs/report_field_dependencies.csv")
EXAMPLE_REPORTS_ROOT = Path("examples/sample_reports/reports")


def parse_args():
    p = argparse.ArgumentParser(
        description="Extract field dependencies from Salesforce *.report-meta.xml files into a CSV."
    )
    p.add_argument(
        "--reports-root",
        default=str(DEFAULT_REPORTS_ROOT),
        help="Root directory to scan for report-meta.xml files.",
    )
    p.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output CSV path.",
    )
    p.add_argument(
        "--example",
        action="store_true",
        help="Run against examples/sample_reports/reports (no Salesforce retrieval required).",
    )
    return p.parse_args()


def get_text(el: ET.Element | None) -> str:
    return el.text.strip() if el is not None and el.text else ""


def iter_report_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.report-meta.xml"))


def report_name_from_path(file_path: Path, reports_root: Path) -> str:
    # reports/<Folder>/<Report>.report-meta.xml -> <Folder>/<Report>
    rel = file_path.relative_to(reports_root).as_posix()
    return rel.replace(".report-meta.xml", "")


def main() -> int:
    args = parse_args()

    reports_root = EXAMPLE_REPORTS_ROOT if args.example else Path(args.reports_root)
    out_path = Path(args.out)

    files = iter_report_files(reports_root)
    if not files:
        raise FileNotFoundError(
            f"No *.report-meta.xml found under: {reports_root}\n"
            f"If you have not retrieved metadata yet, run with --example for training."
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []

    for f in files:
        try:
            tree = ET.parse(f)
        except ET.ParseError:
            # Skip invalid XML rather than blowing up the run
            continue

        root = tree.getroot()
        report_name = report_name_from_path(f, reports_root)

        # 1) Columns (fields used in report output)
        for col_el in root.findall(".//{*}columns"):
            col = get_text(col_el)
            if col:
                rows.append(
                    {
                        "report": report_name,
                        "dependency_type": "column",
                        "reference": col,
                        "file": str(f.as_posix()),
                    }
                )

        # 2) Filter columns (fields used in criteriaItems)
        for item in root.findall(".//{*}criteriaItems"):
            col = get_text(item.find("{*}column"))
            if col:
                rows.append(
                    {
                        "report": report_name,
                        "dependency_type": "filter_column",
                        "reference": col,
                        "file": str(f.as_posix()),
                    }
                )

        # 3) Groupings (if present, these are also dependencies)
        for grp_el in root.findall(".//{*}groupingsDown/{*}name"):
            grp = get_text(grp_el)
            if grp:
                rows.append(
                    {
                        "report": report_name,
                        "dependency_type": "grouping",
                        "reference": grp,
                        "file": str(f.as_posix()),
                    }
                )

        for grp_el in root.findall(".//{*}groupingsAcross/{*}name"):
            grp = get_text(grp_el)
            if grp:
                rows.append(
                    {
                        "report": report_name,
                        "dependency_type": "grouping",
                        "reference": grp,
                        "file": str(f.as_posix()),
                    }
                )

    # stable sort for deterministic CSV output
    rows.sort(key=lambda r: (r["report"], r["dependency_type"], r["reference"]))

    with out_path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=["report", "dependency_type", "reference", "file"])
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] Scanned: {reports_root}")
    print(f"[OK] Report files: {len(files)}")
    print(f"[OK] Rows: {len(rows)}")
    print(f"[OK] Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())