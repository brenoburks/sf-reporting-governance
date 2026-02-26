#!/usr/bin/env python3

import argparse
from pathlib import Path

DEFAULT_OUTPUT = Path("allReportsFullNames.json")
EXAMPLE_INPUT = Path("examples/sample_allReportsFullNames.json")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--example", action="store_true")
    args = parser.parse_args()

    if args.example:
        DEFAULT_OUTPUT.write_text(EXAMPLE_INPUT.read_text())
        print("[OK] Example mode")
        return

    print("Real org mode not used in training")

if __name__ == "__main__":
    main()
