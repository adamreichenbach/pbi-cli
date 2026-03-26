---
name: Power BI DAX
description: Write, execute, and optimize DAX queries and measures for Power BI semantic models. Use when the user mentions DAX, Power BI calculations, querying data, or wants to analyze data in a semantic model.
tools: pbi-cli
---

# Power BI DAX Skill

Execute and validate DAX queries against connected Power BI models.

## Prerequisites

```bash
pip install pbi-cli
pbi setup
pbi connect --data-source localhost:54321
```

## Executing Queries

```bash
# Inline query
pbi dax execute "EVALUATE TOPN(10, Sales)"

# From file
pbi dax execute --file query.dax

# From stdin (piping)
cat query.dax | pbi dax execute -
echo "EVALUATE Sales" | pbi dax execute -

# With options
pbi dax execute "EVALUATE Sales" --max-rows 100
pbi dax execute "EVALUATE Sales" --metrics           # Include execution metrics
pbi dax execute "EVALUATE Sales" --metrics-only      # Metrics without data
pbi dax execute "EVALUATE Sales" --timeout 300       # Custom timeout (seconds)

# JSON output for scripting
pbi --json dax execute "EVALUATE Sales"
```

## Validating Queries

```bash
pbi dax validate "EVALUATE Sales"
pbi dax validate --file query.dax
```

## Cache Management

```bash
pbi dax clear-cache    # Clear the formula engine cache
```

## Creating Measures with DAX

```bash
# Simple aggregation
pbi measure create "Total Sales" -e "SUM(Sales[Amount])" -t Sales

# Time intelligence
pbi measure create "YTD Sales" -e "TOTALYTD(SUM(Sales[Amount]), Calendar[Date])" -t Sales

# Previous year comparison
pbi measure create "PY Sales" -e "CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Calendar[Date]))" -t Sales

# Year-over-year change
pbi measure create "YoY %" -e "DIVIDE([Total Sales] - [PY Sales], [PY Sales])" -t Sales --format-string "0.0%"
```

## Common DAX Patterns

### Explore Model Data

```bash
# List all tables
pbi dax execute "EVALUATE INFO.TABLES()"

# List columns in a table
pbi dax execute "EVALUATE INFO.COLUMNS()"

# Preview table data
pbi dax execute "EVALUATE TOPN(10, Sales)"

# Count rows
pbi dax execute "EVALUATE ROW(\"Count\", COUNTROWS(Sales))"
```

### Aggregations

```bash
# Basic sum
pbi dax execute "EVALUATE ROW(\"Total\", SUM(Sales[Amount]))"

# Group by with aggregation
pbi dax execute "EVALUATE SUMMARIZECOLUMNS(Products[Category], \"Total\", SUM(Sales[Amount]))"

# Multiple aggregations
pbi dax execute "
EVALUATE
SUMMARIZECOLUMNS(
    Products[Category],
    \"Total Sales\", SUM(Sales[Amount]),
    \"Avg Price\", AVERAGE(Sales[UnitPrice]),
    \"Count\", COUNTROWS(Sales)
)
"
```

### Filtering

```bash
# CALCULATE with filter
pbi dax execute "
EVALUATE
ROW(\"Online Sales\", CALCULATE(SUM(Sales[Amount]), Sales[Channel] = \"Online\"))
"

# FILTER with complex condition
pbi dax execute "
EVALUATE
FILTER(
    SUMMARIZECOLUMNS(Products[Name], \"Total\", SUM(Sales[Amount])),
    [Total] > 1000
)
"
```

### Time Intelligence

```bash
# Year-to-date
pbi dax execute "
EVALUATE
ROW(\"YTD\", TOTALYTD(SUM(Sales[Amount]), Calendar[Date]))
"

# Rolling 12 months
pbi dax execute "
EVALUATE
ROW(\"R12\", CALCULATE(
    SUM(Sales[Amount]),
    DATESINPERIOD(Calendar[Date], MAX(Calendar[Date]), -12, MONTH)
))
"
```

### Ranking

```bash
# Top products by sales
pbi dax execute "
EVALUATE
TOPN(
    10,
    ADDCOLUMNS(
        VALUES(Products[Name]),
        \"Total\", CALCULATE(SUM(Sales[Amount]))
    ),
    [Total], DESC
)
"
```

## Performance Tips

- Use `--metrics` to identify slow queries
- Use `--max-rows` to limit result sets during development
- Run `pbi dax clear-cache` before benchmarking
- Prefer `SUMMARIZECOLUMNS` over `SUMMARIZE` for grouping
- Use `CALCULATE` with simple filters instead of nested `FILTER`
- Avoid iterators (`SUMX`, `FILTER`) on large tables when aggregations suffice
