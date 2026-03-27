---
name: Power BI Deployment
description: Import and export TMDL and TMSL formats, manage model lifecycle with transactions, and version-control Power BI semantic models. Use when the user mentions deploying, publishing, migrating, or version-controlling Power BI models.
tools: pbi-cli
---

# Power BI Deployment Skill

Manage model lifecycle with TMDL export/import, transactions, and version control.

## Prerequisites

```bash
pipx install pbi-cli-tool
pbi connect    # Auto-detects Power BI Desktop and installs skills
```

## Connecting to Targets

```bash
# Local Power BI Desktop (auto-detects port)
pbi connect

# Local with explicit port
pbi connect -d localhost:54321

# Named connections for switching
pbi connect -d localhost:54321 --name dev
pbi connections list
pbi connections last
pbi disconnect
```

## TMDL Export and Import

TMDL (Tabular Model Definition Language) is the text-based format for version-controlling Power BI models.

```bash
# Export entire model to TMDL folder
pbi database export-tmdl ./model-tmdl/

# Import TMDL folder into connected model
pbi database import-tmdl ./model-tmdl/
```

## TMSL Export

```bash
# Export as TMSL JSON (for SSAS/AAS compatibility)
pbi database export-tmsl
```

## Database Operations

```bash
# List databases on the connected server
pbi database list
```

## Transaction Management

Use transactions for atomic multi-step changes:

```bash
# Begin a transaction
pbi transaction begin

# Make changes
pbi measure create "New KPI" -e "SUM(Sales[Amount])" -t Sales
pbi measure create "Another KPI" -e "COUNT(Sales[OrderID])" -t Sales

# Commit all changes atomically
pbi transaction commit

# Or rollback if something went wrong
pbi transaction rollback
```

## Table Refresh

```bash
# Refresh individual tables
pbi table refresh Sales --type Full
pbi table refresh Sales --type Automatic
pbi table refresh Sales --type Calculate
pbi table refresh Sales --type DataOnly
```

## Workflow: Version Control with Git

```bash
# 1. Export model to TMDL
pbi database export-tmdl ./model/

# 2. Commit to git
cd model/
git add .
git commit -m "feat: add new revenue measures"

# 3. Later, import back into Power BI Desktop
pbi connect
pbi database import-tmdl ./model/
```

## Workflow: Inspect Model Before Deploy

```bash
# Get model metadata
pbi --json model get

# Check model statistics
pbi --json model stats

# List all objects
pbi --json table list
pbi --json measure list
pbi --json relationship list
```

## Best Practices

- Always export TMDL before making changes (backup)
- Use transactions for multi-object changes
- Test changes in dev before deploying to production
- Use `--json` for scripted deployments
- Store TMDL in git for version history
- Use named connections (`--name`) to avoid accidental changes to wrong environment
