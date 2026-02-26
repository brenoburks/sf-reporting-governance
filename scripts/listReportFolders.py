#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def run(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-org")
    parser.add_argument("--out", default="reportFolders.json")
    parser.add_argument("--example", action="store_true")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.example:
        sample = {
            "status": 0,
            "result": {
                "metadata": [
                    {"fullName": "Operations"},
                    {"fullName": "Service"},
                    {"fullName": "Finance"},
                ]
            },
        }

        out_path.write_text(json.dumps(sample, indent=2))
        print("[OK] Example mode")
        return

    cmd = [
        "sf",
        "org",
        "list",
        "metadata",
        "--metadata-type",
        "ReportFolder",
        "--json",
    ]

    if args.target_org:
        cmd.extend(["--target-org", args.target_org])

    payload = run(cmd)

    out_path.write_text(json.dumps(payload, indent=2))
    print(f"[OK] Wrote {out_path}")


if __name__ == "__main__":
    main()