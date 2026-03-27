# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-27

### Breaking
- Removed MCP server dependency entirely (no more `powerbi-modeling-mcp` binary)
- Removed `connect-fabric` command (future work)
- Removed per-object TMDL export (`table export-tmdl`, `measure export-tmdl`, etc.) -- use `pbi database export-tmdl`
- Removed `model refresh` command
- Removed `security-role export-tmdl` -- use `pbi database export-tmdl`

### Added
- Direct pythonnet/.NET TOM interop (in-process, sub-second commands)
- Bundled Microsoft Analysis Services DLLs (~20MB, no external download needed)
- 2 new Claude Code skills: Diagnostics and Partitions & Expressions (7 total)
- New commands: `trace start/stop/fetch/export`, `transaction begin/commit/rollback`, `calendar list/mark`, `expression list/get/create/delete`, `partition list/create/delete/refresh`, `advanced culture list/get`
- `connections last` command to show last-used connection
- `pbi connect` now auto-installs skills (no separate `pbi skills install` needed)

### Changed
- `pbi setup` now verifies pythonnet + bundled DLLs (no longer downloads a binary)
- Architecture: Click CLI -> tom_backend/adomd_backend -> pythonnet -> .NET TOM (in-process)
- All 7 skills updated to reflect v2 commands and architecture
- README rewritten for v2 architecture

### Removed
- MCP client/server architecture
- Binary manager and auto-download from VS Code Marketplace
- `$PBI_MCP_BINARY` environment variable
- `~/.pbi-cli/bin/` binary directory

## [1.0.6] - 2026-03-26

### Fixed
- Use server-assigned connection name for subsequent commands (fixes "connection not found" mismatch)

## [1.0.5] - 2026-03-26

### Fixed
- Auto-reconnect to saved connection on each command (each invocation starts a fresh MCP server)

## [1.0.4] - 2026-03-26

### Fixed
- Commands now auto-resolve last-used connection from store (no --connection flag needed)

## [1.0.3] - 2026-03-26

### Added
- Support Microsoft Store version of Power BI Desktop for port auto-discovery

### Fixed
- UTF-16 LE encoding when reading Power BI port file
- Updated all 5 skills, error messages, and docs to reflect new install flow

## [1.0.2] - 2026-03-26

### Fixed
- Separate README for GitHub (Mermaid diagrams) and PyPI (text art)

## [1.0.1] - 2026-03-26

### Fixed
- README SVG header and diagrams now render correctly on PyPI

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
