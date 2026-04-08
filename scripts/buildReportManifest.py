#!/usr/bin/env python3
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

BATCH_SIZE = 150
API_VERSION = "66.0"

INPUT = Path("allReportsFullNames.json")
OUT_DIR = Path("manifest")


def build_package(report_names):
    members_xml = "\n".join([f"    <members>{escape(r)}</members>" for r in report_names])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <types>
{members_xml}
    <name>Report</name>
  </types>
  <types>
    <members>*</members>
    <name>ReportFolder</name>
  </types>
  <version>{API_VERSION}</version>
</Package>
"""


def main():
    if not INPUT.exists():
        raise FileNotFoundError("Missing allReportsFullNames.json")

    reports = json.loads(INPUT.read_text())

    if not reports:
        raise ValueError("Report list is empty")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_batches = math.ceil(len(reports) / BATCH_SIZE)

    print(f"Total reports: {len(reports)}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Total batches: {total_batches}")

    for i in range(total_batches):
        batch = reports[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]

        pkg_xml = build_package(batch)
        out_file = OUT_DIR / f"package_reports_{i+1}.xml"

        out_file.write_text(pkg_xml)

        print(f"[OK] Wrote {out_file} ({len(batch)} reports)")


if __name__ == "__main__":
    main()