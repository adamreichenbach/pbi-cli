---
name: Power BI Deployment
description: Deploy Power BI semantic models to Fabric workspaces, import and export TMDL and TMSL formats, and manage model lifecycle. Use when the user mentions deploying, publishing, migrating, or version-controlling Power BI models.
tools: pbi-cli
---

# Power BI Deployment Skill

Manage model lifecycle with TMDL export/import and Fabric workspace deployment.

## Prerequisites

```bash
pipx install pbi-cli-tool
pbi connect    # Auto-detects Power BI Desktop, downloads binary, installs skills
```

## Connecting to Targets

```bash
# Local Power BI Desktop (auto-detects port)
pbi connect

# Local with explicit port
pbi connect -d localhost:54321

# Fabric workspace (cloud)
pbi connect-fabric --workspace "Production" --model "Sales Model"

# Named connections for switching
pbi connect --name dev
pbi connect-fabric --workspace "Production" --model "Sales" --name prod
pbi connections list
```

## TMDL Export and Import

TMDL (Tabular Model Definition Language) is the text-based format for version-controlling Power BI models.

```bash
# Export entire model to TMDL folder
pbi database export-tmdl ./model-tmdl/

# Import TMDL folder into connected model
pbi database import-tmdl ./model-tmdl/

# Export individual objects
pbi model export-tmdl                              # Full model definition
pbi table export-tmdl Sales                         # Single table
pbi measure export-tmdl "Total Revenue" -t Sales    # Single measure
pbi relationship export-tmdl RelName                # Single relationship
pbi security-role export-tmdl "Readers"             # Security role
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

## Model Refresh

```bash
# Refresh entire model
pbi model refresh                        # Automatic (default)
pbi model refresh --type Full            # Full refresh
pbi model refresh --type Calculate       # Recalculate only
pbi model refresh --type DataOnly        # Data only, no recalc
pbi model refresh --type Defragment      # Defragment storage

# Refresh individual tables
pbi table refresh Sales --type Full
```

## Workflow: Version Control with Git

```bash
# 1. Export model to TMDL
pbi database export-tmdl ./model/

# 2. Commit to git
cd model/
git add .
git commit -m "feat: add new revenue measures"

# 3. Deploy to another environment
pbi connect-fabric --workspace "Staging" --model "Sales Model"
pbi database import-tmdl ./model/
```

## Workflow: Promote Dev to Production

```bash
# 1. Connect to dev and export
pbi connect --data-source localhost:54321 --name dev
pbi database export-tmdl ./staging-model/

# 2. Connect to production and import
pbi connect-fabric --workspace "Production" --model "Sales" --name prod
pbi database import-tmdl ./staging-model/

# 3. Refresh production data
pbi model refresh --type Full
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
- Use named connections (`--name`) to avoid accidental deployments to wrong environment
