#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/retrieveReports.sh                 # retrieves all manifest/package_reports_*.xml
#   TARGET_ORG=MyOrg ./scripts/retrieveReports.sh
#   BATCH=2 ./scripts/retrieveReports.sh         # retrieves only batch 2
#
# Notes:
# - Assumes you are running from repo root
# - Assumes manifest files already generated

MANIFEST_DIR="${MANIFEST_DIR:-manifest}"
TARGET_ORG="${TARGET_ORG:-}"      # optional
BATCH="${BATCH:-}"                # optional single batch number

sf_cmd() {
  if [[ -n "$TARGET_ORG" ]]; then
    sf "$@" --target-org "$TARGET_ORG"
  else
    sf "$@"
  fi
}

if [[ ! -d "$MANIFEST_DIR" ]]; then
  echo "[ERROR] Manifest directory not found: $MANIFEST_DIR"
  exit 1
fi

if [[ -n "$BATCH" ]]; then
  mf="$MANIFEST_DIR/package_reports_${BATCH}.xml"
  if [[ ! -f "$mf" ]]; then
    echo "[ERROR] Batch manifest not found: $mf"
    exit 1
  fi

  echo "[INFO] Retrieving batch $BATCH using $mf"
  sf_cmd project retrieve start --manifest "$mf"
  echo "[OK] Done"
  exit 0
fi

manifests=( "$MANIFEST_DIR"/package_reports_*.xml )

if [[ ${#manifests[@]} -eq 0 ]]; then
  echo "[ERROR] No manifests found at $MANIFEST_DIR/package_reports_*.xml"
  exit 1
fi

echo "[INFO] Found ${#manifests[@]} manifest(s)"
i=0
for mf in "${manifests[@]}"; do
  i=$((i+1))
  echo ""
  echo "[INFO] [$i/${#manifests[@]}] Retrieving: $mf"
  sf_cmd project retrieve start --manifest "$mf"
done

echo ""
echo "[OK] Retrieval complete"