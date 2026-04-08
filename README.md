# Salesforce Reporting Governance Framework

A static analysis framework for Salesforce Report metadata. It answers a question that every Salesforce team eventually faces: **"If I change this field, which reports break?"**

## The Problem

Salesforce orgs accumulate hundreds of reports over years. Reports reference fields in filters, columns, groupings, and formulas — but these dependencies are invisible. When someone proposes deprecating a field, changing a picklist, or restructuring an object, there is no built-in way to assess the blast radius across reports.

Teams discover breakage *after* deployment, when dashboards go blank or scheduled reports start failing.

## What This Framework Does

It extracts report metadata from your Salesforce org, parses the XML to identify every field dependency, and produces quantified risk scores at three levels:

1. **Field-level** — Which fields are referenced most, and in what contexts (filters carry more risk than columns)?
2. **Object-level** — Which objects have the most reporting exposure?
3. **Report-level** — Which reports are the most fragile (reference the most fields)?

The primary output is an **executive governance summary** (`governance_summary.md`) designed to support architecture reviews and change advisory boards.

## How It Works

The framework is a pipeline of Python scripts orchestrated by a single shell runner:

```text
Salesforce Org
     │
     ▼
┌─────────────────┐
│ 1. Discover     │  listReportFolders.py → listReportsByFolder.py
│    folders &    │  Enumerates all report folders and report names
│    reports      │  via Salesforce CLI
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Retrieve     │  buildReportManifest.py → retrieveReports.sh
│    metadata     │  Generates batched package.xml manifests,
│                 │  retrieves .report-meta.xml files
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Analyse      │  reportDependencyAnalysis.py
│    dependencies │  Parses XML (ElementTree) to extract every
│                 │  column, filter, and grouping reference
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. Score risk   │  reportRiskScoring.py → objectRiskRollup.py
│    & rank       │  → reportLevelRisk.py
│                 │  Applies weighted scoring model, aggregates
│                 │  at field, object, and report levels
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Generate     │  generateGovernanceReport.py
│    summary      │  Produces governance_summary.md with risk
│                 │  tables, distribution, and review prompts
└─────────────────┘
```

### Risk Scoring Model

Dependencies are weighted by how they are used — a field in a filter has more governance impact than one in a column:

| Dependency Type | Weight | Rationale |
| --- | --- | --- |
| Filter column | 4 | Removing a filtered field silently changes report results |
| Grouping | 3 | Grouping fields define report structure |
| Column | 1 | Columns are visible but lower-impact to remove |

Risk scores combine dependency weights with report count:

```text
risk_score = (reports_referencing × 10) + (weighted_instances × 1)
```

Scores are classified into bands (configurable in `scripts/governance_config.py`):

| Level | Field Threshold | Object Threshold |
| --- | --- | --- |
| Critical | >= 120 | >= 300 |
| High | >= 70 | >= 150 |
| Medium | >= 30 | >= 60 |
| Low | < 30 | < 60 |

Object thresholds are higher because object-level scores aggregate across many fields.

## Quick Start

### Prerequisites

- Python 3.9+
- [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) (`sf`)
- Access to a Salesforce org with metadata API permissions

### Try It Without a Salesforce Org

Run the framework in example mode using bundled sample report metadata:

```bash
git clone https://github.com/brenoburks/sf-reporting-governance.git
cd sf-reporting-governance
./scripts/run_framework.sh --example
```

Review the generated executive summary:

```bash
cat data/outputs/governance_summary.md
```

### Run Against a Live Org

**1. Install inside your Salesforce DX project:**

```bash
cd my-salesforce-project
mkdir -p tools
cd tools
git clone https://github.com/brenoburks/sf-reporting-governance.git
cd ..
```

Your structure should look like:

```text
my-salesforce-project/
├── force-app/
├── sfdx-project.json
└── tools/
    └── sf-reporting-governance/
```

**2. Authenticate:**

```bash
sf org login web
sf org list   # find your org alias
```

**3. Run the framework:**

```bash
DO_RETRIEVE=true ./tools/sf-reporting-governance/scripts/run_framework.sh --org <ORG_ALIAS>
```

**4. Review results:**

All outputs are written to `data/outputs/`:

| File | Description |
| --- | --- |
| `report_field_dependencies.csv` | Raw field dependencies extracted from report XML |
| `report_field_risk_scored.csv` | Field-level risk scores and bands |
| `object_risk_rollup.csv` | Object-level aggregated risk |
| `report_risk_ranked.csv` | Reports ranked by fragility |
| `governance_summary.md` | Executive summary with tables and review prompts |

The primary governance artifact is **`governance_summary.md`**.

### Simulate a Specific Field Change

To check the blast radius of modifying a single field:

```bash
python3 scripts/simulateFieldImpact.py \
  --field "Account.Industry"
```

This shows every report affected, broken down by dependency type.

## Project Structure

```text
sf-reporting-governance/
├── scripts/                     # Framework pipeline
│   ├── run_framework.sh         # Master orchestrator (start here)
│   ├── governance_config.py     # Shared weights and risk bands
│   ├── listReportFolders.py     # Step 1: discover folders
│   ├── listReportsByFolder.py   # Step 2: discover reports
│   ├── buildReportManifest.py   # Step 3: generate package.xml batches
│   ├── retrieveReports.sh       # Step 4: retrieve metadata via SF CLI
│   ├── reportDependencyAnalysis.py  # Step 5: parse XML dependencies
│   ├── reportRiskScoring.py     # Step 6a: field-level scoring
│   ├── objectRiskRollup.py      # Step 6b: object-level rollup
│   ├── reportLevelRisk.py       # Step 6c: report fragility ranking
│   ├── generateGovernanceReport.py  # Step 7: executive summary
│   └── simulateFieldImpact.py   # Ad-hoc field impact simulation
├── examples/                    # Sample report metadata for demo/CI
├── docs/                        # How-to guide
├── data/                        # Generated outputs (gitignored)
├── manifest/                    # Generated package.xml files (gitignored)
└── .github/workflows/           # CI pipeline (runs example mode on every PR)
```

## Tuning the Scoring Model

All weights and risk bands live in [`scripts/governance_config.py`](scripts/governance_config.py). Edit this single file to adjust scoring across the entire framework:

```python
# Dependency type weights
TYPE_WEIGHTS = {
    "column": 1,
    "filter_column": 4,
    "grouping": 3,
}

# Risk classification bands
FIELD_RISK_BANDS = [(120, "Critical"), (70, "High"), (30, "Medium")]
```

After tuning, re-run the framework to regenerate all outputs with the new model.

## Typical Use Cases

- **Field deprecation** — quantify which reports break before removing a field
- **Picklist changes** — assess downstream impact before modifying values
- **Object restructuring** — understand reporting exposure before schema changes
- **Architecture reviews** — present data-backed risk assessments to CAB
- **Org migrations** — inventory reporting dependencies for migration planning

## Important Notes

- This framework is **read-only** — it never modifies or deploys metadata
- Generated files (`data/outputs/`, `manifest/`, `reportFolders.json`, `allReportsFullNames.json`) should not be committed — add them to your project's `.gitignore`
- CI runs the full pipeline in example mode on every push and PR
