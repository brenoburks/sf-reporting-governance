#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def run(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def extract_fullnames(payload):
    res = payload.get("result", [])
    items = res.get("metadata") if isinstance(res, dict) else res

    if items is None:
        items = []

    names = []

    for x in items:
        if isinstance(x, dict) and x.get("fullName"):
            names.append(x["fullName"])
        elif isinstance(x, str):
            names.append(x)

    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org")
    parser.add_argument("--folders-json", default="reportFolders.json")
    parser.add_argument("--out", default="allReportsFullNames.json")
    parser.add_argument("--example", action="store_true")
    args = parser.parse_args()

    folders_path = Path(args.folders_json)
    out_path = Path(args.out)

    if args.example:
        folders_path = Path("examples/reportFolders.json")

    if not folders_path.exists():
        raise FileNotFoundError(f"Missing folders file: {folders_path}")

    folders_payload = json.loads(folders_path.read_text())
    folders = extract_fullnames(folders_payload)

    print("Folder count:", len(folders))

    all_reports = []

    for i, folder in enumerate(folders, start=1):
        print(f"[{i}/{len(folders)}] Listing reports in: {folder}")

        if args.example:
            # Training-safe simulated response
            payload = {
                "status": 0,
                "result": {
                    "metadata": [
                        {"fullName": f"{folder}/Sample_Report_A"},
                        {"fullName": f"{folder}/Sample_Report_B"},
                    ]
                },
            }
        else:
            cmd = [
                "sf",
                "org",
                "list",
                "metadata",
                "--metadata-type",
                "Report",
                "--folder",
                folder,
                "--json",
            ]

            if args.target_org:
                cmd.extend(["--target-org", args.target_org])

            payload = run(cmd)

        all_reports.extend(extract_fullnames(payload))

    # De-dupe (stable ordering)
    seen = set()
    dedup = []

    for r in all_reports:
        if r not in seen:
            seen.add(r)
            dedup.append(r)

    print("\nTotal reports found:", len(dedup))
    print("Sample:", dedup[:10])

    out_path.write_text(json.dumps(dedup, indent=2))
    print(f"\n[OK] Wrote {out_path}")


if __name__ == "__main__":
    main()