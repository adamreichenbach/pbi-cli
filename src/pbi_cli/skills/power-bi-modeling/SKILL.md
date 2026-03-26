---
name: Power BI Modeling
description: Create and manage Power BI semantic model objects including tables, columns, measures, relationships, hierarchies, and calculation groups. Use when the user mentions Power BI modeling, semantic models, or wants to create or modify model objects.
tools: pbi-cli
---

# Power BI Modeling Skill

Use pbi-cli to manage semantic model structure. Requires `pip install pbi-cli` and `pbi setup`.

## Prerequisites

```bash
pip install pbi-cli
pbi setup
pbi connect --data-source localhost:54321
```

## Tables

```bash
pbi table list                                    # List all tables
pbi table get Sales                               # Get table details
pbi table create Sales --mode Import              # Create table
pbi table delete OldTable                         # Delete table
pbi table rename OldName NewName                  # Rename table
pbi table refresh Sales --type Full               # Refresh table data
pbi table schema Sales                            # Get table schema
pbi table mark-date Calendar --date-column Date   # Mark as date table
pbi table export-tmdl Sales                       # Export as TMDL
```

## Columns

```bash
pbi column list --table Sales                                       # List columns
pbi column get Amount --table Sales                                 # Get column details
pbi column create Revenue --table Sales --data-type double --source-column Revenue  # Data column
pbi column create Profit --table Sales --expression "[Revenue]-[Cost]"              # Calculated
pbi column delete OldCol --table Sales                              # Delete column
pbi column rename OldName NewName --table Sales                     # Rename column
```

## Measures

```bash
pbi measure list                                                    # List all measures
pbi measure list --table Sales                                      # Filter by table
pbi measure get "Total Revenue" --table Sales                       # Get details
pbi measure create "Total Revenue" -e "SUM(Sales[Revenue])" -t Sales                        # Basic
pbi measure create "Revenue $" -e "SUM(Sales[Revenue])" -t Sales --format-string "\$#,##0"  # Formatted
pbi measure create "KPI" -e "..." -t Sales --folder "Key Measures" --description "Main KPI" # With metadata
pbi measure update "Total Revenue" -t Sales -e "SUMX(Sales, Sales[Qty]*Sales[Price])"       # Update expression
pbi measure delete "Old Measure" -t Sales                           # Delete
pbi measure rename "Old" "New" -t Sales                             # Rename
pbi measure move "Revenue" -t Sales --to-table Finance              # Move to another table
pbi measure export-tmdl "Total Revenue" -t Sales                    # Export as TMDL
```

## Relationships

```bash
pbi relationship list                              # List all relationships
pbi relationship get RelName                       # Get details
pbi relationship create \
  --from-table Sales --from-column ProductKey \
  --to-table Products --to-column ProductKey       # Create relationship
pbi relationship delete RelName                    # Delete
pbi relationship export-tmdl RelName               # Export as TMDL
```

## Hierarchies

```bash
pbi hierarchy list --table Date                    # List hierarchies
pbi hierarchy get "Calendar" --table Date          # Get details
pbi hierarchy create "Calendar" --table Date       # Create
pbi hierarchy add-level "Calendar" --table Date --column Year --ordinal 0   # Add level
pbi hierarchy delete "Calendar" --table Date       # Delete
```

## Calculation Groups

```bash
pbi calc-group list                                # List calculation groups
pbi calc-group create "Time Intelligence" --description "Time calcs"  # Create group
pbi calc-group items "Time Intelligence"           # List items
pbi calc-group create-item "YTD" \
  --group "Time Intelligence" \
  --expression "CALCULATE(SELECTEDMEASURE(), DATESYTD(Calendar[Date]))"  # Add item
pbi calc-group delete "Time Intelligence"          # Delete group
```

## Workflow: Create a Star Schema

```bash
# 1. Create fact table
pbi table create Sales --mode Import

# 2. Create dimension tables
pbi table create Products --mode Import
pbi table create Calendar --mode Import

# 3. Create relationships
pbi relationship create --from-table Sales --from-column ProductKey --to-table Products --to-column ProductKey
pbi relationship create --from-table Sales --from-column DateKey --to-table Calendar --to-column DateKey

# 4. Mark date table
pbi table mark-date Calendar --date-column Date

# 5. Add measures
pbi measure create "Total Revenue" -e "SUM(Sales[Revenue])" -t Sales --format-string "\$#,##0"
pbi measure create "Total Qty" -e "SUM(Sales[Quantity])" -t Sales --format-string "#,##0"
pbi measure create "Avg Price" -e "AVERAGE(Sales[UnitPrice])" -t Sales --format-string "\$#,##0.00"

# 6. Verify
pbi table list
pbi measure list
pbi relationship list
```

## Best Practices

- Use format strings for currency (`$#,##0`), percentage (`0.0%`), and integer (`#,##0`) measures
- Organize measures into display folders by business domain
- Always mark calendar tables with `mark-date` for time intelligence
- Use `--json` flag when scripting: `pbi --json measure list`
- Export TMDL for version control: `pbi table export-tmdl Sales`
