# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-26

### Added
- Auto-discovery of running Power BI Desktop instances (`pbi connect` without `-d`)
- Auto-setup on first connect: downloads MCP binary and installs Claude Code skills automatically
- 5 Claude Code skills: Modeling, DAX, Deployment, Security, Documentation
- Skill installer (`pbi skills install/list/uninstall`)
- Interactive REPL mode (`pbi repl`) with persistent MCP connection, tab completion, command history
- Error hierarchy (`PbiCliError`, `McpToolError`, `BinaryNotFoundError`, `ConnectionRequiredError`)
- 22 command groups covering all Power BI MCP tool operations
- Binary manager: download Power BI MCP binary from VS Code Marketplace
- Connection management with named connections and persistence
- DAX query execution, validation, and cache clearing
- Full CRUD for measures, tables, columns, relationships
- Model metadata, statistics, and refresh operations
- Database import/export (TMDL and TMSL formats)
- Security role management (row-level security)
- Calculation groups, partitions, perspectives, hierarchies
- Named expressions, calendar tables, diagnostic traces
- Transaction management (begin/commit/rollback)
- Advanced operations: cultures, translations, functions, query groups
- Dual output mode: `--json` for agents, Rich tables for humans
- Named connection support with `--connection` / `-c` flag
- Binary resolution chain: env var, managed binary, VS Code extension fallback
- Cross-platform support: Windows, macOS, Linux (x64 and ARM64)
- CI/CD with GitHub Actions (lint, typecheck, test matrix)
- PyPI publishing via trusted OIDC publisher
