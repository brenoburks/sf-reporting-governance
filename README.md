## Overview

A governance analysis framework for Salesforce Report metadata.
Designed to assess reporting dependency risk before schema, picklist, or lifecycle changes.

## Recommended Installation (Salesforce Project Tooling Model)

Clone this repository inside your Salesforce DX project under a `tools/` directory:

cd my-salesforce-project
mkdir -p tools
cd tools
git clone https://github.com/<your-org>/sf-reporting-governance.git
Your structure should look like:

my-salesforce-project/
  force-app/
  sfdx-project.json
  tools/
    sf-reporting-governance/

The framework will retrieve report metadata into your project’s `force-app` directory and generate governance outputs locally.

## Running Against a Salesforce Org

Authenticate to your org:

sf org login web
Then from your Salesforce project root:

DO_RETRIEVE=true ./tools/sf-reporting-governance/scripts/run_framework.sh --org <ORG_ALIAS>
Example:

DO_RETRIEVE=true ./tools/sf-reporting-governance/scripts/run_framework.sh --org UAT

## Outputs

After execution, outputs will be generated in:

data/outputs/

Key artefacts:

- report_field_dependencies.csv
- report_field_risk_scored.csv
- object_risk_rollup.csv
- report_risk_ranked.csv
- governance_summary.md

The primary executive artefact is:

data/outputs/governance_summary.md

## Important

The following files are generated and should not be committed:

- data/outputs/*
- manifest/*
- reportFolders.json
- allReportsFullNames.json

Add them to your Salesforce project’s `.gitignore`.

## Architecture Philosophy

This framework is a portable analysis engine.

It:
- Retrieves report metadata
- Extracts field-level dependencies
- Applies weighted risk modelling
- Generates executive governance summaries

It is not intended to modify or deploy metadata.
