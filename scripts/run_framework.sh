#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/run_framework.sh --example
  ./scripts/run_framework.sh --org <ORG_ALIAS>

What it does:
  1) List report folders
  2) List report fullNames by folder
  3) Build batched package.xml manifests
  4) (Optional) Retrieve reports (org mode only; set DO_RETRIEVE=true)
  5) Dependency analysis (example uses sample XML; org mode expects retrieved metadata)
  6) Risk scoring + object rollup + report ranking
  7) Executive governance summary
  8) Impact simulation sanity check

Options:
  --example            Run end-to-end using examples/ sample inputs (no org required)
  --org <alias>        Run against a Salesforce org (requires sf auth)
Env Vars:
  DO_RETRIEVE=true     In org mode, also retrieve report metadata using generated manifests
  MANIFEST_DIR=manifest
EOF
}

MODE=""
ORG=""

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --example)
      MODE="example"
      shift
      ;;
    --org)
      MODE="org"
      ORG="${2:-}"
      if [[ -z "$ORG" ]]; then
        echo "[ERROR] --org requires an org alias"
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

MANIFEST_DIR="${MANIFEST_DIR:-manifest}"
DO_RETRIEVE="${DO_RETRIEVE:-false}"

echo "[INFO] Mode: $MODE"
[[ "$MODE" == "org" ]] && echo "[INFO] Target org: $ORG"
echo "[INFO] DO_RETRIEVE=$DO_RETRIEVE"
echo ""

if [[ "$MODE" == "example" ]]; then
  # 1) folders
  python3 scripts/listReportFolders.py --example

  # 2) reports (use the generated folders file)
  python3 scripts/listReportsByFolder.py --example --folders-json reportFolders.json

  # 3) manifests
  python3 scripts/buildReportManifest.py

  # 4) dependency analysis against sample report XML
  python3 scripts/reportDependencyAnalysis.py --example

  # 5) scoring + rollup + report ranking
  python3 scripts/reportRiskScoring.py
  python3 scripts/objectRiskRollup.py
  python3 scripts/reportLevelRisk.py

  # 6) executive governance summary
  python3 scripts/generateGovernanceReport.py

  # 7) impact simulation sanity check
  python3 scripts/simulateFieldImpact.py --field "SVMXC__Service_Order__c.SVMXC__Order_Status__c"

  echo ""
  echo "[OK] Example run complete"
  exit 0
fi

if [[ "$MODE" == "org" ]]; then
  # 1) folders
  python3 scripts/listReportFolders.py --target-org "$ORG"

  # 2) reports
  python3 scripts/listReportsByFolder.py --target-org "$ORG" --folders-json reportFolders.json

  # 3) manifests
  python3 scripts/buildReportManifest.py

  # 4) retrieve metadata (optional)
  if [[ "$DO_RETRIEVE" == "true" ]]; then
    TARGET_ORG="$ORG" MANIFEST_DIR="$MANIFEST_DIR" ./scripts/retrieveReports.sh
  else
    echo "[WARN] Skipping retrieval (set DO_RETRIEVE=true to retrieve report metadata)"
    echo "[WARN] Dependency analysis requires local report-meta.xml files to be present."
  fi

  # 5) dependency analysis against retrieved metadata
  python3 scripts/reportDependencyAnalysis.py --reports-root "force-app/main/default/reports"

  # 6) scoring + rollup + report ranking
  python3 scripts/reportRiskScoring.py
  python3 scripts/objectRiskRollup.py
  python3 scripts/reportLevelRisk.py

  # 7) executive governance summary
  python3 scripts/generateGovernanceReport.py

  echo ""
  echo "[OK] Org run complete"
  exit 0
fi

echo "[ERROR] No mode selected"
usage
exit 1