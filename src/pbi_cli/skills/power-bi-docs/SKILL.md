---
name: Power BI Documentation
description: Auto-document Power BI semantic models by extracting metadata, generating comprehensive documentation, and cataloging all model objects. Use when the user wants to document a Power BI model, create a data dictionary, or audit model contents.
tools: pbi-cli
---

# Power BI Documentation Skill

Generate comprehensive documentation for Power BI semantic models.

## Prerequisites

```bash
pip install pbi-cli-tool
pbi setup
pbi connect --data-source localhost:54321
```

## Quick Model Overview

```bash
pbi --json model get       # Model metadata
pbi --json model stats     # Table/measure/column counts
```

## Catalog All Objects

```bash
# Tables and their structure
pbi --json table list
pbi --json table get Sales
pbi --json table schema Sales

# All measures
pbi --json measure list

# Individual measure details
pbi --json measure get "Total Revenue" --table Sales

# Columns per table
pbi --json column list --table Sales
pbi --json column list --table Products

# Relationships
pbi --json relationship list

# Security roles
pbi --json security-role list

# Hierarchies
pbi --json hierarchy list --table Date

# Calculation groups
pbi --json calc-group list

# Perspectives
pbi --json perspective list

# Named expressions
pbi --json expression list
```

## Export Full Model as TMDL

```bash
pbi database export-tmdl ./model-docs/
```

This creates a human-readable text representation of the entire model.

## Workflow: Generate Model Documentation

Run these commands to gather all information needed for documentation:

```bash
# Step 1: Model overview
pbi --json model get > model-meta.json
pbi --json model stats > model-stats.json

# Step 2: All tables
pbi --json table list > tables.json

# Step 3: All measures
pbi --json measure list > measures.json

# Step 4: All relationships
pbi --json relationship list > relationships.json

# Step 5: Security roles
pbi --json security-role list > security-roles.json

# Step 6: Column details per table (loop through tables)
pbi --json column list --table Sales > columns-sales.json
pbi --json column list --table Products > columns-products.json

# Step 7: Full TMDL export
pbi database export-tmdl ./tmdl-export/
```

Then assemble these JSON files into markdown or HTML documentation.

## Workflow: Data Dictionary

For each table, extract columns and their types:

```bash
# Get schema for key tables
pbi --json table schema Sales
pbi --json table schema Products
pbi --json table schema Calendar
```

## Workflow: Measure Catalog

Create a complete measure inventory:

```bash
# List all measures with expressions
pbi --json measure list

# Export individual measure definitions as TMDL
pbi measure export-tmdl "Total Revenue" --table Sales
pbi measure export-tmdl "YTD Revenue" --table Sales
```

## Translation and Culture Management

For multi-language documentation:

```bash
# List cultures/translations
pbi --json advanced culture list
pbi --json advanced translation list

# Create culture for localization
pbi advanced culture create "fr-FR"
pbi advanced translation create --culture "fr-FR" --object "Total Sales" --translation "Ventes Totales"
```

## Best Practices

- Always use `--json` flag for machine-readable output
- Export TMDL alongside JSON for complete documentation
- Run documentation generation as part of CI/CD pipeline
- Keep documentation in version control alongside TMDL exports
- Include relationship diagrams (generate from `pbi --json relationship list`)
- Document measure business logic, not just DAX expressions
- Tag measures by business domain using display folders
