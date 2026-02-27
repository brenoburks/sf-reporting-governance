# How to Run the Salesforce Reporting Governance Framework

This guide provides step-by-step instructions for running the framework against a Salesforce org and generating reporting risk analysis outputs.

The framework will:

1. Retrieve Salesforce Report metadata
2. Extract field-level dependencies
3. Apply weighted risk modelling
4. Rank report fragility
5. Generate an executive governance summary

## 1. Prerequisites

* Salesforce CLI (sf) installed
* Python 3.10 or higher installed
* Access to a Salesforce org (metadata access required)
* A Salesforce DX project (contains sfdx-project.json and force-app/)

## 2. Clone This Repository

Inside your Salesforce DX project:
```
mkdir -p tools
cd tools
git clone <REPO_URL> sf-reporting-governance
```
Your structure should look like:

```
my-salesforce-project/
├── force-app/
├── sfdx-project.json
└── tools/
    └── sf-reporting-governance/
```

Return to your Salesforce project root:

```
cd ..
```

## 3. Authenticate to Salesforce

Login:

1. sf org login web
2. List available orgs:
3. sf org list

Identify the alias you want to analyse (example: UAT).

## 4. Run the Framework

From the Salesforce project root: 

```
DO_RETRIEVE=true ./tools/sf-reporting-governance/scripts/run_framework.sh --org <ORG_ALIAS>
```

Example: 
```
DO_RETRIEVE=true ./tools/sf-reporting-governance/scripts/run_framework.sh --org UAT
```

### What this does
* Discovers report folders
* Discovers reports within each folder
* Builds batched retrieval manifests
* Retrieves report metadata into force-app/main/default/reports
* Extracts field dependencies
* Generates field-level risk scoring
* Generates object-level rollups
* Generates report-level fragility ranking
* Produces an executive Markdown summary
  
## 5. Review the Results

All outputs are written to:

data/outputs/

### Key artefacts

* report_field_dependencies.csv
* report_field_risk_scored.csv
* object_risk_rollup.csv
* report_risk_ranked.csv
* governance_summary.md

Open the executive summary:

code data/outputs/governance_summary.md

This file is the primary governance artefact.

## 6. Simulate a Specific Field Change

To simulate the blast radius of modifying a specific field:

```
python3 ./tools/sf-reporting-governance/scripts/simulateFieldImpact.py \
  --field "Object__c.Field__c"
```
Example:

```
python3 ./tools/sf-reporting-governance/scripts/simulateFieldImpact.py \
  --field "SVMXC__Service_Order__c.SVMXC__Order_Status__c"
```
  
## 7. Optional: Example Mode (No Org Required)

To run the framework using sample metadata:

```
cd tools/sf-reporting-governance
./scripts/run_framework.sh --example
```

Outputs will still be written to:

data/outputs/

## 8. Important – Do Not Commit Generated Artefacts

Add the following to your Salesforce project’s .gitignore:

```
data/outputs/
manifest/
reportFolders.json
allReportsFullNames.json
*.bak
```

These files are generated locally and should not be committed.

## 9. Typical Governance Workflow

1. Run the framework.
2. Review governance_summary.md.
3. Review high-risk fields and fragile reports.
4. Quantify blast radius.
5. Present findings during architecture or CAB review.

Important Note

* The framework is an analysis engine only.
* It does not modify or deploy metadata.
