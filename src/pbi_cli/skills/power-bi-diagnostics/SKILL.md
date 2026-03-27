---
name: Power BI Diagnostics
description: Troubleshoot Power BI model performance, trace query execution, manage caches, and verify the pbi-cli environment. Use when the user mentions slow queries, performance issues, tracing, profiling, or setup problems.
tools: pbi-cli
---

# Power BI Diagnostics Skill

Troubleshoot performance, trace queries, and verify the pbi-cli environment.

## Prerequisites

```bash
pipx install pbi-cli-tool
pbi connect    # Auto-detects Power BI Desktop and installs skills
```

## Environment Check

```bash
# Verify pythonnet and .NET DLLs are installed
pbi setup

# Show detailed environment info (version, DLL paths, pythonnet status)
pbi setup --info
pbi --json setup --info

# Check CLI version
pbi --version
```

## Model Health Check

```bash
# Quick model overview
pbi --json model get

# Object counts (tables, columns, measures, relationships, partitions)
pbi --json model stats

# List all tables with column/measure counts
pbi --json table list
```

## Query Tracing

Capture diagnostic events during DAX query execution:

```bash
# Start a trace
pbi trace start

# Execute the query you want to profile
pbi dax execute "EVALUATE SUMMARIZECOLUMNS(Products[Category], \"Total\", SUM(Sales[Amount]))"

# Stop the trace
pbi trace stop

# Fetch captured trace events
pbi --json trace fetch

# Export trace events to a file
pbi trace export ./trace-output.json
```

## Cache Management

```bash
# Clear the formula engine cache (do this before benchmarking)
pbi dax clear-cache
```

## Connection Diagnostics

```bash
# List all saved connections
pbi connections list
pbi --json connections list

# Show the last-used connection
pbi connections last

# Reconnect to a specific data source
pbi connect -d localhost:54321

# Disconnect
pbi disconnect
```

## Workflow: Profile a Slow Query

```bash
# 1. Clear cache for a clean benchmark
pbi dax clear-cache

# 2. Start tracing
pbi trace start

# 3. Run the slow query
pbi dax execute "EVALUATE SUMMARIZECOLUMNS(Products[Category], \"Total\", SUM(Sales[Amount]))" --timeout 300

# 4. Stop tracing
pbi trace stop

# 5. Export trace for analysis
pbi trace export ./slow-query-trace.json

# 6. Review trace events
pbi --json trace fetch
```

## Workflow: Model Health Audit

```bash
# 1. Model overview
pbi --json model get
pbi --json model stats

# 2. Check table sizes and structure
pbi --json table list

# 3. Review relationships
pbi --json relationship list

# 4. Check security roles
pbi --json security-role list

# 5. Export full model for offline review
pbi database export-tmdl ./audit-export/
```

## Best Practices

- Clear cache before benchmarking: `pbi dax clear-cache`
- Use `--timeout` for long-running queries to avoid premature cancellation
- Export traces to files for sharing with teammates
- Run `pbi setup --info` first when troubleshooting environment issues
- Use `--json` output for automated monitoring scripts
- Use `pbi repl` for interactive debugging sessions with persistent connection
